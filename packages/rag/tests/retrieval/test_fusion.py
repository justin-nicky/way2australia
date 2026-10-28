"""RRF fusion: hand-computed scores, ties, weights (Spec 007 R7)."""

import inspect
from typing import Any

import pytest
from pydantic import ValidationError
from way2australia_rag.retrieval import fusion
from way2australia_rag.retrieval.fusion import FusionConfig, rrf_fuse
from way2australia_rag.retrieval.models import RetrievedChunk

W = {"dense": 1.0, "bm25": 1.0}


def chunk(point_id: str, rank: int, **over: Any) -> RetrievedChunk:
    values: dict[str, Any] = {
        "rank": rank,
        "point_id": point_id,
        "score": 1.0,
        "document_id": f"doc_{point_id}",
        "document_version": 1,
        "section_id": "s",
        "chunk_position": 0,
        "title": "t",
        "chunk_text": "x",
        "knowledge_domain": "d",
        "source_authority": "business_policy",
        "source_type": "faq",
        "source_url": None,
        "content_language": "en",
        "lote_languages": ["*"],
    }
    values.update(over)
    return RetrievedChunk(**values)


def test_hand_computed_scores_and_order() -> None:
    dense = [chunk("a", 1), chunk("b", 2), chunk("c", 3)]
    bm25 = [chunk("c", 1), chunk("a", 2), chunk("d", 3)]
    fused = rrf_fuse({"dense": dense, "bm25": bm25}, 60, W)
    # a: 1/61 + 1/62; c: 1/63 + 1/61; b: 1/62; d: 1/63
    assert [h.chunk.point_id for h in fused] == ["a", "c", "b", "d"]
    assert fused[0].score == pytest.approx(1 / 61 + 1 / 62)
    assert fused[1].score == pytest.approx(1 / 63 + 1 / 61)
    assert fused[2].score == pytest.approx(1 / 62)
    assert fused[3].score == pytest.approx(1 / 63)
    assert fused[0].leg_ranks == {"dense": 1, "bm25": 2}
    assert fused[2].leg_ranks == {"dense": 2, "bm25": None}
    assert fused[3].leg_ranks == {"dense": None, "bm25": 3}


def test_equal_scores_and_ranks_break_by_point_id() -> None:
    legs = {
        "dense": [chunk("m", 1), chunk("n", 2)],
        "bm25": [chunk("n", 1), chunk("m", 2)],
    }
    fused = rrf_fuse(legs, 60, W)
    # m and n both score 1/61 + 1/62, best rank 1 each: point_id decides.
    assert fused[0].score == fused[1].score
    assert [h.chunk.point_id for h in fused] == ["m", "n"]
    reversed_ids = {
        "dense": [chunk("n", 1), chunk("m", 2)],
        "bm25": [chunk("m", 1), chunk("n", 2)],
    }
    assert [h.chunk.point_id for h in rrf_fuse(reversed_ids, 60, W)] == ["m", "n"]


def test_equal_scores_break_by_best_rank_before_point_id() -> None:
    # k=1: "a" (bm25 rank 2, weight 1.5) scores 1.5/3 = 0.5, "p" (dense rank 1,
    # weight 1) scores 1/2 = 0.5: equal. Best rank 1 beats 2 although "a" < "p"
    # alphabetically would put "a" first if point_id alone decided.
    legs = {"dense": [chunk("p", 1)], "bm25": [chunk("pad", 1), chunk("a", 2)]}
    fused = rrf_fuse(legs, 1, {"dense": 1.0, "bm25": 1.5})
    scores = {h.chunk.point_id: h.score for h in fused}
    assert scores["p"] == scores["a"] == 0.5
    order = [h.chunk.point_id for h in fused]
    assert order == ["pad", "p", "a"]


def test_empty_leg_keeps_the_other_order() -> None:
    dense = [chunk("a", 1), chunk("b", 2), chunk("c", 3)]
    fused = rrf_fuse({"dense": dense, "bm25": []}, 60, W)
    assert [h.chunk.point_id for h in fused] == ["a", "b", "c"]
    assert all(h.leg_ranks["bm25"] is None for h in fused)


def test_both_legs_empty() -> None:
    assert rrf_fuse({"dense": [], "bm25": []}, 60, W) == []


def test_first_seen_chunk_is_kept() -> None:
    d = chunk("a", 1, title="from dense")
    b = chunk("a", 1, title="from bm25")
    fused = rrf_fuse({"dense": [d], "bm25": [b]}, 60, W)
    assert fused[0].chunk.title == "from dense"


def test_duplicate_in_a_leg_counts_best_rank_only() -> None:
    fused = rrf_fuse({"dense": [chunk("a", 1), chunk("a", 2)], "bm25": []}, 60, W)
    assert len(fused) == 1
    assert fused[0].leg_ranks["dense"] == 1
    assert fused[0].score == pytest.approx(1 / 61)


def test_weights_scale_each_leg() -> None:
    legs = {"dense": [chunk("a", 1)], "bm25": [chunk("b", 1)]}
    fused = rrf_fuse(legs, 60, {"dense": 1.0, "bm25": 3.0})
    assert [h.chunk.point_id for h in fused] == ["b", "a"]
    assert fused[0].score == pytest.approx(3 / 61)


def test_fusion_module_has_no_authorization_or_io_surface() -> None:
    imports = [
        line
        for line in inspect.getsource(fusion).splitlines()
        if line.startswith(("import ", "from "))
    ]
    text = "\n".join(imports)
    for forbidden in ("access", "qdrant", "sqlite3", "lexical", "index"):
        assert forbidden not in text
    hints = inspect.signature(rrf_fuse).parameters["legs"].annotation
    assert "RetrievedChunk" in str(hints)


@pytest.mark.parametrize(
    "over",
    [
        {"method": "other"},
        {"k": 0},
        {"candidate_depth": 0},
        {"candidate_depth": 51},
        {"weights": {"dense": 1.0}},
        {"weights": {"dense": 1.0, "bm25": 1.0, "x": 1.0}},
        {"weights": {"dense": 0.0, "bm25": 1.0}},
        {"weights": {"dense": -1.0, "bm25": 1.0}},
        {"extra": 1},
    ],
)
def test_fusion_config_validation(over: dict[str, Any]) -> None:
    values: dict[str, Any] = {
        "method": "rrf",
        "k": 60,
        "weights": W,
        "candidate_depth": 50,
    }
    values.update(over)
    with pytest.raises(ValidationError):
        FusionConfig(**values)
