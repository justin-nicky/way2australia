"""BGE-M3 dense embedder (Spec 004 R6).

``sentence-transformers`` (which brings PyTorch) is an optional dependency group
(``make setup-bge-m3``). It is imported only inside ``_load_model`` so importing
this module never needs it.
"""

import importlib.util
from collections.abc import Sequence
from typing import Any

from way2australia_rag.ingestion.embedding import EmbedderInfo
from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    OptionalDependencyError,
)

BGE_M3_MODEL_ID = "BAAI/bge-m3"
BGE_M3_VECTOR_SIZE = 1024
DEFAULT_BATCH_SIZE = 16
_FLOATING_REVISIONS = frozenset({"main", "latest"})


_MISSING_GROUP_MESSAGE = (
    "BGE-M3 needs the optional 'bge-m3' dependency group; run `make setup-bge-m3`."
)


def _group_installed() -> bool:
    """True when sentence-transformers is importable; never loads it or the model."""
    return importlib.util.find_spec("sentence_transformers") is not None


class BgeM3Embedder:
    """Dense-only, normalized BGE-M3 embeddings pinned to a model revision."""

    def __init__(
        self, revision: str | None, batch_size: int = DEFAULT_BATCH_SIZE
    ) -> None:
        cleaned = (revision or "").strip()
        if not cleaned or cleaned.lower() in _FLOATING_REVISIONS:
            raise IngestionConfigurationError(
                "BGE-M3 requires a pinned model revision (a full commit SHA); "
                "a missing revision, 'main' or 'latest' is refused."
            )
        if batch_size < 1:
            raise IngestionConfigurationError("BGE-M3 batch size must be at least 1.")
        if not _group_installed():
            raise OptionalDependencyError(_MISSING_GROUP_MESSAGE)
        self.info = EmbedderInfo(
            model_id=BGE_M3_MODEL_ID,
            revision=cleaned,
            vector_size=BGE_M3_VECTOR_SIZE,
            normalize=True,
            is_fake=False,
        )
        self._batch_size = batch_size
        self._model: Any = None

    def _load_model(self) -> Any:
        try:
            from sentence_transformers import (  # pyright: ignore[reportMissingImports]
                SentenceTransformer,
            )
        except ImportError as exc:
            raise OptionalDependencyError(_MISSING_GROUP_MESSAGE) from exc
        return SentenceTransformer(self.info.model_id, revision=self.info.revision)

    def _get_model(self) -> Any:
        if self._model is None:
            self._model = self._load_model()
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._get_model().encode(
            list(texts),
            batch_size=self._batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [[float(x) for x in row] for row in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
