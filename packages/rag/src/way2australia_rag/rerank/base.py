"""Reranker contract (Spec 011 R1).

A reranker scores a query against an ordered list of texts. It knows nothing
about access, language applicability, chunks or documents: it receives strings
only, and the texts are data, never instructions.
"""

from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class RerankerInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    revision: str
    max_length: int
    is_fake: bool


class RerankScores(BaseModel):
    """One score per input text, in input order, plus the truncation count."""

    model_config = ConfigDict(frozen=True)

    scores: list[float]
    truncated_pairs: int


class Reranker(Protocol):
    info: RerankerInfo

    @property
    def device(self) -> str | None:
        """`None` until the model is loaded."""
        ...

    def load(self) -> None:
        """Idempotent. May raise `RerankerUnavailableError`."""
        ...

    def score(self, query: str, texts: Sequence[str]) -> RerankScores: ...
