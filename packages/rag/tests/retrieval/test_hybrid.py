"""Hybrid retriever: legs, empty leg, fail closed (Spec 007 R7)."""

from pathlib import Path
from typing import Any

import pytest
from lexical_support import (
    build_production,
    ingest_dense,
    open_lexical,
)
from qdrant_client import QdrantClient, models
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.retrieval import hybrid
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import (
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)
from way2australia_rag.retrieval.fusion import FusionConfig, rrf_fuse
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.models import RetrievalResult, RetrievedChunk
from way2australia_rag.retrieval.retriever import DenseRetriever

from .test_bm25 import (
    DroppedClauseIndex,
    build,
    guest,
    pub,
)

FUSION = FusionConfig(
    method="rrf", k=60, weights={"dense": 1.0, "bm25": 1.0}, candidate_depth=50
)
EMBEDDER = FakeEmbedder()


@pytest.fixture(scope="module")
def dense_pair() -> tuple[QdrantClient, DenseIndex]:
    return ingest_dense()


@pytest.fixture(scope="module")
def production_lexical(
    dense_pair: tuple[QdrantClient, DenseIndex],
    tmp_path_factory: pytest.TempPathFactory,
) -> Any:
    target = tmp_path_factory.mktemp("lex") / "prod.sqlite"
    build_production(target)
    return open_lexical(target)


def real_hybrid(dense: DenseIndex, lexical: Any) -> HybridRetriever:
    return HybridRetriever(
        DenseRetriever(dense, EMBEDDER), BM25Retriever(dense, lexical), FUSION
    )


def test_hybrid_result_shape(
    dense_pair: tuple[QdrantClient, DenseIndex], production_lexical: Any
) -> None:
    dense = dense_pair[1]
    result = real_hybrid(dense, production_lexical).retrieve(
        "Is coaching compulsory?", guest(), 5
    )
    assert result.strategy == "hybrid" == Strategy.HYBRID
    assert result.score_kind == "rrf"
    assert result.top_k == 5
    assert 0 < len(result.hits) <= 5
    assert [h.rank for h in result.hits] == list(range(1, len(result.hits) + 1))
    scores = [h.score for h in result.hits]
    assert scores == sorted(scores, reverse=True)
    for hit in result.hits:
        assert hit.leg_ranks is not None
        assert set(hit.leg_ranks) == {"dense", "bm25"}
    assert result.collection == dense.collection
    assert result.index_version == dense.index_version
    assert result.embedder_is_fake is True
    assert result.lexical is not None
    assert result.lexical.label == "prod.sqlite"
    assert result.query_terms_truncated is False
    assert result.leg_latency_ms is not None
    assert set(result.leg_latency_ms) == {"dense", "bm25"}


@pytest.mark.parametrize("query", ["zzqqxx", "?!", "   ... ---", "ആനക്കൊമ്പ് ശില്പം"])
def test_empty_bm25_leg_keeps_the_dense_order(
    dense_pair: tuple[QdrantClient, DenseIndex], production_lexical: Any, query: str
) -> None:
    dense = dense_pair[1]
    expected = DenseRetriever(dense, EMBEDDER).retrieve(query, guest(), 5)
    bm25 = BM25Retriever(dense, production_lexical).retrieve(query, guest(), 50)
    assert bm25.hits == []
    result = real_hybrid(dense, production_lexical).retrieve(query, guest(), 5)
    assert [h.point_id for h in result.hits] == [h.point_id for h in expected.hits]
    assert all(
        h.leg_ranks is not None and h.leg_ranks["bm25"] is None for h in result.hits
    )


def test_legs_run_at_candidate_depth_then_cut_to_top_k() -> None:
    seen: list[tuple[str, int]] = []

    class Leg:
        def __init__(self, name: str, ids: list[str]) -> None:
            self.name, self.ids = name, ids
            self.strategy = Strategy.DENSE

        def retrieve(
            self, query_text: str, access: ResolvedAccess, top_k: int = 5
        ) -> RetrievalResult:
            seen.append((self.name, top_k))
            return stub_result(self.ids)

    retriever = HybridRetriever(
        Leg("dense", ["a", "b", "c"]), Leg("bm25", ["c", "a"]), FUSION
    )  # pyright: ignore[reportArgumentType]
    result = retriever.retrieve("q", guest(), 2)
    assert seen == [("dense", 50), ("bm25", 50)]
    assert [h.point_id for h in result.hits] == ["a", "c"]
    assert [h.rank for h in result.hits] == [1, 2]
    assert result.hits[0].leg_ranks == {"dense": 1, "bm25": 2}


def chunk(point_id: str, rank: int) -> RetrievedChunk:
    return pub_chunk(point_id, rank)


def pub_chunk(point_id: str, rank: int) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        point_id=point_id,
        score=1.0,
        document_id=f"doc_{point_id}",
        document_version=1,
        section_id="s",
        chunk_position=0,
        title="t",
        chunk_text="x",
        knowledge_domain="d",
        source_authority="business_policy",
        source_type="faq",
        source_url=None,
        content_language="en",
        lote_languages=["*"],
    )


def stub_result(ids: list[str]) -> RetrievalResult:
    return RetrievalResult(
        hits=[pub_chunk(pid, rank) for rank, pid in enumerate(ids, start=1)],
        collection="c",
        index_version="v",
        embedder_model_id="m",
        embedder_revision="r",
        embedder_is_fake=True,
        device=None,
        top_k=50,
        latency_ms=1.0,
    )


class ForbiddenDenseIndex(DenseIndex):
    """A dense store double that returns a staff-scope point (filter ignored)."""

    def search(
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        return [
            models.ScoredPoint(
                id="11111111-1111-5111-8111-111111111111",
                version=0,
                score=0.99,
                payload={"document_id": "doc_staff", "access_scope": "staff"},
            )
        ]


def test_forbidden_bm25_hit_fails_the_whole_query(
    tmp_path: Path, dense_pair: tuple[QdrantClient, DenseIndex]
) -> None:
    dense = dense_pair[1]
    lexical = build(
        tmp_path,
        [
            ("px", pub("doc_x", "secret", access_scope="staff")),
            ("pa", pub("doc_a", "secret")),
        ],
    )
    retriever = HybridRetriever(
        DenseRetriever(dense, EMBEDDER),
        BM25Retriever(dense, DroppedClauseIndex(lexical)),  # pyright: ignore[reportArgumentType]
        FUSION,
    )
    with pytest.raises(RetrievalAuthorizationError) as caught:
        retriever.retrieve("secret", guest(), 5)
    assert caught.value.document_id == "doc_x"


def test_forbidden_dense_hit_fails_the_whole_query(
    tmp_path: Path, dense_pair: tuple[QdrantClient, DenseIndex]
) -> None:
    client, dense = dense_pair
    forbidden = ForbiddenDenseIndex(client, dense.collection, dense.settings)
    lexical = build(tmp_path, [("pa", pub("doc_a", "secret"))])
    retriever = HybridRetriever(
        DenseRetriever(forbidden, EMBEDDER), BM25Retriever(dense, lexical), FUSION
    )
    with pytest.raises(RetrievalAuthorizationError):
        retriever.retrieve("secret", guest(), 5)


@pytest.mark.parametrize("failing", ["dense", "bm25"])
def test_any_other_leg_error_propagates_without_fallback(failing: str) -> None:
    class Boom:
        strategy = Strategy.DENSE

        def retrieve(
            self, query_text: str, access: ResolvedAccess, top_k: int = 5
        ) -> RetrievalResult:
            raise RuntimeError("leg failed")

    class Fine:
        strategy = Strategy.DENSE

        def retrieve(
            self, query_text: str, access: ResolvedAccess, top_k: int = 5
        ) -> RetrievalResult:
            return stub_result(["a", "b"])

    dense = Boom() if failing == "dense" else Fine()
    bm25 = Boom() if failing == "bm25" else Fine()
    with pytest.raises(RuntimeError, match="leg failed"):
        HybridRetriever(dense, bm25, FUSION).retrieve("q", guest(), 5)  # pyright: ignore[reportArgumentType]


def test_fusion_receives_only_the_legs_checked_hits(
    monkeypatch: pytest.MonkeyPatch,
    dense_pair: tuple[QdrantClient, DenseIndex],
    production_lexical: Any,
) -> None:
    calls: list[dict[str, list[Any]]] = []

    def spy(legs: Any, k: int, weights: Any) -> Any:
        calls.append({name: list(hits) for name, hits in legs.items()})
        return rrf_fuse(legs, k, weights)

    monkeypatch.setattr(hybrid, "rrf_fuse", spy)
    dense = dense_pair[1]
    result = real_hybrid(dense, production_lexical).retrieve(
        "Is coaching compulsory?", guest(), 5
    )
    assert len(calls) == 1
    assert list(calls[0]) == ["dense", "bm25"]
    expected_dense = DenseRetriever(dense, EMBEDDER).retrieve(
        "Is coaching compulsory?", guest(), 50
    )
    assert calls[0]["dense"] == expected_dense.hits
    for hits in calls[0].values():
        assert all(isinstance(hit, RetrievedChunk) for hit in hits)
    assert {h.point_id for h in result.hits} <= {
        h.point_id for hits in calls[0].values() for h in hits
    }


@pytest.mark.parametrize("query,top_k", [("", 5), (" ", 5), ("q", 0), ("q", 51)])
def test_request_validation_before_any_leg(query: str, top_k: int) -> None:
    class Never:
        strategy = Strategy.DENSE

        def retrieve(self, *args: Any, **kwargs: Any) -> RetrievalResult:
            raise AssertionError("leg must not run")

    with pytest.raises(RetrievalConfigurationError):
        HybridRetriever(Never(), Never(), FUSION).retrieve(query, guest(), top_k)  # pyright: ignore[reportArgumentType]
