"""Concurrent answer requests and a dense re-open under that load (Spec 013 R7).

Threads call one `TestClient`. Fakes only: no real model or API. `max_in_flight`
is raised so the cap does not turn the burst into 503s.
"""

import threading
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from way2australia_api.main import create_app
from way2australia_rag.retrieval.breaker import BreakerState
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.serving.readiness import Readiness
from way2australia_rag.serving.stack import (
    ServingInputs,
    StackHolder,
    open_serving_stack,
)

from .support import down_client, fake_settings, indexed_client, stack_factory
from .test_answer_route import QUERY, wait_for, write_serving

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BURST = 16


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class _Switch:
    """Client factory whose target can change while requests are in flight."""

    def __init__(self, target: Any) -> None:
        self.target = target

    def __call__(self, _settings: object) -> Any:
        return self.target


def _burst(client: TestClient, body: dict[str, Any], n: int = BURST) -> list[Any]:
    results: list[Any] = [None] * n
    errors: list[BaseException] = []
    barrier = threading.Barrier(n)
    lock = threading.Lock()

    def run(index: int) -> None:
        try:
            barrier.wait(10)
            results[index] = client.post("/v1/answer", json=body)
        except BaseException as exc:  # noqa: BLE001 - reported below
            with lock:
                errors.append(exc)

    threads = [threading.Thread(target=run, args=(index,)) for index in range(n)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
        assert not thread.is_alive()
    assert errors == []
    return results


def _comparable(response: Any) -> dict[str, Any]:
    assert response.status_code == 200, response.text
    payload: dict[str, Any] = response.json()
    payload.pop("request_id")
    return payload


def _ready_app(tmp_path: Path, factory: Any) -> TestClient:
    app = create_app(
        fake_settings(
            serving_config=write_serving(tmp_path, concurrency={"max_in_flight": BURST})
        ),
        stack_factory=factory,
        on_fatal=lambda: None,
    )
    client = TestClient(app, raise_server_exceptions=False)
    client.__enter__()
    wait_for(lambda: client.get("/ready").status_code == 200)
    return client


@pytest.mark.parametrize("mode", ["bm25", "hybrid"])
def test_concurrent_requests_match_the_same_request_alone(
    mode: str, fake_lexical: Path, tmp_path: Path
) -> None:
    assert fake_lexical.is_dir()
    target = down_client() if mode == "bm25" else indexed_client()
    client = _ready_app(tmp_path, stack_factory(target))
    try:
        body = {"query": QUERY}
        alone = _comparable(client.post("/v1/answer", json=body))
        for response in _burst(client, body):
            assert _comparable(response) == alone
    finally:
        client.__exit__(None, None, None)


def test_reopen_during_concurrent_requests_drains_the_old_stack(
    fake_lexical: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert fake_lexical.is_dir()
    clock = _Clock()
    switch = _Switch(down_client())
    up = indexed_client()

    def factory(inputs: ServingInputs, readiness: Readiness) -> StackHolder:
        opened = ServingInputs(
            **{**inputs.__dict__, "client_factory": switch, "clock": clock}
        )
        return open_serving_stack(opened, readiness)

    release = threading.Event()
    arrived = {"n": 0}
    lock = threading.Lock()
    original = FallbackRetriever.retrieve

    def wrapped(self: FallbackRetriever, *args: Any, **kwargs: Any) -> Any:
        if not release.is_set():
            with lock:
                arrived["n"] += 1
                last = arrived["n"] == BURST
            if last:
                switch.target = up
                cooldown = client.app.state.serving_config.breaker.cooldown_s  # type: ignore[attr-defined]
                clock.now += cooldown + 1
                release.set()
            else:
                assert release.wait(20)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(FallbackRetriever, "retrieve", wrapped)
    client = _ready_app(tmp_path, factory)
    try:
        holder = client.app.state.loader.holder  # type: ignore[attr-defined]
        assert holder.breaker is not None
        assert holder.breaker.state is BreakerState.OPEN
        with holder.acquire() as old:
            assert old.dense is False
        results = _burst(client, {"query": QUERY})
        assert holder.dense
        assert holder.breaker.state is BreakerState.CLOSED
        assert old.retired
        assert old.opened.lexical is None
        assert all(response.status_code == 200 for response in results)
    finally:
        client.__exit__(None, None, None)
