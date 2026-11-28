"""Hard generation cap (Spec 013 R6): daemon worker, per-call deadline, CLI path."""

import logging
import subprocess
import sys
import threading
import time
from typing import Any

import pytest
from qdrant_client import QdrantClient
from way2australia_rag.generation import cli
from way2australia_rag.generation.anthropic_api import AnthropicGenerator
from way2australia_rag.generation.base import GeneratorOutput
from way2australia_rag.generation.bedrock import BedrockGenerator
from way2australia_rag.generation.config import AnthropicConfig
from way2australia_rag.generation.deadline import AbandonedWork, run_with_cap
from way2australia_rag.generation.errors import (
    GeneratorUnavailableError,
    UnavailableReason,
)
from way2australia_rag.generation.fake import FakeGenerator, default_fake_info
from way2australia_rag.generation.models import AnswerReason, AnswerStatus
from way2australia_rag.generation.prompts import RenderedPrompt
from way2australia_rag.ingestion import cli as ingestion_cli

from .support import REPO_ROOT, rendered_prompt
from .test_ask_cli import QUERY, SHARED, Factory
from .test_bedrock import APITimeoutError, Clock, StubClient, _config, _message
from .test_service import ACCESS, service

_CAP_S = 0.3
_TOLERANCE_S = 0.5


class BlockingGenerator:
    """Blocks in `generate` until `release` is set. Cap is 0.3 s."""

    def __init__(self, release: threading.Event) -> None:
        self._release = release
        self.finished = threading.Event()
        self.calls = 0
        self.seen_deadline: float | None = None
        self.entered_at: float | None = None
        self.info = default_fake_info()
        self.closed = False

    @property
    def deadline_s(self) -> float:
        return _CAP_S

    def generate(
        self, prompt: RenderedPrompt, *, deadline_s: float | None = None
    ) -> GeneratorOutput:
        self.calls += 1
        self.seen_deadline = deadline_s
        self.entered_at = time.perf_counter()
        # 1 s safety so a missed release cannot stall the suite.
        self._release.wait(timeout=1.0)
        self.finished.set()
        return FakeGenerator().generate(prompt)

    def close(self) -> None:
        self.closed = True
        self._release.set()
        if self.calls:
            assert self.finished.wait(timeout=1.0)


def _track_threads(monkeypatch: pytest.MonkeyPatch) -> list[threading.Thread]:
    spawned: list[threading.Thread] = []
    real = threading.Thread

    def tracking(*args: Any, **kwargs: Any) -> threading.Thread:
        thread = real(*args, **kwargs)
        spawned.append(thread)
        return thread

    monkeypatch.setattr(
        "way2australia_rag.generation.deadline.threading.Thread", tracking
    )
    return spawned


def _join(spawned: list[threading.Thread], release: threading.Event) -> None:
    release.set()
    for thread in spawned:
        thread.join(timeout=1.0)
        assert not thread.is_alive()


def test_fake_generator_has_no_deadline_and_accepts_the_argument() -> None:
    generator = FakeGenerator()
    assert generator.deadline_s is None
    output = generator.generate(rendered_prompt(), deadline_s=1.0)
    assert output.answerable is True


def test_claude_generators_report_their_configured_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = Clock()
    bedrock = BedrockGenerator(
        _config(),
        "test-model",
        "cli",
        client=StubClient([], clock),
        clock=clock,
        sleep=clock.sleep,
    )
    assert bedrock.deadline_s == 30
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    anthropic = AnthropicGenerator(
        AnthropicConfig(
            model_id=None,
            effort="low",
            max_tokens=1024,
            request_timeout_s=20,
            retries=2,
            backoff_s=1.0,
            deadline_s=30,
        ),
        "claude-sonnet-5-5",
        "cli",
        client=StubClient([], clock),
        clock=clock,
        sleep=clock.sleep,
    )
    assert anthropic.deadline_s == 30


def test_per_call_deadline_starts_no_attempt_when_nothing_usable_remains() -> None:
    """Config allows 30 s; a 1 s per-call cap leaves no attempt (min is 1 s)."""
    clock = Clock()
    client = StubClient([_message()], clock)
    generator = BedrockGenerator(
        _config(),
        "test-model",
        "cli",
        client=client,
        clock=clock,
        sleep=clock.sleep,
    )
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt(), deadline_s=1.0)
    assert caught.value.reason == UnavailableReason.DEADLINE
    assert client.requests == []
    assert clock.sleeps == []


def test_a_larger_per_call_deadline_does_not_extend_the_configured_one() -> None:
    clock = Clock()
    client = StubClient([_message()], clock)
    generator = BedrockGenerator(
        _config(request_timeout_s=1, deadline_s=1),
        "test-model",
        "cli",
        client=client,
        clock=clock,
        sleep=clock.sleep,
    )
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt(), deadline_s=30)
    assert caught.value.reason == UnavailableReason.DEADLINE
    assert client.requests == []


def test_no_attempt_starts_after_the_per_call_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One attempt fits in the per-call cap; the retry does not, despite config 30 s."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    for build in (_bedrock, _anthropic):
        clock = Clock()
        client = StubClient([(3.0, APITimeoutError()), _message()], clock)
        generator = build(client, clock)
        with pytest.raises(GeneratorUnavailableError) as caught:
            generator.generate(rendered_prompt(), deadline_s=4.0)
        assert caught.value.reason == UnavailableReason.TIMEOUT
        assert len(client.requests) == 1
        assert client.timeouts == [pytest.approx(4.0)]
        assert clock.sleeps == []


def _bedrock(client: StubClient, clock: Clock) -> BedrockGenerator:
    return BedrockGenerator(
        _config(),
        "test-model",
        "cli",
        client=client,
        clock=clock,
        sleep=clock.sleep,
    )


def _anthropic(client: StubClient, clock: Clock) -> AnthropicGenerator:
    return AnthropicGenerator(
        AnthropicConfig(
            model_id=None,
            effort="low",
            max_tokens=1024,
            request_timeout_s=20,
            retries=2,
            backoff_s=1.0,
            deadline_s=30,
        ),
        "claude-sonnet-5-5",
        "cli",
        client=client,
        clock=clock,
        sleep=clock.sleep,
    )


def test_run_with_cap_returns_or_reraises_when_the_work_finishes(
    caplog: pytest.LogCaptureFixture,
) -> None:
    assert run_with_cap(lambda: 7, 1.0) == 7

    def fail() -> None:
        raise RuntimeError("boom")

    with caplog.at_level(logging.WARNING):
        with pytest.raises(RuntimeError, match="boom"):
            run_with_cap(fail, 1.0)
    assert "abandoned generation work" not in caplog.text


def test_abandoned_work_logs_the_class_and_a_late_callback_runs_at_once(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    release = threading.Event()
    spawned = _track_threads(monkeypatch)
    saved: list[AbandonedWork] = []

    def fn() -> None:
        release.wait(timeout=1.0)
        raise RuntimeError("sentinel-not-for-logs")

    try:
        with caplog.at_level(
            logging.WARNING, logger="way2australia_rag.generation.deadline"
        ):
            with pytest.raises(GeneratorUnavailableError) as caught:
                run_with_cap(fn, 0.05, on_abandoned=saved.append)
            assert caught.value.reason == UnavailableReason.DEADLINE
            assert len(saved) == 1
            ran = threading.Event()
            saved[0].add_done_callback(ran.set)
            assert not ran.is_set()
            release.set()
            assert ran.wait(timeout=1.0)
            immediate: list[str] = []
            saved[0].add_done_callback(lambda: immediate.append("now"))
            assert immediate == ["now"]
        text = caplog.text
        assert "RuntimeError" in text
        assert "sentinel-not-for-logs" not in text
        assert spawned and spawned[0].daemon is True
    finally:
        _join(spawned, release)


def test_an_injected_clock_past_the_cap_does_not_wait_out_the_real_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release = threading.Event()
    spawned = _track_threads(monkeypatch)
    calls = {"n": 0}

    def clock() -> float:
        calls["n"] += 1
        return 0.0 if calls["n"] == 1 else 100.0

    started = time.perf_counter()
    try:
        with pytest.raises(GeneratorUnavailableError):
            run_with_cap(
                lambda: release.wait(timeout=1.0),
                30.0,
                clock=clock,
                on_abandoned=lambda _work: release.set(),
            )
        assert time.perf_counter() - started < 0.5
    finally:
        _join(spawned, release)


def test_blocking_generator_returns_deadline_within_the_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release = threading.Event()
    spawned = _track_threads(monkeypatch)
    generator = BlockingGenerator(release)
    abandoned: list[AbandonedWork] = []
    try:
        started = time.perf_counter()
        response = service(generator).answer(
            "Is coaching compulsory?",
            ACCESS,
            on_abandoned=abandoned.append,
        )
        elapsed = time.perf_counter() - started
        assert elapsed < _CAP_S + _TOLERANCE_S
        assert generator.calls == 1
        assert generator.seen_deadline == _CAP_S
        assert response.status == AnswerStatus.EVIDENCE_ONLY
        assert response.reason == AnswerReason.GENERATOR_UNAVAILABLE
        assert response.sub_reason == "deadline"
        assert len(abandoned) == 1
        ran = threading.Event()
        abandoned[0].add_done_callback(ran.set)
        assert not ran.is_set()
        release.set()
        assert ran.wait(timeout=1.0)
    finally:
        _join(spawned, release)


@pytest.mark.filterwarnings("ignore:Payload indexes have no effect:UserWarning")
def test_ask_cli_applies_the_cap(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Any,
) -> None:
    for name in (
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION_BASE",
        "W2A_TENANT_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    client = QdrantClient(":memory:")
    factory = Factory(client)
    assert (
        ingestion_cli.main(
            ["--repo-root", str(REPO_ROOT), "--embedder", "fake"],
            client_factory=factory,
        )
        == 0
    )
    release = threading.Event()
    spawned = _track_threads(monkeypatch)
    built: list[BlockingGenerator] = []

    def build(*_args: Any, **_kwargs: Any) -> BlockingGenerator:
        built.append(BlockingGenerator(release))
        return built[0]

    monkeypatch.setattr(cli, "build_generator", build)
    try:
        code = cli.main(
            [QUERY, "--repo-root", str(REPO_ROOT), *SHARED],
            client_factory=factory,
        )
        assert code == 0
        generator = built[0]
        assert generator.calls == 1
        assert generator.seen_deadline == _CAP_S
        assert generator.entered_at is not None
        assert time.perf_counter() - generator.entered_at < _CAP_S + _TOLERANCE_S
        out = capsys.readouterr().out
        assert "status: evidence_only" in out
        assert "reason: generator_unavailable" in out
        assert "sub_reason: deadline" in out
    finally:
        _join(spawned, release)


def test_a_process_does_not_hang_on_an_abandoned_daemon_thread() -> None:
    """The CLI uses this helper. A non-daemon worker would block exit for 30 s.

    A full `make ask` subprocess would ingest first; that can exceed the 5 s
    hang budget, so this runs the same cap the CLI hits and exits while the
    worker is still blocked.
    """
    script = """
import threading
from way2australia_rag.generation.deadline import run_with_cap
from way2australia_rag.generation.errors import GeneratorUnavailableError

release = threading.Event()
try:
    run_with_cap(lambda: release.wait(30), 0.05)
except GeneratorUnavailableError:
    pass
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        timeout=5,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
