"""Wall-clock cap for one generation call (Spec 013 R6).

The worker is a daemon thread. A pool worker is joined at interpreter exit and
would make a CLI hang after the cap. Abandoned work keeps running; its result
is discarded and a late exception is logged by class name only.
"""

import logging
import threading
import time
from collections.abc import Callable
from typing import TypeVar

from way2australia_rag.generation.errors import (
    GeneratorUnavailableError,
    UnavailableReason,
)

T = TypeVar("T")

_log = logging.getLogger(__name__)


class AbandonedWork:
    """A generation call that outlived its cap. Callbacks run once, at the end."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[], None]] = []
        self._done = False

    def add_done_callback(self, fn: Callable[[], None]) -> None:
        with self._lock:
            if self._done:
                run_now = True
            else:
                self._callbacks.append(fn)
                run_now = False
        if run_now:
            fn()

    def _finish(self) -> None:
        with self._lock:
            self._done = True
            callbacks = self._callbacks
            self._callbacks = []
        for fn in callbacks:
            fn()


class _Run:
    def __init__(self) -> None:
        self.abandoned = False
        self.finished = False


def _log_abandoned(error: Exception) -> None:
    # Class only: client messages can carry URLs or credentials.
    _log.warning("abandoned generation work raised %s", type(error).__name__)


def run_with_cap(
    fn: Callable[[], T],
    cap_s: float,
    *,
    on_abandoned: Callable[[AbandonedWork], None] | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> T:
    """Run `fn` on a daemon thread and wait at most `cap_s` seconds.

    On time, return the result or re-raise the exception. Past the cap, call
    `on_abandoned` and raise `GeneratorUnavailableError(DEADLINE)`.
    """
    done = threading.Event()
    lock = threading.Lock()
    state = _Run()
    work = AbandonedWork()
    outcome: list[T] = []
    error: list[Exception] = []

    def worker() -> None:
        try:
            outcome.append(fn())
        except Exception as exc:
            error.append(exc)
        finally:
            with lock:
                state.finished = True
                abandoned = state.abandoned
            if abandoned and error:
                _log_abandoned(error[0])
            try:
                work._finish()
            finally:
                done.set()

    threading.Thread(target=worker, daemon=True).start()
    started = clock()
    remaining = cap_s - (clock() - started)
    if remaining < 0:
        remaining = 0.0
    finished_in_time = done.wait(remaining)
    if not finished_in_time:
        with lock:
            if state.finished:
                finished_in_time = True
            else:
                state.abandoned = True
    if finished_in_time:
        if error:
            raise error[0]
        if not outcome:
            raise GeneratorUnavailableError(UnavailableReason.DEADLINE)
        return outcome[0]
    if on_abandoned is not None:
        on_abandoned(work)
    raise GeneratorUnavailableError(UnavailableReason.DEADLINE)
