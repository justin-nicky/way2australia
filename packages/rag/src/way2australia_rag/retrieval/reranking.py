"""Reranking stage on `hybrid` (Spec 011 R4, R5).

`RerankingRetriever` asks the hybrid retriever for the top `depth` fused chunks,
scores them with a `Reranker`, orders them by score, cuts to `top_k` and
re-checks every returned hit. It sits inside `FallbackRetriever`: a dense outage
(`RetrievalUnavailableError`) propagates untouched and BM25 serves without
reranking. A reranker outage (`RerankerUnavailableError`) is caught here only;
the un-reranked hybrid result is served, marked as skipped.

No inference timeout (Spec 011 D-B option 1): inference is local work that a
Python-level timeout cannot pre-empt; the network is touched only by the load at
open time. A binding per-request limit belongs to roadmap item 10.
"""

import math
from time import perf_counter
from typing import Literal

from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.rerank.base import Reranker
from way2australia_rag.rerank.errors import (
    RerankerOutputError,
    RerankerUnavailableError,
    RerankSkipReason,
)
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.applicability import ResolvedLote, check_applicable
from way2australia_rag.retrieval.base import (
    DEFAULT_TOP_K,
    Strategy,
    validate_request,
)
from way2australia_rag.retrieval.errors import (
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.models import (
    RerankRecord,
    RetrievalResult,
    RetrievedChunk,
)

_STAGE_FIELDS = {"rank", "score", "fused_rank", "leg_ranks"}


class RerankingRetriever:
    strategy = Strategy.HYBRID

    def __init__(
        self,
        hybrid: HybridRetriever,
        reranker: Reranker,
        depth: int,
        open_skip: RerankSkipReason | None = None,
    ) -> None:
        self._hybrid = hybrid
        self._reranker = reranker
        self._depth = depth
        self._open_skip = open_skip

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
        *,
        lote: ResolvedLote | None = None,
    ) -> RetrievalResult:
        validate_request(query_text, top_k)
        if top_k > self._depth:
            raise RetrievalConfigurationError(
                f"top_k {top_k} exceeds rerank.depth {self._depth}."
            )
        # A RetrievalUnavailableError from a leg propagates to FallbackRetriever.
        fused = self._hybrid.retrieve(query_text, access, self._depth, lote=lote)
        candidates = list(fused.hits)
        if self._open_skip is not None:
            return self._skipped(fused, top_k, lote, self._open_skip, "open")
        if not candidates:
            return self._finish(fused, [], top_k, lote, 0, 0, 0.0, [])
        started = perf_counter()
        try:
            scored = self._reranker.score(
                query_text, [chunk.chunk_text for chunk in candidates]
            )
        except RerankerUnavailableError as error:
            return self._skipped(fused, top_k, lote, error.reason, "query")
        rerank_ms = (perf_counter() - started) * 1000.0
        scores = scored.scores
        if len(scores) != len(candidates) or not all(
            math.isfinite(value) for value in scores
        ):
            raise RerankerOutputError(
                "malformed reranker output: expected one finite score per candidate."
            )
        hits = self._order(candidates, scores, top_k)
        return self._finish(
            fused,
            hits,
            top_k,
            lote,
            len(candidates),
            scored.truncated_pairs,
            rerank_ms,
            candidates,
        )

    def _order(
        self, candidates: list[RetrievedChunk], scores: list[float], top_k: int
    ) -> list[RetrievedChunk]:
        order = sorted(
            range(len(candidates)), key=lambda i: (-scores[i], candidates[i].rank)
        )[:top_k]
        return [
            candidates[i].model_copy(
                update={
                    "rank": rank,
                    "score": scores[i],
                    "fused_rank": candidates[i].rank,
                }
            )
            for rank, i in enumerate(order, start=1)
        ]

    def _record(
        self,
        candidates: int,
        truncated: int,
        reason: RerankSkipReason | None = None,
        stage: Literal["open", "query"] | None = None,
    ) -> RerankRecord:
        info = self._reranker.info
        return RerankRecord(
            model_id=info.model_id,
            revision=info.revision,
            max_length=info.max_length,
            is_fake=info.is_fake,
            device=self._reranker.device,
            depth=self._depth,
            candidates=candidates,
            truncated_pairs=truncated,
            skipped_reason=reason.value if reason is not None else None,
            stage=stage,
        )

    def _skipped(
        self,
        fused: RetrievalResult,
        top_k: int,
        lote: ResolvedLote | None,
        reason: RerankSkipReason,
        stage: Literal["open", "query"],
    ) -> RetrievalResult:
        hits = list(fused.hits[:top_k])
        self._recheck(hits, list(fused.hits), lote)
        return fused.model_copy(
            update={
                "hits": hits,
                "top_k": top_k,
                "rerank": self._record(0, 0, reason, stage),
            }
        )

    def _finish(
        self,
        fused: RetrievalResult,
        hits: list[RetrievedChunk],
        top_k: int,
        lote: ResolvedLote | None,
        candidates: int,
        truncated: int,
        rerank_ms: float,
        pool: list[RetrievedChunk],
    ) -> RetrievalResult:
        self._recheck(hits, pool, lote)
        legs = dict(fused.leg_latency_ms or {})
        legs["rerank"] = rerank_ms
        return fused.model_copy(
            update={
                "hits": hits,
                "top_k": top_k,
                "score_kind": "cross_encoder",
                "leg_latency_ms": legs,
                "latency_ms": fused.latency_ms + rerank_ms,
                "rerank": self._record(candidates, truncated),
            }
        )

    @staticmethod
    def _recheck(
        hits: list[RetrievedChunk],
        pool: list[RetrievedChunk],
        lote: ResolvedLote | None,
    ) -> None:
        """Defence in depth after the stage (R4).

        A `RetrievedChunk` carries no tenant or scope, so `check_hit` cannot run
        on it; the equivalent guarantee is that every returned hit is one of the
        candidates the hybrid legs already passed through `check_hit` (same
        content, no duplicates). `check_applicable` then runs on its
        `lote_languages` when a `lote` is set.
        """
        known = {
            chunk.point_id: chunk.model_dump(exclude=_STAGE_FIELDS) for chunk in pool
        }
        seen: set[str] = set()
        for hit in hits:
            if hit.point_id in seen or known.get(hit.point_id) != hit.model_dump(
                exclude=_STAGE_FIELDS
            ):
                raise RetrievalAuthorizationError(
                    f"hit for document '{hit.document_id}' was not among the "
                    "authorized candidates.",
                    document_id=hit.document_id,
                )
            seen.add(hit.point_id)
            if lote is not None:
                check_applicable(
                    PointPayload.model_construct(
                        document_id=hit.document_id,
                        lote_languages=hit.lote_languages,
                    ),
                    lote,
                )
