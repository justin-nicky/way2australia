"""Retriever contract, strategy names and the shared request check (Spec 007 R6).

`validate_request` holds the one query/`top_k` rule set used by every retriever,
so the messages stay identical across strategies.
"""

from enum import StrEnum
from typing import Protocol

from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.models import RetrievalResult

MIN_TOP_K, MAX_TOP_K, DEFAULT_TOP_K = 1, 50, 5


class Strategy(StrEnum):
    DENSE = "dense"
    BM25 = "bm25"
    HYBRID = "hybrid"


class Retriever(Protocol):
    strategy: Strategy

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
    ) -> RetrievalResult: ...


def validate_request(query_text: object, top_k: object) -> None:
    if not isinstance(query_text, str) or not query_text.strip():
        raise RetrievalConfigurationError("the query must not be empty.")
    if (
        isinstance(top_k, bool)
        or not isinstance(top_k, int)
        or not MIN_TOP_K <= top_k <= MAX_TOP_K
    ):
        raise RetrievalConfigurationError(
            f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
        )
