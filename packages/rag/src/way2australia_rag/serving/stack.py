"""Serving stack, holder, open and dense re-open (Spec 013 R1, R2, R5).

`open_serving_stack` resolves strategy, reranking and generator from the
committed configuration, shares one locked embedder, one locked reranker, one
generator and one breaker across stack generations, and returns a
`StackHolder`. With Qdrant (or the embedding model) down for a fallback-eligible
reason it starts BM25-only with the breaker open; the first probe request calls
`try_reopen_dense`, which runs the startup checks again before dense rejoins.
"""

import logging
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from threading import Condition, RLock
from typing import Any

from way2australia_rag.generation.base import Generator
from way2australia_rag.generation.build import build_generator
from way2australia_rag.generation.config import GenerationConfig
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.prompts import PromptRegistry, PromptVersion
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.ingestion.cli import ClientFactory, build_embedder
from way2australia_rag.ingestion.config import IngestionConfig, RuntimeSettings
from way2australia_rag.repositories import DocumentRepository
from way2australia_rag.rerank.build import build_reranker
from way2australia_rag.rerank.errors import classify_reranker_error
from way2australia_rag.retrieval.availability import classify_model_error
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.breaker import Admission, CircuitBreaker
from way2australia_rag.retrieval.errors import FallbackReason
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.opening import (
    EmbedderFactory,
    OpenedRetrieval,
    RerankerFactory,
    open_retrieval,
)
from way2australia_rag.retrieval.strategy import RetrievalConfig
from way2australia_rag.serving.config import ServingConfig
from way2australia_rag.serving.locks import LockedEmbedder, LockedReranker
from way2australia_rag.serving.readiness import Readiness

logger = logging.getLogger(__name__)

_WARMUP_QUERY = "warm-up"


class ServingNotReadyError(RuntimeError):
    """No stack is open (not started, or already closed)."""


class ReopenOutcome(StrEnum):
    SWAPPED = "swapped"
    OUTAGE = "outage"
    REFUSED = "refused"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ServingStack:
    opened: OpenedRetrieval
    service: AnswerService
    dense: bool  # False while serving BM25-only after an open-time outage
    leases: int = field(default=0, repr=False)
    retired: bool = field(default=False, repr=False)

    def close(self) -> None:
        """Idempotent; closes the lexical file, then the client."""
        self.opened.close()


@dataclass(frozen=True)
class ServingChoices:
    strategy: Strategy
    rerank: bool
    generator_provider: str | None


def resolve_serving_choices(
    retrieval_config: RetrievalConfig,
    generation_config: GenerationConfig,
    *,
    generator_provider: str | None = None,
) -> ServingChoices:
    """Configuration decides; no library default does (R1, Spec 011 F2)."""
    return ServingChoices(
        strategy=Strategy(retrieval_config.default_strategy),
        rerank=retrieval_config.rerank.enabled,
        generator_provider=generator_provider or generation_config.default_generator,
    )


@dataclass(frozen=True)
class ServingInputs:
    settings: RuntimeSettings
    ingestion_config: IngestionConfig
    retrieval_config: RetrievalConfig
    generation_config: GenerationConfig
    serving_config: ServingConfig
    repo_root: Path
    provider: str  # embedder provider
    reranker_provider: str | None = None
    generator_provider: str | None = None
    # A generator built by the caller (phase 1). Ownership passes to the holder,
    # which closes it at shutdown and on a failed open.
    generator: Generator | None = None
    prompt_version: PromptVersion | None = None
    client_factory: ClientFactory | None = None
    embedder_factory: EmbedderFactory = build_embedder
    reranker_factory: RerankerFactory = build_reranker
    repository: DocumentRepository | None = None
    generator_factory: Callable[..., Generator] = build_generator
    clock: Callable[[], float] = time.monotonic
    drain_timeout_s: float = 5.0


def _close_quietly(resource: object) -> None:
    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception as error:  # noqa: BLE001
            logger.warning("close failed: %s", type(error).__name__)


class StackHolder:
    """Owns the current stack, the shared models, the breaker and the generator."""

    def __init__(self, inputs: ServingInputs, readiness: Readiness | None = None):
        self._inputs = inputs
        self.choices = resolve_serving_choices(
            inputs.retrieval_config,
            inputs.generation_config,
            generator_provider=inputs.generator_provider,
        )
        self.readiness = readiness if readiness is not None else Readiness()
        self._cond = Condition(RLock())
        self._current: ServingStack | None = None
        self._retired: list[ServingStack] = []
        self._closed = False
        self._embedder: LockedEmbedder | None = None
        self._reranker: LockedReranker | None = None
        self._generator: Generator | None = inputs.generator
        self._breaker: CircuitBreaker | None = None
        self._builder = ContextBuilder(inputs.generation_config.context)
        self._prompt = inputs.prompt_version

    # -- public surface ---------------------------------------------------

    @property
    def breaker(self) -> CircuitBreaker | None:
        return self._breaker

    @property
    def generator(self) -> Generator | None:
        return self._generator

    @property
    def dense(self) -> bool:
        with self._cond:
            return self._current is not None and self._current.dense

    @contextmanager
    def acquire(self) -> Iterator[ServingStack]:
        """A ref-counted lease on the current stack."""
        with self._cond:
            stack = self._current
            if self._closed or stack is None:
                raise ServingNotReadyError("no serving stack is open")
            stack.leases += 1
        try:
            yield stack
        finally:
            self._release(stack)

    def try_reopen_dense(self) -> ReopenOutcome:
        """Called only by the probe request on a BM25-only stack."""
        with self._cond:
            current = self._current
            if self._closed or current is None or current.dense:
                return ReopenOutcome.NOT_APPLICABLE
        breaker = self._breaker
        if breaker is None:
            return ReopenOutcome.NOT_APPLICABLE
        try:
            reason = self._ensure_embedder()
            if reason is not None:
                breaker.record_failure(Admission.PROBE, reason)
                return ReopenOutcome.OUTAGE
            opened = open_retrieval(
                Strategy.HYBRID, **self._open_kwargs(breaker=breaker)
            )
        except Exception as error:  # noqa: BLE001 - refused, never served
            logger.warning("dense re-open refused: %s", type(error).__name__)
            breaker.release(Admission.PROBE)
            self.readiness.set_reopen_refused(True)
            return ReopenOutcome.REFUSED
        if opened.fallback_reason is not None:
            reason = opened.fallback_reason
            opened.close()
            breaker.record_failure(Admission.PROBE, reason)
            return ReopenOutcome.OUTAGE
        try:
            stack = self._make_stack(opened, dense=True)
        except BaseException:
            opened.close()
            raise
        self._swap(stack)
        self.readiness.set_reopen_refused(False)
        self._sync_rerank_flag(opened)
        return ReopenOutcome.SWAPPED

    def close(self) -> None:
        """Shutdown: close the current stack, drain retired ones (bounded), then
        the models and the generator."""
        with self._cond:
            if self._closed:
                return
            self._closed = True
            current, self._current = self._current, None
        if current is not None:
            current.close()
        with self._cond:
            self._cond.wait_for(
                lambda: all(s.leases == 0 for s in self._retired),
                timeout=self._inputs.drain_timeout_s,
            )
            retired, self._retired = self._retired, []
        for stack in retired:
            stack.close()
        for resource in (self._embedder, self._reranker, self._generator):
            if resource is not None:
                _close_quietly(resource)

    # -- startup ----------------------------------------------------------

    def start(self) -> None:
        inputs = self._inputs
        choices = self.choices
        if self._generator is None:
            self._generator = inputs.generator_factory(
                inputs.generation_config, choices.generator_provider
            )
        if self._prompt is None:
            config = inputs.generation_config
            self._prompt = PromptRegistry(inputs.repo_root).get(
                config.prompt.id, config.prompt.version
            )
        outage: FallbackReason | None = None
        if choices.strategy in (Strategy.DENSE, Strategy.HYBRID):
            outage = self._ensure_embedder()
        if choices.rerank and choices.strategy is Strategy.HYBRID:
            self._preload_reranker()
        self._breaker = self._new_breaker(None)
        self.readiness.set_breaker_provider(lambda: self._breaker)
        if choices.strategy is Strategy.HYBRID and outage is not None:
            opened = open_retrieval(
                Strategy.BM25, **self._open_kwargs(rerank=False, bm25=True)
            )
            stack = self._bm25_only(opened, outage)
        else:
            opened = open_retrieval(
                choices.strategy, **self._open_kwargs(breaker=self._breaker)
            )
            if opened.fallback_reason is not None:
                stack = self._bm25_only(opened, opened.fallback_reason)
            else:
                stack = self._make_stack(
                    opened, dense=choices.strategy is not Strategy.BM25
                )
        with self._cond:
            self._current = stack
        self._sync_rerank_flag(stack.opened)

    # -- internals --------------------------------------------------------

    def _new_breaker(self, reason: FallbackReason | None) -> CircuitBreaker:
        cfg = self._inputs.serving_config.breaker
        return CircuitBreaker(
            cfg.failure_threshold,
            cfg.cooldown_s,
            self._inputs.clock,
            open_reason=reason,
        )

    def _open_kwargs(
        self,
        *,
        breaker: CircuitBreaker | None = None,
        rerank: bool | None = None,
        bm25: bool = False,
    ) -> dict[str, Any]:
        inputs = self._inputs
        use_rerank = self.choices.rerank if rerank is None else rerank
        embedder = self._embedder
        return {
            "settings": inputs.settings,
            "ingestion_config": inputs.ingestion_config,
            "retrieval_config": inputs.retrieval_config,
            "provider": inputs.provider,
            "repo_root": inputs.repo_root,
            "client_factory": inputs.client_factory,
            "embedder_factory": lambda _c, _p: embedder,
            "repository": inputs.repository,
            "rerank": use_rerank and not bm25,
            "reranker_factory": lambda _c, _p: self._reranker,
            "top_k": inputs.generation_config.retrieval.top_k,
            "breaker": breaker,
        }

    def _ensure_embedder(self) -> FallbackReason | None:
        """Build and warm the shared embedder once. An eligible failure is an
        outage (returned); anything else propagates."""
        if self._embedder is not None:
            return None
        inputs = self._inputs
        try:
            locked = LockedEmbedder(
                inputs.embedder_factory(inputs.ingestion_config, inputs.provider)
            )
            locked.embed_query(_WARMUP_QUERY)
        except Exception as error:
            mapped = classify_model_error(error)
            if mapped is None:
                raise
            return mapped.reason
        self._embedder = locked
        return None

    def _preload_reranker(self) -> None:
        inputs = self._inputs
        if self._reranker is None:
            self._reranker = LockedReranker(
                inputs.reranker_factory(
                    inputs.retrieval_config.rerank, inputs.reranker_provider
                )
            )
        try:
            self._reranker.load()
        except Exception as error:
            if classify_reranker_error(error) is None:
                raise
            # Sticky skip (D077): the wrapper re-raises it on every later load.

    def _bm25_only(
        self, opened: OpenedRetrieval, reason: FallbackReason
    ) -> ServingStack:
        assert opened.lexical is not None
        breaker = self._new_breaker(reason)
        self._breaker = breaker
        opened.retriever = FallbackRetriever(
            None,
            BM25Retriever(opened.identity, opened.lexical),
            reason,
            breaker=breaker,
            on_probe=self._probe,
        )
        try:
            return self._make_stack(opened, dense=False)
        except BaseException:
            opened.close()
            raise

    def _probe(self) -> Retriever | None:
        if self.try_reopen_dense() is not ReopenOutcome.SWAPPED:
            return None
        with self._cond:
            assert self._current is not None
            return self._current.opened.retriever

    def _make_stack(self, opened: OpenedRetrieval, *, dense: bool) -> ServingStack:
        assert self._generator is not None and self._prompt is not None
        service = AnswerService(
            opened.retriever,
            self._builder,
            self._prompt,
            self._generator,
            self._inputs.generation_config,
        )
        return ServingStack(opened, service, dense)

    def _swap(self, new: ServingStack) -> None:
        to_close: ServingStack | None = None
        with self._cond:
            old, self._current = self._current, new
            if old is not None:
                old.retired = True
                if old.leases == 0:
                    to_close = old
                else:
                    self._retired.append(old)
        if to_close is not None:
            to_close.close()

    def _release(self, stack: ServingStack) -> None:
        close_now = False
        with self._cond:
            stack.leases -= 1
            if stack.retired and stack.leases == 0:
                if stack in self._retired:
                    self._retired.remove(stack)
                close_now = True
            self._cond.notify_all()
        if close_now:
            stack.close()

    def _sync_rerank_flag(self, opened: OpenedRetrieval) -> None:
        skipped = opened.rerank_open_skip is not None or (
            self._reranker is not None and self._reranker.load_failed
        )
        self.readiness.set_rerank_skipped(skipped)


def open_serving_stack(
    inputs: ServingInputs, readiness: Readiness | None = None
) -> StackHolder:
    """Open the stack from configuration. On any failure everything opened,
    including a generator passed in, is closed and the error propagates."""
    holder = StackHolder(inputs, readiness)
    try:
        holder.start()
    except BaseException:
        holder.close()
        raise
    return holder
