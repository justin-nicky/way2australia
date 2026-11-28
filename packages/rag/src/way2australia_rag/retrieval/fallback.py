"""Fallback policy for `hybrid` (Spec 008 R6, Spec 013 R4).

`FallbackRetriever` serves BM25 when the dense side is unavailable, either
because the open failed (`primary is None`) or because a query's dense leg
raised `RetrievalUnavailableError`. Nothing else is caught: a BM25 error, an
authorization error or any other error propagates.

With `breaker=None` (the CLIs, D058) no state is kept, so every query tries
the primary again. A breaker skips the dense leg while it is open and allows
one probe after the cool-down. `on_probe` is the BM25-only hook (no primary):
T5 calls it on that probe. The hook may return the retriever this request
should continue on; `None` serves BM25. The hook owns `record_failure` and
`release`. If it returns a retriever while the probe is still half-open, this
class records success before continuing, so access and `lote` stay on the
retrieve call.
"""

from collections.abc import Callable
from time import perf_counter

from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import (
    DEFAULT_TOP_K,
    Retriever,
    Strategy,
    validate_request,
)
from way2australia_rag.retrieval.breaker import Admission, BreakerState, CircuitBreaker
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.models import RetrievalResult


class FallbackRetriever:
    strategy = Strategy.HYBRID

    def __init__(
        self,
        primary: Retriever | None,
        fallback: Retriever,
        open_reason: FallbackReason | None,
        *,
        breaker: CircuitBreaker | None = None,
        on_probe: Callable[[], Retriever | None] | None = None,
    ) -> None:
        if primary is None and open_reason is None:
            raise ValueError("a missing primary needs an open_reason")
        self._primary = primary
        self._fallback = fallback
        self._open_reason = open_reason
        self._breaker = breaker
        self._on_probe = on_probe

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
        *,
        lote: ResolvedLote | None = None,
    ) -> RetrievalResult:
        validate_request(query_text, top_k)
        started = perf_counter()
        if self._breaker is None:
            return self._retrieve_without_breaker(
                query_text, access, top_k, lote, started
            )
        return self._retrieve_with_breaker(query_text, access, top_k, lote, started)

    def _retrieve_without_breaker(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int,
        lote: ResolvedLote | None,
        started: float,
    ) -> RetrievalResult:
        reason = self._open_reason
        if self._primary is not None:
            try:
                result = self._primary.retrieve(query_text, access, top_k, lote=lote)
            except RetrievalUnavailableError as error:
                reason = error.reason
            else:
                return result.model_copy(
                    update={"requested_strategy": Strategy.HYBRID.value}
                )
        assert reason is not None
        return self._serve(reason, started, query_text, access, top_k, lote)

    def _retrieve_with_breaker(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int,
        lote: ResolvedLote | None,
        started: float,
    ) -> RetrievalResult:
        breaker = self._breaker
        assert breaker is not None
        admission = breaker.admit()
        if admission is Admission.SKIP or (
            self._primary is None and admission is not Admission.PROBE
        ):
            reason = (
                breaker.last_reason
                if admission is Admission.SKIP
                else self._open_reason
            )
            assert reason is not None
            return self._serve(reason, started, query_text, access, top_k, lote)
        if self._primary is None:
            return self._probe_without_primary(
                breaker, started, query_text, access, top_k, lote
            )
        try:
            result = self._primary.retrieve(query_text, access, top_k, lote=lote)
        except RetrievalUnavailableError as error:
            breaker.record_failure(admission, error.reason)
            reason = error.reason
        except BaseException:
            if admission is Admission.PROBE:
                breaker.release(admission)
            raise
        else:
            breaker.record_success(admission)
            return result.model_copy(
                update={"requested_strategy": Strategy.HYBRID.value}
            )
        return self._serve(reason, started, query_text, access, top_k, lote)

    def _probe_without_primary(
        self,
        breaker: CircuitBreaker,
        started: float,
        query_text: str,
        access: ResolvedAccess,
        top_k: int,
        lote: ResolvedLote | None,
    ) -> RetrievalResult:
        replacement: Retriever | None = None
        if self._on_probe is None:
            breaker.release(Admission.PROBE)
        else:
            try:
                replacement = self._on_probe()
            except BaseException:
                if breaker.state is BreakerState.HALF_OPEN:
                    breaker.release(Admission.PROBE)
                raise
            if replacement is not None and breaker.state is BreakerState.HALF_OPEN:
                breaker.record_success(Admission.PROBE)
            elif replacement is None and breaker.state is BreakerState.HALF_OPEN:
                breaker.release(Admission.PROBE)
        if replacement is not None:
            return replacement.retrieve(query_text, access, top_k, lote=lote)
        reason = breaker.last_reason
        assert reason is not None
        return self._serve(reason, started, query_text, access, top_k, lote)

    def _serve(
        self,
        reason: FallbackReason,
        started: float,
        query_text: str,
        access: ResolvedAccess,
        top_k: int,
        lote: ResolvedLote | None,
    ) -> RetrievalResult:
        attempt_ms = (perf_counter() - started) * 1000.0
        served = self._fallback.retrieve(query_text, access, top_k, lote=lote)
        return served.model_copy(
            update={
                "requested_strategy": Strategy.HYBRID.value,
                "fallback_reason": reason.value,
                "latency_ms": attempt_ms + served.latency_ms,
                "leg_latency_ms": {
                    "dense_attempt": attempt_ms,
                    "bm25": served.latency_ms,
                },
            }
        )
