"""Binding a lexical index to the dense index (Spec 007 R5). In-memory Qdrant,
fake embedder; never a real model and never a real collection."""

import hashlib
from pathlib import Path
from typing import Any

import pytest
from lexical_support import (
    BASE,
    COLLECTION,
    VERSION,
    build_production,
    ingest_dense,
    open_lexical,
    rewrite_settings,
)
from qdrant_client import QdrantClient
from way2australia_rag.lexical.store import (
    LexicalIndexBindingError,
    source_chunk_digest,
)
from way2australia_rag.retrieval import index as index_module
from way2australia_rag.retrieval.errors import IndexBindingError

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)


def test_chunk_identities_scroll_pages_and_hold_no_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, dense = ingest_dense()
    expected = dense.chunk_identities()
    monkeypatch.setattr(index_module, "_SCROLL_PAGE", 2)
    paged = dense.chunk_identities()
    assert sorted(paged) == sorted(expected)
    assert len(paged) == len(set(paged)) > 2
    for point, document_id, version, content_hash in paged:
        assert isinstance(version, int)
        assert document_id and content_hash and point


def test_bind_succeeds_for_a_matching_build(tmp_path: Path) -> None:
    _, dense = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    index = open_lexical(target)
    index.bind_to(dense)
    assert index.settings.source_chunk_digest == source_chunk_digest(
        dense.chunk_identities()
    )
    index.close()


def test_open_and_bind_never_write(tmp_path: Path) -> None:
    _, dense = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    before_bytes = target.read_bytes()
    before_stat = target.stat().st_mtime_ns
    index = open_lexical(target)
    index.bind_to(dense)
    index.search('"naati"', "c.tenant_id = ?", ("way2australia",), 3)
    index.close()
    assert target.read_bytes() == before_bytes
    assert target.stat().st_mtime_ns == before_stat
    assert sorted(p.name for p in tmp_path.iterdir()) == ["lex.sqlite"]


def test_bind_does_not_write_to_qdrant(tmp_path: Path) -> None:
    client, dense = ingest_dense()
    build_production(tmp_path / "lex.sqlite")
    names = {
        "upsert",
        "delete",
        "create_collection",
        "delete_collection",
        "set_payload",
    }
    called: list[str] = []

    class Spy:
        def __init__(self, inner: QdrantClient) -> None:
            self._inner = inner

        def __getattr__(self, name: str) -> Any:
            if name in names:
                called.append(name)
            return getattr(self._inner, name)

    dense._client = Spy(client)  # type: ignore[assignment]
    index = open_lexical(tmp_path / "lex.sqlite")
    index.bind_to(dense)
    index.close()
    assert called == []


@pytest.mark.parametrize(
    ("changes", "needle"),
    [
        ({"dense_identity.embedder_revision": "999"}, "embedder_revision"),
        ({"dense_identity.embedder_model_id": "other"}, "embedder_model_id"),
        ({"dense_identity.collection": "x-v1"}, "dense_identity.collection"),
        ({"dense_identity.index_version": "v7"}, "dense_identity.index_version"),
        ({"chunker_name": "recursive"}, "chunker_name"),
        ({"chunker_version": "99"}, "chunker_version"),
        ({"chunker_max_chunk_chars": 17}, "chunker_max_chunk_chars"),
        ({"hash_contract": "content-hash-v0"}, "hash_contract"),
    ],
)
def test_bind_refuses_identity_and_chunker_mismatch(
    tmp_path: Path, changes: dict, needle: str
) -> None:
    _, dense = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    rewrite_settings(target, **changes)
    index = open_lexical(target)
    with pytest.raises(LexicalIndexBindingError, match=needle) as error:
        index.bind_to(dense)
    assert "make index-lexical" in str(error.value)
    index.close()


def test_bind_refuses_chunk_set_mismatch_with_counts(tmp_path: Path) -> None:
    import sqlite3

    _, dense = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    connection = sqlite3.connect(target)
    points = [
        r[0] for r in connection.execute("SELECT point_id FROM chunks ORDER BY 1")
    ]
    with connection:
        connection.execute("DELETE FROM chunks WHERE point_id = ?", (points[0],))
        connection.execute(
            "UPDATE chunks SET content_hash = 'changed' WHERE point_id = ?",
            (points[1],),
        )
        connection.execute(
            "INSERT INTO chunks (point_id, document_id, document_version, "
            "content_hash, owner_present, payload_json) VALUES "
            "('extra', 'doc_extra', 1, 'h', 1, '{}')"
        )
        identities = connection.execute(
            "SELECT point_id, document_id, document_version, content_hash FROM chunks"
        ).fetchall()
    connection.close()
    # keep the recorded digest consistent with the tampered table so the
    # refusal comes from the digest comparison against Qdrant, not from open
    rewrite_settings(target, source_chunk_digest=source_chunk_digest(identities))
    index = open_lexical(target)
    with pytest.raises(LexicalIndexBindingError) as error:
        index.bind_to(dense)
    message = str(error.value)
    assert "only in the dense index: 1" in message
    assert "only in the lexical index: 1" in message
    assert "different document_version or content_hash: 1" in message
    assert "make index-lexical" in message
    assert isinstance(error.value, IndexBindingError)
    index.close()


def test_bind_refuses_when_qdrant_content_changed(tmp_path: Path) -> None:
    client, _ = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    # a lexical file built for a stale digest
    rewrite_settings(target, source_chunk_digest=hashlib.sha256(b"stale").hexdigest())
    _, dense = ingest_dense(client)  # same client, idempotent re-ingest
    index = open_lexical(target)
    with pytest.raises(LexicalIndexBindingError, match="chunk set"):
        index.bind_to(dense)
    index.close()


def test_collection_constants_agree() -> None:
    assert COLLECTION == f"{BASE}-{VERSION}"
