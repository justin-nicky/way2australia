"""Generation config loader and generator factory (Spec 012 R5, D-C)."""

import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml
from way2australia_rag.generation.build import build_generator
from way2australia_rag.generation.config import (
    GenerationConfig,
    load_generation_config,
)
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.fake import FakeGenerator
from way2australia_rag.ingestion.errors import OptionalDependencyError

from .support import REPO_ROOT

COMMITTED = REPO_ROOT / "config/generation.yaml"


def _raw() -> dict[str, Any]:
    return yaml.safe_load(COMMITTED.read_text(encoding="utf-8"))


def _write(tmp_path: Path, raw: Any) -> Path:
    path = tmp_path / "generation.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


def _load(tmp_path: Path, raw: dict[str, Any]) -> GenerationConfig:
    return load_generation_config(_write(tmp_path, raw), REPO_ROOT)


def test_committed_file_loads_with_no_default_generator_model_or_pricing() -> None:
    # Read from the file: D-C says null until T6.
    raw = _raw()
    assert raw["default_generator"] is None
    assert raw["bedrock"]["model_id"] is None
    assert raw["bedrock"]["inference_profile"] is None
    assert raw["pricing"] == {"input_per_mtok": None, "output_per_mtok": None}
    config = load_generation_config(COMMITTED)
    assert config.default_generator is None
    assert config.bedrock.endpoint == "runtime"
    assert config.bedrock.region == "ap-south-1"
    assert config.bedrock.effort == "low"
    assert (config.bedrock.max_tokens, config.bedrock.request_timeout_s) == (1024, 20)
    assert (config.bedrock.retries, config.bedrock.backoff_s) == (2, 1.0)
    assert config.bedrock.deadline_s == 30
    assert (config.context.max_blocks, config.context.max_chars) == (5, 8000)
    assert config.retrieval.top_k == 5
    assert config.evidence_only.snippet_chars == 240
    assert config.languages.script_to_language == {"malayalam": "ml"}
    assert config.estimate.chars_per_token == 2.0
    assert config.estimate.assumed_output_tokens == 400


def test_unknown_key_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["surprise"] = 1
    with pytest.raises(GeneratorConfigurationError, match="surprise"):
        _load(tmp_path, raw)


def test_unknown_nested_key_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["bedrock"]["temperature"] = 0
    with pytest.raises(GeneratorConfigurationError, match="bedrock.temperature"):
        _load(tmp_path, raw)


def test_deadline_below_request_timeout_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["bedrock"]["deadline_s"] = 10
    with pytest.raises(GeneratorConfigurationError, match="bedrock"):
        _load(tmp_path, raw)


@pytest.mark.parametrize("retries", [-1, 6])
def test_retries_outside_range_is_refused(tmp_path: Path, retries: int) -> None:
    raw = _raw()
    raw["bedrock"]["retries"] = retries
    with pytest.raises(GeneratorConfigurationError, match="bedrock.retries"):
        _load(tmp_path, raw)


@pytest.mark.parametrize("max_tokens", [63, 8193])
def test_max_tokens_outside_range_is_refused(tmp_path: Path, max_tokens: int) -> None:
    raw = _raw()
    raw["bedrock"]["max_tokens"] = max_tokens
    with pytest.raises(GeneratorConfigurationError, match="bedrock.max_tokens"):
        _load(tmp_path, raw)


def test_boundary_values_are_accepted(tmp_path: Path) -> None:
    raw = _raw()
    raw["bedrock"].update(retries=5, max_tokens=8192, deadline_s=20)
    config = _load(tmp_path, raw)
    assert (config.bedrock.retries, config.bedrock.max_tokens) == (5, 8192)


def test_top_k_above_rerank_depth_is_refused_when_reranking_is_enabled(
    tmp_path: Path,
) -> None:
    raw = _raw()
    raw["retrieval"]["top_k"] = 21
    with pytest.raises(GeneratorConfigurationError, match="retrieval.top_k"):
        _load(tmp_path, raw)


def test_top_k_above_rerank_depth_is_accepted_when_reranking_is_off(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "config/prompts", root / "config/prompts")
    retrieval = yaml.safe_load((REPO_ROOT / "config/retrieval.yaml").read_text())
    retrieval["rerank"]["enabled"] = False
    (root / "config/retrieval.yaml").write_text(yaml.safe_dump(retrieval))
    raw = _raw()
    raw["retrieval"]["top_k"] = 30
    config = load_generation_config(_write(tmp_path, raw), root)
    assert config.retrieval.top_k == 30


def test_unknown_prompt_pair_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["prompt"]["version"] = 99
    with pytest.raises(GeneratorConfigurationError, match="prompt"):
        _load(tmp_path, raw)


def test_wrong_schema_version_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["schema_version"] = "2.0"
    with pytest.raises(GeneratorConfigurationError, match="schema_version"):
        _load(tmp_path, raw)


def test_unreadable_and_non_mapping_files_are_refused(tmp_path: Path) -> None:
    with pytest.raises(GeneratorConfigurationError, match="cannot read"):
        load_generation_config(tmp_path / "missing.yaml", REPO_ROOT)
    path = tmp_path / "list.yaml"
    path.write_text("- 1\n", encoding="utf-8")
    with pytest.raises(GeneratorConfigurationError, match="mapping"):
        load_generation_config(path, REPO_ROOT)


def test_refusals_do_not_leak_the_directory(tmp_path: Path) -> None:
    raw = _raw()
    raw["bedrock"]["retries"] = 9
    with pytest.raises(GeneratorConfigurationError) as caught:
        _load(tmp_path, raw)
    assert str(tmp_path) not in str(caught.value)


def test_pricing_and_model_id_may_be_set(tmp_path: Path) -> None:
    raw = _raw()
    raw["default_generator"] = "bedrock"
    raw["bedrock"]["model_id"] = "some-model"
    raw["pricing"] = {"input_per_mtok": 3.0, "output_per_mtok": 15.0}
    config = _load(tmp_path, raw)
    assert config.default_generator == "bedrock"
    assert config.pricing.input_per_mtok == 3.0


def test_no_default_generator_is_refused() -> None:
    config = load_generation_config(COMMITTED)
    with pytest.raises(GeneratorConfigurationError, match="--generator"):
        build_generator(config)


def test_fake_provider_builds_a_fake() -> None:
    config = load_generation_config(COMMITTED)
    assert isinstance(build_generator(config, "fake"), FakeGenerator)


def test_bedrock_without_a_model_id_is_refused() -> None:
    config = load_generation_config(COMMITTED)
    with pytest.raises(GeneratorConfigurationError, match="--model-id"):
        build_generator(config, "bedrock")


def test_unknown_provider_is_refused() -> None:
    config = load_generation_config(COMMITTED)
    with pytest.raises(GeneratorConfigurationError, match="unknown generator"):
        build_generator(config, "other")


def test_bedrock_with_a_model_id_override_needs_the_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "anthropic", None)
    config = load_generation_config(COMMITTED)
    with pytest.raises(OptionalDependencyError, match="make setup-bedrock"):
        build_generator(config, "bedrock", "some-model")


def test_bedrock_override_is_recorded_in_the_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    stub = SimpleNamespace(close=lambda: None)
    sdk = SimpleNamespace(
        AnthropicBedrock=lambda **_: stub, AnthropicBedrockMantle=lambda **_: stub
    )
    monkeypatch.setitem(sys.modules, "anthropic", sdk)
    config = load_generation_config(COMMITTED)
    generator = build_generator(config, "bedrock", "some-model", "env")
    assert generator.info.model_id == "some-model"
    assert generator.info.model_id_source == "env"
    assert generator.info.is_fake is False


# --- T5b: schema 1.1 and the anthropic section ---------------------------------------


def test_committed_file_has_the_anthropic_section_with_null_model() -> None:
    raw = _raw()
    assert raw["schema_version"] == "1.1"
    assert raw["default_generator"] is None
    assert raw["anthropic"]["model_id"] is None
    assert raw["bedrock"]["model_id"] is None
    assert raw["pricing"] == {"input_per_mtok": None, "output_per_mtok": None}
    config = load_generation_config(COMMITTED)
    assert config.anthropic.effort == "low"
    assert (config.anthropic.max_tokens, config.anthropic.request_timeout_s) == (
        1024,
        20,
    )
    assert (config.anthropic.retries, config.anthropic.backoff_s) == (2, 1.0)
    assert config.anthropic.deadline_s == 30


def test_old_schema_version_is_refused(tmp_path: Path) -> None:
    raw = _raw()
    raw["schema_version"] = "1.0"
    with pytest.raises(GeneratorConfigurationError, match="schema_version"):
        _load(tmp_path, raw)


@pytest.mark.parametrize(
    "key", ["endpoint", "region", "inference_profile", "temperature"]
)
def test_anthropic_section_has_no_extra_keys(tmp_path: Path, key: str) -> None:
    raw = _raw()
    raw["anthropic"][key] = "x"
    with pytest.raises(GeneratorConfigurationError, match=f"anthropic.{key}"):
        _load(tmp_path, raw)


def test_anthropic_section_value_rules(tmp_path: Path) -> None:
    for field, value in (("retries", 9), ("max_tokens", 10), ("max_tokens", 9000)):
        raw = _raw()
        raw["anthropic"][field] = value
        with pytest.raises(GeneratorConfigurationError, match=f"anthropic.{field}"):
            _load(tmp_path, raw)
    raw = _raw()
    raw["anthropic"]["deadline_s"] = 10
    with pytest.raises(GeneratorConfigurationError, match="anthropic"):
        _load(tmp_path, raw)


def test_anthropic_may_be_the_default_generator(tmp_path: Path) -> None:
    raw = _raw()
    raw["default_generator"] = "anthropic"
    raw["anthropic"]["model_id"] = "claude-sonnet-5-5"
    assert _load(tmp_path, raw).default_generator == "anthropic"


def test_anthropic_without_a_model_id_is_refused() -> None:
    config = load_generation_config(COMMITTED)
    with pytest.raises(GeneratorConfigurationError, match="--model-id"):
        build_generator(config, "anthropic")


def test_anthropic_override_is_recorded_in_the_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    stub = SimpleNamespace(close=lambda: None)
    monkeypatch.setitem(
        sys.modules, "anthropic", SimpleNamespace(Anthropic=lambda **_: stub)
    )
    config = load_generation_config(COMMITTED)
    generator = build_generator(config, "anthropic", "claude-haiku-5-5", "env")
    assert generator.info.provider == "anthropic"
    assert generator.info.model_id == "claude-haiku-5-5"
    assert generator.info.model_id_source == "env"
