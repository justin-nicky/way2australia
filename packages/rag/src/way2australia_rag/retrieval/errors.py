"""Retrieval error hierarchy. Messages never carry chunk text, paths or secrets."""

from enum import StrEnum


class RetrievalError(Exception):
    """Base class for all retrieval failures."""


class RetrievalConfigurationError(RetrievalError):
    """Retrieval configuration, role or settings are invalid or not implemented."""


class IndexBindingError(RetrievalError):
    """The index cannot be bound to the requested embedder or index version."""


class RetrievalAuthorizationError(RetrievalError):
    """A retrieved hit violates the access policy (fail closed).

    `document_id` is the hit's document ID (`<unreadable>` when absent).
    """

    def __init__(self, message: str, *, document_id: str) -> None:
        super().__init__(message)
        self.document_id = document_id


class FallbackReason(StrEnum):
    """Why a retrieval leg was unavailable (Spec 008 R1). Closed set."""

    QDRANT_UNAVAILABLE = "qdrant_unavailable"
    QDRANT_TIMEOUT = "qdrant_timeout"
    MODEL_UNAVAILABLE = "model_unavailable"


_UNAVAILABLE_MESSAGES = {
    FallbackReason.QDRANT_UNAVAILABLE: "the vector store is unavailable",
    FallbackReason.QDRANT_TIMEOUT: "the vector store timed out",
    FallbackReason.MODEL_UNAVAILABLE: (
        "the embedding model could not be loaded because of a network failure"
    ),
}


class RetrievalUnavailableError(RetrievalError):
    """A retrieval dependency is unreachable (the only fallback-eligible error).

    The message comes from `reason` alone: never the original exception text,
    which can carry URLs or credentials.
    """

    def __init__(self, reason: FallbackReason) -> None:
        reason = FallbackReason(reason)
        super().__init__(f"{_UNAVAILABLE_MESSAGES[reason]} ({reason.value}).")
        self.reason = reason
