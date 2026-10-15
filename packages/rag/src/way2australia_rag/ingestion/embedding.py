"""Embedder interface and the deterministic fake embedder (Spec 004 R5).

Embedding is dense-only. The fake needs no model and no PyTorch, so unit tests
and CI can run the whole ingestion path.
"""

import hashlib
import math
from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from way2australia_rag.ingestion.errors import IngestionConfigurationError

FAKE_MODEL_ID = "fake-hash-embedder"
FAKE_REVISION = "1"
DEFAULT_FAKE_VECTOR_SIZE = 64


class EmbedderInfo(BaseModel):
    """Identity and settings of an embedder; recorded in the index settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    revision: str
    vector_size: int
    normalize: bool
    is_fake: bool
    settings: dict[str, str | int | float | bool] = {}


class Embedder(Protocol):
    info: EmbedderInfo

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class FakeEmbedder:
    """Deterministic SHA-256-derived dense embedder. Never business truth."""

    def __init__(self, vector_size: int = DEFAULT_FAKE_VECTOR_SIZE) -> None:
        if vector_size < 1:
            raise IngestionConfigurationError(
                "Fake embedder vector size must be at least 1."
            )
        self.info = EmbedderInfo(
            model_id=FAKE_MODEL_ID,
            revision=FAKE_REVISION,
            vector_size=vector_size,
            normalize=True,
            is_fake=True,
        )

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        size = self.info.vector_size
        raw: list[float] = []
        counter = 0
        seed = text.encode("utf-8")
        while len(raw) < size:
            digest = hashlib.sha256(counter.to_bytes(4, "big") + seed).digest()
            raw.extend((byte - 127.5) / 127.5 for byte in digest)
            counter += 1
        vector = raw[:size]
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0.0:  # practically unreachable; keep the output well-defined
            vector[0] = 1.0
            return vector
        return [v / norm for v in vector]
