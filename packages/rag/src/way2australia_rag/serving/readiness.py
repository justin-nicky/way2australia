"""Readiness state for `GET /ready` (Spec 013 R8).

State names and reason codes only: no path, URL, collection name or exception
text. Breaker reasons are derived at read time from the breaker the holder
currently owns; `abandoned_generation` comes from a provider callback the API
registers (the slot pool), so this module does not depend on `apps/api`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from threading import Lock
from typing import Any

from way2australia_rag.retrieval.breaker import BreakerState, CircuitBreaker


class Phase(StrEnum):
    STARTING = "starting"
    READY = "ready"
    FAILED = "failed"


class DegradedReason(StrEnum):
    DENSE_CIRCUIT_OPEN = "dense_circuit_open"
    DENSE_CIRCUIT_HALF_OPEN = "dense_circuit_half_open"
    RERANK_SKIPPED = "rerank_skipped"
    DENSE_REOPEN_REFUSED = "dense_reopen_refused"
    ABANDONED_GENERATION = "abandoned_generation"


@dataclass(frozen=True)
class ReadinessSnapshot:
    status: str  # starting | failed | ok | degraded
    degraded_reasons: tuple[str, ...]
    breaker: str | None
    abandoned_in_flight: int | None
    fake: bool

    @property
    def http_status(self) -> int:
        return 200 if self.status in ("ok", "degraded") else 503

    def to_body(self) -> dict[str, Any]:
        if self.status in ("starting", "failed"):
            return {"status": self.status, "fake": self.fake}
        body: dict[str, Any] = {
            "status": self.status,
            "degraded_reasons": list(self.degraded_reasons),
            "breaker": self.breaker,
            "fake": self.fake,
        }
        if self.abandoned_in_flight is not None:
            body["abandoned_in_flight"] = self.abandoned_in_flight
        return body


class Readiness:
    def __init__(self, *, fake: bool = False) -> None:
        self._lock = Lock()
        self._phase = Phase.STARTING
        self._fake = fake
        self._rerank_skipped = False
        self._reopen_refused = False
        self._breaker_provider: Callable[[], CircuitBreaker | None] = lambda: None
        self._abandoned_provider: Callable[[], int] = lambda: 0

    @property
    def phase(self) -> Phase:
        with self._lock:
            return self._phase

    def set_ready(self) -> None:
        with self._lock:
            self._phase = Phase.READY

    def set_failed(self) -> None:
        with self._lock:
            self._phase = Phase.FAILED

    def set_rerank_skipped(self, value: bool) -> None:
        with self._lock:
            self._rerank_skipped = value

    def set_reopen_refused(self, value: bool) -> None:
        with self._lock:
            self._reopen_refused = value

    def set_breaker_provider(
        self, provider: Callable[[], CircuitBreaker | None]
    ) -> None:
        with self._lock:
            self._breaker_provider = provider

    def set_abandoned_provider(self, provider: Callable[[], int]) -> None:
        with self._lock:
            self._abandoned_provider = provider

    def snapshot(self) -> ReadinessSnapshot:
        with self._lock:
            phase = self._phase
            fake = self._fake
            rerank_skipped = self._rerank_skipped
            reopen_refused = self._reopen_refused
            breaker_provider = self._breaker_provider
            abandoned_provider = self._abandoned_provider
        if phase is not Phase.READY:
            return ReadinessSnapshot(phase.value, (), None, None, fake)
        breaker = breaker_provider()
        state = breaker.state if breaker is not None else BreakerState.CLOSED
        abandoned = abandoned_provider()
        reasons: list[DegradedReason] = []
        if state is BreakerState.OPEN:
            reasons.append(DegradedReason.DENSE_CIRCUIT_OPEN)
        elif state is BreakerState.HALF_OPEN:
            reasons.append(DegradedReason.DENSE_CIRCUIT_HALF_OPEN)
        if rerank_skipped:
            reasons.append(DegradedReason.RERANK_SKIPPED)
        if reopen_refused:
            reasons.append(DegradedReason.DENSE_REOPEN_REFUSED)
        if abandoned > 0:
            reasons.append(DegradedReason.ABANDONED_GENERATION)
        return ReadinessSnapshot(
            "degraded" if reasons else "ok",
            tuple(reason.value for reason in reasons),
            state.value,
            abandoned if abandoned > 0 else None,
            fake,
        )
