"""QdrantIndexStore against Docker Qdrant at localhost:6333 (Spec 004 R13).

Skipped with a clear reason when Qdrant is unreachable. Uses a unique temporary
collection base and removes every collection it created.
"""

import uuid
from collections.abc import Iterator

import pytest
from qdrant_client import QdrantClient, models
from test_store import make_points, make_settings  # type: ignore[import-not-found]
from way2australia_rag.ingestion.errors import IndexSettingsMismatchError
from way2australia_rag.ingestion.settings import IndexSettings
from way2australia_rag.ingestion.store import (
    DENSE_VECTOR_NAME,
    KEYWORD_INDEX_FIELDS,
    SETTINGS_POINT_ID,
    QdrantIndexStore,
)

QDRANT_URL = "http://localhost:6333"
VERSION = "v1"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_client() -> Iterator[QdrantClient]:
    client = QdrantClient(url=QDRANT_URL, timeout=5)
    try:
        client.get_collections()
    except Exception as error:  # any connection failure means "not reachable"
        client.close()
        pytest.skip(
            f"Qdrant is not reachable at {QDRANT_URL} "
            f"({type(error).__name__}); run `docker compose up -d qdrant`"
        )
    yield client
    client.close()


@pytest.fixture
def store(live_client: QdrantClient) -> Iterator[QdrantIndexStore]:
    base = f"w2a-it-{uuid.uuid4().hex[:12]}"
    store = QdrantIndexStore(live_client, base, VERSION)
    try:
        yield store
    finally:
        for name in (store.collection, store.settings_collection):
            if live_client.collection_exists(name):
                live_client.delete_collection(name)


def test_settings_storage_and_refusal(
    live_client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    found = live_client.retrieve(store.settings_collection, ids=[SETTINGS_POINT_ID])
    assert IndexSettings.model_validate(found[0].payload) == make_settings()
    store.ensure_collection(make_settings())
    with pytest.raises(IndexSettingsMismatchError, match="chunker_version"):
        store.ensure_collection(make_settings(chunker_version="2"))
    assert live_client.collection_exists(store.collection)


def test_replace_and_delete_flows(store: QdrantIndexStore) -> None:
    store.ensure_collection(make_settings())
    store.replace_document("doc_a", make_points("doc_a", ["s1", "s2", "s3"]))
    store.replace_document("doc_b", make_points("doc_b", ["main"]))
    assert len(store.read_state()["doc_a"].point_ids) == 3
    two = make_points("doc_a", ["s1", "s2"], content_hash="c" * 64, version=2)
    store.replace_document("doc_a", two)
    state = store.read_state()
    assert state["doc_a"].point_ids == {p.point_id for p in two}
    assert state["doc_a"].document_version == 2
    store.delete_documents(["doc_a"])
    assert set(store.read_state()) == {"doc_b"}


def _keyword_indexed(client: QdrantClient, name: str) -> set[str]:
    schema = client.get_collection(name).payload_schema
    return {
        field
        for field, info in schema.items()
        if info.data_type == models.PayloadSchemaType.KEYWORD
    }


def test_collection_has_keyword_indexes_and_cosine_dense_vector(
    live_client: QdrantClient, store: QdrantIndexStore
) -> None:
    settings = make_settings()
    store.ensure_collection(settings)
    info = live_client.get_collection(store.collection)
    assert set(KEYWORD_INDEX_FIELDS) <= _keyword_indexed(live_client, store.collection)
    vectors = info.config.params.vectors
    assert isinstance(vectors, dict)
    dense = vectors[DENSE_VECTOR_NAME]
    assert dense.size == settings.embedder_vector_size
    assert dense.distance == models.Distance.COSINE


def test_empty_without_settings_recreates_dropped_indexes(
    live_client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    for field in KEYWORD_INDEX_FIELDS:
        live_client.delete_payload_index(store.collection, field)
    assert not _keyword_indexed(live_client, store.collection)
    live_client.delete_collection(store.settings_collection)
    store.ensure_collection(make_settings())
    assert set(KEYWORD_INDEX_FIELDS) <= _keyword_indexed(live_client, store.collection)
    assert live_client.collection_exists(store.settings_collection)


def test_repeated_create_payload_index_is_harmless(
    live_client: QdrantClient, store: QdrantIndexStore
) -> None:
    store.ensure_collection(make_settings())
    for field in KEYWORD_INDEX_FIELDS:
        live_client.create_payload_index(
            store.collection,
            field_name=field,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
    assert set(KEYWORD_INDEX_FIELDS) <= _keyword_indexed(live_client, store.collection)
