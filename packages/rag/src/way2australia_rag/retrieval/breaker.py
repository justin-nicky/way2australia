"""Circuit breaker for the dense leg of hybrid (Spec 013 R4).

One lock covers every transition. Closed admits every caller. After
`failure_threshold` consecutive eligible failures the breaker is open until
the cool-down ends, then exactly one caller is the probe. `release` ends a
probe that has no eligible verdict: it opens a new cool-down and does not
count a failure.
"""

import time
from collections.abc import Callable
from enum import StrEnum
from threading import Lock

from way2australia_rag.retrieval.errors import FallbackReason


class BreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class Admission(StrEnum):
    DENSE = "dense"
    PROBE = "probe"
    SKIP = "skip"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        cooldown_s: float,
        clock: Callable[[], float] = time.monotonic,
        open_reason: FallbackReason | None = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_s = cooldown_s
        self._clock = clock
        self._lock = Lock()
        self._consecutive_failures = 0
        self._open_until: float | None = None
        if open_reason is None:
            self._state = BreakerState.CLOSED
            self._last_reason: FallbackReason | None = None
        else:
            self._state = BreakerState.OPEN
            self._last_reason = FallbackReason(open_reason)
            self._open_until = clock() + cooldown_s

    def admit(self) -> Admission:
        with self._lock:
            if self._state is BreakerState.CLOSED:
                return Admission.DENSE
            if self._state is BreakerState.HALF_OPEN:
                return Admission.SKIP
            if self._open_until is None or self._clock() >= self._open_until:
                self._state = BreakerState.HALF_OPEN
                return Admission.PROBE
            return Admission.SKIP

    def record_success(self, admission: Admission) -> None:
        with self._lock:
            if admission is Admission.DENSE and self._state is BreakerState.CLOSED:
                self._consecutive_failures = 0
                return
            if admission is Admission.PROBE and self._state is BreakerState.HALF_OPEN:
                self._close()

    def record_failure(self, admission: Admission, reason: FallbackReason) -> None:
        with self._lock:
            reason = FallbackReason(reason)
            if admission is Admission.DENSE and self._state is BreakerState.CLOSED:
                self._consecutive_failures += 1
                self._last_reason = reason
                if self._consecutive_failures >= self._failure_threshold:
                    self._open()
                return
            if admission is Admission.PROBE and self._state is BreakerState.HALF_OPEN:
                self._consecutive_failures += 1
                self._last_reason = reason
                self._open()

    def release(self, admission: Admission) -> None:
        """End a probe with no eligible verdict. Does not count a failure."""
        with self._lock:
            if admission is Admission.PROBE and self._state is BreakerState.HALF_OPEN:
                self._open()

    @property
    def state(self) -> BreakerState:
        with self._lock:
            return self._state

    @property
    def last_reason(self) -> FallbackReason | None:
        with self._lock:
            return self._last_reason

    def _open(self) -> None:
        self._state = BreakerState.OPEN
        self._open_until = self._clock() + self._cooldown_s

    def _close(self) -> None:
        self._state = BreakerState.CLOSED
        self._consecutive_failures = 0
        self._open_until = None
