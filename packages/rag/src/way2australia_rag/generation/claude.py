"""Shared Claude Messages adapter (Spec 012 R4, R5, R17; design "Direct Anthropic API
generator", "Bedrock adapter").

Holds what the Bedrock and direct-API generators share: the request builder, the
attempt loop with deadline and backoff, the D-B error table and output parsing.
Each generator builds its own client and `GeneratorInfo`, then delegates here. The
adapter speaks the Anthropic Messages surface only and never imports an SDK.
"""

import json
import time
from collections.abc import Callable
from typing import Any, Protocol

import jsonschema

from way2australia_rag.generation.base import GeneratorOutput, GeneratorUsage
from way2australia_rag.generation.errors import (
    GeneratorConfigurationError,
    GeneratorDeclinedError,
    GeneratorOutputError,
    GeneratorUnavailableError,
    UnavailableReason,
)
from way2australia_rag.generation.prompts import RenderedPrompt

# Stop instead of starting an attempt that has this much time or less left.
_MIN_ATTEMPT_S = 1.0
_CAUSE_DEPTH = 4

# D-B: HTTP statuses retried, then served as evidence only.
_STATUS_REASON: dict[int, UnavailableReason] = {
    408: UnavailableReason.TIMEOUT,
    429: UnavailableReason.THROTTLED,
    500: UnavailableReason.SERVER_ERROR,
    502: UnavailableReason.SERVER_ERROR,
    503: UnavailableReason.SERVER_ERROR,
    504: UnavailableReason.SERVER_ERROR,
    529: UnavailableReason.SERVER_ERROR,
}
# D-B: statuses that are configuration errors, never retried (413 added 2026-11-10).
_CONFIG_STATUSES = frozenset({400, 401, 403, 404, 413})
# botocore credential and region errors, matched by type name (not imported).
_CREDENTIAL_ERROR_NAMES = frozenset(
    {
        "NoCredentialsError",
        "PartialCredentialsError",
        "CredentialRetrievalError",
        "TokenRetrievalError",
        "NoRegionError",
        "ProfileNotFound",
        "UnauthorizedSSOTokenError",
        "SSOTokenLoadError",
    }
)


def _type_names(error: BaseException) -> set[str]:
    return {cls.__name__ for cls in type(error).__mro__}


def _classify_one(
    error: BaseException,
) -> UnavailableReason | GeneratorConfigurationError | None:
    names = _type_names(error)
    if names & _CREDENTIAL_ERROR_NAMES:
        return GeneratorConfigurationError(
            f"AWS credentials or region are not usable ({type(error).__name__}); "
            "check the default AWS credential chain."
        )
    if "APITimeoutError" in names:
        return UnavailableReason.TIMEOUT
    if "APIConnectionError" in names:
        return UnavailableReason.CONNECTION
    status = getattr(error, "status_code", None)
    if isinstance(status, int) and "APIStatusError" in names:
        if status in _STATUS_REASON:
            return _STATUS_REASON[status]
        if status in _CONFIG_STATUSES:
            return GeneratorConfigurationError(
                f"the model request was refused (HTTP {status}, "
                f"{type(error).__name__}); check the model ID, access, region "
                "and request size."
            )
    return None


def classify_error(
    error: BaseException,
) -> UnavailableReason | GeneratorConfigurationError | None:
    """D-B table by SDK exception type; a wrapped error only through `__cause__`.

    `__context__` is ignored on purpose (D057): an unrelated error raised while
    handling another is not evidence of an outage.
    """
    current: BaseException | None = error
    for _ in range(_CAUSE_DEPTH):
        if current is None:
            return None
        verdict = _classify_one(current)
        if verdict is not None:
            return verdict
        current = current.__cause__
    return None


def _retry_after_s(error: BaseException) -> float | None:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    try:
        raw = headers.get("retry-after")
    except AttributeError:
        return None
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


class ClaudeLimits(Protocol):
    """The configuration fields the adapter reads (BedrockConfig, AnthropicConfig)."""

    @property
    def effort(self) -> str: ...
    @property
    def max_tokens(self) -> int: ...
    @property
    def request_timeout_s(self) -> float: ...
    @property
    def retries(self) -> int: ...
    @property
    def backoff_s(self) -> float: ...
    @property
    def deadline_s(self) -> float: ...


class ClaudeMessagesAdapter:
    def __init__(
        self,
        client: Any,
        model: str,
        config: ClaudeLimits,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        check_response: Callable[[Any], None] | None = None,
    ) -> None:
        self._client = client
        self._model = model
        self._config = config
        self._clock = clock
        self._sleep = sleep
        # Runs before parsing; None (Bedrock) checks nothing.
        self._check_response = check_response

    def _request(self, prompt: RenderedPrompt) -> dict[str, Any]:
        return {
            "model": self._model,
            "max_tokens": self._config.max_tokens,
            "system": prompt.system,
            "messages": [{"role": "user", "content": prompt.user}],
            "output_config": {
                "format": {"type": "json_schema", "schema": prompt.output_schema},
                "effort": self._config.effort,
            },
        }

    def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
        config = self._config
        request = self._request(prompt)
        deadline = self._clock() + config.deadline_s
        attempts = 0
        last_outage: UnavailableReason | None = None
        for attempt in range(config.retries + 1):
            remaining = deadline - self._clock()
            if remaining <= _MIN_ATTEMPT_S:
                # DEADLINE only when no error caused it; otherwise keep the
                # classified sub-reason (T3 review F1).
                raise GeneratorUnavailableError(
                    last_outage or UnavailableReason.DEADLINE
                )
            timeout = min(config.request_timeout_s, remaining)
            attempts += 1
            try:
                message = self._client.with_options(timeout=timeout).messages.create(
                    **request
                )
            except Exception as error:
                verdict = classify_error(error)
                if verdict is None:
                    raise
                if isinstance(verdict, GeneratorConfigurationError):
                    raise verdict from error
                last_outage = verdict
                remaining = deadline - self._clock()
                if remaining <= 0 or attempt == config.retries:
                    raise GeneratorUnavailableError(verdict) from error
                delay = config.backoff_s * 2**attempt
                hinted = _retry_after_s(error)
                if hinted is not None:
                    delay = max(delay, hinted)
                if remaining - delay <= _MIN_ATTEMPT_S:
                    # The wait leaves no usable attempt before the deadline: stop
                    # now, without sleeping, and keep the classified sub-reason.
                    raise GeneratorUnavailableError(verdict) from error
                self._sleep(delay)
                continue
            if self._check_response is not None:
                self._check_response(message)
            return self._parse(message, prompt, attempts)
        raise GeneratorUnavailableError(  # pragma: no cover
            last_outage or UnavailableReason.DEADLINE
        )

    def _parse(
        self, message: Any, prompt: RenderedPrompt, attempts: int
    ) -> GeneratorOutput:
        stop_reason = getattr(message, "stop_reason", None)
        if stop_reason == "refusal":
            raise GeneratorDeclinedError("the model refused to answer")
        if stop_reason == "max_tokens":
            raise GeneratorOutputError("max_tokens")
        text = next(
            (
                block.text
                for block in getattr(message, "content", [])
                if getattr(block, "type", None) == "text"
            ),
            None,
        )
        if text is None:
            raise GeneratorOutputError("json", "no text block in the response")
        try:
            data = json.loads(text)
        except ValueError as error:
            raise GeneratorOutputError("json") from error
        try:
            jsonschema.validate(data, prompt.output_schema)
        except jsonschema.ValidationError as error:
            raise GeneratorOutputError("schema") from error
        usage = getattr(message, "usage", None)
        return GeneratorOutput(
            answerable=data["answerable"],
            answer=data["answer"],
            citations=list(data["citations"]),
            usage=GeneratorUsage(
                input_tokens=getattr(usage, "input_tokens", None),
                output_tokens=getattr(usage, "output_tokens", None),
                attempts=attempts,
            ),
            stop_reason=stop_reason,
            response_model=getattr(message, "model", None),
        )

    def close(self) -> None:
        close = getattr(self._client, "close", None)
        if callable(close):
            close()
