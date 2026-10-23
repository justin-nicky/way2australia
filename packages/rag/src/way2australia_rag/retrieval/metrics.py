"""Document-level retrieval metrics (Spec 005 R7).

Pure functions over ranked document IDs. No chunk, point or section IDs: goldens
stay bound to `document_id` (C13).
"""

import math
from collections.abc import Sequence

from way2australia_rag.retrieval.models import RetrievedChunk


def dedupe_documents(hits: Sequence[RetrievedChunk]) -> list[str]:
    """Document IDs in rank order, each at its first (best) rank."""
    seen: set[str] = set()
    ranked: list[str] = []
    for hit in hits:
        if hit.document_id not in seen:
            seen.add(hit.document_id)
            ranked.append(hit.document_id)
    return ranked


def hit_rate_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(doc in relevant for doc in ranked[:k]) else 0.0


def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    if not relevant:
        raise ValueError("relevant must not be empty")
    return len(relevant & set(ranked[:k])) / len(relevant)


def reciprocal_rank(ranked: Sequence[str], relevant: set[str]) -> float:
    for position, doc in enumerate(ranked, start=1):
        if doc in relevant:
            return 1.0 / position
    return 0.0


def random_hit_rate(k: int, n_documents: int) -> float:
    """Random-retrieval expectation min(1, k/N); N is the distinct document count."""
    if n_documents < 1:
        raise ValueError("n_documents must be at least 1")
    return min(1.0, k / n_documents)


def percentile(values: Sequence[float], q: float) -> float:
    """Nearest-rank percentile, q in (0, 100]."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0 < q <= 100:
        raise ValueError("q must be in (0, 100]")
    ordered = sorted(values)
    return ordered[math.ceil(q / 100 * len(ordered)) - 1]
