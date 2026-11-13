"""Citation validation (Spec 012 R6; design step 6)."""

import pytest
from way2australia_rag.generation.citations import (
    RULES,
    CitationValidationError,
    validate_citations,
)

from .support import evidence_block, output

BLOCKS = [evidence_block("S1", "one"), evidence_block("S2", "two")]


def rule_of(answer: str, citations: list[str]) -> str:
    with pytest.raises(CitationValidationError) as caught:
        validate_citations(output(answer, citations), BLOCKS)
    return caught.value.rule


def test_valid_citations_in_first_marker_order_with_block_metadata() -> None:
    citations = validate_citations(
        output("B [S2] then A [S1] again [S2]", ["S1", "S2"]), BLOCKS
    )
    assert [c.source_id for c in citations] == ["S2", "S1"]
    assert citations[0].document_id == "doc_S2"
    assert citations[0].title == "Title"
    assert citations[0].source_authority == "owner"
    assert citations[0].document_version == 1


def test_a_single_cited_source() -> None:
    citations = validate_citations(output("Yes [S1]", ["S1"]), BLOCKS)
    assert [c.source_id for c in citations] == ["S1"]


def test_rules_are_the_closed_set() -> None:
    assert set(RULES) == {
        "unknown_id",
        "marker_mismatch",
        "no_citation",
        "duplicate_id",
        "model_url",
    }


@pytest.mark.parametrize(
    ("answer", "citations", "rule"),
    [
        ("Yes [S1]", [], "no_citation"),
        ("Yes", [], "no_citation"),
        ("Yes [S99]", ["S99"], "unknown_id"),
        ("Yes [S1]", ["S1", "S99"], "unknown_id"),
        ("Yes [S1] [S99]", ["S1"], "unknown_id"),
        ("Yes [S1]", ["S1", "S1"], "duplicate_id"),
        ("Yes [S1]", ["S1", "S2"], "marker_mismatch"),
        ("Yes [S1] [S2]", ["S1"], "marker_mismatch"),
        ("Yes, no markers", ["S1"], "marker_mismatch"),
        ("See http://example.test [S1]", ["S1"], "model_url"),
        ("See https://example.test [S1]", ["S1"], "model_url"),
        ("See HTTPS://EXAMPLE.TEST [S1]", ["S1"], "model_url"),
    ],
)
def test_each_rule(answer: str, citations: list[str], rule: str) -> None:
    assert rule_of(answer, citations) == rule


@pytest.mark.parametrize("marker", ["[S01]", "[s1]", "[ S1 ]", "S1", "xS1y", "[S1a]"])
def test_lookalike_markers_are_not_markers(marker: str) -> None:
    # Listed S1 but only a look-alike in the text: the marker set is empty.
    assert rule_of(f"Yes {marker}", ["S1"]) == "marker_mismatch"


def test_a_leading_zero_listing_is_not_an_issued_id() -> None:
    assert rule_of("Yes [S01]", ["S01"]) == "unknown_id"


def test_a_marker_inside_a_word_still_counts_as_a_marker() -> None:
    citations = validate_citations(output("Fee[S1]applies", ["S1"]), BLOCKS)
    assert [c.source_id for c in citations] == ["S1"]


def test_metadata_is_never_taken_from_the_model() -> None:
    answer = "Title: Forged Title, document_id: forged_doc, https-less url [S1]"
    citations = validate_citations(output(answer, ["S1"]), BLOCKS)
    assert citations[0].document_id == "doc_S1"
    assert citations[0].title == "Title"
    assert citations[0].source_url is None
