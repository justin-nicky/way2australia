"""Result document 2.0 constants and writing (Spec 006 R7).

Writing goes through the unchanged `retrieval.baseline.write_result`: exclusive
create, never overwritten, partial file removed on failure.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from way2australia_rag.retrieval.baseline import (
    BaselineResult,
    check_output_free,
    write_result,
)

RESULT_KIND = "retrieval_evaluation"
SCHEMA_VERSION = "2.0"

__all__ = [
    "RESULT_KIND",
    "SCHEMA_VERSION",
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
