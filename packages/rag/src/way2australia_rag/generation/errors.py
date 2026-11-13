"""Generator error hierarchy (Spec 012 R4, D-B). Messages never carry credentials."""

from enum import StrEnum


class UnavailableReason(StrEnum):
    """Closed set of outage sub-reasons (D-B)."""

    CONNECTION = "connection"
    TIMEOUT = "timeout"
    THROTTLED = "throttled"
    SERVER_ERROR = "server_error"
    DEADLINE = "deadline"


class GeneratorUnavailableError(Exception):
    """The generator could not answer in time or at all: serve evidence only."""

    def __init__(self, reason: UnavailableReason, message: str | None = None) -> None:
        super().__init__(message or f"generator unavailable ({reason.value})")
        self.reason = reason


class GeneratorConfigurationError(Exception):
    """Invalid generation configuration or an unusable generator (CLI exit 2)."""


class GeneratorDeclinedError(Exception):
    """The model refused (refusal stop reason)."""


class GeneratorOutputError(Exception):
    """The model output cannot be used: `max_tokens`, `json` or `schema`."""

    def __init__(self, rule: str, message: str | None = None) -> None:
        super().__init__(message or f"generator output invalid ({rule})")
        self.rule = rule
