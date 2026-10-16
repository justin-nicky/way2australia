"""QdrantIndexStore tests on in-memory Qdrant (Spec 004 R7, R9, R13)."""

from typing import Any

import pytest
from qdrant_client import QdrantClient
from test_chunking import make_document  # type: ignore[import-not-found]
from way2australia_rag.ingestion.chunking import Chunk, HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.errors import (
    IndexSettingsMismatchError,
    IngestionConfigurationError,
)
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import build_payload
from way2australia_rag.ingestion.settings import (
    IndexSettings,
    build_index_settings,
    collection_name,
)
from way2australia_rag.ingestion.store import (
    SETTINGS_POINT_ID,
    IndexPoint,
    QdrantIndexStore,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BASE = "w2a-test"
VERSION = "v1"


def make_settings(**overrides: Any) -> IndexSettings:
    base = build_index_settings(VERSION, FakeEmbedder().info, HeadingChunker())
    return base.model_copy(update=overrides)


def make_points(
    document_id: str,
    sections: list[str],
    content_hash: str = "a" * 64,
    version: int = 1,
) -> list[IndexPoint]:
    embedder = FakeEmbedder()
    document = make_document(
        "body",
        document_id=document_id,
        document_version=version,
        content_hash=content_hash,
    )
    points = []
    for position, section in enumerate(sections):
        chunk = Chunk(section_id=section, position=position, text=f"text {section}")
        points.append(
            IndexPoint(
                point_id=point_id(document_id, section, position),
                vector=embedder.embed_documents([chunk.text])[0],
                payload=build_payload(document, chunk),
            )
        )
    return points


@pytest.fixture
def client() -> QdrantClient:
    return QdrantClient(":memory:")


@pytest.fixture
def store(client: QdrantClient) -> QdrantIndexStore:
    return QdrantIndexStore(client, BASE, VERSION)


def snapshot(client: QdrantClient) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in client.get_collections().collections:
        records, _ = client.scroll(item.name, limit=1000, with_payload=True)
        out[item.name] = sorted((str(r.id), str(r.payload)) for r in records)
    return out


def test_absent_creates_both_and_writes_settings(
    client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    name = collection_name(BASE, VERSION)
    assert client.collection_exists(name)
    assert client.collection_exists(name + "-settings")
    found = client.retrieve(name + "-settings", ids=[SETTINGS_POINT_ID])
    assert len(found) == 1
    assert IndexSettings.model_validate(found[0].payload) == make_settings()
    assert client.count(name + "-settings").count == 1


def test_equal_settings_proceed(client: QdrantClient, store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    store.replace_document("doc_a", make_points("doc_a", ["main"]))
    before = snapshot(client)
    store.ensure_collection(make_settings())
    assert snapshot(client) == before


def test_differing_settings_refuse_without_writes(
    client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    store.replace_document("doc_a", make_points("doc_a", ["main"]))
    before = snapshot(client)
    with pytest.raises(IndexSettingsMismatchError, match="embedder_model_id"):
        store.ensure_collection(make_settings(embedder_model_id="other"))
    assert snapshot(client) == before


def test_non_empty_without_settings_refuses(client: QdrantClient) -> None:
    store = QdrantIndexStore(client, BASE, VERSION)
    store.ensure_collection(make_settings())
    store.replace_document("doc_a", make_points("doc_a", ["main"]))
    client.delete_collection(store.settings_collection)
    before = snapshot(client)
    with pytest.raises(IndexSettingsMismatchError, match="unknown provenance"):
        store.ensure_collection(make_settings())
    assert snapshot(client) == before
    assert not client.collection_exists(store.settings_collection)


def test_empty_without_settings_writes_them(client: QdrantClient) -> None:
    store = QdrantIndexStore(client, BASE, VERSION)
    store.ensure_collection(make_settings())
    client.delete_collection(store.settings_collection)
    store.ensure_collection(make_settings())
    found = client.retrieve(store.settings_collection, ids=[SETTINGS_POINT_ID])
    assert IndexSettings.model_validate(found[0].payload) == make_settings()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("embedder_model_id", "other-model"),
        ("embedder_revision", "2"),
        ("embedder_vector_size", 128),
        ("embedder_normalize", False),
        ("chunker_version", "2"),
        ("chunker_max_chunk_chars", 999),
        ("embedder_is_fake", False),
        ("chunker_name", "other"),
    ],
)
def test_mismatch_per_field_refuses_naming_field(
    client: QdrantClient, store: QdrantIndexStore, field: str, value: Any
) -> None:
    store.ensure_collection(make_settings())
    before = snapshot(client)
    with pytest.raises(IndexSettingsMismatchError, match=field):
        store.ensure_collection(make_settings(**{field: value}))
    assert snapshot(client) == before


def test_hash_contract_change_does_not_refuse(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    store.ensure_collection(make_settings(hash_contract="content-hash-v999"))


def test_index_version_mismatch_with_store_is_configuration_error(
    store: QdrantIndexStore,
) -> None:
    with pytest.raises(IngestionConfigurationError):
        store.ensure_collection(make_settings(index_version="v2"))


def test_read_state_round_trip(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    assert store.read_state() == {}
    a = make_points("doc_a", ["main", "other"], content_hash="a" * 64, version=2)
    b = make_points("doc_b", ["main"], content_hash="b" * 64, version=1)
    store.replace_document("doc_a", a)
    store.replace_document("doc_b", b)
    state = store.read_state()
    assert set(state) == {"doc_a", "doc_b"}
    assert state["doc_a"].document_version == 2
    assert state["doc_a"].content_hash == "a" * 64
    assert state["doc_a"].point_ids == {p.point_id for p in a}
    assert state["doc_b"].point_ids == {p.point_id for p in b}


def test_replace_shrinking_leaves_no_orphan(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    store.replace_document("doc_a", make_points("doc_a", ["s1", "s2", "s3"]))
    store.replace_document("doc_b", make_points("doc_b", ["main"]))
    assert len(store.read_state()["doc_a"].point_ids) == 3
    two = make_points("doc_a", ["s1", "s2"], content_hash="c" * 64, version=2)
    store.replace_document("doc_a", two)
    state = store.read_state()
    assert state["doc_a"].point_ids == {p.point_id for p in two}
    assert state["doc_a"].content_hash == "c" * 64
    assert len(state["doc_b"].point_ids) == 1


def test_delete_documents(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    for name in ("doc_a", "doc_b", "doc_c"):
        store.replace_document(name, make_points(name, ["main"]))
    store.delete_documents(["doc_a", "doc_c"])
    assert set(store.read_state()) == {"doc_b"}
    store.delete_documents([])
    assert set(store.read_state()) == {"doc_b"}


def test_payload_and_named_vector_stored(
    client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    points = make_points("doc_a", ["main"])
    store.replace_document("doc_a", points)
    record = client.retrieve(
        store.collection, ids=[points[0].point_id], with_payload=True, with_vectors=True
    )[0]
    assert record.payload == points[0].payload.model_dump(mode="json")
    assert isinstance(record.vector, dict)
    assert list(record.vector) == ["dense"]


def test_read_state_paginates(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    for n in range(3):
        store.replace_document(
            f"d{n}", make_points(f"d{n}", [f"s{i}" for i in range(100)])
        )
    state = store.read_state()
    assert {len(v.point_ids) for v in state.values()} == {100}
