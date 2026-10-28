"""Result document constants, reading (1.0, 2.0, 2.1) and writing (Spec 006 R7,
Spec 007 R9).

Writing goes through the unchanged `retrieval.baseline.write_result`: exclusive
create, never overwritten, partial file removed on failure.
"""

import json
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
SCHEMA_VERSION = "2.1"
LEGACY_KIND = "retrieval_baseline"
LEGACY_SCHEMA_VERSION = "1.0"
SUPPORTED_FORMATS = {
    (LEGACY_KIND, LEGACY_SCHEMA_VERSION),
    (RESULT_KIND, "2.0"),
    (RESULT_KIND, SCHEMA_VERSION),
}
# Versions whose case rows carry `source_authority` (2.0 and later).
AUTHORITY_VERSIONS = {"2.0", SCHEMA_VERSION}

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
    """Read a `retrieval_baseline` 1.0 or `retrieval_evaluation` 2.0 or 2.1 file.

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
            "(supported: retrieval_baseline 1.0, retrieval_evaluation 2.0 and 2.1)",
        )
    try:
        return _build_run(name, raw, str(kind), str(version), label)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise _unreadable(label, name, "is malformed or incomplete") from error


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
    latency = raw.get("latency_ms") or {}
    lexical = raw.get("lexical_index")  # 2.1 only; 1.0 and 2.0 have none
    strategy = raw.get("retrieval_strategy") or "dense"
    if (
        version == "2.1"
        and strategy in ("bm25", "hybrid")
        and not isinstance(lexical, dict)
    ):
        # A malformed file must never skip the lexical identity refusal.
        raise _unreadable(
            label, name, f"is a {strategy} run without a lexical_index object"
        )
    info = {
        # 1.0 and 2.0 files are dense runs.
        "retrieval_strategy": strategy,
        "lexical": lexical if isinstance(lexical, dict) else None,
        "collection": raw.get("collection"),
        "index_version": raw.get("index_version"),
        "embedder_model_id": settings.get("embedder_model_id"),
        "embedder_revision": settings.get("embedder_revision"),
        "device": raw.get("device"),
        "git_commit": raw.get("git_commit"),
        "latency_p50": latency.get("p50"),
        "latency_p95": latency.get("p95"),
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
