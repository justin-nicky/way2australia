"""Dense retriever (Spec 005 R5).

Authorization comes only from the `ResolvedAccess` argument: the filter is built
by `build_access_filter` and every hit is re-checked by `check_hit` (fail
closed). Nothing from the query text reaches either. No score threshold and no
language filter or language-specific code.
"""

from time import perf_counter

from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    check_hit,
)
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.models import RetrievalResult, RetrievedChunk

MIN_TOP_K, MAX_TOP_K, DEFAULT_TOP_K = 1, 50, 5


class DenseRetriever:
    def __init__(self, index: DenseIndex, embedder: Embedder) -> None:
        self._index = index
        self._embedder = embedder

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
    ) -> RetrievalResult:
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
        started = perf_counter()
        vector = self._embedder.embed_query(query_text)
        points = self._index.search(vector, build_access_filter(access), top_k)
        latency_ms = (perf_counter() - started) * 1000.0
        checked = [(point, check_hit(point.payload or {}, access)) for point in points]
        checked.sort(key=lambda pair: pair[0].score, reverse=True)
        hits = [
            RetrievedChunk(
                rank=rank,
                point_id=str(point.id),
                score=float(point.score),
                document_id=payload.document_id,
                document_version=payload.document_version,
                section_id=payload.section_id,
                chunk_position=payload.chunk_position,
                title=payload.title,
                chunk_text=payload.chunk_text,
                knowledge_domain=payload.knowledge_domain,
                source_authority=payload.source_authority,
                source_type=payload.source_type,
                source_url=payload.source_url,
                content_language=payload.content_language,
                lote_languages=list(payload.lote_languages),
            )
            for rank, (point, payload) in enumerate(checked, start=1)
        ]
        settings = self._index.settings
        return RetrievalResult(
            hits=hits,
            collection=self._index.collection,
            index_version=self._index.index_version,
            embedder_model_id=settings.embedder_model_id,
            embedder_revision=settings.embedder_revision,
            embedder_is_fake=settings.embedder_is_fake,
            device=self._embedder.device,
            top_k=top_k,
            latency_ms=latency_ms,
        )
