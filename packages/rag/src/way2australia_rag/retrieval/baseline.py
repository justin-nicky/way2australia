"""Retrieval baseline runner (Spec 005 R8).

`run_baseline` is read-only on Qdrant, `evaluation/` and `knowledge/`. Every case
is retrieved with the one server-resolved `ResolvedAccess`; a case's own
`access_context` is never consulted. The result document holds no query text,
chunk text, absolute paths or secrets. `write_result` is the only writer and it
never overwrites.
"""

import json
import subprocess
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.retrieval.access import ResolvedAccess, build_access_filter
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.goldens import GoldenCase, SuiteRef
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.metrics import (
    dedupe_documents,
    hit_rate_at_k,
    percentile,
    random_hit_rate,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.retriever import DenseRetriever

SCHEMA_VERSION = "1.0"
FAKE_NOTE = "not a quality measurement"


@dataclass(frozen=True)
class BaselineResult:
    document: dict[str, Any]


def git_state(repo_root: Path) -> tuple[str | None, bool | None]:
    """(commit, dirty) from git in `repo_root`; (None, None) if unavailable."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None, None
    return head or None, bool(status.strip())


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4)


def _aggregate(rows: list[dict[str, Any]], k: int) -> dict[str, Any]:
    return {
        f"hit_rate_at_{k}": _mean([1.0 if r["hit"] else 0.0 for r in rows]),
        f"recall_at_{k}": _mean([r["recall"] for r in rows]),
        "mrr": _mean([r["reciprocal_rank"] for r in rows]),
        "n": len(rows),
    }


def _slices(rows: list[dict[str, Any]], key: str, k: int) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return {name: _aggregate(groups[name], k) for name in sorted(groups)}


def run_baseline(
    *,
    retriever: DenseRetriever,
    index: DenseIndex,
    embedder: Embedder,
    access: ResolvedAccess,
    cases: list[GoldenCase],
    excluded_case_count: int,
    suite: SuiteRef,
    release_id: str,
    top_k: int,
    allow_fake: bool,
    repo_root: Path,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> BaselineResult:
    if index.settings.embedder_is_fake and not allow_fake:
        raise RetrievalConfigurationError(
            "the index was built with the fake embedder; pass --allow-fake to run "
            "anyway (the result is not a quality measurement)."
        )
    if not cases:
        raise RetrievalConfigurationError("no golden cases to run.")
    document_count = index.document_count(build_access_filter(access))
    if document_count < 1:
        raise RetrievalConfigurationError(
            "no documents are visible under the access filter."
        )

    started = perf_counter()
    retriever.retrieve(cases[0].query, access, top_k)  # unmeasured warm-up
    warmup_ms = (perf_counter() - started) * 1000.0
    # A real BgeM3Embedder reports no device until the model has loaded.
    device = embedder.device

    rows: list[dict[str, Any]] = []
    for case in cases:
        result = retriever.retrieve(case.query, access, top_k)
        ranked = dedupe_documents(result.hits)
        relevant = set(case.relevant_document_ids)
        rows.append(
            {
                "case_id": case.case_id,
                "case_version": case.case_version,
                "query_language": case.query_language,
                "category": case.category,
                "ranked_document_ids": ranked,
                "relevant_document_ids": sorted(relevant),
                "hit": hit_rate_at_k(ranked, relevant, top_k) == 1.0,
                "recall": recall_at_k(ranked, relevant, top_k),
                "reciprocal_rank": reciprocal_rank(ranked, relevant),
                "latency_ms": round(result.latency_ms, 3),
            }
        )

    latencies = [r["latency_ms"] for r in rows]
    settings = index.settings
    commit, dirty = git_state(repo_root)
    notes = [
        f"Top-{top_k} over {document_count} indexed documents is optimistic; compare "
        f"HitRate@{top_k} with the random expectation "
        f"min(1, {top_k}/{document_count}).",
        "The index was not verified against the declared release's document snapshot.",
        "Model load and the warm-up query are excluded from p50/p95.",
    ]
    if settings.embedder_is_fake:
        notes.append(FAKE_NOTE)
    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "retrieval_baseline",
        "created_at": clock().astimezone(UTC).isoformat(),
        "git_commit": commit,
        "git_dirty": dirty,
        "evaluation_suite_id": suite.evaluation_suite_id,
        "evaluation_suite_version": suite.version,
        "declared_knowledge_release_id": release_id,
        "release_snapshot_verified": False,
        "collection": index.collection,
        "index_version": index.index_version,
        "index_settings": settings.model_dump(mode="json"),
        "retrieval_strategy": "dense",
        "top_k": top_k,
        "device": device,
        "embedder_is_fake": settings.embedder_is_fake,
        "case_count": len(rows),
        "excluded_case_count": excluded_case_count,
        "document_count": document_count,
        "random_hit_rate_at_k": round(random_hit_rate(top_k, document_count), 4),
        "random_hit_rate_formula": f"min(1, {top_k}/{document_count})",
        "metrics": {
            "overall": _aggregate(rows, top_k),
            "by_query_language": _slices(rows, "query_language", top_k),
            "by_category": _slices(rows, "category", top_k),
        },
        "latency_ms": {
            "p50": round(percentile(latencies, 50), 3),
            "p95": round(percentile(latencies, 95), 3),
            "warmup_ms": round(warmup_ms, 3),
            "measured_cases": len(rows),
        },
        "cases": rows,
        "notes": notes,
    }
    return BaselineResult(document=document)


def default_output_path(repo_root: Path, index_version: str, now: datetime) -> Path:
    stamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return (
        repo_root
        / "experiments"
        / "results"
        / f"retrieval-baseline-{index_version}-{stamp}.json"
    )


def check_output_free(path: Path) -> None:
    if path.exists():
        raise RetrievalConfigurationError(
            f"output file '{path.name}' already exists; it is never overwritten."
        )


def write_result(path: Path, result: BaselineResult) -> None:
    """Create `path` exclusively. Serialises first so a failure writes nothing."""
    check_output_free(path)
    text = json.dumps(result.document, indent=2, ensure_ascii=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except FileExistsError as error:
        raise RetrievalConfigurationError(
            f"output file '{path.name}' already exists; it is never overwritten."
        ) from error
    except OSError as error:
        # The file may exist now (disk full mid-write): remove our partial file.
        path.unlink(missing_ok=True)
        raise RetrievalConfigurationError(
            f"could not write output file '{path.name}'; nothing was kept."
        ) from error
