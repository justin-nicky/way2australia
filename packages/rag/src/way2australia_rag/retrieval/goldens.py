"""Compatibility wrapper for the legacy `retrieval-baseline` readers (Spec 006 R12).

The reading logic lives in `way2australia_rag.evaluation`. This module keeps the
Spec 005 names, the "exactly one `golden_answerable` dataset" rule, the case
selection, the excluded count and the messages, and re-raises evaluation
configuration errors as `RetrievalConfigurationError`. Only the golden dataset is
read, so a problem in another dataset cannot change legacy behavior. Nothing here
writes.
"""

from pathlib import Path

from pydantic import BaseModel

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    CaseStatus,
    DatasetRef,
    DatasetType,
    GoldenCase,
)
from way2australia_rag.evaluation.suite import (
    declared_release_id as _declared_release_id,
)
from way2australia_rag.evaluation.suite import read_dataset, read_manifest
from way2australia_rag.retrieval.errors import RetrievalConfigurationError

GOLDEN_DATASET_TYPE = DatasetType.GOLDEN_ANSWERABLE.value

__all__ = [
    "GOLDEN_DATASET_TYPE",
    "GoldenCase",
    "SuiteRef",
    "declared_release_id",
    "load_golden_cases",
    "load_suite",
]


class SuiteRef(BaseModel):
    evaluation_suite_id: str
    version: int
    golden_dataset_path: str


def load_suite(repo_root: Path, suite_path: str | Path) -> SuiteRef:
    """Read the suite manifest and locate its `golden_answerable` dataset."""
    try:
        manifest = read_manifest(repo_root, suite_path)
    except EvaluationConfigurationError as error:
        raise RetrievalConfigurationError(str(error)) from error
    datasets = [d for d in manifest.datasets if d.type is DatasetType.GOLDEN_ANSWERABLE]
    if len(datasets) != 1:
        name = Path(str(suite_path)).name
        raise RetrievalConfigurationError(f"'{name}' is not a valid evaluation suite.")
    return SuiteRef(
        evaluation_suite_id=manifest.evaluation_suite_id,
        version=manifest.version,
        golden_dataset_path=datasets[0].path,
    )


def load_golden_cases(repo_root: Path, suite: SuiteRef) -> tuple[list[GoldenCase], int]:
    """Kept cases (active, answerable, non-empty `relevant_document_ids`) and the
    number of cases excluded."""
    ref = DatasetRef(type=DatasetType.GOLDEN_ANSWERABLE, path=suite.golden_dataset_path)
    try:
        cases = read_dataset(repo_root, ref)
    except EvaluationConfigurationError as error:
        raise RetrievalConfigurationError(str(error)) from error
    kept = [
        c
        for c in cases
        if isinstance(c, GoldenCase)
        and c.status == CaseStatus.ACTIVE.value
        and c.answerable
        and c.relevant_document_ids
    ]
    return kept, len(cases) - len(kept)


def declared_release_id(repo_root: Path, release_id: str) -> str:
    """Read `knowledge/releases/<id>.json` and require a matching release ID."""
    try:
        return _declared_release_id(repo_root, release_id)
    except EvaluationConfigurationError as error:
        raise RetrievalConfigurationError(str(error)) from error
