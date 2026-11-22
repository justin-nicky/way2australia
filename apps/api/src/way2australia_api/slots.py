"""Answer slots (Spec 013 R10).

`try_acquire` never blocks. A slot whose generation outlived its cap is
transferred to the abandoned work and released when that work ends, so a
runaway generation keeps its slot (and is visible in readiness).
"""

from threading import Lock

from way2australia_rag.generation.deadline import AbandonedWork

_HELD, _TRANSFERRED, _RELEASED = "held", "transferred", "released"


class SlotPool:
    def __init__(self, max_in_flight: int) -> None:
        self._max = max_in_flight
        self._lock = Lock()
        self._in_flight = 0
        self._abandoned = 0

    def try_acquire(self) -> "Slot | None":
        with self._lock:
            if self._in_flight >= self._max:
                return None
            self._in_flight += 1
        return Slot(self)

    @property
    def in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    @property
    def abandoned_in_flight(self) -> int:
        with self._lock:
            return self._abandoned


class Slot:
    def __init__(self, pool: SlotPool) -> None:
        self._pool = pool
        self._state = _HELD

    def release(self) -> None:
        """Idempotent; a no-op once the slot belongs to abandoned work."""
        pool = self._pool
        with pool._lock:
            if self._state != _HELD:
                return
            self._state = _RELEASED
            pool._in_flight -= 1

    def transfer(self, work: AbandonedWork) -> None:
        pool = self._pool
        with pool._lock:
            if self._state != _HELD:
                return
            self._state = _TRANSFERRED
            pool._abandoned += 1
        work.add_done_callback(self._finish)

    def _finish(self) -> None:
        pool = self._pool
        with pool._lock:
            if self._state != _TRANSFERRED:
                return
            self._state = _RELEASED
            pool._abandoned -= 1
            pool._in_flight -= 1
