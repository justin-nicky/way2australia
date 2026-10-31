"""Standalone lexical open: identity, freshness and `document_count`
(Spec 008 R3, R4). No Qdrant client, no embedder, no model."""

import asyncio
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from lexical_support import (
    COLLECTION,
    VERSION,
    build_production,
    identity,
    payload,
    rewrite_settings,
)
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion import embedding
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.freshness import verify_fresh
from way2australia_rag.lexical.store import (
    REBUILD_ADVICE,
    LexicalIndex,
    LexicalIndexBindingError,
)
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_body_sha256, sha256_hex
from way2australia_rag.retrieval.access import build_sql_access_clause, resolve_access
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.opening import open_standalone_lexical

MANIFEST = "knowledge/manifest/document_manifest.jsonl"


def expected(**over: Any) -> IndexIdentity:
    info = FakeEmbedder().info
    values: dict[str, Any] = {
        "collection": COLLECTION,
        "index_version": VERSION,
        "embedder_model_id": info.model_id,
        "embedder_revision": info.revision,
        "embedder_is_fake": True,
        "source": "lexical_file",
    }
    values.update(over)
    return IndexIdentity(**values)


def settings_for(directory: Path) -> RuntimeSettings:
    return RuntimeSettings.model_validate(
        {"QDRANT_COLLECTION_BASE": "w2a-lex", "W2A_LEXICAL_INDEX_DIR": str(directory)}
    )


def copy_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "knowledge", root / "knowledge")
    return root


def repo_at(root: Path) -> LocalDocumentRepository:
    return LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))


def build_from(root: Path, directory: Path, **over: Any) -> Path:
    target = lexical_index_path(directory, COLLECTION)
    entries = asyncio.run(production_entries(repo_at(root), HeadingChunker()))
    build_lexical_index(entries, target, identity(**over))
    return target


def rewrite_document(root: Path, document_id: str) -> None:
    """Edit one document body and keep the manifest hashes valid."""
    manifest = root / MANIFEST
    lines = manifest.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        record = json.loads(line)
        if record["document_id"] == document_id:
            path = root / record["path"]
            text = path.read_text(encoding="utf-8") + "\nAn added sentence.\n"
            path.write_text(text, encoding="utf-8")
            _, body = split_frontmatter(text)
            record["sha256"] = sha256_hex(text.encode("utf-8"))
            record["body_sha256"] = compute_body_sha256(body)
        out.append(json.dumps(record, ensure_ascii=False))
    manifest.write_text("\n".join(out) + "\n", encoding="utf-8")


def remove_document(root: Path, document_id: str) -> None:
    manifest = root / MANIFEST
    kept = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if json.loads(line)["document_id"] != document_id
    ]
    manifest.write_text("\n".join(kept) + "\n", encoding="utf-8")


def first_document_id() -> str:
    first = (REPO_ROOT / MANIFEST).read_text(encoding="utf-8").splitlines()[0]
    return json.loads(first)["document_id"]


@pytest.fixture
def built(tmp_path: Path) -> tuple[Path, Path]:
    root = copy_repository(tmp_path)
    directory = tmp_path / "lex"
    build_from(root, directory)
    return root, directory


def open_it(root: Path, directory: Path, **over: Any) -> LexicalIndex:
    return open_standalone_lexical(
        settings_for(directory), root, expected(**over), HeadingChunker(), repo_at(root)
    )


def test_standalone_open_needs_no_client_and_no_embedder(
    built: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(*_a: object, **_k: object) -> None:
        raise AssertionError("must not be called")

    root, directory = built
    wanted = expected()  # built before the patches: it reads the fake's info only
    monkeypatch.setattr(QdrantClient, "__init__", boom)
    monkeypatch.setattr(embedding.FakeEmbedder, "__init__", boom)
    before = set(sys.modules)
    lexical = open_standalone_lexical(
        settings_for(directory), root, wanted, HeadingChunker(), repo_at(root)
    )
    lexical.close()
    heavy = {"torch", "sentence_transformers", "transformers"}
    assert not heavy & (set(sys.modules) - before)


@pytest.mark.parametrize(
    ("field", "change"),
    [
        ("dense_identity.collection", {"collection": "other-v1"}),
        ("dense_identity.index_version", {"index_version": "v9"}),
        ("dense_identity.embedder_model_id", {"embedder_model_id": "other/model"}),
        ("dense_identity.embedder_revision", {"embedder_revision": "r2"}),
    ],
)
def test_each_dense_identity_field_mismatch_is_refused(
    built: tuple[Path, Path], field: str, change: dict[str, str], tmp_path: Path
) -> None:
    root, directory = built
    # The file is found by the expected collection, so rewrite what the file
    # records instead of what is asked for.
    value = next(iter(change.values()))
    rewrite_settings(lexical_index_path(directory, COLLECTION), **{field: "x-" + value})
    with pytest.raises(LexicalIndexBindingError) as caught:
        open_it(root, directory)
    message = str(caught.value)
    assert field in message and REBUILD_ADVICE in message
    assert str(tmp_path) not in message and str(root) not in message


@pytest.mark.parametrize(
    "field",
    ["chunker_name", "chunker_version", "chunker_max_chunk_chars", "hash_contract"],
)
def test_chunker_and_hash_contract_mismatch_is_refused(
    built: tuple[Path, Path], field: str
) -> None:
    root, directory = built
    value: Any = 1 if field == "chunker_max_chunk_chars" else "zz"
    rewrite_settings(lexical_index_path(directory, COLLECTION), **{field: value})
    with pytest.raises(LexicalIndexBindingError, match=field):
        open_it(root, directory)


def test_missing_file_is_refused_with_advice(tmp_path: Path) -> None:
    with pytest.raises(LexicalIndexBindingError, match="make index-lexical"):
        open_it(copy_repository(tmp_path), tmp_path / "nowhere")


def test_freshness_passes_on_a_matching_copy(built: tuple[Path, Path]) -> None:
    root, directory = built
    lexical = open_it(root, directory)
    try:
        verify_fresh(lexical, repo_at(root), HeadingChunker())
        assert lexical.settings.chunk_count > 0
    finally:
        lexical.close()


def test_freshness_passes_on_the_real_corpus(tmp_path: Path) -> None:
    build_production(tmp_path / "lex.sqlite")
    lexical = LexicalIndex.open(tmp_path / "lex.sqlite", COLLECTION, VERSION)
    try:
        verify_fresh(lexical, repo_at(REPO_ROOT), HeadingChunker())
    finally:
        lexical.close()


def test_freshness_refuses_after_a_body_edit(built: tuple[Path, Path]) -> None:
    root, directory = built
    rewrite_document(root, first_document_id())
    with pytest.raises(LexicalIndexBindingError) as caught:
        open_it(root, directory)
    message = str(caught.value)
    assert "stale" in message and REBUILD_ADVICE in message
    assert "with different document_version or content_hash: 1" in message
    assert "An added sentence" not in message and str(root) not in message


def test_freshness_refuses_after_a_document_is_removed(
    built: tuple[Path, Path],
) -> None:
    root, directory = built
    remove_document(root, first_document_id())
    with pytest.raises(LexicalIndexBindingError) as caught:
        open_it(root, directory)
    message = str(caught.value)
    assert "chunks only in the repository: 0" in message
    assert "only in the lexical index: 1" in message


def test_refusal_closes_the_file(
    built: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    closed: list[bool] = []
    original = LexicalIndex.close

    def tracking(self: LexicalIndex) -> None:
        closed.append(True)
        original(self)

    monkeypatch.setattr(LexicalIndex, "close", tracking)
    root, directory = built
    rewrite_document(root, first_document_id())
    with pytest.raises(LexicalIndexBindingError):
        open_it(root, directory)
    assert closed == [True]


def test_document_count_honors_the_access_clause(tmp_path: Path) -> None:
    entries = [
        ("p1", payload("doc_a", "alpha")),
        ("p2", payload("doc_a", "beta")),
        ("p3", payload("doc_b", "gamma")),
        ("p4", payload("doc_staff", "delta", scope="staff")),
        ("p5", payload("doc_other", "eps", tenant_id="other")),
        ("p6", payload("doc_owned", "zeta", owner_user_id="u1")),
    ]
    target = tmp_path / "lex.sqlite"
    build_lexical_index(entries, target, identity())
    lexical = LexicalIndex.open(target, COLLECTION, VERSION)
    try:
        context = AccessContext(role=Role.GUEST, tenant_id="way2australia")
        access = resolve_access(context)
        where, params = build_sql_access_clause(access)
        assert lexical.document_count(where, params) == 2
        assert lexical.document_count("1 = 1", ()) == 5
    finally:
        lexical.close()
