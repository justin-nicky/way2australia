"""`config/serving.yaml` (Spec 013 R5-R10): strict loader and cross-file budget check.

Messages name fields only: never a path, a value or parser text.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from way2australia_rag.generation.config import GenerationConfig
from way2australia_rag.retrieval.strategy import RetrievalConfig

DEFAULT_SERVING_CONFIG = "config/serving.yaml"


class ServingConfigurationError(Exception):
    """The serving configuration is invalid. The message is path- and value-free."""


class _Strict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class RequestLimits(_Strict):
    max_query_chars: int = Field(ge=1, le=4000)
    max_body_bytes: int = Field(ge=1024, le=1_048_576)


class ConcurrencyConfig(_Strict):
    max_in_flight: int = Field(ge=1, le=64)
    retry_after_busy_s: int = Field(ge=1, le=300)
    retry_after_not_ready_s: int = Field(ge=1, le=300)


class BudgetConfig(_Strict):
    request_s: float = Field(gt=0, le=600)
    min_generation_s: float = Field(ge=0, le=60)


class BreakerConfig(_Strict):
    failure_threshold: int = Field(ge=1, le=20)
    cooldown_s: float = Field(ge=1, le=600)


class ServingConfig(_Strict):
    schema_version: Literal["1.0"]
    request: RequestLimits
    concurrency: ConcurrencyConfig
    budget: BudgetConfig
    breaker: BreakerConfig


def generator_deadline_s(config: GenerationConfig, provider: str | None) -> float:
    """The configured deadline of the generator that will serve (0 for `fake`).

    `provider` overrides `default_generator`, as `build_generator` resolves it.
    """
    chosen = provider or config.default_generator
    if chosen == "bedrock":
        return float(config.bedrock.deadline_s)
    if chosen == "anthropic":
        return float(config.anthropic.deadline_s)
    return 0.0


def check_budget(
    serving: ServingConfig,
    generation: GenerationConfig,
    retrieval: RetrievalConfig,
    generator_provider: str | None = None,
) -> None:
    """The request budget must leave room for one bounded retrieval and a full
    generation deadline: `request_s >= deadline_s + query_timeout_s +
    min_generation_s`."""
    needed = (
        generator_deadline_s(generation, generator_provider)
        + retrieval.qdrant.query_timeout_s
        + serving.budget.min_generation_s
    )
    if serving.budget.request_s < needed:
        raise ServingConfigurationError(
            "serving config: check budget.request_s (below the generator "
            "deadline_s plus qdrant.query_timeout_s plus budget.min_generation_s)"
        )


def load_serving_config(
    path: Path,
    *,
    generation_config: GenerationConfig,
    retrieval_config: RetrievalConfig,
    generator_provider: str | None = None,
) -> ServingConfig:
    """Load, validate strictly and run the cross-file budget check."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise ServingConfigurationError(
            f"cannot read serving config '{path.name}' ({type(error).__name__})"
        ) from None
    if not isinstance(raw, dict):
        raise ServingConfigurationError(
            f"serving config '{path.name}' must be a YAML mapping"
        )
    try:
        config = ServingConfig.model_validate(raw)
    except ValidationError as error:
        fields = sorted(
            {
                ".".join(str(part) for part in e["loc"]) or "<root>"
                for e in error.errors()
            }
        )
        raise ServingConfigurationError(
            f"invalid serving config '{path.name}': check {', '.join(fields)}"
        ) from None
    check_budget(config, generation_config, retrieval_config, generator_provider)
    return config
