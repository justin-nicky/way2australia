"""Section-level metrics (Spec 006 R6)."""

from way2australia_rag.evaluation.sections import (
    NO_SECTIONS_NOTE,
    dedupe_sections,
    section_key,
    section_report,
)
from way2australia_rag.retrieval.models import RetrievedChunk


def hit(rank: int, doc: str, section: str) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank, point_id=f"p{rank}", score=1.0 / rank, document_id=doc,
        document_version=1, section_id=section, chunk_position=0, title="t",
        chunk_text="c", knowledge_domain="d", source_authority="a",
        source_type="s", source_url=None, content_language="en",
        lote_languages=["*"],
    )  # fmt: skip


def test_keys_dedupe_at_best_rank() -> None:
    hits = [hit(1, "d1", "s1"), hit(2, "d1", "s1"), hit(3, "d1", "s2")]
    assert dedupe_sections(hits) == ["d1#s1", "d1#s2"]
    assert section_key("d1", "s1") == "d1#s1"


def test_metrics_on_synthetic_cases() -> None:
    rows = [
        {"ranked_section_ids": ["d#a", "d#b"], "relevant_section_ids": ["d#b"]},
        {"ranked_section_ids": ["d#a"], "relevant_section_ids": ["d#z", "d#a"]},
        {"ranked_section_ids": ["d#a"], "relevant_section_ids": ["d#q"]},
        {"ranked_section_ids": ["d#a"], "relevant_section_ids": []},
    ]
    report = section_report(rows, 5)
    assert report["measurable_cases"] == 3
    assert report["hit_rate_at_5"] == round(2 / 3, 4)
    assert report["recall_at_5"] == round((1.0 + 0.5 + 0.0) / 3, 4)
    assert report["mrr"] == round((0.5 + 1.0 + 0.0) / 3, 4)


def test_zero_measurable_reports_a_note_and_no_metrics() -> None:
    rows = [{"ranked_section_ids": ["d#main"], "relevant_section_ids": []}]
    report = section_report(rows, 5)
    assert report == {"measurable_cases": 0, "note": NO_SECTIONS_NOTE}
