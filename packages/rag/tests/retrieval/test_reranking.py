"""The reranking stage (Spec 011 R4, R5): ordering, skips, re-check, fallback order."""

from collections.abc import Sequence
from typing import Any

import pytest
from way2australia_core import AccessContext, Role
from way2australia_rag.rerank.base import RerankerInfo, RerankScores
from way2australia_rag.rerank.errors import (
    RerankerOutputError,
    RerankerUnavailableError,
    RerankSkipReason,
)
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    LanguageApplicabilityError,
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.models import RetrievalResult, RetrievedChunk
from way2australia_rag.retrieval.reranking import RerankingRetriever

FUSION = FusionConfig(
    method="rrf", k=60, weights={"dense": 1.0, "bm25": 1.0}, candidate_depth=50
)
DEPTH = 6


def access() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def make_chunk(point_id: str, *, lote: list[str] | None = None) -> RetrievedChunk:
    return RetrievedChunk(
        rank=1,
        point_id=point_id,
        score=1.0,
        document_id=f"doc_{point_id}",
        document_version=1,
        section_id="s",
        chunk_position=0,
        title="t",
        chunk_text=f"text of {point_id}",
        knowledge_domain="d",
        source_authority="business_policy",
        source_type="faq",
        source_url=None,
        content_language="en",
        lote_languages=lote or ["*"],
    )


class Leg:
    strategy = Strategy.DENSE

    def __init__(
        self,
        chunks: list[RetrievedChunk],
        error: Exception | None = None,
    ) -> None:
        self.chunks = chunks
        self.error = error
        self.calls: list[int] = []

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = 5,
        *,
        lote: object = None,
    ) -> RetrievalResult:
        self.calls.append(top_k)
        if self.error is not None:
            raise self.error
        hits = [c.model_copy(update={"rank": r}) for r, c in enumerate(self.chunks, 1)]
        return RetrievalResult(
            hits=hits,
            collection="c",
            index_version="v",
            embedder_model_id="m",
            embedder_revision="r",
            embedder_is_fake=True,
            device=None,
            top_k=top_k,
            latency_ms=1.0,
        )


class Scripted:
    """A reranker with fixed scores; satisfies the `Reranker` protocol."""

    def __init__(self, scores: list[float]) -> None:
        self.info = RerankerInfo(
            model_id="scripted", revision="rev", max_length=512, is_fake=True
        )
        self._scores = scores
        self.texts: list[str] = []

    @property
    def device(self) -> str | None:
        return "fake"

    def load(self) -> None:
        return None

    def score(self, query: str, texts: Sequence[str]) -> RerankScores:
        self.texts = list(texts)
        return RerankScores(scores=self._scores[: len(texts)], truncated_pairs=2)


def hybrid(ids: list[str], bm25_ids: list[str] | None = None) -> HybridRetriever:
    chunks = {i: make_chunk(i) for i in ids}
    return HybridRetriever(
        Leg([chunks[i] for i in ids]),
        Leg([chunks[i] for i in (bm25_ids if bm25_ids is not None else ids)]),
        FUSION,
    )  # pyright: ignore[reportArgumentType]


def stage(reranker: Any, ids: list[str] | None = None, **kw: Any) -> RerankingRetriever:
    return RerankingRetriever(
        hybrid(ids if ids is not None else ["a", "b", "c", "d"]), reranker, DEPTH, **kw
    )


def test_orders_by_score_cuts_top_k_and_keeps_provenance() -> None:
    reranker = Scripted([0.1, 0.9, 0.5, 0.7])
    result = stage(reranker).retrieve("q", access(), 3)
    assert [h.point_id for h in result.hits] == ["b", "d", "c"]
    assert [h.rank for h in result.hits] == [1, 2, 3]
    assert [h.score for h in result.hits] == [0.9, 0.7, 0.5]
    assert [h.fused_rank for h in result.hits] == [2, 4, 3]
    assert all(h.leg_ranks is not None for h in result.hits)
    assert result.hits[0].leg_ranks == {"dense": 2, "bm25": 2}
    assert result.strategy == "hybrid" and result.score_kind == "cross_encoder"
    assert result.top_k == 3
    assert reranker.texts == [f"text of {i}" for i in "abcd"]  # chunk text as data
    record = result.rerank
    assert record is not None
    assert (record.model_id, record.revision, record.device) == (
        "scripted",
        "rev",
        "fake",
    )
    assert (record.depth, record.candidates, record.truncated_pairs) == (DEPTH, 4, 2)
    assert record.skipped_reason is None and record.stage is None
    assert result.leg_latency_ms is not None and "rerank" in result.leg_latency_ms
    assert set(result.leg_latency_ms) == {"dense", "bm25", "rerank"}


def test_ties_are_broken_by_fused_rank() -> None:
    result = stage(Scripted([0.5, 0.5, 0.5, 0.5])).retrieve("q", access(), 4)
    assert [h.point_id for h in result.hits] == ["a", "b", "c", "d"]


def test_hybrid_is_asked_for_depth_candidates() -> None:
    retriever = stage(Scripted([0.0] * 4))
    retriever.retrieve("q", access(), 2)
    hybrid_inner = retriever._hybrid  # pyright: ignore[reportPrivateUsage]
    assert isinstance(hybrid_inner, HybridRetriever)
    assert hybrid_inner._dense.calls == [50]  # type: ignore[attr-defined]  # pyright: ignore


def test_top_k_above_depth_is_a_configuration_error() -> None:
    with pytest.raises(RetrievalConfigurationError, match="rerank.depth"):
        stage(Scripted([0.0] * 4)).retrieve("q", access(), DEPTH + 1)


@pytest.mark.parametrize("mode", ["count", "nan"])
def test_malformed_output_fails_closed(mode: str) -> None:
    reranker = FakeReranker(malformed=mode)  # type: ignore[arg-type]
    with pytest.raises(RerankerOutputError):
        stage(reranker).retrieve("q", access(), 3)


def test_no_candidates_does_not_call_the_reranker() -> None:
    reranker = FakeReranker()
    result = stage(reranker, ids=[]).retrieve("q", access(), 3)
    assert result.hits == [] and reranker.score_calls == 0
    assert result.rerank is not None and result.rerank.candidates == 0


# --- re-check after the stage (R4) ------------------------------------------


class Defective(RerankingRetriever):
    """A stage with an ordering defect, for the re-check tests."""

    def __init__(self, *args: Any, defect: str, **kw: Any) -> None:
        super().__init__(*args, **kw)
        self._defect = defect

    def _order(
        self, candidates: list[RetrievedChunk], scores: list[float], top_k: int
    ) -> list[RetrievedChunk]:
        good = super()._order(candidates, scores, top_k)
        if self._defect == "foreign":
            return [make_chunk("zzz").model_copy(update={"rank": 1}), *good[1:]]
        if self._defect == "duplicate":
            return [good[0], good[0].model_copy(update={"rank": 2}), *good[2:]]
        return [good[0].model_copy(update={"title": "tampered"}), *good[1:]]


@pytest.mark.parametrize("defect", ["foreign", "duplicate", "tampered"])
def test_a_stage_defect_raises_an_authorization_error(defect: str) -> None:
    retriever = Defective(
        hybrid(["a", "b", "c"]), Scripted([0.9, 0.5, 0.1]), DEPTH, defect=defect
    )
    with pytest.raises(RetrievalAuthorizationError):
        retriever.retrieve("q", access(), 3)


def ml_hybrid() -> HybridRetriever:
    chunks = [make_chunk("a"), make_chunk("b", lote=["ml"])]
    return HybridRetriever(Leg(chunks), Leg(chunks), FUSION)  # pyright: ignore


def test_non_applicable_row_with_lote_raises() -> None:
    retriever = RerankingRetriever(ml_hybrid(), Scripted([0.9, 0.5]), DEPTH)
    with pytest.raises(LanguageApplicabilityError):
        retriever.retrieve("q", access(), 2, lote=ResolvedLote("ta"))
    ok = retriever.retrieve("q", access(), 2, lote=ResolvedLote("ml"))
    assert ok.lote == "ml" and len(ok.hits) == 2


def test_recheck_also_runs_on_both_skip_paths() -> None:
    open_skip = RerankingRetriever(
        ml_hybrid(), FakeReranker(), DEPTH, RerankSkipReason.MODEL_UNAVAILABLE
    )
    with pytest.raises(LanguageApplicabilityError):
        open_skip.retrieve("q", access(), 2, lote=ResolvedLote("ta"))
    query_skip = RerankingRetriever(ml_hybrid(), FakeReranker(fail_on_call=1), DEPTH)
    with pytest.raises(LanguageApplicabilityError):
        query_skip.retrieve("q", access(), 2, lote=ResolvedLote("ta"))


# --- skips and fallback order (R5) ------------------------------------------


def test_query_time_reranker_failure_serves_hybrid_not_bm25() -> None:
    reranker = FakeReranker(fail_on_call=1)
    bm25 = Leg([make_chunk("bm")])
    retriever = FallbackRetriever(stage(reranker), bm25, None)  # pyright: ignore
    plain = hybrid(["a", "b", "c", "d"]).retrieve("q", access(), 3)

    skipped = retriever.retrieve("q", access(), 3)
    assert skipped.strategy == "hybrid" and skipped.fallback_reason is None
    assert skipped.requested_strategy == "hybrid"
    assert [h.point_id for h in skipped.hits] == [h.point_id for h in plain.hits]
    assert skipped.hits == plain.hits and skipped.score_kind == "rrf"
    assert bm25.calls == []
    assert skipped.rerank is not None
    assert (skipped.rerank.skipped_reason, skipped.rerank.stage) == (
        "model_unavailable",
        "query",
    )
    # The next query tries again.
    again = retriever.retrieve("q", access(), 3)
    assert again.rerank is not None and again.rerank.skipped_reason is None
    assert again.score_kind == "cross_encoder"


def test_reranker_error_is_not_a_retrieval_unavailable_error() -> None:
    assert not issubclass(RerankerUnavailableError, RetrievalUnavailableError)


@pytest.mark.parametrize("per_query", [True, False])
def test_dense_outage_serves_bm25_without_reranking(per_query: bool) -> None:
    reranker = FakeReranker()
    bm25 = Leg([make_chunk("bm")])
    outage = RetrievalUnavailableError(FallbackReason.QDRANT_UNAVAILABLE)
    if per_query:
        dense = Leg([make_chunk("a")], error=outage)
        primary: Any = RerankingRetriever(
            HybridRetriever(dense, Leg([make_chunk("a")]), FUSION),  # pyright: ignore
            reranker,
            DEPTH,
        )
        retriever = FallbackRetriever(primary, bm25, None)  # pyright: ignore
    else:
        retriever = FallbackRetriever(None, bm25, outage.reason)  # pyright: ignore
    result = retriever.retrieve("q", access(), 3)
    assert result.fallback_reason == "qdrant_unavailable"
    assert result.rerank is None
    assert reranker.score_calls == 0 and reranker.load_calls == 0


def test_open_skip_is_sticky_and_never_reloads() -> None:
    reranker = FakeReranker()
    retriever = stage(reranker, open_skip=RerankSkipReason.MODEL_TIMEOUT)
    plain = hybrid(["a", "b", "c", "d"]).retrieve("q", access(), 3)
    for _ in range(3):
        result = retriever.retrieve("q", access(), 3)
        assert result.hits == plain.hits
        assert result.rerank is not None
        assert (result.rerank.skipped_reason, result.rerank.stage) == (
            "model_timeout",
            "open",
        )
    assert reranker.load_calls == 0 and reranker.score_calls == 0


def test_other_scoring_errors_propagate() -> None:
    class Boom(Scripted):
        def score(self, query: str, texts: Sequence[str]) -> RerankScores:
            raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        stage(Boom([])).retrieve("q", access(), 3)
