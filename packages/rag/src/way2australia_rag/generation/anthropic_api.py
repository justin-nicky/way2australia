"""Direct Anthropic API generator (Spec 012 R17, T5b; design "Direct Anthropic API
generator").

Development and evaluation endpoint while Bedrock quotas are 0; Bedrock stays the
production target. Client construction follows the installed SDK's own docstring
(`anthropic` 2.6.0, `Anthropic.__init__`, read 2026-11-10; docs
https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python): an explicit
`api_key=` makes the client ignore every other credential source
(`ANTHROPIC_AUTH_TOKEN`, profiles, OAuth, workload identity), so it is the only
credential passed. SDK retries are off (`max_retries=0`); the shared adapter owns
attempts and the deadline.

The SDK is imported only in `__init__`. The key is read once from `ANTHROPIC_API_KEY`
and never appears in a message, identity or result.
"""

import importlib
import os
import re
import time
from collections.abc import Callable
from typing import Any, Literal

from way2australia_rag.generation.base import GeneratorInfo, GeneratorOutput
from way2australia_rag.generation.claude import ClaudeMessagesAdapter, classify_error
from way2australia_rag.generation.config import AnthropicConfig
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.prompts import RenderedPrompt
from way2australia_rag.ingestion.errors import OptionalDependencyError

KEY_VARIABLE = "ANTHROPIC_API_KEY"
_MISSING_EXTRA_MESSAGE = (
    "the anthropic generator needs the optional 'anthropic' extra; "
    "run `make setup-anthropic`."
)
# Environment variables that would redirect requests or add headers (for example a
# server-side fallback beta header); refused so results come from the named model.
_REFUSED_VARIABLES = ("ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS")
# A dotted prefix marks a Bedrock-form ID (`global.`, `apac.`, `anthropic.`).
_BEDROCK_FORM = re.compile(r"^[a-z]+\.")


def check_model_id_form(model_id: str) -> None:
    if _BEDROCK_FORM.match(model_id):
        raise GeneratorConfigurationError(
            f"model ID {model_id!r} is a Bedrock-form ID; the anthropic generator "
            "needs a bare model ID such as claude-sonnet-5-5."
        )


class AnthropicGenerator:
    def __init__(
        self,
        config: AnthropicConfig,
        model_id: str,
        model_id_source: Literal["config", "cli", "env"],
        *,
        client: Any | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """`client` is the test seam: when given, the SDK is not imported.

        Every refusal below happens before a client is built, with or without the seam.
        """
        check_model_id_form(model_id)
        for name in _REFUSED_VARIABLES:
            if name in os.environ:
                raise GeneratorConfigurationError(
                    f"{name} is set; unset it so requests go to the Anthropic API "
                    "with no redirection or extra headers."
                )
        key = os.environ.get(KEY_VARIABLE, "")
        if not key.strip():
            raise GeneratorConfigurationError(
                f"{KEY_VARIABLE} is not set; the anthropic generator reads its "
                "key only from that variable."
            )
        self._model_id = model_id
        self._client = client if client is not None else self._build_client(key)
        self._adapter = ClaudeMessagesAdapter(
            self._client,
            model_id,
            config,
            clock=clock,
            sleep=sleep,
            check_response=self._check_response,
        )
        self.info = GeneratorInfo(
            provider="anthropic",
            model_id=model_id,
            model_id_source=model_id_source,
            endpoint="api",
            region=None,
            inference_profile=None,
            effort=config.effort,
            max_tokens=config.max_tokens,
            request_timeout_s=config.request_timeout_s,
            retries=config.retries,
            deadline_s=config.deadline_s,
            is_fake=False,
        )

    @staticmethod
    def _build_client(key: str) -> Any:
        try:
            sdk = importlib.import_module("anthropic")
        except ImportError as error:
            raise OptionalDependencyError(_MISSING_EXTRA_MESSAGE) from error
        try:
            # An explicit api_key makes the SDK ignore every other credential source.
            return sdk.Anthropic(api_key=key, max_retries=0)
        except Exception as error:
            # Never echo the exception text: it could carry the key.
            raise GeneratorConfigurationError(
                f"cannot create the Anthropic client ({type(error).__name__})."
            ) from None

    def _check_response(self, message: Any) -> None:
        """Exact match; a missing `model` is a mismatch (design: response model)."""
        got = getattr(message, "model", None)
        if got != self._model_id:
            raise GeneratorConfigurationError(
                f"the response model {got!r} differs from the configured model "
                f"{self._model_id!r}; no answer is used."
            )

    def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
        return self._adapter.generate(prompt)

    def close(self) -> None:
        self._adapter.close()


__all__ = ["AnthropicGenerator", "check_model_id_form", "classify_error"]
