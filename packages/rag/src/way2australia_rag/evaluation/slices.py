"""Slice reports and small-corpus honesty (Spec 006 R5).

Slice keys come from case data and the document repository, never from
hard-coded language codes. The only language data read here is the active set in
`config/language_registry.json` (read only).
"""

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.suite import inside, read_json

SMALL_SAMPLE_THRESHOLD = 10
BASE_LANGUAGE = "en"
LANGUAGE_REGISTRY = "config/language_registry.json"
UNKNOWN_AUTHORITY = "unknown"


def _mean(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4)


def aggregate(rows: Sequence[Mapping[str, Any]], k: int) -> dict[str, Any]:
    """Same keys, rounding and meaning as the 1.0 aggregate, plus `small_sample`."""
    return {
        f"hit_rate_at_{k}": _mean([1.0 if r["hit"] else 0.0 for r in rows]),
        f"recall_at_{k}": _mean([r["recall"] for r in rows]),
        "mrr": _mean([r["reciprocal_rank"] for r in rows]),
        "n": len(rows),
        "small_sample": len(rows) < SMALL_SAMPLE_THRESHOLD,
    }


def source_authority_key(
    relevant_document_ids: Sequence[str], authorities: Mapping[str, str]
) -> str:
    """Sorted, `+`-joined set of the relevant documents' source authorities.

    A multi-authority case lands in one slice, so slices stay disjoint.
    """
    found = {authorities[d] for d in relevant_document_ids if d in authorities}
    return "+".join(sorted(found)) if found else UNKNOWN_AUTHORITY


def slice_by(
    rows: Sequence[Mapping[str, Any]], key: str, k: int
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return {name: aggregate(groups[name], k) for name in sorted(groups)}


def active_registry_languages(repo_root: Path) -> list[str]:
    """`en` plus every `product_support` language whose status is `active`."""
    raw = read_json(inside(repo_root, LANGUAGE_REGISTRY))
    support = raw.get("product_support") if isinstance(raw, dict) else None
    if not isinstance(support, dict):
        raise EvaluationConfigurationError(
            "'language_registry.json' has no product_support section."
        )
    codes = {BASE_LANGUAGE}
    for entry in support.values():
        if (
            isinstance(entry, dict)
            and entry.get("status") == "active"
            and isinstance(entry.get("internal_code"), str)
        ):
            codes.add(entry["internal_code"])
    return sorted(codes)


def absent_query_languages(
    registry_languages: Sequence[str], present: Sequence[str]
) -> list[str]:
    """Active registry languages with no golden case, sorted."""
    return sorted(set(registry_languages) - set(present))
