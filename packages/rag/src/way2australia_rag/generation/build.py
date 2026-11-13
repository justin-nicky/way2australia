"""Generator factory (Spec 012 R5, D-C): `fake`, `bedrock` and `anthropic`."""

from typing import Literal

from way2australia_rag.generation.base import Generator
from way2australia_rag.generation.config import GenerationConfig
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.fake import FakeGenerator


def build_generator(
    config: GenerationConfig,
    provider: str | None = None,
    model_id_override: str | None = None,
    model_id_override_source: Literal["cli", "env"] = "cli",
) -> Generator:
    """`provider` overrides `config.default_generator` (for example `--generator fake`).

    `bedrock` needs a model ID: `model_id_override` (CLI or environment), else
    `bedrock.model_id`. D-C: neither exists before T6.
    """
    chosen = provider or config.default_generator
    if chosen is None:
        raise GeneratorConfigurationError(
            "no generator is configured; pass --generator fake, --generator bedrock "
            "or --generator anthropic."
        )
    if chosen == "fake":
        return FakeGenerator()
    if chosen == "bedrock":
        model_id = model_id_override or config.bedrock.model_id
        if not model_id:
            raise GeneratorConfigurationError(
                "the bedrock generator needs a model ID; pass --model-id <id> "
                "(bedrock.model_id is not set in config/generation.yaml)."
            )
        source: Literal["config", "cli", "env"] = (
            model_id_override_source if model_id_override else "config"
        )
        # Imported here so the fake path never touches the Bedrock module.
        from way2australia_rag.generation.bedrock import BedrockGenerator

        return BedrockGenerator(config.bedrock, model_id, source)
    if chosen == "anthropic":
        model_id = model_id_override or config.anthropic.model_id
        if not model_id:
            raise GeneratorConfigurationError(
                "the anthropic generator needs a model ID; pass --model-id <id> "
                "(anthropic.model_id is not set in config/generation.yaml)."
            )
        source = model_id_override_source if model_id_override else "config"
        from way2australia_rag.generation.anthropic_api import AnthropicGenerator

        return AnthropicGenerator(config.anthropic, model_id, source)
    raise GeneratorConfigurationError(f"unknown generator provider {chosen!r}")
