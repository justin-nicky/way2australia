"""Opening the retrieval stack (Spec 008 R3, R5, R6).

`open_retrieval` is the one place that turns a strategy name into an opened
retriever for `make retrieve` and `make eval-retrieval`. `bm25` is opened
standalone: no embedder, no Qdrant client, no model. `hybrid` falls back to
that same path when the dense side is unavailable at open time.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.ingestion.cli import (
    ClientFactory,
    build_chunker,
    build_embedder,
)
from way2australia_rag.ingestion.config import (
    IngestionConfig,
    RuntimeSettings,
)
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.ingestion.settings import IndexSettings
from way2australia_rag.lexical.build import default_lexical_dir, lexical_index_path
from way2australia_rag.lexical.freshness import verify_fresh
from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.repositories import (
    DocumentRepository,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    build_sql_access_clause,
)
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.strategy import (
    RetrievalConfig,
    build_retriever,
    open_bound_lexical,
)

EmbedderFactory = Callable[[IngestionConfig, str], Embedder]


def open_standalone_lexical(
    settings: RuntimeSettings,
    repo_root: Path,
    expected: IndexIdentity,
    chunker: Chunker,
    repository: DocumentRepository,
) -> LexicalIndex:
    """Open the lexical file with no Qdrant client and no embedder: file identity,
    configured dense identity and chunker, then freshness against the repository.
    Any refusal closes the file and raises `LexicalIndexBindingError`."""
    directory = settings.lexical_index_dir or default_lexical_dir(repo_root)
    if not directory.is_absolute():
        directory = repo_root / directory
    lexical = LexicalIndex.open(
        lexical_index_path(directory, expected.collection),
        expected.collection,
        expected.index_version,
    )
    try:
        lexical.check_identity(expected, chunker, HASH_CONTRACT)
        verify_fresh(lexical, repository, chunker)
    except BaseException:
        lexical.close()
        raise
    return lexical


@dataclass
class OpenedRetrieval:
    """An opened retriever and what the callers report about it.

    `embedder` and `index_settings` are `None` when the run never built an
    embedder or never reached Qdrant (`bm25`)."""

    retriever: Retriever
    identity: IndexIdentity
    document_count: Callable[[ResolvedAccess], int]
    embedder: Embedder | None
    index_settings: IndexSettings | None
    lexical: LexicalIndex | None

    def close(self) -> None:
        if self.lexical is not None:
            self.lexical.close()
            self.lexical = None


def open_retrieval(
    strategy: Strategy,
    *,
    settings: RuntimeSettings,
    ingestion_config: IngestionConfig,
    retrieval_config: RetrievalConfig,
    provider: str,
    repo_root: Path,
    client_factory: ClientFactory | None = None,
    embedder_factory: EmbedderFactory = build_embedder,
    repository: DocumentRepository | None = None,
) -> OpenedRetrieval:
    """Open the stack for `strategy` (`dense`, `bm25` or `hybrid`)."""
    strategy = Strategy(strategy)
    if strategy == Strategy.BM25:
        chunker = build_chunker(ingestion_config)
        repository = repository or LocalDocumentRepository(
            LocalRepositoryConfig(repo_root=repo_root)
        )
        expected = IndexIdentity.expected(ingestion_config, settings, provider)
        lexical = open_standalone_lexical(
            settings, repo_root, expected, chunker, repository
        )

        def lexical_count(access: ResolvedAccess) -> int:
            where, params = build_sql_access_clause(access)
            return lexical.document_count(where, params)

        try:
            retriever = build_retriever(
                strategy, expected, None, None, lexical, retrieval_config
            )
        except BaseException:
            lexical.close()
            raise
        return OpenedRetrieval(retriever, expected, lexical_count, None, None, lexical)

    embedder = embedder_factory(ingestion_config, provider)  # missing extra exits here
    timeouts = retrieval_config.qdrant
    client = None
    try:
        client = (
            client_factory(settings)
            if client_factory is not None
            else retrieval_client_factory(settings, timeouts)
        )
        index = DenseIndex.open(
            client,
            settings.collection_base,
            ingestion_config.index_version,
            embedder.info,
            query_timeout_s=timeouts.query_timeout_s,
        )
        identity = IndexIdentity.from_dense(index)
        lexical = None
        if strategy == Strategy.HYBRID:
            lexical = open_bound_lexical(settings, repo_root, index)
    except RetrievalUnavailableError as error:
        if strategy != Strategy.HYBRID:
            raise
        # Hybrid only: serve BM25 from the standalone-opened lexical file.
        _close_quietly(client)
        return _open_fallback(
            error.reason,
            settings=settings,
            ingestion_config=ingestion_config,
            retrieval_config=retrieval_config,
            provider=provider,
            repo_root=repo_root,
            embedder=embedder,
            repository=repository,
        )

    def dense_count(access: ResolvedAccess) -> int:
        return index.document_count(build_access_filter(access))

    try:
        retriever = build_retriever(
            strategy, identity, index, embedder, lexical, retrieval_config
        )
    except BaseException:
        if lexical is not None:
            lexical.close()
        raise
    return OpenedRetrieval(
        retriever, identity, dense_count, embedder, index.settings, lexical
    )


def _close_quietly(client: object) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        try:
            close()
        except Exception:  # noqa: BLE001 - best effort on a failed connection
            pass


def _open_fallback(
    reason: FallbackReason,
    *,
    settings: RuntimeSettings,
    ingestion_config: IngestionConfig,
    retrieval_config: RetrievalConfig,
    provider: str,
    repo_root: Path,
    embedder: Embedder,
    repository: DocumentRepository | None,
) -> OpenedRetrieval:
    """Open-time hybrid fallback: BM25 over the standalone lexical file."""
    chunker = build_chunker(ingestion_config)
    repository = repository or LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=repo_root)
    )
    expected = IndexIdentity.expected(ingestion_config, settings, provider)
    lexical = open_standalone_lexical(
        settings, repo_root, expected, chunker, repository
    )

    def lexical_count(access: ResolvedAccess) -> int:
        where, params = build_sql_access_clause(access)
        return lexical.document_count(where, params)

    retriever = FallbackRetriever(None, BM25Retriever(expected, lexical), reason)
    return OpenedRetrieval(retriever, expected, lexical_count, embedder, None, lexical)
