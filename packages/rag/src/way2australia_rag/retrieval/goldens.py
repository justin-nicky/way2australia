"""Read-only suite, golden-case and declared-release readers (Spec 005 R8).

A stand-in until Spec 006's governed suite loader replaces it. Nothing here
writes. A golden case's own `access_context` is loaded only to be ignored:
retrieval always uses the server-resolved guest access. Error messages carry
file names only, never absolute paths or case text.
"""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from way2australia_rag.retrieval.errors import RetrievalConfigurationError

GOLDEN_DATASET_TYPE = "golden_answerable"
_RELEASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class GoldenCase(BaseModel):
    """The fields the baseline needs; new case fields never break loading."""

    model_config = ConfigDict(extra="ignore")

    case_id: str
    case_version: int
    query: str
    query_language: str
    category: str
    relevant_document_ids: list[str]
    answerable: bool
    status: str
    access_context: dict[str, Any] | None = None  # never used for access


class SuiteRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    evaluation_suite_id: str
    version: int
    golden_dataset_path: str


def _inside(repo_root: Path, relative: str) -> Path:
    root = repo_root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise RetrievalConfigurationError(
            f"'{Path(relative).name}' resolves outside the repository."
        )
    return path


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RetrievalConfigurationError(
            f"cannot read '{path.name}' as JSON."
        ) from error


def load_suite(repo_root: Path, suite_path: str | Path) -> SuiteRef:
    """Read the suite manifest and locate its `golden_answerable` dataset."""
    path = _inside(repo_root, str(suite_path))
    raw = _read_json(path)
    try:
        datasets = [d for d in raw["datasets"] if d["type"] == GOLDEN_DATASET_TYPE]
        if len(datasets) != 1:
            raise KeyError(GOLDEN_DATASET_TYPE)
        dataset_path = str(datasets[0]["path"])
        suite = SuiteRef(
            evaluation_suite_id=raw["evaluation_suite_id"],
            version=raw["version"],
            golden_dataset_path=dataset_path,
        )
    except (KeyError, TypeError, ValidationError) as error:
        raise RetrievalConfigurationError(
            f"'{path.name}' is not a valid evaluation suite."
        ) from error
    _inside(repo_root, dataset_path)  # refuse escaping paths now
    return suite


def load_golden_cases(repo_root: Path, suite: SuiteRef) -> tuple[list[GoldenCase], int]:
    """Kept cases (active, answerable, non-empty `relevant_document_ids`) and the
    number of cases excluded."""
    path = _inside(repo_root, suite.golden_dataset_path)
    kept: list[GoldenCase] = []
    total = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise RetrievalConfigurationError(f"cannot read '{path.name}'.") from error
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        total += 1
        try:
            case = GoldenCase.model_validate_json(line)
        except ValidationError as error:
            raise RetrievalConfigurationError(
                f"'{path.name}' line {number} is not a valid golden case."
            ) from error
        if case.status == "active" and case.answerable and case.relevant_document_ids:
            kept.append(case)
    return kept, total - len(kept)


def declared_release_id(repo_root: Path, release_id: str) -> str:
    """Read `knowledge/releases/<id>.json` and require a matching release ID."""
    if not _RELEASE_ID.match(release_id):
        raise RetrievalConfigurationError("the release ID is not valid.")
    path = _inside(repo_root, f"knowledge/releases/{release_id}.json")
    raw = _read_json(path)
    found = raw.get("knowledge_release_id") if isinstance(raw, dict) else None
    if found != release_id:
        raise RetrievalConfigurationError(
            f"'{path.name}' does not declare knowledge_release_id '{release_id}'."
        )
    return release_id
