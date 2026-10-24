"""Read-only evaluation suite loader (Spec 006 R1, R3).

Nothing here writes. A case's own `access_context` is loaded only to be ignored.
Unknown dataset types and paths resolving outside the repository are refused.
Error messages carry file names and line numbers only, never absolute paths or
case text.
"""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    CASE_MODELS,
    CaseBase,
    DatasetRef,
    DatasetType,
    GoldenCase,
    LoadedSuite,
    SecurityCase,
    SuiteManifest,
    UnanswerableCase,
)

_RELEASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_CASE_LABELS = {
    DatasetType.GOLDEN_ANSWERABLE: "golden case",
    DatasetType.UNANSWERABLE_REFUSAL: "unanswerable case",
    DatasetType.SECURITY: "security case",
}


def inside(repo_root: Path, relative: str) -> Path:
    """Resolve `relative` under `repo_root`; refuse anything that escapes it."""
    root = repo_root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise EvaluationConfigurationError(
            f"'{Path(relative).name}' resolves outside the repository."
        )
    return path


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise EvaluationConfigurationError(
            f"cannot read '{path.name}' as JSON."
        ) from error


def read_manifest(repo_root: Path, suite_path: str | Path) -> SuiteManifest:
    """Read and type the suite manifest. Does not read the datasets."""
    path = inside(repo_root, str(suite_path))
    raw = read_json(path)
    try:
        for dataset in raw["datasets"]:
            if dataset["type"] not in {t.value for t in DatasetType}:
                raise EvaluationConfigurationError(
                    f"'{path.name}' lists an unknown dataset type."
                )
        manifest = SuiteManifest.model_validate(raw)
    except (KeyError, TypeError, ValidationError) as error:
        raise EvaluationConfigurationError(
            f"'{path.name}' is not a valid evaluation suite."
        ) from error
    for dataset in manifest.datasets:
        inside(repo_root, dataset.path)  # refuse escaping paths now
    return manifest


def read_dataset(repo_root: Path, ref: DatasetRef) -> list[CaseBase]:
    """All case lines of one dataset, typed by `ref.type`. Blank lines are skipped."""
    path = inside(repo_root, ref.path)
    model = CASE_MODELS[ref.type]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise EvaluationConfigurationError(f"cannot read '{path.name}'.") from error
    cases: list[CaseBase] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            cases.append(model.model_validate_json(line))
        except ValidationError as error:
            raise EvaluationConfigurationError(
                f"'{path.name}' line {number} is not a valid {_CASE_LABELS[ref.type]}."
            ) from error
    return cases


def load_suite(repo_root: Path, suite_path: str | Path) -> LoadedSuite:
    """Read the manifest and every dataset it lists."""
    manifest = read_manifest(repo_root, suite_path)
    suite = LoadedSuite(manifest=manifest)
    for ref in manifest.datasets:
        cases = read_dataset(repo_root, ref)
        for case in cases:
            if isinstance(case, GoldenCase):
                suite.goldens.append(case)
            elif isinstance(case, UnanswerableCase):
                suite.unanswerable.append(case)
            elif isinstance(case, SecurityCase):
                suite.security.append(case)
    return suite


def declared_release_id(repo_root: Path, release_id: str) -> str:
    """Read `knowledge/releases/<id>.json` and require a matching release ID."""
    if not _RELEASE_ID.match(release_id):
        raise EvaluationConfigurationError("the release ID is not valid.")
    path = inside(repo_root, f"knowledge/releases/{release_id}.json")
    raw = read_json(path)
    found = raw.get("knowledge_release_id") if isinstance(raw, dict) else None
    if found != release_id:
        raise EvaluationConfigurationError(
            f"'{path.name}' does not declare knowledge_release_id '{release_id}'."
        )
    return release_id
