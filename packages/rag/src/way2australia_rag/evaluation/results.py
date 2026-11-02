"""Result document constants, reading (1.0 through 2.3) and writing (Spec 006 R7,
Spec 007 R9, Spec 008 R9, Spec 009 R7).

Writing goes through the unchanged `retrieval.baseline.write_result`: exclusive
create, never overwritten, partial file removed on failure.
"""

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from way2australia_rag.evaluation.errors import NotComparableError
from way2australia_rag.retrieval.baseline import (
    BaselineResult,
    check_output_free,
    write_result,
)
from way2australia_rag.retrieval.text import safe_text

RESULT_KIND = "retrieval_evaluation"
SCHEMA_VERSION = "2.3"
_LEGACY_SCHEMA_VERSION = "2.2"
LEGACY_KIND = "retrieval_baseline"
LEGACY_SCHEMA_VERSION = "1.0"
SUPPORTED_FORMATS = {
    (LEGACY_KIND, LEGACY_SCHEMA_VERSION),
    (RESULT_KIND, "2.0"),
    (RESULT_KIND, "2.1"),
    (RESULT_KIND, SCHEMA_VERSION),
    (RESULT_KIND, _LEGACY_SCHEMA_VERSION),
}
# Versions whose case rows carry `source_authority` (2.0 and later).
AUTHORITY_VERSIONS = {"2.0", "2.1", _LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}

__all__ = [
    "CaseRow",
    "ComparableRun",
    "read_result",
    "RESULT_KIND",
    "SCHEMA_VERSION",
    "AUTHORITY_VERSIONS",
    "check_output_free",
    "default_output_path",
    "write_document",
]


def default_output_path(repo_root: Path, index_version: str, now: datetime) -> Path:
    stamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return (
        repo_root
        / "experiments"
        / "results"
        / f"retrieval-evaluation-{index_version}-{stamp}.json"
    )


def write_document(path: Path, document: dict[str, Any]) -> None:
    write_result(path, BaselineResult(document=document))


@dataclass(frozen=True)
class CaseRow:
    hit: bool
    recall: float
    reciprocal_rank: float
    query_language: str
    category: str
    source_authority: str | None  # 2.0 and later


@dataclass(frozen=True)
class ComparableRun:
    """What `eval-compare` needs from a result file. `name` is the file name only."""

    name: str
    kind: str
    schema_version: str
    suite_id: str
    suite_version: int
    top_k: int
    document_count: int
    embedder_is_fake: bool
    cases: dict[tuple[str, int], CaseRow]
    info: dict[str, Any] = field(default_factory=dict)


def _unreadable(label: str, name: str, why: str) -> NotComparableError:
    return NotComparableError(
        f"not comparable: {label} file '{name}' {why}; produce it with "
        "`make eval-retrieval` (or `make retrieval-baseline` for a 1.0 file)."
    )


def _num(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def read_result(path: Path, label: str = "result") -> ComparableRun:
    """Read a `retrieval_baseline` 1.0 or `retrieval_evaluation` 2.0, 2.1 or 2.2 file.

    Anything else raises `NotComparableError` (exit 2 in the CLI). Only the file
    name appears in messages.
    """
    name = Path(path).name
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise _unreadable(label, name, "cannot be read as JSON") from error
    if not isinstance(raw, dict):
        raise _unreadable(label, name, "is not a JSON object")
    kind, version = raw.get("kind"), raw.get("schema_version")
    if (kind, version) not in SUPPORTED_FORMATS:
        raise _unreadable(
            label,
            name,
            f"has kind {kind!r} and schema_version {version!r} "
            "(supported: retrieval_baseline 1.0, "
            "retrieval_evaluation 2.0, 2.1, 2.2 and 2.3)",
        )
    try:
        return _build_run(name, raw, str(kind), str(version), label)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise _unreadable(label, name, "is malformed or incomplete") from error


def _served_strategy(raw: dict[str, Any], name: str, label: str) -> tuple[str, str]:
    """The single served strategy of a 2.2 file and its requested strategy.

    A file that mixes served strategies (or whose case rows disagree with its
    `served_strategies`) is refused: no single strategy describes it."""
    served = raw["served_strategies"]
    requested = raw["requested_strategy"]
    if not (
        isinstance(served, list)
        and served
        and all(isinstance(x, str) for x in served)
        and isinstance(requested, str)
    ):
        raise ValueError("malformed")
    counts = Counter(str(item["served_strategy"]) for item in raw["cases"])
    if len(served) > 1 or set(counts) - set(served):
        detail = (
            "golden cases "
            + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
            + "; served_strategies: "
            + ", ".join(sorted(set(served) | set(counts)))
        )
        raise _mixed(label, name, detail)
    return served[0], requested


def _mixed(label: str, name: str, detail: str) -> NotComparableError:
    return NotComparableError(
        f"not comparable: {label} file '{name}' mixes served strategies "
        f"({detail}); re-run when the system is stable."
    )


def _build_run(
    name: str, raw: dict[str, Any], kind: str, version: str, label: str
) -> ComparableRun:
    def need(ok: bool) -> None:
        if not ok:
            raise ValueError("malformed")

    suite_id, suite_version = (
        raw["evaluation_suite_id"],
        raw["evaluation_suite_version"],
    )
    top_k, documents = raw["top_k"], raw["document_count"]
    fake = raw["embedder_is_fake"]
    need(isinstance(suite_id, str) and isinstance(suite_version, int))
    need(isinstance(top_k, int) and isinstance(documents, int))
    need(isinstance(fake, bool) and isinstance(raw["cases"], list))
    cases: dict[tuple[str, int], CaseRow] = {}
    seen: set[str] = set()
    for item in raw["cases"]:
        key = (item["case_id"], item["case_version"])
        need(isinstance(key[0], str) and isinstance(key[1], int))
        if key[0] in seen:
            raise _unreadable(
                label, name, f"repeats case_id '{safe_text(key[0])}' in its cases"
            )
        seen.add(key[0])
        need(isinstance(item["hit"], bool))
        need(_num(item["recall"]) and _num(item["reciprocal_rank"]))
        authority = (
            item.get("source_authority") if version in AUTHORITY_VERSIONS else None
        )
        cases[key] = CaseRow(
            hit=item["hit"],
            recall=float(item["recall"]),
            reciprocal_rank=float(item["reciprocal_rank"]),
            query_language=str(item["query_language"]),
            category=str(item["category"]),
            source_authority=None if authority is None else str(authority),
        )
    settings = raw.get("index_settings") or {}
    identity = raw.get("dense_identity") if version in ("2.2", SCHEMA_VERSION) else None
    if not isinstance(identity, dict):
        identity = {}
    latency = raw.get("latency_ms") or {}
    lexical = raw.get("lexical_index")  # 2.1 and later; 1.0 and 2.0 have none
    strategy = raw.get("retrieval_strategy") or "dense"
    requested = strategy
    latency_path = None
    if version in ("2.2", SCHEMA_VERSION):
        strategy, requested = _served_strategy(raw, name, label)
        paths = latency.get("by_served_path") or {}
        latency_path = next(iter(paths)) if len(paths) == 1 else None
    if (
        version in ("2.1", "2.2", SCHEMA_VERSION)
        and strategy in ("bm25", "hybrid")
        and not isinstance(lexical, dict)
    ):
        # A malformed file must never skip the lexical identity refusal.
        raise _unreadable(
            label, name, f"is a {strategy} run without a lexical_index object"
        )
    info = {
        # 1.0 and 2.0 files are dense runs; 2.2 records the served strategy.
        "retrieval_strategy": strategy,
        "requested_strategy": requested,
        "lexical": lexical if isinstance(lexical, dict) else None,
        "collection": raw.get("collection"),
        "index_version": raw.get("index_version"),
        # the settings recorded in Qdrant, else the configured identity (2.2)
        "embedder_model_id": settings.get(
            "embedder_model_id", identity.get("embedder_model_id")
        ),
        "embedder_revision": settings.get(
            "embedder_revision", identity.get("embedder_revision")
        ),
        "device": raw.get("device"),
        "git_commit": raw.get("git_commit"),
        "latency_p50": latency.get("p50"),
        "latency_p95": latency.get("p95"),
        "latency_path": latency_path,
        "metric_unit": raw.get("metric_unit"),
        "chunker": raw.get("chunker"),
        "ingestion_config": raw.get("ingestion_config"),
        "chunk_stats": raw.get("chunk_stats"),
    }
    return ComparableRun(
        name=name,
        kind=kind,
        schema_version=version,
        suite_id=suite_id,
        suite_version=suite_version,
        top_k=top_k,
        document_count=documents,
        embedder_is_fake=fake,
        cases=cases,
        info=info,
    )
