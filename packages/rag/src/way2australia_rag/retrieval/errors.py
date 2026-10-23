"""Retrieval error hierarchy. Messages never carry chunk text, paths or secrets."""


class RetrievalError(Exception):
    """Base class for all retrieval failures."""


class RetrievalConfigurationError(RetrievalError):
    """Retrieval configuration, role or settings are invalid or not implemented."""


class IndexBindingError(RetrievalError):
    """The index cannot be bound to the requested embedder or index version."""


class RetrievalAuthorizationError(RetrievalError):
    """A retrieved hit violates the access policy (fail closed)."""
