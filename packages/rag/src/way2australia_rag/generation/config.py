"""Generation configuration (Spec 012 R5): schema `1.1` of `config/generation.yaml`."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from way2australia_rag.generation.errors import GeneratorConfigurationError

DEFAULT_GENERATION_CONFIG = "config/generation.yaml"
SCHEMA_VERSION = "1.1"


class _Strict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ContextConfig(_Strict):
    """Evidence budget: block count and total evidence characters."""

    max_blocks: int = Field(ge=1)
    max_chars: int = Field(ge=1)


class PromptSelection(_Strict):
    id: str = Field(min_length=1)
    version: int = Field(ge=1)


class RetrievalSelection(_Strict):
    top_k: int = Field(ge=1)


class EvidenceOnlyConfig(_Strict):
    snippet_chars: int = Field(ge=1)


class LanguagesConfig(_Strict):
    script_to_language: dict[str, str]


class BedrockConfig(_Strict):
    endpoint: Literal["runtime", "mantle"]
    region: str = Field(min_length=1)
    model_id: str | None
    inference_profile: str | None
    effort: Literal["low", "medium", "high"]
    max_tokens: int = Field(ge=64, le=8192)
    request_timeout_s: float = Field(gt=0)
    retries: int = Field(ge=0, le=5)
    backoff_s: float = Field(ge=0)
    deadline_s: float = Field(gt=0)

    @model_validator(mode="after")
    def _deadline_covers_one_request(self) -> "BedrockConfig":
        if self.deadline_s < self.request_timeout_s:
            raise ValueError("bedrock.deadline_s must not be below request_timeout_s")
        return self


class AnthropicConfig(_Strict):
    """Direct Anthropic API (2026-11-10): the `bedrock:` value rules, no endpoint,
    region or inference profile."""

    model_id: str | None
    effort: Literal["low", "medium", "high"]
    max_tokens: int = Field(ge=64, le=8192)
    request_timeout_s: float = Field(gt=0)
    retries: int = Field(ge=0, le=5)
    backoff_s: float = Field(ge=0)
    deadline_s: float = Field(gt=0)

    @model_validator(mode="after")
    def _deadline_covers_one_request(self) -> "AnthropicConfig":
        if self.deadline_s < self.request_timeout_s:
            raise ValueError("anthropic.deadline_s must not be below request_timeout_s")
        return self


class PricingConfig(_Strict):
    """USD per million tokens; null until the user fills them in (D-C)."""

    input_per_mtok: float | None = Field(ge=0)
    output_per_mtok: float | None = Field(ge=0)


class EstimateConfig(_Strict):
    chars_per_token: float = Field(gt=0)
    assumed_output_tokens: int = Field(ge=0)


class GenerationConfig(_Strict):
    schema_version: Literal["1.1"]
    default_generator: Literal["bedrock", "anthropic", "fake"] | None
    prompt: PromptSelection
    retrieval: RetrievalSelection
    context: ContextConfig
    evidence_only: EvidenceOnlyConfig
    languages: LanguagesConfig
    bedrock: BedrockConfig
    anthropic: AnthropicConfig
    pricing: PricingConfig
    estimate: EstimateConfig


def _error_fields(error: ValidationError) -> str:
    fields = sorted(
        {
            ".".join(str(part) for part in entry["loc"]) or "<root>"
            for entry in error.errors()
        }
    )
    return ", ".join(fields)


def load_generation_config(
    path: Path, repo_root: Path | None = None
) -> GenerationConfig:
    """Load and validate; any problem is a `GeneratorConfigurationError`.

    `repo_root` locates `config/retrieval.yaml` (the `top_k` vs `rerank.depth`
    check) and `config/prompts/` (the prompt pair check). Default: the repository
    this package lives in.
    """
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise GeneratorConfigurationError(
            f"cannot read generation config '{path.name}' ({type(error).__name__})"
        ) from None
    if not isinstance(raw, dict):
        raise GeneratorConfigurationError(
            f"generation config '{path.name}' must be a YAML mapping"
        )
    try:
        config = GenerationConfig.model_validate(raw)
    except ValidationError as error:
        raise GeneratorConfigurationError(
            f"invalid generation config '{path.name}': check {_error_fields(error)}"
        ) from None
    _check_cross_files(config, repo_root or Path(__file__).resolve().parents[5])
    return config


def _check_cross_files(config: GenerationConfig, repo_root: Path) -> None:
    # Imported here: retrieval and prompts import this package's siblings.
    from way2australia_rag.generation.prompts import (
        PromptConfigurationError,
        PromptRegistry,
    )
    from way2australia_rag.retrieval.errors import RetrievalConfigurationError
    from way2australia_rag.retrieval.strategy import load_retrieval_config

    try:
        retrieval = load_retrieval_config(repo_root / "config/retrieval.yaml")
    except RetrievalConfigurationError as error:
        raise GeneratorConfigurationError(str(error)) from None
    if retrieval.rerank.enabled and config.retrieval.top_k > retrieval.rerank.depth:
        raise GeneratorConfigurationError(
            "generation config: check retrieval.top_k (above rerank.depth "
            f"{retrieval.rerank.depth} while reranking is enabled)"
        )
    try:
        PromptRegistry(repo_root).get(config.prompt.id, config.prompt.version)
    except PromptConfigurationError as error:
        raise GeneratorConfigurationError(
            f"generation config: check prompt ({error})"
        ) from None
