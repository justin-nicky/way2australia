"""Fallback policy for `hybrid` (Spec 008 R6).

`FallbackRetriever` serves BM25 when the dense side is unavailable, either
because the open failed (`primary is None`) or because a query's dense leg
raised `RetrievalUnavailableError`. Nothing else is caught: a BM25 error, an
authorization error or any other error propagates. No state is kept between
queries, so every query tries the primary again (no circuit breaker).
"""

from time import perf_counter

from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import (
    DEFAULT_TOP_K,
    Retriever,
    Strategy,
    validate_request,
)
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
    ) -> None:
        if primary is None and open_reason is None:
            raise ValueError("a missing primary needs an open_reason")
        self._primary = primary
        self._fallback = fallback
        self._open_reason = open_reason

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
    ) -> RetrievalResult:
        validate_request(query_text, top_k)
        started = perf_counter()
        reason = self._open_reason
        if self._primary is not None:
            try:
                result = self._primary.retrieve(query_text, access, top_k)
            except RetrievalUnavailableError as error:
                reason = error.reason
            else:
                return result.model_copy(
                    update={"requested_strategy": Strategy.HYBRID.value}
                )
        assert reason is not None
        attempt_ms = (perf_counter() - started) * 1000.0
        served = self._fallback.retrieve(query_text, access, top_k)
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
