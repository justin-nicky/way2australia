import asyncio
import json
import shutil
from pathlib import Path

import pytest
from way2australia_core.documents import AccessScope, ApprovalStatus
from way2australia_rag.repositories import (
    DocumentNotFoundError,
    DocumentQuery,
    DocumentRepository,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    ManifestValidationError,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_MANIFEST = REPO_ROOT / "knowledge/manifest/document_manifest.jsonl"
SEED_IDS = {
    json.loads(line)["document_id"]
    for line in SEED_MANIFEST.read_text(encoding="utf-8").splitlines()
    if line.strip()
}

integration = pytest.mark.integration


def seed_repository() -> LocalDocumentRepository:
    return LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))


@integration
def test_seed_corpus_loads_through_repository_abstraction() -> None:
    repository: DocumentRepository = seed_repository()

    documents = asyncio.run(repository.list_documents())

    assert {d.document_id for d in documents} == SEED_IDS
    assert len(documents) == len(SEED_IDS)
    assert all(d.content and len(d.content_hash) == 64 for d in documents)
    assert all(d.access_scope is AccessScope.PUBLIC for d in documents)


@integration
def test_list_order_is_stable_and_cached() -> None:
    repository = seed_repository()

    first = asyncio.run(repository.list_documents())
    second = asyncio.run(repository.list_documents())

    assert [d.document_id for d in first] == sorted(d.document_id for d in first)
    assert first == second


@integration
def test_get_document_by_id_and_version() -> None:
    repository = seed_repository()

    latest = asyncio.run(repository.get_document("business_001_overview_scope"))
    pinned = asyncio.run(repository.get_document("business_001_overview_scope", 1))

    assert latest == pinned
    assert latest.title == "Way2Australia public offering and assistant scope"
    assert not latest.content.startswith("---")


@integration
def test_get_document_missing_raises_not_found() -> None:
    repository = seed_repository()

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(repository.get_document("does_not_exist"))
    with pytest.raises(DocumentNotFoundError):
        asyncio.run(repository.get_document("business_001_overview_scope", 99))


@integration
def test_language_filter_is_data_driven_and_does_not_affect_access() -> None:
    repository = seed_repository()

    ml = asyncio.run(repository.list_documents(DocumentQuery(lote_language="ml")))
    xx = asyncio.run(repository.list_documents(DocumentQuery(lote_language="xx")))
    explicit_ml = {d.document_id for d in ml if "*" not in d.lote_languages}

    assert "language_ml_001_naati_policy" in explicit_ml
    assert all("ml" in d.lote_languages for d in ml if d.document_id in explicit_ml)
    # Only global knowledge applies to an unlisted language.
    assert xx
    assert all(d.lote_languages == ("*",) for d in xx)
    assert {d.document_id for d in xx}.isdisjoint(explicit_ml)
    assert all(d.access_scope is AccessScope.PUBLIC for d in ml + xx)


@integration
def test_query_filters_are_applied() -> None:
    repository = seed_repository()

    none_staff = asyncio.run(
        repository.list_documents(
            DocumentQuery(allowed_access_scopes=frozenset({AccessScope.STAFF}))
        )
    )
    approved = asyncio.run(
        repository.list_documents(
            DocumentQuery(approval_status=ApprovalStatus.APPROVED)
        )
    )

    assert none_staff == []
    assert len(approved) == len(SEED_IDS)


def _copy_seed(tmp_path: Path) -> Path:
    for rel in ("knowledge/schemas", "knowledge/public"):
        shutil.copytree(REPO_ROOT / rel, tmp_path / rel)
    return tmp_path


def _write_manifest(root: Path, extra: list[dict[str, object]]) -> None:
    records = [
        json.loads(line)
        for line in SEED_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    path = root / "knowledge/manifest/document_manifest.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(json.dumps(r) for r in records + extra) + "\n", encoding="utf-8"
    )


@integration
def test_documents_outside_approved_roots_are_never_loaded(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    fixture_src = REPO_ROOT / "tests/fixtures/security/poisoned_public_document.md"
    for rel in (
        "tests/fixtures/security/poisoned_public_document.md",
        "evaluation/doc.md",
        "docs/doc.md",
        "sources/raw/doc.md",
        "knowledge/releases/doc.md",
    ):
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(fixture_src, dest)
    base = json.loads(SEED_MANIFEST.read_text(encoding="utf-8").splitlines()[0])
    extra = [
        {**base, "document_id": f"outside_{i}", "path": rel}
        for i, rel in enumerate(
            (
                "tests/fixtures/security/poisoned_public_document.md",
                "evaluation/doc.md",
                "docs/doc.md",
                "sources/raw/doc.md",
                "knowledge/releases/doc.md",
                "knowledge/public/business_evil/doc.md",
            )
        )
    ]
    _write_manifest(root, extra)

    documents = asyncio.run(
        LocalDocumentRepository(LocalRepositoryConfig(repo_root=root)).list_documents()
    )

    assert {d.document_id for d in documents} == SEED_IDS


@integration
def test_repository_does_not_depend_on_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    documents = asyncio.run(seed_repository().list_documents())

    assert len(documents) == len(SEED_IDS)


def test_invalid_document_fails_load_without_leaking_paths(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    _write_manifest(root, [])
    doc = root / "knowledge/public/business/business_001_overview_scope.md"
    doc.write_text(
        doc.read_text(encoding="utf-8").replace(
            'access_scope: "public"', 'access_scope: "everyone"'
        ),
        encoding="utf-8",
    )
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))

    with pytest.raises(ManifestValidationError) as exc_info:
        asyncio.run(repository.list_documents())

    assert "business_001_overview_scope" in str(exc_info.value)
    assert "access_scope" in str(exc_info.value)
    assert str(tmp_path) not in str(exc_info.value)


def test_invalid_schema_raises_repository_error(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    _write_manifest(root, [])
    (root / "knowledge/schemas/document_metadata.schema.json").write_text(
        '{"type": 12}', encoding="utf-8"
    )
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))

    with pytest.raises(ManifestValidationError, match="schema is invalid"):
        asyncio.run(repository.list_documents())


def test_unreadable_files_do_not_leak_absolute_paths(tmp_path: Path) -> None:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=tmp_path))

    with pytest.raises(ManifestValidationError) as exc_info:
        asyncio.run(repository.list_documents())

    assert str(tmp_path) not in str(exc_info.value)
