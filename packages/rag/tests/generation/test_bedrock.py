"""BedrockGenerator against stub clients (Spec 012 R4, D-A, D-B). No SDK, no AWS."""

import json
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest
from way2australia_rag.generation.bedrock import BedrockGenerator, classify_error
from way2australia_rag.generation.config import BedrockConfig
from way2australia_rag.generation.errors import (
    GeneratorConfigurationError,
    GeneratorDeclinedError,
    GeneratorOutputError,
    GeneratorUnavailableError,
    UnavailableReason,
)
from way2australia_rag.ingestion.errors import OptionalDependencyError

from .support import rendered_prompt


# Stand-ins named like the SDK's exception classes (classification is by type name).
class APIConnectionError(Exception):
    pass


class APITimeoutError(APIConnectionError):
    pass


class APIStatusError(Exception):
    def __init__(self, status: int, headers: dict[str, str] | None = None) -> None:
        super().__init__(f"HTTP {status}")
        self.status_code = status
        self.response = SimpleNamespace(headers=headers or {})


class NoCredentialsError(Exception):
    pass


def _config(**overrides: Any) -> BedrockConfig:
    values: dict[str, Any] = {
        "endpoint": "runtime",
        "region": "ap-south-1",
        "model_id": None,
        "inference_profile": None,
        "effort": "low",
        "max_tokens": 1024,
        "request_timeout_s": 20,
        "retries": 2,
        "backoff_s": 1.0,
        "deadline_s": 30,
    }
    values.update(overrides)
    return BedrockConfig(**values)


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def _message(
    payload: Any = None, *, stop_reason: str = "end_turn", content: Any = None
):
    if content is None:
        body = (
            payload
            if payload is not None
            else {
                "answerable": True,
                "answer": "Yes [S1]",
                "citations": ["S1"],
            }
        )
        text = body if isinstance(body, str) else json.dumps(body)
        content = [SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=content,
        usage=SimpleNamespace(input_tokens=11, output_tokens=7),
    )


class StubClient:
    """Each script step is an exception, a message, or `(seconds, result)`."""

    def __init__(self, script: list[Any], clock: Clock | None = None) -> None:
        self.script = list(script)
        self.clock = clock
        self.requests: list[dict[str, Any]] = []
        self.timeouts: list[float] = []
        self.closed = False
        self.messages = SimpleNamespace(create=self._create)
        self._timeout: float | None = None

    def with_options(self, **options: Any) -> "StubClient":
        self._timeout = options["timeout"]
        return self

    def _create(self, **request: Any) -> Any:
        assert self._timeout is not None
        self.timeouts.append(self._timeout)
        self.requests.append(request)
        step = self.script.pop(0)
        if isinstance(step, tuple):
            seconds, step = step
            assert self.clock is not None
            self.clock.now += seconds
        if isinstance(step, BaseException):
            raise step
        return step

    def close(self) -> None:
        self.closed = True


def _generator(
    script: list[Any], clock: Clock | None = None, **config: Any
) -> tuple[BedrockGenerator, StubClient, Clock]:
    clock = clock or Clock()
    client = StubClient(script, clock)
    generator = BedrockGenerator(
        _config(**config),
        "test-model",
        "cli",
        client=client,
        clock=clock,
        sleep=clock.sleep,
    )
    return generator, client, clock


def test_request_shape_has_structured_output_and_no_forbidden_fields() -> None:
    generator, client, _ = _generator([_message()])
    prompt = rendered_prompt()
    generator.generate(prompt)
    request = client.requests[0]
    assert request["model"] == "test-model"
    assert request["max_tokens"] == 1024
    assert request["system"] == prompt.system
    assert request["messages"] == [{"role": "user", "content": prompt.user}]
    assert request["output_config"] == {
        "format": {"type": "json_schema", "schema": prompt.output_schema},
        "effort": "low",
    }
    for forbidden in ("temperature", "top_p", "top_k", "thinking", "tools", "stream"):
        assert forbidden not in request
    assert client.timeouts == [20]


def test_inference_profile_is_the_request_model() -> None:
    generator, client, _ = _generator([_message()], inference_profile="apac.profile")
    generator.generate(rendered_prompt())
    assert client.requests[0]["model"] == "apac.profile"
    assert generator.info.model_id == "test-model"
    assert generator.info.inference_profile == "apac.profile"


def test_info_records_identity() -> None:
    generator, _, _ = _generator([])
    info = generator.info
    assert info.provider == "bedrock"
    assert info.model_id_source == "cli"
    assert (info.endpoint, info.region, info.effort) == ("runtime", "ap-south-1", "low")
    assert (info.retries, info.deadline_s, info.is_fake) == (2, 30, False)


def test_success_returns_usage_attempts_and_stop_reason() -> None:
    generator, _, _ = _generator([_message()])
    output = generator.generate(rendered_prompt())
    assert output.answerable is True
    assert output.citations == ["S1"]
    assert output.usage.input_tokens == 11
    assert output.usage.output_tokens == 7
    assert output.usage.attempts == 1
    assert output.stop_reason == "end_turn"


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (APIConnectionError(), UnavailableReason.CONNECTION),
        (APITimeoutError(), UnavailableReason.TIMEOUT),
        (APIStatusError(408), UnavailableReason.TIMEOUT),
        (APIStatusError(429), UnavailableReason.THROTTLED),
        (APIStatusError(500), UnavailableReason.SERVER_ERROR),
        (APIStatusError(502), UnavailableReason.SERVER_ERROR),
        (APIStatusError(503), UnavailableReason.SERVER_ERROR),
        (APIStatusError(504), UnavailableReason.SERVER_ERROR),
        (APIStatusError(529), UnavailableReason.SERVER_ERROR),
    ],
)
def test_eligible_errors_are_retried_then_unavailable(
    error: Exception, reason: UnavailableReason
) -> None:
    generator, client, _ = _generator([error, error, error])
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.reason == reason
    assert len(client.requests) == 3


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_configuration_statuses_are_not_retried(status: int) -> None:
    generator, client, _ = _generator([APIStatusError(status)])
    with pytest.raises(GeneratorConfigurationError) as caught:
        generator.generate(rendered_prompt())
    assert len(client.requests) == 1
    assert str(status) in str(caught.value)


def test_credential_error_is_a_configuration_error() -> None:
    generator, client, _ = _generator([NoCredentialsError("secret detail")])
    with pytest.raises(GeneratorConfigurationError) as caught:
        generator.generate(rendered_prompt())
    assert len(client.requests) == 1
    assert "secret detail" not in str(caught.value)


def test_other_errors_propagate() -> None:
    generator, _, _ = _generator([ValueError("boom"), APIStatusError(418)])
    with pytest.raises(ValueError):
        generator.generate(rendered_prompt())
    with pytest.raises(APIStatusError):
        generator.generate(rendered_prompt())


def test_explicit_cause_chain_is_classified() -> None:
    try:
        raise APIConnectionError() from None
    except APIConnectionError as inner:
        wrapped = RuntimeError("wrapped")
        wrapped.__cause__ = inner
    assert classify_error(wrapped) == UnavailableReason.CONNECTION


def test_context_is_ignored() -> None:
    # An implicit context (no `from`) is not evidence of an outage (D057).
    try:
        try:
            raise APIConnectionError()
        except APIConnectionError:
            raise RuntimeError("unrelated")
    except RuntimeError as outer:
        assert isinstance(outer.__context__, APIConnectionError)
        assert classify_error(outer) is None


def test_retries_back_off_with_a_fake_clock() -> None:
    generator, client, clock = _generator(
        [APIConnectionError(), APIStatusError(503), _message()]
    )
    output = generator.generate(rendered_prompt())
    assert clock.sleeps == [1.0, 2.0]
    assert output.usage.attempts == 3
    assert len(client.requests) == 3


def test_exhausted_retries_do_not_sleep_after_the_last_attempt() -> None:
    generator, _, clock = _generator([APIConnectionError()] * 3)
    with pytest.raises(GeneratorUnavailableError):
        generator.generate(rendered_prompt())
    assert clock.sleeps == [1.0, 2.0]


def test_deadline_stops_further_attempts_even_mid_retry() -> None:
    clock = Clock()
    # Attempt 1 uses 25 s of the 30 s deadline; attempt 2 is bounded to the 4 s left.
    generator, client, _ = _generator(
        [(25, APITimeoutError()), (3.5, APITimeoutError()), _message()], clock
    )
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.reason == UnavailableReason.DEADLINE
    assert client.timeouts == [20, pytest.approx(4.0)]
    assert len(client.requests) == 2


def test_no_attempt_starts_with_one_second_or_less_left() -> None:
    clock = Clock()
    generator, client, _ = _generator(
        [(29.5, APITimeoutError()), _message()], clock, retries=2
    )
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.reason == UnavailableReason.DEADLINE
    assert len(client.requests) == 1


def test_retry_after_within_the_deadline_is_honoured() -> None:
    generator, _, clock = _generator(
        [APIStatusError(429, {"retry-after": "3"}), _message()]
    )
    generator.generate(rendered_prompt())
    assert clock.sleeps == [3.0]


def test_retry_after_beyond_the_deadline_is_not_honoured() -> None:
    generator, client, clock = _generator(
        [APIStatusError(429, {"retry-after": "100"}), _message()]
    )
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.reason == UnavailableReason.DEADLINE
    assert clock.sleeps == []
    assert len(client.requests) == 1


def test_refusal_stop_reason_is_declined() -> None:
    generator, _, _ = _generator([_message(stop_reason="refusal")])
    with pytest.raises(GeneratorDeclinedError):
        generator.generate(rendered_prompt())


def test_max_tokens_stop_reason_is_an_output_error() -> None:
    generator, _, _ = _generator([_message(stop_reason="max_tokens")])
    with pytest.raises(GeneratorOutputError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.rule == "max_tokens"


@pytest.mark.parametrize(
    ("payload", "rule"),
    [
        ("not json", "json"),
        ("[1, 2]", "schema"),
        ({"answerable": True, "answer": "x"}, "schema"),
        ({"answerable": "yes", "answer": "x", "citations": []}, "schema"),
        ({"answerable": True, "answer": "x", "citations": ["s1"]}, "schema"),
        (
            {"answerable": True, "answer": "x", "citations": [], "extra": 1},
            "schema",
        ),
    ],
)
def test_json_and_schema_failures(payload: Any, rule: str) -> None:
    generator, _, _ = _generator([_message(payload)])
    with pytest.raises(GeneratorOutputError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.rule == rule


def test_no_text_block_is_a_json_failure() -> None:
    generator, _, _ = _generator([_message(content=[SimpleNamespace(type="thinking")])])
    with pytest.raises(GeneratorOutputError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.rule == "json"


def test_thinking_blocks_are_ignored_and_first_text_block_is_used() -> None:
    body = {"answerable": False, "answer": "", "citations": []}
    content = [
        SimpleNamespace(type="thinking", thinking="..."),
        SimpleNamespace(type="text", text=json.dumps(body)),
        SimpleNamespace(type="text", text="ignored"),
    ]
    generator, _, _ = _generator([_message(content=content)])
    assert generator.generate(rendered_prompt()).answerable is False


def test_close_closes_the_client() -> None:
    generator, client, _ = _generator([])
    generator.close()
    assert client.closed is True


def _fake_sdk(monkeypatch: pytest.MonkeyPatch, **raises: Exception) -> dict[str, list]:
    calls: dict[str, list] = {"AnthropicBedrock": [], "AnthropicBedrockMantle": []}

    def make(name: str):
        def factory(**kwargs: Any) -> object:
            calls[name].append(kwargs)
            if name in raises:
                raise raises[name]
            return StubClient([])

        return factory

    module = SimpleNamespace(
        AnthropicBedrock=make("AnthropicBedrock"),
        AnthropicBedrockMantle=make("AnthropicBedrockMantle"),
    )
    monkeypatch.setitem(sys.modules, "anthropic", module)
    return calls


@pytest.mark.parametrize(
    ("endpoint", "client_class"),
    [("runtime", "AnthropicBedrock"), ("mantle", "AnthropicBedrockMantle")],
)
def test_client_is_built_by_endpoint_with_sdk_retries_off(
    monkeypatch: pytest.MonkeyPatch, endpoint: str, client_class: str
) -> None:
    calls = _fake_sdk(monkeypatch)
    BedrockGenerator(_config(endpoint=endpoint), "m", "env")
    assert calls[client_class] == [{"aws_region": "ap-south-1", "max_retries": 0}]
    other = ({"AnthropicBedrock", "AnthropicBedrockMantle"} - {client_class}).pop()
    assert calls[other] == []


def test_client_construction_credential_failure_is_a_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fake_sdk(monkeypatch, AnthropicBedrock=NoCredentialsError("x"))
    with pytest.raises(GeneratorConfigurationError):
        BedrockGenerator(_config(), "m", "cli")


def test_missing_extra_names_the_setup_target(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "anthropic", None)
    with pytest.raises(OptionalDependencyError, match="make setup-bedrock"):
        BedrockGenerator(_config(), "m", "cli")


def test_importing_generation_modules_does_not_import_the_sdk() -> None:
    script = (
        "import pkgutil, importlib, sys\n"
        "import way2australia_rag.generation as g\n"
        "for m in pkgutil.iter_modules(g.__path__):\n"
        "    importlib.import_module('way2australia_rag.generation.' + m.name)\n"
        "bad = [n for n in ('anthropic', 'boto3', 'botocore') if n in sys.modules]\n"
        "sys.exit(1 if bad else 0)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
