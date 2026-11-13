"""Bedrock generator (Spec 012 R4, R5; design "Bedrock adapter", D-A, D-B).

Uses the Anthropic Python SDK's Bedrock clients (docs:
https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock and
https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python, read 2026-11-07):
`AnthropicBedrock` (`endpoint: runtime`, InvokeModel) or `AnthropicBedrockMantle`
(`endpoint: mantle`). Both take `aws_region` and `max_retries`; credentials come from
the default AWS chain. The SDK is imported only in `__init__`; nothing else in this
package imports it. SDK retries are off: the loop below owns attempts and the deadline.
"""

import importlib
import time
from collections.abc import Callable
from typing import Any, Literal

from way2australia_rag.generation.base import GeneratorInfo, GeneratorOutput
from way2australia_rag.generation.claude import ClaudeMessagesAdapter, classify_error
from way2australia_rag.generation.config import BedrockConfig
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.prompts import RenderedPrompt
from way2australia_rag.ingestion.errors import OptionalDependencyError

__all__ = ["BedrockGenerator", "classify_error"]

_MISSING_EXTRA_MESSAGE = (
    "the Bedrock generator needs the optional 'bedrock' extra; "
    "run `make setup-bedrock`."
)


class BedrockGenerator:
    def __init__(
        self,
        config: BedrockConfig,
        model_id: str,
        model_id_source: Literal["config", "cli", "env"],
        *,
        client: Any | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """`client` is the test seam: when given, the SDK is not imported."""
        self._client = client if client is not None else self._build_client(config)
        self._adapter = ClaudeMessagesAdapter(
            self._client,
            config.inference_profile or model_id,
            config,
            clock=clock,
            sleep=sleep,
        )
        self.info = GeneratorInfo(
            provider="bedrock",
            model_id=model_id,
            model_id_source=model_id_source,
            endpoint=config.endpoint,
            region=config.region,
            inference_profile=config.inference_profile,
            effort=config.effort,
            max_tokens=config.max_tokens,
            request_timeout_s=config.request_timeout_s,
            retries=config.retries,
            deadline_s=config.deadline_s,
            is_fake=False,
        )

    @staticmethod
    def _build_client(config: BedrockConfig) -> Any:
        try:
            sdk = importlib.import_module("anthropic")
        except ImportError as error:
            raise OptionalDependencyError(_MISSING_EXTRA_MESSAGE) from error
        factory = (
            sdk.AnthropicBedrockMantle
            if config.endpoint == "mantle"
            else sdk.AnthropicBedrock
        )
        try:
            return factory(aws_region=config.region, max_retries=0)
        except Exception as error:
            verdict = classify_error(error)
            if isinstance(verdict, GeneratorConfigurationError):
                raise verdict from error
            raise GeneratorConfigurationError(
                f"cannot create the Bedrock client ({type(error).__name__})."
            ) from error

    def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
        return self._adapter.generate(prompt)

    def close(self) -> None:
        self._adapter.close()
