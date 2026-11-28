"""Startup, readiness, fake mode and shutdown (Spec 013 R2, R8, R16)."""

import logging
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from way2australia_api.config import Settings
from way2australia_api.lifespan import StartupError
from way2australia_api.main import create_app

from .support import (
    SENTINEL_KEY,
    SENTINEL_URL,
    CountingClient,
    CountingEmbedder,
    CountingGenerator,
    CountingReranker,
    down_client,
    fake_settings,
    indexed_client,
    stack_factory,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)


def wait_for(predicate: Any, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "timed out"
        time.sleep(0.02)


def ready_body(client: TestClient) -> tuple[int, dict[str, Any]]:
    response = client.get("/ready")
    return response.status_code, response.json()


def assert_safe(message: str, tmp_path: Path) -> None:
    assert str(tmp_path) not in message
    assert SENTINEL_KEY not in message
    assert SENTINEL_URL not in message


# --- phase 1 failures stop startup -----------------------------------------------


def start(settings: Any, **kwargs: Any) -> None:
    with TestClient(create_app(settings, **kwargs)):
        pass


def test_invalid_serving_config_stops_startup(
    tmp_path: Path, generators: list[CountingGenerator]
) -> None:
    bad = tmp_path / "serving.yaml"
    bad.write_text("schema_version: '1.0'\nunknown_key: 1\n", encoding="utf-8")
    with pytest.raises(StartupError) as caught:
        start(fake_settings(serving_config=bad))
    assert "serving config" in str(caught.value)
    assert_safe(str(caught.value), tmp_path)
    assert generators == []  # failed before the generator was built


def test_unknown_prompt_stops_startup_before_a_generator_is_built(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    generators: list[CountingGenerator],
) -> None:
    from way2australia_api import lifespan

    real = lifespan.load_generation_config

    def wrong_prompt(*args: Any, **kwargs: Any) -> Any:
        config = real(*args, **kwargs)
        return config.model_copy(
            update={"prompt": config.prompt.model_copy(update={"version": 99})}
        )

    monkeypatch.setattr(lifespan, "load_generation_config", wrong_prompt)
    with pytest.raises(StartupError) as caught:
        start(fake_settings())
    assert "PromptConfigurationError" in str(caught.value)
    assert_safe(str(caught.value), tmp_path)
    # The prompt is read before the generator is built.
    assert generators == []


def test_tokenizer_mismatch_stops_startup_and_closes_the_generator_once(
    tmp_path: Path,
    fake_lexical: Path,
    monkeypatch: pytest.MonkeyPatch,
    generators: list[CountingGenerator],
    lexical_handles: dict[str, int],
) -> None:
    from way2australia_api import lifespan

    real = lifespan.load_retrieval_config

    def other_tokenizer(path: Path) -> Any:
        config = real(path)
        return config.model_copy(
            update={
                "lexical": config.lexical.model_copy(update={"tokenizer": "lexical-v1"})
            }
        )

    monkeypatch.setattr(lifespan, "load_retrieval_config", other_tokenizer)
    with pytest.raises(StartupError) as caught:
        start(fake_settings())
    assert "tokenizer" in str(caught.value)
    assert_safe(str(caught.value), tmp_path)
    assert [g.closed for g in generators] == [1]
    assert lexical_handles["opened"] == lexical_handles["closed"] == 1


def test_missing_lexical_file_stops_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    generators: list[CountingGenerator],
) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(empty))
    with pytest.raises(StartupError) as caught:
        start(fake_settings())
    assert "does not exist" in str(caught.value)
    assert_safe(str(caught.value), tmp_path)
    assert [g.closed for g in generators] == [1]


def test_unexpected_phase_one_error_reports_the_class_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from way2australia_api import lifespan

    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError(f"cannot open {tmp_path} {SENTINEL_KEY}")

    monkeypatch.setattr(lifespan, "load_retrieval_config", boom)
    with pytest.raises(StartupError) as caught:
        start(fake_settings())
    assert str(caught.value) == "startup failed: OSError"


# --- readiness ---------------------------------------------------------------


def test_readiness_is_starting_while_the_loader_blocks_then_ok(
    fake_lexical: Path, generators: list[CountingGenerator]
) -> None:
    gate = threading.Event()
    client = indexed_client()
    app = create_app(fake_settings(), stack_factory=stack_factory(client, gate=gate))
    with TestClient(app) as http:
        status, body = ready_body(http)
        assert (status, body) == (503, {"status": "starting", "fake": True})
        assert http.get("/health").json() == {"status": "ok"}
        gate.set()
        wait_for(lambda: ready_body(http)[0] == 200)
        status, body = ready_body(http)
        assert status == 200
        assert body == {
            "status": "ok",
            "degraded_reasons": [],
            "breaker": "closed",
            "fake": True,
        }
    assert client.close_calls == 1


def test_breaker_open_start_is_degraded(
    fake_lexical: Path, generators: list[CountingGenerator]
) -> None:
    app = create_app(fake_settings(), stack_factory=stack_factory(down_client()))
    with TestClient(app) as http:
        wait_for(lambda: ready_body(http)[0] == 200)
        _status, body = ready_body(http)
        assert body["status"] == "degraded"
        assert body["degraded_reasons"] == ["dense_circuit_open"]
        assert body["breaker"] == "open"


def test_reranker_skip_is_degraded(
    fake_lexical: Path, generators: list[CountingGenerator]
) -> None:
    factory = stack_factory(
        indexed_client(), reranker=CountingReranker(fail_on_load=True)
    )
    app = create_app(fake_settings(), stack_factory=factory)
    with TestClient(app) as http:
        wait_for(lambda: ready_body(http)[0] == 200)
        _status, body = ready_body(http)
        assert body["status"] == "degraded"
        assert body["degraded_reasons"] == ["rerank_skipped"]
        assert body["breaker"] == "closed"


def test_phase_two_non_eligible_error_fails_and_calls_on_fatal(
    fake_lexical: Path,
    generators: list[CountingGenerator],
    lexical_handles: dict[str, int],
) -> None:
    from qdrant_client import QdrantClient

    empty = CountingClient(QdrantClient(":memory:"))  # no collection: not eligible
    fatal = threading.Event()
    app = create_app(
        fake_settings(), stack_factory=stack_factory(empty), on_fatal=fatal.set
    )
    with TestClient(app) as http:
        assert fatal.wait(10)
        assert ready_body(http) == (503, {"status": "failed", "fake": True})
        assert http.get("/health").status_code == 200
        # Everything opened is closed, the generator exactly once.
        assert [g.closed for g in generators] == [1]
        assert empty.close_calls == 1
        assert lexical_handles["opened"] == lexical_handles["closed"]
    assert [g.closed for g in generators] == [1]  # shutdown closes nothing twice


def test_health_response_is_unchanged() -> None:
    response = TestClient(create_app(fake_settings())).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- fake mode -------------------------------------------------------------------


def test_fake_mode_reports_fake_and_logs_a_warning(
    fake_lexical: Path,
    generators: list[CountingGenerator],
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = create_app(fake_settings(), stack_factory=stack_factory(indexed_client()))
    with caplog.at_level(logging.WARNING, logger="way2australia_api.lifespan"):
        with TestClient(app) as http:
            wait_for(lambda: ready_body(http)[0] == 200)
            assert ready_body(http)[1]["fake"] is True
    assert any("fake mode" in record.getMessage() for record in caplog.records)


def test_real_mode_readiness_is_not_fake() -> None:
    settings = Settings(repo_root=Path("."), api_fake=False)
    status, body = ready_body(TestClient(create_app(settings)))
    assert status == 503 and body["fake"] is False


def test_api_fake_reads_w2a_api_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    assert Settings().api_fake is False
    monkeypatch.setenv("W2A_API_FAKE", "1")
    assert Settings().api_fake is True


# --- shutdown --------------------------------------------------------------------


def test_shutdown_closes_every_resource_once(
    fake_lexical: Path,
    generators: list[CountingGenerator],
    lexical_handles: dict[str, int],
) -> None:
    client = indexed_client()
    embedders: list[CountingEmbedder] = []

    def embedder(config: Any, _provider: str) -> CountingEmbedder:
        embedders.append(CountingEmbedder(config.embedder.fake_vector_size))
        return embedders[-1]

    reranker = CountingReranker()
    factory = stack_factory(client, reranker=reranker, embedder=embedder)
    app = create_app(fake_settings(), stack_factory=factory)
    with TestClient(app) as http:
        wait_for(lambda: ready_body(http)[0] == 200)
        assert [g.closed for g in generators] == [0]
    assert [g.closed for g in generators] == [1]
    assert client.close_calls == 1
    assert [e.closed for e in embedders] == [1]
    assert reranker.closed == 1
    assert lexical_handles["opened"] == lexical_handles["closed"] == 2


def test_shutdown_before_the_loader_finishes_closes_what_it_opens(
    fake_lexical: Path, generators: list[CountingGenerator]
) -> None:
    gate = threading.Event()
    client = indexed_client()
    app = create_app(fake_settings(), stack_factory=stack_factory(client, gate=gate))
    with TestClient(app):
        pass  # shut down while the loader still waits
    gate.set()
    wait_for(lambda: client.close_calls == 1)
    assert [g.closed for g in generators] == [1]
