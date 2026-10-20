import asyncio
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from way2australia_core.documents import KnowledgeDocument
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
    ManifestValidationError,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import (
    CONTENT_HASH_METADATA_FIELDS,
    HASH_CONTRACT,
    canonical_json,
    compute_body_sha256,
    compute_content_hash,
    sha256_hex,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_MANIFEST = REPO_ROOT / "knowledge/manifest/document_manifest.jsonl"

META: dict[str, Any] = {
    "document_id": "doc_a",
    "document_version": 1,
    "title": "Doc A",
    "knowledge_domain": "business_overview",
    "tenant_id": "way2australia",
    "access_scope": "public",
    "owner_user_id": None,
    "content_language": "en",
    "language_scope": "global",
    "lote_languages": ["*"],
    "source_authority": "owner_approved",
    "source_type": "owner_approved_knowledge_base",
    "source_url": None,
    "approval_status": "approved",
    "lifecycle_status": "active",
    "retrieval_enabled": True,
    "synthetic": False,
    "effective_from": None,
    "effective_to": None,
    "last_reviewed_at": "2026-10-09",
    "introduced_in_release": "seed-v1",
    "path": "knowledge/public/business/a.md",
}
BODY = "# Title\n\nLine one.\nLine two.\n"


def h(body: str = BODY, **changes: Any) -> str:
    return compute_content_hash(body, {**META, **changes})


def test_content_hash_is_stable_and_pinned() -> None:
    assert h() == h()
    assert len(h()) == 64
    # Pins the recipe: any change to fields/canonicalization must bump HASH_CONTRACT.
    assert HASH_CONTRACT == "content-hash-v1"
    # Independent re-statement of the documented recipe.
    metadata = {f: META[f] for f in CONTENT_HASH_METADATA_FIELDS}
    payload = {
        "hash_contract": "content-hash-v1",
        "body_sha256": hashlib.sha256(BODY.strip().encode("utf-8")).hexdigest(),
        "metadata": metadata,
    }
    text = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    assert h() == hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_crlf_and_lf_bodies_hash_identically() -> None:
    crlf = BODY.replace("\n", "\r\n")
    assert compute_body_sha256(crlf) == compute_body_sha256(BODY)
    assert h(crlf) == h(BODY)
    assert h("\n\n" + BODY + "  \n") == h(BODY)


def test_body_change_changes_content_hash() -> None:
    assert h(BODY + "More.") != h()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("access_scope", "staff"),
        ("lote_languages", ["ml"]),
        ("content_language", "ml"),
        ("lifecycle_status", "deprecated"),
        ("retrieval_enabled", False),
        ("synthetic", True),
        ("effective_from", "2026-01-01"),
    ],
)
def test_retrieval_affecting_metadata_changes_content_hash(
    field: str, value: Any
) -> None:
    assert h(**{field: value}) != h()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("last_reviewed_at", "2027-01-01"),
        ("path", "knowledge/public/business/moved/b.md"),
        ("introduced_in_release", "seed-v2"),
        ("document_version", 2),
        ("document_id", "doc_b"),
        ("sha256", "f" * 64),
    ],
)
def test_non_retrieval_metadata_does_not_change_content_hash(
    field: str, value: Any
) -> None:
    assert h(**{field: value}) == h()


def test_excluded_fields_are_not_in_the_hashed_list() -> None:
    excluded = {
        "document_id",
        "document_version",
        "last_reviewed_at",
        "introduced_in_release",
        "path",
        "sha256",
        "schema_version",
    }
    assert excluded.isdisjoint(CONTENT_HASH_METADATA_FIELDS)


def test_lote_languages_keep_stored_order() -> None:
    assert h(lote_languages=["ml", "ta"]) != h(lote_languages=["ta", "ml"])


def test_absent_optional_fields_hash_as_null() -> None:
    sparse = {k: v for k, v in META.items() if k not in ("source_url", "effective_to")}
    assert compute_content_hash(BODY, sparse) == h()


def test_canonical_json_is_sorted_compact_and_keeps_unicode() -> None:
    assert canonical_json({"b": "മലയാളം", "a": [1, None]}) == (
        '{"a":[1,null],"b":"മലയാളം"}'
    )


def test_seed_documents_match_manifest_hashes() -> None:
    records = [
        json.loads(line)
        for line in SEED_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 13
    for rec in records:
        raw = (REPO_ROOT / rec["path"]).read_bytes()
        body = split_frontmatter(raw.decode("utf-8"))[1]
        assert compute_body_sha256(body) == rec["body_sha256"], rec["document_id"]
        assert sha256_hex(raw) == rec["sha256"], rec["document_id"]


@pytest.mark.integration
def test_repository_content_hash_is_content_hash_v1() -> None:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(repository.list_documents())

    assert len(documents) == 13
    assert len({d.content_hash for d in documents}) == 13
    for d in documents:
        fields = {name: getattr(d, name) for name in KnowledgeDocument.model_fields}
        assert d.content_hash == compute_content_hash(d.content, fields)


def _copy_seed(tmp_path: Path) -> Path:
    for rel in ("knowledge/schemas", "knowledge/public", "knowledge/manifest"):
        shutil.copytree(REPO_ROOT / rel, tmp_path / rel)
    return tmp_path


def _load(root: Path) -> list[KnowledgeDocument]:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))
    return asyncio.run(repository.list_documents())


DOC = "knowledge/public/business/business_001_overview_scope.md"


def test_manifest_hash_mismatch_raises(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    doc = root / DOC
    doc.write_text(
        doc.read_text(encoding="utf-8") + "\nAn unreviewed edit.\n", encoding="utf-8"
    )

    with pytest.raises(ManifestValidationError) as exc_info:
        _load(root)

    message = str(exc_info.value)
    assert "business_001_overview_scope: body_sha256" in message
    assert "business_001_overview_scope: sha256" in message
    assert str(tmp_path) not in message


def test_raw_sha256_mismatch_alone_raises(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    doc = root / DOC
    doc.write_text(doc.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")

    with pytest.raises(ManifestValidationError) as exc_info:
        _load(root)

    message = str(exc_info.value)
    assert "business_001_overview_scope: sha256" in message
    assert "body_sha256" not in message


def test_moving_a_file_does_not_change_content_hash(tmp_path: Path) -> None:
    root = _copy_seed(tmp_path)
    before = {d.document_id: d.content_hash for d in _load(root)}

    new_rel = "knowledge/public/business/moved/business_001_overview_scope.md"
    (root / new_rel).parent.mkdir()
    shutil.move(root / DOC, root / new_rel)
    manifest = root / "knowledge/manifest/document_manifest.jsonl"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(DOC, new_rel), encoding="utf-8"
    )

    assert {d.document_id: d.content_hash for d in _load(root)} == before
