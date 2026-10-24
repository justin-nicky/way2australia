"""Section-level metrics (Spec 006 R6).

Matches `"<document_id>#<section_id>"` keys, never chunk or point IDs. The
metric functions are the unchanged `retrieval/metrics.py` ones, called with
section keys instead of document IDs. A case is measurable only when its
`relevant_section_ids` (the same key form) is non-empty.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from way2australia_rag.retrieval.metrics import (
    hit_rate_at_k,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.models import RetrievedChunk

NO_SECTIONS_NOTE = "no active golden case has relevant_section_ids"


def section_key(document_id: str, section_id: str) -> str:
    return f"{document_id}#{section_id}"


def dedupe_sections(hits: Sequence[RetrievedChunk]) -> list[str]:
    """Section keys in rank order, each at its first (best) rank."""
    seen: set[str] = set()
    ranked: list[str] = []
    for hit in hits:
        key = section_key(hit.document_id, hit.section_id)
        if key not in seen:
            seen.add(key)
            ranked.append(key)
    return ranked


def section_report(rows: Sequence[Mapping[str, Any]], k: int) -> dict[str, Any]:
    """`rows` hold `ranked_section_ids` and `relevant_section_ids`."""
    measurable = [r for r in rows if r["relevant_section_ids"]]
    report: dict[str, Any] = {"measurable_cases": len(measurable)}
    if not measurable:
        report["note"] = NO_SECTIONS_NOTE
        return report
    hits, recalls, rrs = [], [], []
    for row in measurable:
        ranked = list(row["ranked_section_ids"])
        relevant = set(row["relevant_section_ids"])
        hits.append(hit_rate_at_k(ranked, relevant, k))
        recalls.append(recall_at_k(ranked, relevant, k))
        rrs.append(reciprocal_rank(ranked, relevant))
    n = len(measurable)
    report[f"hit_rate_at_{k}"] = round(sum(hits) / n, 4)
    report[f"recall_at_{k}"] = round(sum(recalls) / n, 4)
    report["mrr"] = round(sum(rrs) / n, 4)
    return report
