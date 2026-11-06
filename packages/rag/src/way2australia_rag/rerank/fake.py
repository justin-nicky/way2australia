"""Deterministic fake reranker for tests (Spec 011 R1). No extra, no download."""

import hashlib
import math
from collections.abc import Callable, Sequence
from typing import Literal

from way2australia_rag.rerank.base import RerankerInfo, RerankScores
from way2australia_rag.rerank.errors import RerankerUnavailableError, RerankSkipReason

PREFER_BONUS = 10.0


def stable_score(query: str, text: str) -> float:
    """A float in [0, 1) from a stable hash of the pair (never Python's `hash`)."""
    digest = hashlib.sha256(f"{query}\x00{text}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


class FakeReranker:
    def __init__(
        self,
        *,
        model_id: str = "fake-reranker",
        revision: str = "fake",
        max_length: int = 512,
        prefer: Callable[[str], bool] | None = None,
        fail_on_load: bool = False,
        fail_on_call: int | None = None,
        malformed: Literal["count", "nan"] | None = None,
    ) -> None:
        self.info = RerankerInfo(
            model_id=model_id, revision=revision, max_length=max_length, is_fake=True
        )
        self._prefer = prefer
        self._fail_on_load = fail_on_load
        self._fail_on_call = fail_on_call
        self._malformed = malformed
        self._loaded = False
        self.load_calls = 0
        self.score_calls = 0

    @property
    def device(self) -> str | None:
        return "fake" if self._loaded else None

    def load(self) -> None:
        self.load_calls += 1
        if self._fail_on_load:
            raise RerankerUnavailableError(RerankSkipReason.MODEL_UNAVAILABLE)
        self._loaded = True

    def score(self, query: str, texts: Sequence[str]) -> RerankScores:
        if not self._loaded:
            self.load()
        self.score_calls += 1
        if self._fail_on_call is not None and self.score_calls == self._fail_on_call:
            raise RerankerUnavailableError(RerankSkipReason.MODEL_UNAVAILABLE)
        scores = [
            stable_score(query, text)
            + (PREFER_BONUS if self._prefer is not None and self._prefer(text) else 0.0)
            for text in texts
        ]
        if self._malformed == "count":
            scores = scores[:-1]
        elif self._malformed == "nan" and scores:
            scores[0] = math.nan
        query_words = len(query.split())
        limit = self.info.max_length
        truncated = sum(1 for t in texts if query_words + len(t.split()) > limit)
        return RerankScores(scores=scores, truncated_pairs=truncated)
