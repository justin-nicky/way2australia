"""Failure classification for the fallback policy (Spec 008 R1).

Only a transport failure is "unavailable". Both classifiers return `None` for
anything else, and the caller re-raises the original exception unchanged, so a
configuration or data problem never turns into a silent fallback.

Nothing here reads an exception's text: reasons come from `FallbackReason` only.
"""

import socket

import httpx
from qdrant_client.http.exceptions import ResponseHandlingException

from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalUnavailableError,
)

MAX_CAUSE_LINKS = 10


def _optional_types(*names: tuple[str, str]) -> tuple[type[BaseException], ...]:
    """Exception classes from optional packages; absent packages are skipped."""
    found: list[type[BaseException]] = []
    for module_name, class_name in names:
        try:
            module = __import__(module_name, fromlist=[class_name])
            found.append(getattr(module, class_name))
        except (ImportError, AttributeError):
            continue
    return tuple(found)


# Network or timeout types accepted anywhere in the explicit cause chain.
_NETWORK_TYPES: tuple[type[BaseException], ...] = (
    httpx.TimeoutException,
    httpx.NetworkError,  # includes httpx.ConnectError
    TimeoutError,
    ConnectionError,
    socket.gaierror,
    *_optional_types(
        ("requests.exceptions", "ConnectionError"),
        ("requests.exceptions", "Timeout"),
        ("urllib3.exceptions", "NewConnectionError"),
        ("urllib3.exceptions", "TimeoutError"),
    ),
)

# Offline mode with a missing cache is a configuration state, not an outage.
# It subclasses ConnectionError, so it must be excluded explicitly. The hub is
# only present with the bge-m3 extra; without it the hub cannot be the cause.
_EXCLUDED_TYPES: tuple[type[BaseException], ...] = _optional_types(
    ("huggingface_hub.errors", "OfflineModeIsEnabled"),
)


def classify_qdrant_error(error: BaseException) -> RetrievalUnavailableError | None:
    """Map a qdrant-client failure to a reason, or `None` (not eligible).

    qdrant-client wraps transport errors as `ResponseHandlingException` and keeps
    the original in `.source`. Exactly that one level is unwrapped; `__cause__`
    and `__context__` are never followed, so an unrelated error raised while
    handling a network error is not an outage.
    """
    candidate: object = error
    if isinstance(error, ResponseHandlingException):
        candidate = error.source
    if isinstance(candidate, httpx.TimeoutException):
        return RetrievalUnavailableError(FallbackReason.QDRANT_TIMEOUT)
    if isinstance(candidate, httpx.NetworkError):
        return RetrievalUnavailableError(FallbackReason.QDRANT_UNAVAILABLE)
    return None


def classify_model_error(error: BaseException) -> RetrievalUnavailableError | None:
    """Map a model load or download failure to `model_unavailable`, or `None`.

    transformers and the hub raise `OSError` for configuration errors (unknown
    model ID or revision, gated repository, corrupt cache) as well as outages,
    so the type alone is not enough: the explicit `__cause__` chain (`raise ...
    from`, at most `MAX_CAUSE_LINKS` links, starting at the error itself) must
    contain a network or timeout error. `__context__` is never followed.
    """
    chain: list[BaseException] = []
    link: BaseException | None = error
    while link is not None and len(chain) < MAX_CAUSE_LINKS and link not in chain:
        chain.append(link)
        link = link.__cause__
    if _EXCLUDED_TYPES and any(isinstance(item, _EXCLUDED_TYPES) for item in chain):
        return None
    if any(isinstance(item, _NETWORK_TYPES) for item in chain):
        return RetrievalUnavailableError(FallbackReason.MODEL_UNAVAILABLE)
    return None
