"""Document-level metric tests on hand-built rankings (Spec 005 R7, R11)."""

import pytest
from way2australia_rag.retrieval.metrics import (
    dedupe_documents,
    hit_rate_at_k,
    percentile,
    random_hit_rate,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.models import RetrievedChunk


def chunk(rank: int, document_id: str) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        point_id=f"p{rank}",
        score=1.0 / rank,
        document_id=document_id,
        document_version=1,
        section_id="main",
        chunk_position=rank,
        title="t",
        chunk_text="c",
        knowledge_domain="business",
        source_authority="owner_approved",
        source_type="faq",
        source_url=None,
        content_language="en",
        lote_languages=["*"],
    )


def test_dedupe_keeps_first_rank() -> None:
    hits = [chunk(1, "a"), chunk(2, "b"), chunk(3, "a"), chunk(4, "c")]
    assert dedupe_documents(hits) == ["a", "b", "c"]


def test_hit_rate_and_cutoff() -> None:
    assert hit_rate_at_k(["a", "b", "c"], {"c"}, 3) == 1.0
    assert hit_rate_at_k(["a", "b", "c"], {"c"}, 2) == 0.0
    assert hit_rate_at_k([], {"c"}, 5) == 0.0


def test_recall_with_several_relevant() -> None:
    assert recall_at_k(["a", "x", "b"], {"a", "b", "c", "d"}, 5) == 0.5
    assert recall_at_k(["a", "x", "b"], {"a", "b"}, 2) == 0.5
    assert recall_at_k(["x"], {"a"}, 5) == 0.0
    with pytest.raises(ValueError):
        recall_at_k(["a"], set(), 5)


def test_reciprocal_rank() -> None:
    assert reciprocal_rank(["x", "y", "a"], {"a", "z"}) == pytest.approx(1 / 3)
    assert reciprocal_rank(["a"], {"a"}) == 1.0
    assert reciprocal_rank(["x", "y"], {"a"}) == 0.0


def test_random_hit_rate_cap_and_minimum() -> None:
    assert random_hit_rate(5, 13) == pytest.approx(5 / 13)
    assert random_hit_rate(5, 5) == 1.0
    assert random_hit_rate(5, 3) == 1.0
    with pytest.raises(ValueError):
        random_hit_rate(5, 0)


def test_percentile_nearest_rank() -> None:
    values = [10.0, 20.0, 30.0, 40.0]
    assert percentile(values, 50) == 20.0
    assert percentile(values, 95) == 40.0
    assert percentile([7.0], 50) == 7.0
    assert percentile(list(range(1, 101)), 95) == 95
    with pytest.raises(ValueError):
        percentile([], 50)
