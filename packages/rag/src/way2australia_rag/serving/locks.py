"""Model locks for the threadpool route (Spec 013 R7).

One lock serializes embedder calls and a separate one serializes reranker
calls, so one request can embed while another reranks. Identity (`info`) and
`device` pass through unlocked: they are read-only after construction.
"""

from collections.abc import Sequence
from threading import Lock

from way2australia_rag.ingestion.embedding import Embedder, EmbedderInfo
from way2australia_rag.rerank.base import Reranker, RerankerInfo, RerankScores
from way2australia_rag.rerank.errors import classify_reranker_error


class LockedEmbedder:
    def __init__(self, inner: Embedder) -> None:
        self._inner = inner
        self._lock = Lock()
        self.info: EmbedderInfo = inner.info

    @property
    def device(self) -> str | None:
        return self._inner.device

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        with self._lock:
            return self._inner.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        with self._lock:
            return self._inner.embed_query(text)

    def close(self) -> None:
        close = getattr(self._inner, "close", None)
        if callable(close):
            close()


class LockedReranker:
    """Serializes `load` and `score`.

    An eligible load failure is sticky for the life of the process (D077): later
    `load` calls re-raise it without asking the model again, so a re-opened stack
    keeps the open-time skip instead of silently turning reranking back on.
    """

    def __init__(self, inner: Reranker) -> None:
        self._inner = inner
        self._lock = Lock()
        self._load_failure: Exception | None = None
        self.info: RerankerInfo = inner.info

    @property
    def device(self) -> str | None:
        return self._inner.device

    @property
    def load_failed(self) -> bool:
        with self._lock:
            return self._load_failure is not None

    def load(self) -> None:
        with self._lock:
            if self._load_failure is not None:
                raise self._load_failure
            try:
                self._inner.load()
            except Exception as error:
                if classify_reranker_error(error) is not None:
                    self._load_failure = error
                raise

    def score(self, query: str, texts: Sequence[str]) -> RerankScores:
        with self._lock:
            return self._inner.score(query, texts)

    def close(self) -> None:
        close = getattr(self._inner, "close", None)
        if callable(close):
            close()
