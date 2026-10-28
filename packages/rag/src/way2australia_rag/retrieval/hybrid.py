"""Hybrid retriever: dense + BM25 legs fused with RRF (Spec 007 R7).

Each leg filters inside its own query and re-checks every hit (`check_hit`)
before returning, so fusion only ever sees authorized hits (D040). The legs run
sequentially; any exception from either leg propagates: there is no catch and
no single-leg fallback, so a failing leg fails the whole query.
"""

from time import perf_counter

from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import (
    DEFAULT_TOP_K,
    Retriever,
    Strategy,
    validate_request,
)
from way2australia_rag.retrieval.fusion import FusionConfig, rrf_fuse
from way2australia_rag.retrieval.metrics import dedupe_documents
from way2australia_rag.retrieval.models import RetrievalResult


class HybridRetriever:
    strategy = Strategy.HYBRID

    def __init__(self, dense: Retriever, bm25: Retriever, fusion: FusionConfig) -> None:
        self._dense = dense
        self._bm25 = bm25
        self._fusion = fusion

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
    ) -> RetrievalResult:
        validate_request(query_text, top_k)
        started = perf_counter()
        depth = self._fusion.candidate_depth
        dense = self._dense.retrieve(query_text, access, depth)
        bm25 = self._bm25.retrieve(query_text, access, depth)
        fused = rrf_fuse(
            {"dense": dense.hits, "bm25": bm25.hits},
            self._fusion.k,
            self._fusion.weights,
        )[:top_k]
        hits = [
            item.chunk.model_copy(
                update={
                    "rank": rank,
                    "score": item.score,
                    "leg_ranks": item.leg_ranks,
                }
            )
            for rank, item in enumerate(fused, start=1)
        ]
        latency_ms = (perf_counter() - started) * 1000.0
        return RetrievalResult(
            hits=hits,
            collection=dense.collection,
            index_version=dense.index_version,
            embedder_model_id=dense.embedder_model_id,
            embedder_revision=dense.embedder_revision,
            embedder_is_fake=dense.embedder_is_fake,
            device=dense.device,
            top_k=top_k,
            latency_ms=latency_ms,
            strategy=Strategy.HYBRID.value,
            score_kind="rrf",
            leg_latency_ms={"dense": dense.latency_ms, "bm25": bm25.latency_ms},
            lexical=bm25.lexical,
            query_terms_truncated=bm25.query_terms_truncated,
            leg_document_ranks={
                "dense": dedupe_documents(dense.hits),
                "bm25": dedupe_documents(bm25.hits),
            },
        )
