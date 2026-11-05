"""BAAI/bge-reranker-v2-m3 cross-encoder adapter (Spec 011 R2).

``sentence-transformers`` is the optional ``reranker`` extra
(``make setup-bge-m3``). It is imported only inside ``load()`` so importing this
module never needs it.
"""

import importlib.util
from collections.abc import Sequence
from typing import Any

from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    OptionalDependencyError,
)
from way2australia_rag.rerank.base import RerankerInfo, RerankScores
from way2australia_rag.rerank.errors import (
    RerankerUnavailableError,
    classify_reranker_error,
    is_offline_not_cached,
)
from way2australia_rag.retrieval.errors import RetrievalConfigurationError

BGE_RERANKER_MODEL_ID = "BAAI/bge-reranker-v2-m3"
_FLOATING_REVISIONS = frozenset({"main", "latest"})

_MISSING_EXTRA_MESSAGE = (
    "The reranker needs the optional 'reranker' dependency group; "
    "run `make setup-bge-m3`."
)
_OFFLINE_MESSAGE = (
    "The reranker weights are not cached and the Hugging Face hub is offline; "
    "run `make setup-bge-m3` and cache the pinned reranker revision while online."
)


def _extra_installed() -> bool:
    """True when sentence-transformers is importable; never loads it or the model."""
    return importlib.util.find_spec("sentence_transformers") is not None


class BgeRerankerV2M3:
    def __init__(
        self, revision: str | None, max_length: int = 512, batch_size: int = 16
    ) -> None:
        cleaned = (revision or "").strip()
        if not cleaned or cleaned.lower() in _FLOATING_REVISIONS:
            raise IngestionConfigurationError(
                "The reranker requires a pinned model revision (a full commit SHA); "
                "a missing revision, 'main' or 'latest' is refused."
            )
        if batch_size < 1:
            raise IngestionConfigurationError("Reranker batch size must be at least 1.")
        if max_length < 1:
            raise IngestionConfigurationError("Reranker max_length must be at least 1.")
        if not _extra_installed():
            raise OptionalDependencyError(_MISSING_EXTRA_MESSAGE)
        self.info = RerankerInfo(
            model_id=BGE_RERANKER_MODEL_ID,
            revision=cleaned,
            max_length=max_length,
            is_fake=False,
        )
        self._batch_size = batch_size
        self._model: Any = None
        self._identity_activation: Any = None

    @property
    def device(self) -> str | None:
        if self._model is None:
            return None
        return str(getattr(self._model, "device", None))

    def _load_model(self) -> Any:
        try:
            from sentence_transformers import (  # pyright: ignore[reportMissingImports]
                CrossEncoder,
            )
            from torch import nn  # pyright: ignore[reportMissingImports]
        except ImportError as exc:
            raise OptionalDependencyError(_MISSING_EXTRA_MESSAGE) from exc
        self._identity_activation = nn.Identity()
        return CrossEncoder(
            self.info.model_id,
            revision=self.info.revision,
            max_length=self.info.max_length,
        )

    def _wrap(self, error: Exception) -> Exception:
        """Eligible outage -> `RerankerUnavailableError`; offline-not-cached ->
        configuration error; anything else is returned unchanged."""
        if isinstance(error, (OptionalDependencyError, RerankerUnavailableError)):
            return error
        if is_offline_not_cached(error):
            wrapped = RetrievalConfigurationError(_OFFLINE_MESSAGE)
            wrapped.__cause__ = error
            return wrapped
        unavailable = classify_reranker_error(error)
        if unavailable is not None:
            unavailable.__cause__ = error
            return unavailable
        return error

    def load(self) -> None:
        if self._model is not None:
            return
        try:
            self._model = self._load_model()
        except Exception as error:
            wrapped = self._wrap(error)
            if wrapped is error:
                raise
            raise wrapped from error

    def _count_truncated(self, query: str, texts: Sequence[str]) -> int:
        tokenizer = self._model.tokenizer
        count = 0
        for text in texts:
            encoded = tokenizer(query, text, truncation=False)
            if len(encoded["input_ids"]) > self.info.max_length:
                count += 1
        return count

    def score(self, query: str, texts: Sequence[str]) -> RerankScores:
        if not texts:
            return RerankScores(scores=[], truncated_pairs=0)
        self.load()
        pairs = [(query, text) for text in texts]
        try:
            raw = self._model.predict(
                pairs,
                batch_size=self._batch_size,
                activation_fn=self._identity_activation,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            truncated = self._count_truncated(query, texts)
        except Exception as error:
            wrapped = self._wrap(error)
            if wrapped is error:
                raise
            raise wrapped from error
        return RerankScores(scores=[float(x) for x in raw], truncated_pairs=truncated)
