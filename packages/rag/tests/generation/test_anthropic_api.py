"""AnthropicGenerator and the shared Claude adapter against stub clients (Spec 012
R17, T5b). No SDK call, no network, no key."""

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from way2australia_rag.generation.anthropic_api import AnthropicGenerator
from way2australia_rag.generation.bedrock import BedrockGenerator
from way2australia_rag.generation.config import AnthropicConfig, BedrockConfig
from way2australia_rag.generation.errors import (
    GeneratorConfigurationError,
    GeneratorDeclinedError,
    GeneratorUnavailableError,
    UnavailableReason,
)
from way2australia_rag.ingestion.errors import OptionalDependencyError

from .support import REPO_ROOT, rendered_prompt
from .test_bedrock import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Clock,
    StubClient,
    _message,
)

KEY = "sk-test-DO-NOT-LEAK-123"
MODEL = "claude-sonnet-5-5"


@pytest.fixture(autouse=True)
def _key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", KEY)


def _config(**overrides: Any) -> AnthropicConfig:
    values: dict[str, Any] = {
        "model_id": None,
        "effort": "low",
        "max_tokens": 1024,
        "request_timeout_s": 20,
        "retries": 2,
        "backoff_s": 1.0,
        "deadline_s": 30,
    }
    values.update(overrides)
    return AnthropicConfig(**values)


def _reply(model: str | None = MODEL, **kwargs: Any) -> Any:
    message = _message(**kwargs)
    if model is not None:
        message.model = model
    return message


class OptionsStub(StubClient):
    def __init__(self, *a: Any, **k: Any) -> None:
        super().__init__(*a, **k)
        self.options: list[dict[str, Any]] = []

    def with_options(self, **options: Any) -> "StubClient":
        self.options.append(options)
        return super().with_options(**options)


def _generator(
    script: list[Any], **config: Any
) -> tuple[AnthropicGenerator, OptionsStub, Clock]:
    clock = Clock()
    client = OptionsStub(script, clock)
    generator = AnthropicGenerator(
        _config(**config), MODEL, "cli", client=client, clock=clock, sleep=clock.sleep
    )
    return generator, client, clock


def _fake_sdk(monkeypatch: pytest.MonkeyPatch, raises: Exception | None = None):
    calls: list[dict[str, Any]] = []

    def factory(**kwargs: Any) -> object:
        calls.append(kwargs)
        if raises:
            raise raises
        return StubClient([])

    monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(Anthropic=factory))
    return calls


def test_client_gets_the_explicit_key_and_sdk_retries_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _fake_sdk(monkeypatch)
    AnthropicGenerator(_config(), MODEL, "env")
    assert calls == [{"api_key": KEY, "max_retries": 0}]


def test_auth_token_alone_is_not_a_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _fake_sdk(monkeypatch)
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "token-value")
    with pytest.raises(GeneratorConfigurationError, match="ANTHROPIC_API_KEY") as e:
        AnthropicGenerator(_config(), MODEL, "env")
    assert "token-value" not in str(e.value)
    assert calls == []


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_or_empty_key_is_refused(
    monkeypatch: pytest.MonkeyPatch, value: str | None
) -> None:
    calls = _fake_sdk(monkeypatch)
    if value is None:
        monkeypatch.delenv("ANTHROPIC_API_KEY")
    else:
        monkeypatch.setenv("ANTHROPIC_API_KEY", value)
    with pytest.raises(GeneratorConfigurationError, match="ANTHROPIC_API_KEY"):
        AnthropicGenerator(_config(), MODEL, "env")
    assert calls == []


@pytest.mark.parametrize("name", ["ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS"])
def test_redirecting_variables_are_refused_naming_the_variable_only(
    monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    calls = _fake_sdk(monkeypatch)
    monkeypatch.setenv(name, "https://example.invalid/secret-host")
    with pytest.raises(GeneratorConfigurationError, match=name) as e:
        AnthropicGenerator(_config(), MODEL, "env")
    assert "example.invalid" not in str(e.value)
    assert calls == []


@pytest.mark.parametrize(
    "model_id",
    ["global.anthropic.claude-sonnet-5-5", "anthropic.claude-x", "apac.claude-x"],
)
def test_bedrock_form_model_ids_are_refused(
    monkeypatch: pytest.MonkeyPatch, model_id: str
) -> None:
    calls = _fake_sdk(monkeypatch)
    with pytest.raises(GeneratorConfigurationError, match="Bedrock-form") as e:
        AnthropicGenerator(_config(), model_id, "cli")
    assert model_id in str(e.value)
    assert calls == []


def test_bare_model_ids_are_accepted() -> None:
    for model_id in ("claude-sonnet-5-5", "claude-haiku-5-5"):
        AnthropicGenerator(_config(), model_id, "cli", client=StubClient([]))


def test_request_has_exact_keys_no_fallbacks_and_no_extra_options() -> None:
    generator, client, _ = _generator([_reply()])
    prompt = rendered_prompt()
    generator.generate(prompt)
    request = client.requests[0]
    assert set(request) == {
        "model",
        "max_tokens",
        "system",
        "messages",
        "output_config",
    }
    assert request["model"] == MODEL
    assert request["output_config"] == {
        "format": {"type": "json_schema", "schema": prompt.output_schema},
        "effort": "low",
    }
    assert "fallbacks" not in request
    assert [set(o) for o in client.options] == [{"timeout"}]


def test_info_records_the_api_identity_without_the_key() -> None:
    generator, _, _ = _generator([])
    info = generator.info
    assert (info.provider, info.endpoint, info.region) == ("anthropic", "api", None)
    assert info.inference_profile is None and info.is_fake is False
    assert info.model_id == MODEL and info.model_id_source == "cli"
    assert KEY not in info.model_dump_json()


def test_success_records_the_response_model() -> None:
    generator, _, _ = _generator([_reply()])
    output = generator.generate(rendered_prompt())
    assert output.response_model == MODEL
    assert output.usage.attempts == 1


@pytest.mark.parametrize(
    "got", ["claude-sonnet-5-5-20261101", "claude-haiku-5-5", None]
)
def test_response_model_mismatch_or_missing_is_a_configuration_error(
    got: str | None,
) -> None:
    generator, _, _ = _generator([_reply(model=got)])
    with pytest.raises(GeneratorConfigurationError) as e:
        generator.generate(rendered_prompt())
    assert MODEL in str(e.value) and repr(got) in str(e.value)
    assert KEY not in str(e.value)


def test_refusal_is_declined() -> None:
    generator, _, _ = _generator([_reply(stop_reason="refusal")])
    with pytest.raises(GeneratorDeclinedError):
        generator.generate(rendered_prompt())


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (APIConnectionError(), UnavailableReason.CONNECTION),
        (APITimeoutError(), UnavailableReason.TIMEOUT),
        (APIStatusError(408), UnavailableReason.TIMEOUT),
        (APIStatusError(429), UnavailableReason.THROTTLED),
        *[
            (APIStatusError(s), UnavailableReason.SERVER_ERROR)
            for s in (500, 502, 503, 504, 529)
        ],
    ],
)
def test_outages_are_retried_then_unavailable(
    error: Exception, reason: UnavailableReason
) -> None:
    generator, client, _ = _generator([error, error, error])
    with pytest.raises(GeneratorUnavailableError) as caught:
        generator.generate(rendered_prompt())
    assert caught.value.reason == reason and len(client.requests) == 3


@pytest.mark.parametrize("status", [400, 401, 403, 404, 413])
def test_configuration_statuses_are_not_retried(status: int) -> None:
    generator, client, _ = _generator([APIStatusError(status)])
    with pytest.raises(GeneratorConfigurationError) as caught:
        generator.generate(rendered_prompt())
    assert len(client.requests) == 1 and str(status) in str(caught.value)


def test_413_is_a_configuration_error_on_bedrock_too() -> None:
    clock = Clock()
    client = StubClient([APIStatusError(413)], clock)
    config = BedrockConfig(
        endpoint="runtime",
        region="ap-south-1",
        model_id=None,
        inference_profile=None,
        effort="low",
        max_tokens=1024,
        request_timeout_s=20,
        retries=2,
        backoff_s=1.0,
        deadline_s=30,
    )
    generator = BedrockGenerator(config, "m", "cli", client=client, clock=clock)
    with pytest.raises(GeneratorConfigurationError, match="413"):
        generator.generate(rendered_prompt())
    assert len(client.requests) == 1


def test_other_errors_propagate() -> None:
    generator, _, _ = _generator([ValueError("boom")])
    with pytest.raises(ValueError):
        generator.generate(rendered_prompt())


def test_key_never_appears_when_the_sdk_constructor_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fake_sdk(monkeypatch, raises=RuntimeError(f"bad key {KEY}"))
    with pytest.raises(GeneratorConfigurationError) as e:
        AnthropicGenerator(_config(), MODEL, "env")
    assert KEY not in str(e.value) and KEY not in repr(e.value.__cause__)


def test_close_closes_the_client() -> None:
    generator, client, _ = _generator([])
    generator.close()
    assert client.closed is True


def test_missing_extra_names_the_setup_target(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "anthropic", None)
    with pytest.raises(OptionalDependencyError, match="make setup-anthropic"):
        AnthropicGenerator(_config(), MODEL, "env")


def test_importing_the_module_does_not_import_the_sdk() -> None:
    script = (
        "import sys\n"
        "attempts = []\n"
        "class Recorder:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name.split('.')[0] in ('anthropic', 'boto3', 'botocore'):\n"
        "            attempts.append(name)\n"
        "        return None\n"
        "sys.meta_path.insert(0, Recorder())\n"
        "import way2australia_rag.generation.anthropic_api\n"
        "import way2australia_rag.generation.claude\n"
        "import way2australia_rag.generation.build\n"
        "sys.exit(1 if attempts else 0)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_smoke_module_overrides_the_conftest_environment_fixture() -> None:
    """No API call: `--setup-plan` executes nothing. With the opt-in variable set,
    the smoke module must not set up the conftest fixture (which would delete the
    key and the model ID); its override has no `monkeypatch` dependency."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC_")}
    env["W2A_RUN_ANTHROPIC_SMOKE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--setup-plan",
            "-p",
            "no:cacheprovider",
            str(Path(__file__).with_name("test_anthropic_smoke.py")),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    out = result.stdout
    assert "test_anthropic_returns_schema_valid_cited_output" in out, out
    assert "_no_aws_environment" in out, out
    assert "_no_aws_environment (fixtures used: monkeypatch)" not in out, out
