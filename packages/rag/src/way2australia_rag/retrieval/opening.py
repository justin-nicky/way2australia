"""Opening the retrieval stack (Spec 008 R3, R5, R6).

`open_retrieval` is the one place that turns a strategy name into an opened
retriever for `make retrieve` and `make eval-retrieval`. `bm25` is opened
standalone: no embedder, no Qdrant client, no model. `hybrid` falls back to
that same path when the dense side is unavailable at open time.
"""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol

from way2australia_rag.ingestion.chunker_build import chunker_identity_for_run
from way2australia_rag.ingestion.chunking import ChunkerIdentity
from way2australia_rag.ingestion.cli import ClientFactory, build_embedder
from way2australia_rag.ingestion.config import IngestionConfig, RuntimeSettings
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.ingestion.settings import IndexSettings
from way2australia_rag.lexical.build import default_lexical_dir, lexical_index_path
from way2australia_rag.lexical.freshness import verify_fresh
from way2australia_rag.lexical.store import LexicalIndex, LexicalIndexBindingError
from way2australia_rag.repositories import (
    DocumentRepository,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.rerank.base import Reranker
from way2australia_rag.rerank.build import build_reranker
from way2australia_rag.rerank.errors import RerankSkipReason, classify_reranker_error
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.applicability import (
    ResolvedLote,
    dense_query_filter,
    sql_access_with_lote,
)
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.strategy import (
    RerankConfig,
    RetrievalConfig,
    build_retriever,
    open_bound_lexical,
)

EmbedderFactory = Callable[[IngestionConfig, str], Embedder]
RerankerFactory = Callable[[RerankConfig, str | None], Reranker]

_LOTE_COLUMN_ADVICE = (
    "(lexical settings 1.1); run `make index-lexical` for this collection "
    "and index_version."
)


def _lexical_document_count(
    lexical: LexicalIndex,
    access: ResolvedAccess,
    lote: ResolvedLote | None,
) -> int:
    if lote is not None and not lexical.has_lote_column:
        raise LexicalIndexBindingError(
            f"lexical index '{lexical.label}' has no lote_languages column "
            + _LOTE_COLUMN_ADVICE
        )
    where, params = sql_access_with_lote(access, lote)
    return lexical.document_count(where, params)


class DocumentCounter(Protocol):
    def __call__(
        self, access: ResolvedAccess, lote: ResolvedLote | None = None
    ) -> int: ...


def open_standalone_lexical(
    settings: RuntimeSettings,
    repo_root: Path,
    expected: IndexIdentity,
    configured_chunker: ChunkerIdentity,
    repository: DocumentRepository,
) -> LexicalIndex:
    """Open the lexical file with no Qdrant client and no embedder."""
    directory = settings.lexical_index_dir or default_lexical_dir(repo_root)
    if not directory.is_absolute():
        directory = repo_root / directory
    lexical = LexicalIndex.open(
        lexical_index_path(directory, expected.collection),
        expected.collection,
        expected.index_version,
    )
    try:
        lexical.check_identity(expected, configured_chunker, HASH_CONTRACT)
        verify_fresh(lexical, repository, configured_chunker)
    except BaseException:
        lexical.close()
        raise
    return lexical


def _open_standalone(
    *,
    settings: RuntimeSettings,
    repo_root: Path,
    ingestion_config: IngestionConfig,
    provider: str,
    repository: DocumentRepository | None,
    configured_chunker: ChunkerIdentity,
) -> tuple[LexicalIndex, IndexIdentity, DocumentCounter]:
    """The one standalone-lexical open, shared by the `bm25` branch and the
    open-time fallback (Spec 008 F4): configured identity, no client, no model."""
    repository = repository or LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=repo_root)
    )
    expected = IndexIdentity.expected(ingestion_config, settings, provider)
    lexical = open_standalone_lexical(
        settings, repo_root, expected, configured_chunker, repository
    )

    def lexical_count(access: ResolvedAccess, lote: ResolvedLote | None = None) -> int:
        return _lexical_document_count(lexical, access, lote)

    return lexical, expected, lexical_count


def _chunks_per_document(
    lexical: LexicalIndex | None, index: DenseIndex | None
) -> Callable[[], dict[str, int]]:
    def counts() -> dict[str, int]:
        if lexical is not None:
            return lexical.chunks_per_document()
        if index is not None:
            tallies: Counter[str] = Counter()
            for _point, document_id, _version, _hash in index.chunk_identities():
                tallies[document_id] += 1
            return dict(tallies)
        return {}

    return counts


@dataclass
class OpenedRetrieval:
    retriever: Retriever
    identity: IndexIdentity
    document_count: DocumentCounter
    chunks_per_document: Callable[[], dict[str, int]]
    embedder: Embedder | None
    index_settings: IndexSettings | None
    lexical: LexicalIndex | None
    reranker: Reranker | None = None
    # Wall time of the reranker load at open (Spec 011 R6); None when not loaded.
    rerank_load_ms: float | None = None
    # The Qdrant client this stack opened (None on a standalone `bm25` stack or
    # after an open-time fallback). `close()` owns it (Spec 013 R2).
    client: object | None = None

    def close(self) -> None:
        """Close the lexical file, then the client. Idempotent."""
        lexical, self.lexical = self.lexical, None
        client, self.client = self.client, None
        try:
            if lexical is not None:
                lexical.close()
        finally:
            _close_quietly(client)


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
    rerank: bool = False,
    reranker_factory: RerankerFactory = build_reranker,
    reranker_provider: str | None = None,
    top_k: int | None = None,
) -> OpenedRetrieval:
    """Open the stack for `strategy` (`dense`, `bm25` or `hybrid`).

    With `rerank` the reranker is built and loaded here, once (Spec 011 D-A): an
    eligible load failure skips reranking for the whole run (`stage: "open"`);
    any other load error propagates. With `rerank` off `reranker_factory` is
    never called.

    `top_k` is the largest result size the caller will ask for: with `rerank`
    and `top_k > rerank.depth` the open is refused before any model is built
    (Spec 011 F3). Every failure after the Qdrant client exists closes the client
    and any opened lexical file (Spec 013 R2)."""
    strategy = Strategy(strategy)
    if rerank and strategy != Strategy.HYBRID:
        raise RetrievalConfigurationError(
            "reranking applies to the hybrid strategy only."
        )
    if rerank and top_k is not None and top_k > retrieval_config.rerank.depth:
        raise RetrievalConfigurationError(
            f"top_k {top_k} exceeds rerank.depth {retrieval_config.rerank.depth}."
        )
    configured_chunker = chunker_identity_for_run(ingestion_config, provider)
    if strategy == Strategy.BM25:
        lexical, expected, lexical_count = _open_standalone(
            settings=settings,
            repo_root=repo_root,
            ingestion_config=ingestion_config,
            provider=provider,
            repository=repository,
            configured_chunker=configured_chunker,
        )
        try:
            retriever = build_retriever(
                strategy, expected, None, None, lexical, retrieval_config
            )
        except BaseException:
            lexical.close()
            raise
        return OpenedRetrieval(
            retriever,
            expected,
            lexical_count,
            _chunks_per_document(lexical, None),
            None,
            None,
            lexical,
        )

    embedder = embedder_factory(ingestion_config, provider)
    reranker = (
        reranker_factory(retrieval_config.rerank, reranker_provider) if rerank else None
    )
    timeouts = retrieval_config.qdrant
    client = None
    lexical = None
    try:
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
            if strategy == Strategy.HYBRID:
                lexical = open_bound_lexical(settings, repo_root, index)
        except RetrievalUnavailableError as error:
            if strategy != Strategy.HYBRID:
                raise
            _close_quietly(client)
            client = None
            return _open_fallback(
                error.reason,
                settings=settings,
                ingestion_config=ingestion_config,
                retrieval_config=retrieval_config,
                provider=provider,
                repo_root=repo_root,
                embedder=embedder,
                repository=repository,
                configured_chunker=configured_chunker,
            )

        def dense_count(
            access: ResolvedAccess, lote: ResolvedLote | None = None
        ) -> int:
            return index.document_count(dense_query_filter(access, lote))

        load_started = perf_counter()
        open_skip = _load_reranker(reranker)
        load_ms = (
            (perf_counter() - load_started) * 1000.0 if reranker is not None else None
        )
        retriever = build_retriever(
            strategy,
            identity,
            index,
            embedder,
            lexical,
            retrieval_config,
            reranker,
            open_skip,
        )
    except BaseException:
        # Close what this call opened; nothing leaks from a failed open.
        try:
            if lexical is not None:
                lexical.close()
        finally:
            _close_quietly(client)
        raise
    return OpenedRetrieval(
        retriever,
        identity,
        dense_count,
        _chunks_per_document(lexical, index),
        embedder,
        index.settings,
        lexical,
        reranker,
        load_ms,
        client,
    )


def _load_reranker(reranker: Reranker | None) -> RerankSkipReason | None:
    """Load once at open. An eligible outage becomes the sticky open-stage skip;
    anything else (including offline-not-cached) propagates."""
    if reranker is None:
        return None
    try:
        reranker.load()
    except Exception as error:
        mapped = classify_reranker_error(error)
        if mapped is None:
            raise
        return mapped.reason
    return None


def _close_quietly(client: object) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        try:
            close()
        except Exception:  # noqa: BLE001
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
    configured_chunker: ChunkerIdentity,
) -> OpenedRetrieval:
    lexical, expected, lexical_count = _open_standalone(
        settings=settings,
        repo_root=repo_root,
        ingestion_config=ingestion_config,
        provider=provider,
        repository=repository,
        configured_chunker=configured_chunker,
    )
    try:
        retriever = FallbackRetriever(None, BM25Retriever(expected, lexical), reason)
    except BaseException:
        lexical.close()
        raise
    return OpenedRetrieval(
        retriever,
        expected,
        lexical_count,
        _chunks_per_document(lexical, None),
        embedder,
        None,
        lexical,
    )
