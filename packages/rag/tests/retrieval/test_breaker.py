"""Circuit breaker for the dense leg (Spec 013 R4, D058, D062)."""

import threading
from pathlib import Path
from typing import Any

import httpx
import pytest
from conftest import REPO_ROOT
from qdrant_client.http.exceptions import UnexpectedResponse
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.breaker import Admission, BreakerState, CircuitBreaker
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import load_retrieval_config

from .test_fallback import access, client_at, closed_port
from .test_hybrid import stub_result
from .test_opening import fake_lexical  # noqa: F401  (fixture)
from .test_opening_lifecycle import (
    Factory,
    RerankerFactory,
    ingested,  # noqa: F401  (fixture)
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

_COOLDOWN_S = 10.0


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Scripted:
    """Primary whose queued exceptions are raised, then a hybrid result."""

    strategy = Strategy.HYBRID

    def __init__(self, *events: Exception | None) -> None:
        self.events = list(events)
        self.seen: list[tuple[ResolvedAccess, int, ResolvedLote | None]] = []

    def fail_with(self, error: Exception | None) -> None:
        self.events.append(error)

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = 5,
        *,
        lote: ResolvedLote | None = None,
    ) -> RetrievalResult:
        self.seen.append((access, top_k, lote))
        event = self.events.pop(0) if self.events else None
        if event is not None:
            raise event
        return stub_result(["a"]).model_copy(
            update={"strategy": "hybrid", "score_kind": "rrf"}
        )


class SpyBm25:
    strategy = Strategy.BM25

    def __init__(self) -> None:
        self.seen: list[tuple[ResolvedAccess, int, ResolvedLote | None]] = []

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = 5,
        *,
        lote: ResolvedLote | None = None,
    ) -> RetrievalResult:
        self.seen.append((access, top_k, lote))
        return stub_result(["b"]).model_copy(
            update={"strategy": "bm25", "score_kind": "bm25"}
        )


def guest() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def unavailable(reason: FallbackReason) -> RetrievalUnavailableError:
    return RetrievalUnavailableError(reason)


def status_error() -> UnexpectedResponse:
    return UnexpectedResponse(503, "Service Unavailable", b"", httpx.Headers())


def fail(
    breaker: CircuitBreaker, reason: FallbackReason = FallbackReason.QDRANT_UNAVAILABLE
) -> None:
    assert breaker.admit() is Admission.DENSE
    breaker.record_failure(Admission.DENSE, reason)


def test_threshold_reached_opens() -> None:
    clock = Clock()
    breaker = CircuitBreaker(3, _COOLDOWN_S, clock)
    fail(breaker, FallbackReason.QDRANT_UNAVAILABLE)
    fail(breaker, FallbackReason.QDRANT_UNAVAILABLE)
    assert breaker.state is BreakerState.CLOSED
    fail(breaker, FallbackReason.QDRANT_TIMEOUT)
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is FallbackReason.QDRANT_TIMEOUT
    assert breaker.admit() is Admission.SKIP
    clock.now = _COOLDOWN_S
    assert breaker.admit() is Admission.PROBE
    assert breaker.state is BreakerState.HALF_OPEN


def test_success_while_closed_resets_the_count() -> None:
    clock = Clock()
    breaker = CircuitBreaker(3, _COOLDOWN_S, clock)
    fail(breaker)
    fail(breaker)
    assert breaker.admit() is Admission.DENSE
    breaker.record_success(Admission.DENSE)
    fail(breaker)
    fail(breaker)
    assert breaker.state is BreakerState.CLOSED
    fail(breaker)
    assert breaker.state is BreakerState.OPEN


def test_one_probe_among_eight_concurrent_admits() -> None:
    clock = Clock()
    breaker = CircuitBreaker(1, _COOLDOWN_S, clock)
    fail(breaker)
    clock.now = _COOLDOWN_S
    barrier = threading.Barrier(8)
    found: list[Admission] = []
    errors: list[BaseException] = []
    guard = threading.Lock()

    def worker() -> None:
        try:
            barrier.wait(timeout=1)
            admission = breaker.admit()
        except BaseException as error:  # noqa: BLE001 - the join must still run
            with guard:
                errors.append(error)
            return
        with guard:
            found.append(admission)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    try:
        for thread in threads:
            thread.join(timeout=1)
            assert not thread.is_alive()
    finally:
        for thread in threads:
            thread.join(timeout=1)
    assert errors == []
    assert found.count(Admission.PROBE) == 1
    assert found.count(Admission.SKIP) == 7
    assert breaker.state is BreakerState.HALF_OPEN
    clock.now = _COOLDOWN_S + 100
    assert breaker.admit() is Admission.SKIP


def test_probe_success_closes() -> None:
    clock = Clock()
    breaker = CircuitBreaker(2, _COOLDOWN_S, clock)
    fail(breaker)
    fail(breaker)
    clock.now = _COOLDOWN_S
    assert breaker.admit() is Admission.PROBE
    clock.now = _COOLDOWN_S + 100
    assert breaker.admit() is Admission.SKIP
    breaker.record_success(Admission.PROBE)
    assert breaker.state is BreakerState.CLOSED
    assert breaker.admit() is Admission.DENSE
    fail(breaker)
    assert breaker.state is BreakerState.CLOSED


def test_probe_failure_reopens_with_a_new_cooldown() -> None:
    clock = Clock()
    breaker = CircuitBreaker(1, _COOLDOWN_S, clock)
    fail(breaker, FallbackReason.QDRANT_UNAVAILABLE)
    clock.now = _COOLDOWN_S
    assert breaker.admit() is Admission.PROBE
    clock.now = 12.0
    breaker.record_failure(Admission.PROBE, FallbackReason.QDRANT_TIMEOUT)
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is FallbackReason.QDRANT_TIMEOUT
    clock.now = 21.9
    assert breaker.admit() is Admission.SKIP
    clock.now = 22.0
    assert breaker.admit() is Admission.PROBE


def test_release_reopens_without_counting() -> None:
    clock = Clock()
    breaker = CircuitBreaker(3, _COOLDOWN_S, clock)
    reason = FallbackReason.QDRANT_UNAVAILABLE
    fail(breaker, reason)
    fail(breaker, reason)
    assert breaker.state is BreakerState.CLOSED
    breaker.release(Admission.DENSE)
    assert breaker.state is BreakerState.CLOSED
    fail(breaker, reason)
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is reason

    clock.now = _COOLDOWN_S
    assert breaker.admit() is Admission.PROBE
    clock.now = 25.0
    assert breaker.admit() is Admission.SKIP
    breaker.release(Admission.PROBE)
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is reason
    assert breaker.admit() is Admission.SKIP
    clock.now = 35.0
    assert breaker.admit() is Admission.PROBE


def test_breaker_created_open_admits_a_probe_only_after_the_cooldown() -> None:
    clock = Clock()
    breaker = CircuitBreaker(3, 30.0, clock, FallbackReason.MODEL_UNAVAILABLE)
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is FallbackReason.MODEL_UNAVAILABLE
    assert breaker.admit() is Admission.SKIP
    clock.now = 29.9
    assert breaker.admit() is Admission.SKIP
    clock.now = 30.0
    assert breaker.admit() is Admission.PROBE
    assert breaker.state is BreakerState.HALF_OPEN


def test_skip_serves_bm25_with_the_last_reason_and_calls_no_primary() -> None:
    clock = Clock()
    breaker = CircuitBreaker(1, 30.0, clock)
    primary = Scripted(unavailable(FallbackReason.QDRANT_TIMEOUT))
    fallback = SpyBm25()
    retriever = FallbackRetriever(primary, fallback, None, breaker=breaker)
    lote = ResolvedLote("ml")
    resolved = guest()

    failed = retriever.retrieve("q", resolved, 4, lote=lote)
    assert failed.strategy == "bm25"
    assert failed.fallback_reason == "qdrant_timeout"
    assert failed.requested_strategy == "hybrid"
    assert primary.seen == [(resolved, 4, lote)]
    assert fallback.seen == [(resolved, 4, lote)]
    assert fallback.seen[0][0] is resolved and fallback.seen[0][2] is lote
    assert breaker.state is BreakerState.OPEN

    skipped = retriever.retrieve("q", resolved, 4, lote=lote)
    assert skipped.strategy == "bm25"
    last = breaker.last_reason
    assert last is FallbackReason.QDRANT_TIMEOUT
    assert skipped.fallback_reason == last.value
    assert skipped.requested_strategy == "hybrid"
    assert primary.seen == [(resolved, 4, lote)]
    legs = skipped.leg_latency_ms
    assert legs is not None and set(legs) == {"dense_attempt", "bm25"}
    assert legs["dense_attempt"] < 500
    assert fallback.seen[-1] == (resolved, 4, lote)
    assert fallback.seen[-1][0] is resolved and fallback.seen[-1][2] is lote


def test_primary_success_resets_consecutive_failures() -> None:
    clock = Clock()
    breaker = CircuitBreaker(2, _COOLDOWN_S, clock)
    primary = Scripted(unavailable(FallbackReason.QDRANT_UNAVAILABLE), None)
    retriever = FallbackRetriever(primary, SpyBm25(), None, breaker=breaker)
    assert retriever.retrieve("q", guest(), 3).strategy == "bm25"
    assert retriever.retrieve("q", guest(), 3).strategy == "hybrid"
    assert breaker.state is BreakerState.CLOSED
    primary.fail_with(unavailable(FallbackReason.QDRANT_UNAVAILABLE))
    assert retriever.retrieve("q", guest(), 3).strategy == "bm25"
    assert breaker.state is BreakerState.CLOSED
    primary.fail_with(unavailable(FallbackReason.QDRANT_TIMEOUT))
    assert retriever.retrieve("q", guest(), 3).fallback_reason == "qdrant_timeout"
    assert breaker.state is BreakerState.OPEN


def test_qdrant_http_status_error_propagates_and_is_not_counted() -> None:
    clock = Clock()
    breaker = CircuitBreaker(2, _COOLDOWN_S, clock)
    primary = Scripted(status_error())
    fallback = SpyBm25()
    retriever = FallbackRetriever(primary, fallback, None, breaker=breaker)
    with pytest.raises(UnexpectedResponse):
        retriever.retrieve("q", guest(), 3)
    assert fallback.seen == []
    assert breaker.state is BreakerState.CLOSED
    assert breaker.last_reason is None

    primary.fail_with(unavailable(FallbackReason.QDRANT_UNAVAILABLE))
    retriever.retrieve("q", guest(), 3)
    assert breaker.state is BreakerState.CLOSED
    primary.fail_with(unavailable(FallbackReason.QDRANT_UNAVAILABLE))
    retriever.retrieve("q", guest(), 3)
    assert breaker.state is BreakerState.OPEN


def test_qdrant_http_status_error_during_a_probe_releases() -> None:
    clock = Clock()
    breaker = CircuitBreaker(1, _COOLDOWN_S, clock)
    reason = FallbackReason.QDRANT_TIMEOUT
    primary = Scripted(unavailable(reason))
    fallback = SpyBm25()
    retriever = FallbackRetriever(primary, fallback, None, breaker=breaker)
    retriever.retrieve("q", guest(), 3)
    assert breaker.state is BreakerState.OPEN
    clock.now = _COOLDOWN_S
    primary.fail_with(status_error())
    with pytest.raises(UnexpectedResponse):
        retriever.retrieve("q", guest(), 3)
    assert len(fallback.seen) == 1
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is reason
    assert breaker.admit() is Admission.SKIP


def test_probe_without_a_primary_continues_on_the_hook_retriever() -> None:
    clock = Clock()
    reason = FallbackReason.MODEL_UNAVAILABLE
    breaker = CircuitBreaker(3, _COOLDOWN_S, clock, reason)
    fallback = SpyBm25()
    replacement = Scripted(None)
    calls: list[BreakerState] = []

    def hook() -> Scripted:
        calls.append(breaker.state)
        return replacement

    retriever = FallbackRetriever(
        None, fallback, reason, breaker=breaker, on_probe=hook
    )
    lote = ResolvedLote("ml")
    resolved = guest()
    skipped = retriever.retrieve("q", resolved, 4, lote=lote)
    assert calls == []
    assert skipped.fallback_reason == "model_unavailable"
    assert fallback.seen == [(resolved, 4, lote)]

    clock.now = _COOLDOWN_S
    result = retriever.retrieve("q", resolved, 4, lote=lote)
    assert calls == [BreakerState.HALF_OPEN]
    assert breaker.state is BreakerState.CLOSED
    assert result.strategy == "hybrid"
    assert replacement.seen == [(resolved, 4, lote)]
    assert replacement.seen[0][0] is resolved and replacement.seen[0][2] is lote
    assert len(fallback.seen) == 1


def test_probe_hook_continues_dense_on_the_shared_breaker() -> None:
    clock = Clock()
    reason = FallbackReason.QDRANT_UNAVAILABLE
    breaker = CircuitBreaker(1, _COOLDOWN_S, clock, reason)
    inner_primary = Scripted(None)
    inner = FallbackRetriever(inner_primary, SpyBm25(), None, breaker=breaker)
    outer_bm25 = SpyBm25()

    def hook() -> FallbackRetriever:
        return inner

    outer = FallbackRetriever(None, outer_bm25, reason, breaker=breaker, on_probe=hook)
    clock.now = _COOLDOWN_S
    result = outer.retrieve("q", guest(), 3)
    assert result.strategy == "hybrid"
    assert result.fallback_reason is None
    assert len(inner_primary.seen) == 1
    assert outer_bm25.seen == []
    assert breaker.state is BreakerState.CLOSED


def test_probe_hook_outage_serves_bm25_and_a_raised_error_releases() -> None:
    clock = Clock()
    reason = FallbackReason.QDRANT_UNAVAILABLE
    breaker = CircuitBreaker(1, _COOLDOWN_S, clock, reason)
    fallback = SpyBm25()

    def fail_probe() -> None:
        breaker.record_failure(Admission.PROBE, FallbackReason.QDRANT_TIMEOUT)
        return None

    retriever = FallbackRetriever(
        None, fallback, reason, breaker=breaker, on_probe=fail_probe
    )
    clock.now = _COOLDOWN_S
    served = retriever.retrieve("q", guest(), 3)
    assert served.fallback_reason == "qdrant_timeout"
    assert served.strategy == "bm25"
    assert breaker.state is BreakerState.OPEN
    assert len(fallback.seen) == 1

    clock.now = _COOLDOWN_S + _COOLDOWN_S

    def explode() -> None:
        raise status_error()

    retriever_raises = FallbackRetriever(
        None, fallback, reason, breaker=breaker, on_probe=explode
    )
    with pytest.raises(UnexpectedResponse):
        retriever_raises.retrieve("q", guest(), 3)
    assert len(fallback.seen) == 1
    assert breaker.state is BreakerState.OPEN
    assert breaker.last_reason is FallbackReason.QDRANT_TIMEOUT
    assert breaker.admit() is Admission.SKIP


def _open(factory: Any, breaker: CircuitBreaker, *, rerank: bool = False) -> Any:
    extra: dict[str, Any] = {}
    if rerank:
        extra["reranker_factory"] = RerankerFactory()
    return open_retrieval(
        Strategy.HYBRID,
        settings=load_runtime_settings(RetrievalConfigurationError),
        ingestion_config=load_ingestion_config(REPO_ROOT / "config/ingestion.yaml"),
        retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
        provider="fake",
        repo_root=REPO_ROOT,
        client_factory=factory,
        rerank=rerank,
        breaker=breaker,
        **extra,
    )


def test_open_retrieval_passes_the_breaker_to_every_fallback(
    fake_lexical: Path,  # noqa: F811
    ingested: Any,  # noqa: F811
) -> None:
    clock = Clock()
    plain = CircuitBreaker(3, 30.0, clock, FallbackReason.QDRANT_TIMEOUT)
    opened = _open(Factory(ingested), plain)
    try:
        result = opened.retriever.retrieve("q", access(), 3)
        assert result.strategy == "bm25"
        assert result.fallback_reason == "qdrant_timeout"
        legs = result.leg_latency_ms
        assert legs is not None and legs["dense_attempt"] < 500
    finally:
        opened.close()

    reranked_breaker = CircuitBreaker(3, 30.0, clock, FallbackReason.QDRANT_TIMEOUT)
    reranked = _open(Factory(ingested), reranked_breaker, rerank=True)
    try:
        result = reranked.retriever.retrieve("q", access(), 3)
        assert result.strategy == "bm25"
        assert result.fallback_reason == "qdrant_timeout"
    finally:
        reranked.close()

    # The open failed with qdrant_unavailable. SKIP must report the breaker's
    # reason, which is how a missing `breaker=` argument fails this assertion.
    fallback_breaker = CircuitBreaker(
        3, 30.0, Clock(), FallbackReason.MODEL_UNAVAILABLE
    )
    fallen = _open(client_at(closed_port()), fallback_breaker)
    try:
        result = fallen.retriever.retrieve("q", access(), 3)
        assert fallen.client is None
        assert result.strategy == "bm25"
        assert result.fallback_reason == "model_unavailable"
    finally:
        fallen.close()
