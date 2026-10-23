"""DenseIndex read-only binding tests on in-memory Qdrant (Spec 005 R4)."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from qdrant_client import QdrantClient, models
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import EmbedderInfo, FakeEmbedder
from way2australia_rag.ingestion.settings import (
    IndexSettings,
    build_index_settings,
    collection_name,
)
from way2australia_rag.ingestion.store import (
    DENSE_VECTOR_NAME,
    SETTINGS_COLLECTION_SUFFIX,
    SETTINGS_POINT_ID,
    QdrantIndexStore,
    read_index_settings,
)
from way2australia_rag.retrieval.errors import IndexBindingError
from way2australia_rag.retrieval.index import DenseIndex

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BASE = "w2a-test"
VERSION = "v1"
COLLECTION = collection_name(BASE, VERSION)
WRITE_CALLS = (
    "create_collection",
    "recreate_collection",
    "delete_collection",
    "update_collection",
    "upsert",
    "delete",
    "set_payload",
    "overwrite_payload",
    "delete_payload",
    "clear_payload",
    "create_payload_index",
    "delete_payload_index",
    "update_vectors",
    "delete_vectors",
    "upload_points",
    "upload_collection",
    "batch_update_points",
)


def fake_info() -> EmbedderInfo:
    return FakeEmbedder().info


def make_settings(**over: Any) -> IndexSettings:
    base = build_index_settings(VERSION, fake_info(), HeadingChunker())
    return base.model_copy(update=over)


def payload(document_id: str, scope: str = "public") -> dict[str, Any]:
    return {"document_id": document_id, "access_scope": scope}


@pytest.fixture
def client() -> QdrantClient:
    c = QdrantClient(":memory:")
    QdrantIndexStore(c, BASE, VERSION).ensure_collection(make_settings())
    return c


def open_index(client: QdrantClient, info: EmbedderInfo | None = None) -> DenseIndex:
    return DenseIndex.open(client, BASE, VERSION, info or fake_info())


def test_open_succeeds_when_matching(client: QdrantClient) -> None:
    index = open_index(client)
    assert index.collection == COLLECTION
    assert index.index_version == VERSION
    assert index.settings == make_settings()


def test_chunker_and_hash_contract_not_compared(client: QdrantClient) -> None:
    other = make_settings(
        chunker_name="other", chunker_max_chunk_chars=5, hash_contract="x"
    )
    client.upsert(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        points=[
            models.PointStruct(
                id=SETTINGS_POINT_ID,
                vector=[1.0],
                payload=other.model_dump(mode="json"),
            )
        ],
    )
    assert open_index(client).settings == other


def test_missing_collection_refused() -> None:
    with pytest.raises(IndexBindingError, match="does not exist"):
        open_index(QdrantClient(":memory:"))


def test_missing_settings_collection_refused(client: QdrantClient) -> None:
    client.delete_collection(COLLECTION + SETTINGS_COLLECTION_SUFFIX)
    with pytest.raises(IndexBindingError, match="settings collection"):
        open_index(client)


def test_missing_settings_record_refused(client: QdrantClient) -> None:
    client.delete(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        points_selector=models.PointIdsList(points=[SETTINGS_POINT_ID]),
    )
    with pytest.raises(IndexBindingError, match="no index settings"):
        open_index(client)


def test_malformed_settings_refused_without_values(client: QdrantClient) -> None:
    client.set_payload(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        payload={"embedder_vector_size": "SECRET-VALUE", "stray": "SECRET-VALUE"},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexBindingError) as error:
        open_index(client)
    message = str(error.value)
    assert "embedder_vector_size" in message and "stray" in message
    assert "SECRET-VALUE" not in message


def test_foreign_settings_refused(client: QdrantClient) -> None:
    client.overwrite_payload(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        payload={"hello": "world"},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexBindingError, match="malformed or foreign"):
        open_index(client)


def test_index_version_mismatch_refused(client: QdrantClient) -> None:
    client.set_payload(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        payload={"index_version": "v9"},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexBindingError, match="index_version: recorded 'v9'"):
        open_index(client)


@pytest.mark.parametrize(
    ("settings_field", "value", "info_field"),
    [
        ("embedder_model_id", "other/model", "model_id"),
        ("embedder_revision", "rev-2", "revision"),
        ("embedder_vector_size", 99, "vector_size"),
        ("embedder_normalize", False, "normalize"),
        ("embedder_is_fake", False, "is_fake"),
    ],
)
def test_each_embedder_field_mismatch_refused(
    client: QdrantClient, settings_field: str, value: Any, info_field: str
) -> None:
    client.set_payload(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        payload={settings_field: value},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexBindingError) as error:
        open_index(client)
    assert f"{settings_field}: recorded {value!r}" in str(error.value)


def test_fake_embedder_against_real_index_refused(client: QdrantClient) -> None:
    client.set_payload(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        payload={"embedder_is_fake": False},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexBindingError, match="embedder_is_fake"):
        open_index(client)


def test_real_embedder_against_fake_index_refused(client: QdrantClient) -> None:
    real = fake_info().model_copy(update={"is_fake": False})
    with pytest.raises(IndexBindingError, match="embedder_is_fake: recorded True"):
        open_index(client, real)


def test_each_differing_field_is_named(client: QdrantClient) -> None:
    info = fake_info().model_copy(update={"model_id": "m2", "revision": "r2"})
    with pytest.raises(IndexBindingError) as error:
        open_index(client, info)
    message = str(error.value)
    assert "embedder_model_id" in message and "embedder_revision" in message


def test_missing_dense_vector_refused() -> None:
    c = QdrantClient(":memory:")
    c.create_collection(
        COLLECTION,
        vectors_config={
            "other": models.VectorParams(size=8, distance=models.Distance.COSINE)
        },
    )
    c.create_collection(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
    )
    c.upsert(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        points=[
            models.PointStruct(
                id=SETTINGS_POINT_ID,
                vector=[1.0],
                payload=make_settings().model_dump(mode="json"),
            )
        ],
    )
    with pytest.raises(IndexBindingError, match="no 'dense' vector"):
        open_index(c)


def test_wrong_size_dense_vector_refused() -> None:
    c = QdrantClient(":memory:")
    size = fake_info().vector_size
    c.create_collection(
        COLLECTION,
        vectors_config={
            DENSE_VECTOR_NAME: models.VectorParams(
                size=size + 1, distance=models.Distance.COSINE
            )
        },
    )
    c.create_collection(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
    )
    c.upsert(
        COLLECTION + SETTINGS_COLLECTION_SUFFIX,
        points=[
            models.PointStruct(
                id=SETTINGS_POINT_ID,
                vector=[1.0],
                payload=make_settings().model_dump(mode="json"),
            )
        ],
    )
    with pytest.raises(IndexBindingError, match="vector size"):
        open_index(c)


def test_read_index_settings_public_behavior(client: QdrantClient) -> None:
    assert read_index_settings(client, COLLECTION) == make_settings()
    assert read_index_settings(client, "nonexistent") is None


def seed(client: QdrantClient, rows: list[tuple[int, dict[str, Any]]]) -> None:
    size = fake_info().vector_size
    client.upsert(
        COLLECTION,
        points=[
            models.PointStruct(
                id=i,
                vector={DENSE_VECTOR_NAME: [1.0] + [0.0] * (size - 1)},
                payload=p,
            )
            for i, p in rows
        ],
    )


def scope_filter(*scopes: str) -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="access_scope", match=models.MatchAny(any=list(scopes))
            )
        ]
    )


def test_document_count_respects_filter_and_is_distinct(client: QdrantClient) -> None:
    seed(
        client,
        [
            (1, payload("a")),
            (2, payload("a")),
            (3, payload("b")),
            (4, payload("c", "staff")),
        ],
    )
    index = open_index(client)
    assert index.document_count(scope_filter("public")) == 2
    assert index.document_count(scope_filter("staff")) == 1
    assert index.document_count(scope_filter("public", "staff")) == 3
    assert index.document_count(scope_filter("admin")) == 0


def test_search_uses_filter_and_returns_payload(client: QdrantClient) -> None:
    seed(client, [(1, payload("a")), (2, payload("b", "staff"))])
    index = open_index(client)
    size = fake_info().vector_size
    hits = index.search([1.0] + [0.0] * (size - 1), scope_filter("public"), 5)
    assert [h.payload["document_id"] for h in hits if h.payload] == ["a"]
    assert hits[0].vector is None


def test_dense_index_makes_no_write_calls(client: QdrantClient) -> None:
    seed(client, [(1, payload("a"))])
    spy = MagicMock(wraps=client)
    index = DenseIndex.open(spy, BASE, VERSION, fake_info())
    size = fake_info().vector_size
    index.search([1.0] + [0.0] * (size - 1), scope_filter("public"), 3)
    index.document_count(scope_filter("public"))
    called = {name for name, *_ in (c for c in spy.method_calls)}
    assert {"query_points", "scroll"} <= called  # the spy saw real work
    assert called <= {
        "collection_exists",
        "get_collection",
        "retrieve",
        "query_points",
        "scroll",
    }
    assert not called & set(WRITE_CALLS)


def test_document_count_missing_document_id_is_a_binding_error(
    client: QdrantClient,
) -> None:
    seed(client, [(1, payload("a"))])
    index = open_index(client)
    client.delete_payload(COLLECTION, keys=["document_id"], points=[1])
    with pytest.raises(IndexBindingError, match="document_id"):
        index.document_count(models.Filter())


def test_document_count_spans_multiple_scroll_pages(
    client: QdrantClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("way2australia_rag.retrieval.index._SCROLL_PAGE", 2)
    # 9 points, 4 distinct documents, duplicates spread across several pages.
    ids = ["a", "b", "a", "c", "a", "b", "d", "c", "a"]
    seed(client, [(i + 1, payload(d)) for i, d in enumerate(ids)])
    spy = MagicMock(wraps=client)
    index = DenseIndex.open(spy, BASE, VERSION, fake_info())
    assert index.document_count(scope_filter("public")) == 4
    assert spy.scroll.call_count > 1
