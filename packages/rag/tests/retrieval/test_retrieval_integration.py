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
from way2australia_rag.ingestion.chunker_build import build_chunker
from way2australia_rag.ingestion.config import (
    RuntimeSettings,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.ingestion.store import QdrantIndexStore
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import DenseIdentity, LexicalIdentityInput
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.retriever import DenseRetriever
from way2australia_rag.retrieval.strategy import QdrantTimeouts, load_retrieval_config

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
            build_chunker(config, FakeTokenizer()),
            embedder,
            store,
            config.embedder.batch_size,
            FakeTokenizer(),
            None,
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


def test_hybrid_with_the_fake_reranker_through_open_retrieval(
    live_client: QdrantClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Spec 011 T2: the reranking stage on Docker Qdrant, hits re-checked."""
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    base = f"w2a-t011-{uuid.uuid4().hex[:8]}"
    collection = collection_name(base, config.index_version)
    store = QdrantIndexStore(live_client, base, config.index_version)
    embedder = FakeEmbedder(config.embedder.fake_vector_size)
    tokenizer = FakeTokenizer()
    chunker = build_chunker(config, tokenizer)
    repository = LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=Path(REPO_ROOT))
    )
    try:
        service = IngestionService(
            repository,
            GUEST_PUBLIC_POLICY,
            chunker,
            embedder,
            store,
            config.embedder.batch_size,
            tokenizer,
            None,
        )
        report = asyncio.run(service.run())
        assert not report.failures
        model_id, revision = embedder_identity(config, "fake")
        directory = tmp_path / "lex"
        build_lexical_index(
            asyncio.run(production_entries(repository, chunker, tokenizer, None)),
            lexical_index_path(directory, collection),
            LexicalIdentityInput(
                collection=collection,
                index_version=config.index_version,
                dense_identity=DenseIdentity(
                    collection=collection,
                    index_version=config.index_version,
                    embedder_model_id=model_id,
                    embedder_revision=revision,
                ),
                chunker=chunker.identity,
                hash_contract=HASH_CONTRACT,
            ),
        )
        for name in ("QDRANT_API_KEY", "W2A_TENANT_ID"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.setenv("QDRANT_URL", QDRANT_URL)
        monkeypatch.setenv("QDRANT_COLLECTION_BASE", base)
        monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
        monkeypatch.chdir(tmp_path)
        reranker = FakeReranker()
        opened = open_retrieval(
            Strategy.HYBRID,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=config,
            retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
            provider="fake",
            repo_root=Path(REPO_ROOT),
            rerank=True,
            reranker_factory=lambda _config, _provider: reranker,
        )
        try:
            access = resolve_access(
                AccessContext(role=Role.GUEST, tenant_id="way2australia")
            )
            result = opened.retriever.retrieve("Is coaching compulsory?", access, 5)
        finally:
            opened.close()
        assert result.hits and result.score_kind == "cross_encoder"
        assert result.rerank is not None and result.rerank.skipped_reason is None
        assert {h.document_id for h in result.hits} <= set(report.added)
        assert reranker.load_calls == 1
    finally:
        for name in (store.collection, store.settings_collection):
            if live_client.collection_exists(name):
                live_client.delete_collection(name)
