"""Serving stack, holder, startup and dense re-open (Spec 013 R1, R2, R5)."""

import threading
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from generation.support import generation_config
from qdrant_client import QdrantClient
from retrieval.test_cli import ingest
from retrieval.test_fallback import client_at, closed_port
from retrieval.test_opening import fake_lexical  # noqa: F401  (fixture)
from retrieval.test_opening_lifecycle import CountingClient
from way2australia_rag.generation.fake import FakeGenerator
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.lexical.store import LexicalIndex, LexicalIndexBindingError
from way2australia_rag.rerank.errors import RerankerUnavailableError, RerankSkipReason
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.breaker import BreakerState
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.strategy import load_retrieval_config
from way2australia_rag.serving.config import load_serving_config
from way2australia_rag.serving.stack import (
    ReopenOutcome,
    ServingInputs,
    ServingNotReadyError,
    StackHolder,
    open_serving_stack,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

COOLDOWN = 30.0


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class SwitchFactory:
    """Qdrant client factory whose target can be switched between down and up."""

    def __init__(self, target: Any) -> None:
        self.target = target
        self.calls = 0

    def __call__(self, settings: object) -> Any:
        self.calls += 1
        return self.target(settings) if callable(self.target) else self.target


def down() -> Any:
    return client_at(closed_port())


class CountingEmbedder(FakeEmbedder):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.warmed = 0
        self.closed = 0

    def embed_query(self, text: str) -> list[float]:
        self.warmed += 1
        return super().embed_query(text)

    def close(self) -> None:
        self.closed += 1


class EmbedderFactory:
    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls = 0
        self.built: list[CountingEmbedder] = []

    def __call__(self, config: Any, _provider: str) -> CountingEmbedder:
        self.calls += 1
        if self.calls <= self.fail_times:
            error = OSError("unreachable")
            error.__cause__ = ConnectionError("net")
            raise error
        embedder = CountingEmbedder(config.embedder.fake_vector_size)
        self.built.append(embedder)
        return embedder


class ClosingReranker(FakeReranker):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.closed = 0

    def close(self) -> None:
        self.closed += 1


class RerankerFactory:
    def __init__(self, reranker: FakeReranker) -> None:
        self.reranker = reranker
        self.calls = 0

    def __call__(self, _config: Any, _provider: str | None = None) -> FakeReranker:
        self.calls += 1
        return self.reranker


@pytest.fixture
def lexical_closes(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []
    original = LexicalIndex.close

    def counting(self: LexicalIndex) -> None:
        calls.append(1)
        original(self)

    monkeypatch.setattr(LexicalIndex, "close", counting)
    return calls


@pytest.fixture
def up_client() -> CountingClient:
    inner = QdrantClient(":memory:")
    ingest(inner)
    return CountingClient(inner)


def make_inputs(
    factory: Any,
    *,
    clock: Clock | None = None,
    embedder_factory: Any = None,
    reranker: FakeReranker | None = None,
    generator: FakeGenerator | None = None,
    strategy: Strategy | None = None,
    rerank: bool | None = None,
    generator_provider: str | None = "fake",
    drain_timeout_s: float = 5.0,
) -> ServingInputs:
    retrieval = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    updates: dict[str, Any] = {}
    if strategy is not None:
        updates["default_strategy"] = strategy
    if rerank is not None:
        updates["rerank"] = retrieval.rerank.model_copy(update={"enabled": rerank})
    if updates:
        retrieval = retrieval.model_copy(update=updates)
    generation = generation_config()
    serving = load_serving_config(
        REPO_ROOT / "config/serving.yaml",
        generation_config=generation,
        retrieval_config=retrieval,
        generator_provider=generator_provider,
    )
    extra: dict[str, Any] = {}
    if embedder_factory is not None:
        extra["embedder_factory"] = embedder_factory
    # Never the real model: the default is a fake that loads.
    extra["reranker_factory"] = RerankerFactory(reranker or ClosingReranker())
    if generator is not None:
        extra["generator"] = generator
    return ServingInputs(
        settings=load_runtime_settings(RetrievalConfigurationError),
        ingestion_config=load_ingestion_config(REPO_ROOT / "config/ingestion.yaml"),
        retrieval_config=retrieval,
        generation_config=generation,
        serving_config=serving,
        repo_root=REPO_ROOT,
        provider="fake",
        generator_provider=generator_provider,
        client_factory=factory,
        clock=clock or Clock(),
        drain_timeout_s=drain_timeout_s,
        **extra,
    )


def ask(holder: StackHolder, stack: Any = None) -> Any:
    access = resolve_access(guest_access(load_runtime_settings()))
    if stack is not None:
        return stack.opened.retriever.retrieve("Is coaching compulsory?", access, 5)
    with holder.acquire() as leased:
        return leased.opened.retriever.retrieve("Is coaching compulsory?", access, 5)


# --- configuration decides (R1) -----------------------------------------------


def test_server_follows_configuration_not_library_defaults(
    fake_lexical: Path,  # noqa: F811
) -> None:
    reranker = ClosingReranker()
    factory = RerankerFactory(reranker)
    inputs = make_inputs(SwitchFactory(down()), strategy=Strategy.BM25, rerank=False)
    inputs = ServingInputs(**{**inputs.__dict__, "reranker_factory": factory})
    holder = open_serving_stack(inputs)
    try:
        assert holder.choices.strategy is Strategy.BM25
        assert holder.choices.rerank is False
        assert holder.choices.generator_provider == "fake"
        with holder.acquire() as stack:
            assert stack.opened.reranker is None
            assert stack.opened.client is None
            assert stack.dense is False
        assert factory.calls == 0
        assert isinstance(holder.generator, FakeGenerator)
    finally:
        holder.close()


def test_hybrid_with_rerank_off_serves_without_a_reranker(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    factory = RerankerFactory(ClosingReranker())
    inputs = make_inputs(SwitchFactory(up_client), rerank=False)
    inputs = ServingInputs(**{**inputs.__dict__, "reranker_factory": factory})
    holder = open_serving_stack(inputs)
    try:
        with holder.acquire() as stack:
            assert stack.dense and stack.opened.reranker is None
        assert factory.calls == 0
        assert ask(holder).fallback_reason is None
    finally:
        holder.close()


# --- start with dense down (R5) -------------------------------------------------


def test_start_with_qdrant_down_is_bm25_only_with_the_breaker_open(
    fake_lexical: Path,  # noqa: F811
) -> None:
    holder = open_serving_stack(make_inputs(SwitchFactory(down())))
    try:
        holder.readiness.set_ready()
        assert holder.dense is False
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.OPEN
        assert holder.readiness.snapshot().degraded_reasons == ("dense_circuit_open",)
        result = ask(holder)
        assert result.fallback_reason == "qdrant_unavailable"
        assert result.hits
    finally:
        holder.close()


def test_probe_success_with_matching_collection_swaps_and_drains(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
    lexical_closes: list[int],
) -> None:
    clock = Clock()
    factory = SwitchFactory(down())
    holder = open_serving_stack(make_inputs(factory, clock=clock))
    try:
        factory.target = up_client
        clock.now += COOLDOWN + 1
        with holder.acquire() as old:
            assert old.dense is False
            result = ask(holder, old)  # the probe request, leased on the old stack
            assert result.fallback_reason is None  # served by the new dense stack
            with holder.acquire() as new:
                assert new is not old and new.dense
            # In-flight work keeps the old stack open until the lease ends.
            assert old.opened.lexical is not None
        assert old.opened.lexical is None  # drained and closed after its lease
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.CLOSED
        assert holder.dense
        assert up_client.close_calls == 0
    finally:
        holder.close()
    assert up_client.close_calls == 1


@pytest.mark.parametrize("how", ["bind", "missing_collection"])
def test_probe_with_a_mismatched_collection_is_refused(
    how: str,
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = Clock()
    target: Any = up_client
    if how == "bind":

        def mismatch(self: LexicalIndex, dense: object) -> None:
            raise LexicalIndexBindingError("mismatch")

        monkeypatch.setattr(LexicalIndex, "bind_to", mismatch)
    else:
        target = CountingClient(QdrantClient(":memory:"))
    factory = SwitchFactory(down())
    holder = open_serving_stack(make_inputs(factory, clock=clock))
    try:
        holder.readiness.set_ready()
        factory.target = target
        clock.now += COOLDOWN + 1
        result = ask(holder)
        assert result.fallback_reason is not None  # BM25 still serves
        assert holder.dense is False
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.OPEN
        reasons = holder.readiness.snapshot().degraded_reasons
        assert "dense_reopen_refused" in reasons
        assert target.close_calls == 1  # the failed attempt's client was closed
        # The breaker is open for a new cool-down: no second attempt yet.
        calls = factory.calls
        ask(holder)
        assert factory.calls == calls
    finally:
        holder.close()


def test_probe_failure_reopens_the_breaker(
    fake_lexical: Path,  # noqa: F811
) -> None:
    clock = Clock()
    factory = SwitchFactory(down())
    holder = open_serving_stack(make_inputs(factory, clock=clock))
    try:
        clock.now += COOLDOWN + 1
        calls = factory.calls
        result = ask(holder)
        assert factory.calls == calls + 1  # one probe attempt
        assert result.fallback_reason == "qdrant_unavailable"
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.OPEN
        ask(holder)
        assert factory.calls == calls + 1  # cool-down restarted
        assert (
            "dense_reopen_refused" not in holder.readiness.snapshot().degraded_reasons
        )
    finally:
        holder.close()


# --- embedder failure at start (R5) ---------------------------------------------


def test_embedder_failure_at_start_is_retried_by_the_first_probe(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    clock = Clock()
    embedders = EmbedderFactory(fail_times=1)
    holder = open_serving_stack(
        make_inputs(SwitchFactory(up_client), clock=clock, embedder_factory=embedders)
    )
    try:
        assert holder.dense is False  # Qdrant was never needed to learn that
        assert holder.breaker is not None
        assert holder.breaker.last_reason is not None
        assert holder.breaker.last_reason.value == "model_unavailable"
        assert embedders.calls == 1
        clock.now += COOLDOWN + 1
        assert ask(holder).fallback_reason is None
        assert embedders.calls == 2
        assert [e.warmed for e in embedders.built] == [1 + 1]  # warm-up + one query
        assert holder.dense
    finally:
        holder.close()
    assert embedders.built[0].closed == 1


def test_failing_embedder_retry_reopens_the_breaker(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    clock = Clock()
    embedders = EmbedderFactory(fail_times=2)
    holder = open_serving_stack(
        make_inputs(SwitchFactory(up_client), clock=clock, embedder_factory=embedders)
    )
    try:
        clock.now += COOLDOWN + 1
        result = ask(holder)
        assert embedders.calls == 2
        assert result.fallback_reason == "model_unavailable"
        assert holder.dense is False
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.OPEN
        assert up_client.close_calls == 0  # Qdrant was not touched
    finally:
        holder.close()


# --- reranker skip is sticky ----------------------------------------------------


def test_sticky_reranker_skip_survives_a_reopen(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    clock = Clock()
    reranker = ClosingReranker(fail_on_load=True)
    factory = SwitchFactory(down())
    holder = open_serving_stack(
        make_inputs(factory, clock=clock, reranker=reranker, rerank=True)
    )
    try:
        holder.readiness.set_ready()
        assert holder.readiness.snapshot().degraded_reasons == (
            "dense_circuit_open",
            "rerank_skipped",
        )
        factory.target = up_client
        clock.now += COOLDOWN + 1
        ask(holder)
        assert holder.dense
        assert holder.readiness.snapshot().degraded_reasons == ("rerank_skipped",)
        assert reranker.load_calls == 1  # asked once, never again
    finally:
        holder.close()
    assert reranker.closed == 1


def test_reranker_loaded_once_and_reused_by_the_reopened_stack(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    clock = Clock()
    reranker = ClosingReranker()
    factory = SwitchFactory(down())
    holder = open_serving_stack(
        make_inputs(factory, clock=clock, reranker=reranker, rerank=True)
    )
    try:
        factory.target = up_client
        clock.now += COOLDOWN + 1
        ask(holder)
        with holder.acquire() as stack:
            assert stack.dense and stack.opened.reranker is not None
        assert holder.readiness.snapshot().degraded_reasons == ()
    finally:
        holder.close()


# --- lifecycle (R2) -------------------------------------------------------------


def test_shutdown_closes_everything_once(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
    lexical_closes: list[int],
) -> None:
    generator = FakeGenerator()
    reranker = ClosingReranker()
    embedders = EmbedderFactory()
    holder = open_serving_stack(
        make_inputs(
            SwitchFactory(up_client),
            generator=generator,
            reranker=reranker,
            rerank=True,
            embedder_factory=embedders,
        )
    )
    assert up_client.close_calls == 0
    holder.close()
    holder.close()  # idempotent
    assert up_client.close_calls == 1
    assert len(lexical_closes) == 1
    assert generator.closed
    assert reranker.closed == 1
    assert embedders.built[0].closed == 1
    with pytest.raises(ServingNotReadyError):
        with holder.acquire():
            pass


def test_startup_failure_closes_everything_opened(
    fake_lexical: Path,  # noqa: F811
) -> None:
    generator = FakeGenerator()
    embedders = EmbedderFactory()
    empty = CountingClient(QdrantClient(":memory:"))  # collection absent: not eligible
    with pytest.raises(Exception):  # noqa: B017, PT011 - the class is not the point
        open_serving_stack(
            make_inputs(
                SwitchFactory(empty), generator=generator, embedder_factory=embedders
            )
        )
    assert empty.close_calls == 1
    assert generator.closed
    assert embedders.built[0].closed == 1


def test_startup_failure_in_the_reranker_closes_models_and_generator(
    fake_lexical: Path,  # noqa: F811
) -> None:
    class Broken(ClosingReranker):
        def load(self) -> None:
            raise ValueError("configuration")

    generator = FakeGenerator()
    reranker = Broken()
    embedders = EmbedderFactory()
    with pytest.raises(ValueError):
        open_serving_stack(
            make_inputs(
                SwitchFactory(down()),
                generator=generator,
                reranker=reranker,
                rerank=True,
                embedder_factory=embedders,
            )
        )
    assert generator.closed and reranker.closed == 1
    assert embedders.built[0].closed == 1


def test_shutdown_drains_a_lease_for_a_bounded_time(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
    lexical_closes: list[int],
) -> None:
    clock = Clock()
    factory = SwitchFactory(down())
    holder = open_serving_stack(make_inputs(factory, clock=clock, drain_timeout_s=0.05))
    factory.target = up_client
    clock.now += COOLDOWN + 1
    lease = holder.acquire()
    old = lease.__enter__()
    try:
        ask(holder, old)  # swap while `old` is leased
        assert old.retired and old.opened.lexical is not None
        closer = threading.Thread(target=holder.close)
        closer.start()
        closer.join(5)
        assert not closer.is_alive()
        assert old.opened.lexical is None  # closed after the bounded wait
    finally:
        lease.__exit__(None, None, None)


def test_try_reopen_is_not_applicable_on_a_dense_stack(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    holder = open_serving_stack(make_inputs(SwitchFactory(up_client)))
    try:
        assert holder.try_reopen_dense() is ReopenOutcome.NOT_APPLICABLE
    finally:
        holder.close()


def test_reranker_outage_at_load_is_reported_as_skip_reason(
    fake_lexical: Path,  # noqa: F811
    up_client: CountingClient,
) -> None:
    class Down(ClosingReranker):
        def load(self) -> None:
            self.load_calls += 1
            raise RerankerUnavailableError(RerankSkipReason.MODEL_TIMEOUT)

    holder = open_serving_stack(
        make_inputs(SwitchFactory(up_client), reranker=Down(), rerank=True)
    )
    try:
        holder.readiness.set_ready()
        assert holder.readiness.snapshot().degraded_reasons == ("rerank_skipped",)
        assert ask(holder).hits
    finally:
        holder.close()
