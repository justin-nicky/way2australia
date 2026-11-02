"""Recursive v1 ingestion against Docker Qdrant (Spec 009 T3)."""

import asyncio
import uuid
from collections.abc import Iterator

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient, models
from test_store import make_settings  # type: ignore[import-not-found]
from way2australia_rag.ingestion.chunker_build import build_chunker, chunk_token_cap
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import load_ingestion_config
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.settings import IndexSettings
from way2australia_rag.ingestion.store import (
    SETTINGS_POINT_ID,
    QdrantIndexStore,
    read_index_settings,
)
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)

QDRANT_URL = "http://localhost:6333"
RECURSIVE = REPO_ROOT / "experiments/configs/chunking/recursive-128.yaml"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_client() -> Iterator[QdrantClient]:
    client = QdrantClient(url=QDRANT_URL, timeout=5)
    try:
        client.get_collections()
    except Exception as error:
        client.close()
        pytest.skip(
            f"Qdrant is not reachable at {QDRANT_URL} "
            f"({type(error).__name__}); run `docker compose up -d qdrant`"
        )
    yield client
    client.close()


def test_recursive_ingest_and_idempotent_rerun(live_client: QdrantClient) -> None:
    config = load_ingestion_config(RECURSIVE)
    base = f"w2a-t009-{uuid.uuid4().hex[:8]}"
    tokenizer = FakeTokenizer()
    chunker = build_chunker(config, tokenizer)
    embedder = FakeEmbedder(config.embedder.fake_vector_size)
    store = QdrantIndexStore(live_client, base, config.index_version)
    service = IngestionService(
        LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT)),
        GUEST_PUBLIC_POLICY,
        chunker,
        embedder,
        store,
        config.embedder.batch_size,
        tokenizer,
        chunk_token_cap(config),
    )
    try:
        first = asyncio.run(service.run())
        assert not first.failures
        assert len(first.added) > 0
        state = store.read_state()
        assert any(len(entry.point_ids) > 1 for entry in state.values())
        second = asyncio.run(service.run())
        assert not second.failures
        assert second.added == [] and second.updated == [] and second.deleted == []
    finally:
        for name in (store.collection, store.settings_collection):
            if live_client.collection_exists(name):
                live_client.delete_collection(name)


def test_collection_with_1_0_settings_still_binds(live_client: QdrantClient) -> None:
    base = f"w2a-t009-{uuid.uuid4().hex[:8]}"
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    version = config.index_version
    store = QdrantIndexStore(live_client, base, version)
    legacy = make_settings(index_version=version)
    legacy_payload = {
        "schema_version": "1.0",
        **{
            k: v
            for k, v in legacy.model_dump().items()
            if k not in ("schema_version", "chunker_params", "chunker_tokenizer")
        },
        "chunker_max_chunk_chars": legacy.chunker_params["max_chunk_chars"],
    }
    wanted = IndexSettings.from_stored(legacy_payload)
    store._create_collection(wanted)
    store._ensure_payload_indexes()
    if not live_client.collection_exists(store.settings_collection):
        live_client.create_collection(
            store.settings_collection,
            vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
        )
    live_client.upsert(
        store.settings_collection,
        points=[
            models.PointStruct(
                id=SETTINGS_POINT_ID,
                vector=[1.0],
                payload=legacy_payload,
            )
        ],
        wait=True,
    )
    try:
        embedder = FakeEmbedder(config.embedder.fake_vector_size)
        tokenizer = FakeTokenizer()
        service = IngestionService(
            LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT)),
            GUEST_PUBLIC_POLICY,
            HeadingChunker(),
            embedder,
            store,
            config.embedder.batch_size,
            tokenizer,
            None,
        )
        report = asyncio.run(service.run())
        assert not report.failures
        assert report.added
        recorded = read_index_settings(live_client, store.collection)
        assert recorded is not None
        assert recorded.chunker_params == {"max_chunk_chars": 2000}
        raw = live_client.retrieve(
            store.settings_collection, ids=[SETTINGS_POINT_ID], with_payload=True
        )[0].payload
        assert raw is not None
        assert raw["schema_version"] == "1.0"
    finally:
        for name in (store.collection, store.settings_collection):
            if live_client.collection_exists(name):
                live_client.delete_collection(name)
