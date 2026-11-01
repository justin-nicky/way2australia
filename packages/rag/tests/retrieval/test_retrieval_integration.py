"""Retrieval against Docker Qdrant (Spec 005 R11).

Fake-ingests the seed corpus into a unique throwaway collection base, retrieves
under guest access, then removes only its own collections. Skipped when Qdrant is
unreachable. Never touches other collections.
"""

import asyncio
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import RuntimeSettings, load_ingestion_config
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.store import QdrantIndexStore
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.retriever import DenseRetriever
from way2australia_rag.retrieval.strategy import QdrantTimeouts

QDRANT_URL = "http://localhost:6333"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_client() -> Iterator[QdrantClient]:
    # Bounded requests: a hanging Qdrant fails within seconds (Spec 008 T1 F3).
    client = retrieval_client_factory(
        RuntimeSettings.model_validate({"QDRANT_URL": QDRANT_URL}),
        QdrantTimeouts(connect_timeout_s=5, query_timeout_s=5),
    )
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


def test_seed_corpus_retrieval_under_guest_access(live_client: QdrantClient) -> None:
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    base = f"w2a-it-ret-{uuid.uuid4().hex[:12]}"
    store = QdrantIndexStore(live_client, base, config.index_version)
    embedder = FakeEmbedder(config.embedder.fake_vector_size)
    repository = LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=Path(REPO_ROOT))
    )
    try:
        service = IngestionService(
            repository,
            GUEST_PUBLIC_POLICY,
            HeadingChunker(config.chunker.max_chunk_chars),
            embedder,
            store,
            config.embedder.batch_size,
        )
        report = asyncio.run(service.run())
        assert not report.failures
        indexed = set(report.added)
        assert indexed

        index = DenseIndex.open(live_client, base, config.index_version, embedder.info)
        access = resolve_access(
            AccessContext(role=Role.GUEST, tenant_id="way2australia")
        )
        result = DenseRetriever(index, embedder).retrieve(
            "Is coaching compulsory?", access, top_k=5
        )
        assert result.hits
        assert {h.document_id for h in result.hits} <= indexed
        assert result.collection == store.collection
        assert result.embedder_is_fake is True
    finally:
        for name in (store.collection, store.settings_collection):
            if live_client.collection_exists(name):
                live_client.delete_collection(name)
