"""Reranker failure classification (Spec 011 R1, R5).

Only a transport failure while fetching model files is "unavailable"; the same
chain rules as `classify_model_error` apply (explicit `__cause__` only,
`MAX_CAUSE_LINKS`, `__context__` never followed). Offline mode with weights not
cached is a configuration state and is never a skip, even when a network error
appears deeper in the chain. Nothing here reads an exception's text.
"""

from enum import StrEnum

import httpx

from way2australia_rag.retrieval.availability import (
    _NETWORK_TYPES,  # pyright: ignore[reportPrivateUsage]
    _cause_chain,  # pyright: ignore[reportPrivateUsage]
    _optional_types,  # pyright: ignore[reportPrivateUsage]
)


class RerankSkipReason(StrEnum):
    MODEL_UNAVAILABLE = "model_unavailable"
    MODEL_TIMEOUT = "model_timeout"


class RerankerUnavailableError(Exception):
    """The reranker could not be loaded or called because of an outage.

    Deliberately not a `RetrievalUnavailableError`: the reranking stage alone
    catches it, so a reranker outage can never become a BM25 fallback.
    """

    def __init__(self, reason: RerankSkipReason) -> None:
        super().__init__(f"reranker unavailable ({reason.value})")
        self.reason = reason


class RerankerOutputError(Exception):
    """Malformed reranker output (wrong count, non-finite score). Fail closed."""


_TIMEOUT_TYPES: tuple[type[BaseException], ...] = (
    httpx.TimeoutException,
    TimeoutError,
    *_optional_types(
        ("requests.exceptions", "Timeout"),
        ("urllib3.exceptions", "TimeoutError"),
    ),
)

# Offline mode / nothing cached: a configuration error, excluded even when a
# network error appears deeper in the chain.
_OFFLINE_TYPES: tuple[type[BaseException], ...] = _optional_types(
    ("huggingface_hub.errors", "OfflineModeIsEnabled"),
    ("huggingface_hub.errors", "LocalEntryNotFoundError"),
)


def is_offline_not_cached(error: BaseException) -> bool:
    """True when the cause chain holds a hub offline / not-cached error."""
    return bool(_OFFLINE_TYPES) and any(
        isinstance(item, _OFFLINE_TYPES) for item in _cause_chain(error)
    )


def classify_reranker_error(error: BaseException) -> RerankerUnavailableError | None:
    """Map a model load or call failure to a skip reason, or `None` (not eligible)."""
    if isinstance(error, RerankerUnavailableError):
        return error
    chain = _cause_chain(error)
    if is_offline_not_cached(error):
        return None
    if any(isinstance(item, _TIMEOUT_TYPES) for item in chain):
        return RerankerUnavailableError(RerankSkipReason.MODEL_TIMEOUT)
    if any(isinstance(item, _NETWORK_TYPES) for item in chain):
        return RerankerUnavailableError(RerankSkipReason.MODEL_UNAVAILABLE)
    return None
