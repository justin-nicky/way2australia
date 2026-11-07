"""Context builder (Spec 012 R1, R13)."""

import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError
from way2australia_rag.generation.config import ContextConfig
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.retrieval.models import RetrievedChunk

REPO_ROOT = Path(__file__).resolve().parents[4]
GENERATION_SRC = REPO_ROOT / "packages/rag/src/way2australia_rag/generation"


def hit(rank: int, text: str, **overrides: object) -> RetrievedChunk:
    fields: dict[str, object] = {
        "rank": rank,
        "point_id": f"p{rank}",
        "score": 1.0 / rank,
        "document_id": f"doc_{rank}",
        "document_version": 2,
        "section_id": f"sec_{rank}",
        "chunk_position": 0,
        "title": f"Title {rank}",
        "chunk_text": text,
        "knowledge_domain": "business",
        "source_authority": "owner",
        "source_type": "markdown",
        "source_url": f"https://example.org/{rank}",
        "content_language": "en",
        "lote_languages": ["*"],
    }
    fields.update(overrides)
    return RetrievedChunk(**fields)  # type: ignore[arg-type]


def builder(max_blocks: int = 5, max_chars: int = 1000) -> ContextBuilder:
    return ContextBuilder(ContextConfig(max_blocks=max_blocks, max_chars=max_chars))


def test_exact_duplicate_keeps_higher_rank() -> None:
    blocks, stats = builder().build([hit(1, "same"), hit(2, "other"), hit(3, "same")])
    assert [b.document_id for b in blocks] == ["doc_1", "doc_2"]
    assert stats.received == 3
    assert stats.deduplicated == 1


def test_normalized_duplicate_whitespace_and_nfc() -> None:
    composed = "café fee"
    decomposed = "  café\n\tfee "
    blocks, stats = builder().build([hit(1, composed), hit(2, decomposed)])
    assert [b.document_id for b in blocks] == ["doc_1"]
    assert stats.deduplicated == 1


def test_original_text_is_kept_not_normalized() -> None:
    blocks, _ = builder().build([hit(1, "a  b\n c")])
    assert blocks[0].chunk_text == "a  b\n c"


def test_different_text_is_kept() -> None:
    blocks, stats = builder().build([hit(1, "fee is 10"), hit(2, "fee is 11")])
    assert len(blocks) == 2
    assert stats.deduplicated == 0


def test_max_blocks_cap_drops_lowest_ranked() -> None:
    hits = [hit(i, f"text {i}") for i in range(1, 6)]
    blocks, stats = builder(max_blocks=2).build(hits)
    assert [b.source_id for b in blocks] == ["S1", "S2"]
    assert [b.document_id for b in blocks] == ["doc_1", "doc_2"]
    assert stats.dropped_by_budget == 3
    assert stats.blocks == 2


def test_max_chars_cap_drops_whole_blocks() -> None:
    hits = [hit(1, "a" * 40), hit(2, "b" * 40), hit(3, "c" * 40)]
    blocks, stats = builder(max_chars=100).build(hits)
    assert len(blocks) == 2
    assert all(len(b.chunk_text) == 40 for b in blocks)
    assert stats.chars == 80
    assert stats.dropped_by_budget == 1


def test_block_larger_than_max_chars_is_dropped_never_cut() -> None:
    blocks, stats = builder(max_chars=10).build([hit(1, "x" * 11)])
    assert blocks == []
    assert stats.dropped_by_budget == 1
    assert stats.chars == 0


def test_oversized_block_does_not_let_a_lower_rank_jump_ahead() -> None:
    blocks, stats = builder(max_chars=10).build([hit(1, "x" * 11), hit(2, "ok")])
    assert blocks == []
    assert stats.dropped_by_budget == 2


def test_empty_input() -> None:
    blocks, stats = builder().build([])
    assert blocks == []
    assert (stats.received, stats.deduplicated, stats.dropped_by_budget) == (0, 0, 0)
    assert (stats.blocks, stats.chars) == (0, 0)


def test_ids_follow_final_order_after_dedup() -> None:
    blocks, _ = builder().build([hit(1, "a"), hit(2, "a"), hit(3, "b")])
    assert [(b.source_id, b.document_id) for b in blocks] == [
        ("S1", "doc_1"),
        ("S2", "doc_3"),
    ]


def test_metadata_comes_from_the_hit_payload() -> None:
    h = hit(
        1,
        "body",
        document_id="business_009_x",
        document_version=7,
        section_id="s_9",
        title="A title",
        source_authority="naati",
        source_url=None,
        content_language="ml",
    )
    (block,), _ = builder().build([h])
    assert block.source_id == "S1"
    assert block.document_id == "business_009_x"
    assert block.document_version == 7
    assert block.section_id == "s_9"
    assert block.title == "A title"
    assert block.source_authority == "naati"
    assert block.source_url is None
    assert block.content_language == "ml"
    assert block.chunk_text == "body"


def test_deterministic() -> None:
    hits = [hit(1, "a"), hit(2, "a"), hit(3, "b"), hit(4, "c" * 2000)]
    first = builder().build(hits)
    second = builder().build(hits)
    assert first == second


def test_all_stats_counts() -> None:
    texts = ["aaaa", "aaaa", "bbbb", "cccc", "dddd"]
    hits = [hit(i, t) for i, t in enumerate(texts, start=1)]
    blocks, stats = builder(max_blocks=2).build(hits)
    assert stats.received == 5
    assert stats.deduplicated == 1
    assert stats.dropped_by_budget == 2
    assert stats.blocks == len(blocks) == 2
    assert stats.chars == 8


def test_input_hits_not_mutated() -> None:
    hits = [hit(1, "a"), hit(2, "a")]
    snapshot = [h.model_dump() for h in hits]
    builder().build(hits)
    assert [h.model_dump() for h in hits] == snapshot


@pytest.mark.parametrize("field", ["max_blocks", "max_chars"])
def test_config_requires_positive_values(field: str) -> None:
    values = {"max_blocks": 1, "max_chars": 1, field: 0}
    with pytest.raises(ValidationError):
        ContextConfig(**values)


def test_generation_source_has_no_language_code_or_name() -> None:
    registry = json.loads((REPO_ROOT / "config/language_registry.json").read_text())
    needles: set[str] = set()
    for key, entry in registry["product_support"].items():
        needles.add(key.lower())
        needles.add(str(entry.get("display_name", "")).lower())
    codes = {str(e["internal_code"]) for e in registry["product_support"].values()}
    needles.discard("")
    files = sorted(GENERATION_SRC.glob("*.py"))
    assert files
    for path in files:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for needle in needles:
            assert needle not in lowered, f"{path.name} mentions {needle!r}"
        for code in codes:
            pattern = rf"""["']{re.escape(code)}["']"""
            assert not re.search(pattern, text), f"{path.name} has literal {code!r}"
