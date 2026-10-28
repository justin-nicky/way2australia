"""Status exclusion counts; `suggested` is never returned (Spec 006 R3)."""

import json
import shutil
from pathlib import Path

from conftest import REPO_ROOT, live_suite_rows
from way2australia_rag.evaluation.models import DatasetType
from way2australia_rag.evaluation.suite import load_suite

SUITE = "evaluation/suites/public-eval-v2.json"


def golden_count() -> int:
    return len(live_suite_rows("golden_answerable"))


def suite_with_statuses(tmp_path: Path, statuses: list[str]):  # noqa: ANN201
    shutil.copytree(REPO_ROOT / "evaluation", tmp_path / "evaluation")
    path = tmp_path / "evaluation/datasets/v2/golden_public.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    for row, status in zip(rows, statuses, strict=False):
        row["status"] = status
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return load_suite(tmp_path, SUITE)


def test_exclusions_counted_by_status(tmp_path: Path) -> None:
    suite = suite_with_statuses(
        tmp_path,
        ["suggested", "suggested", "deprecated", "review_required", "replaced"],
    )
    kind = DatasetType.GOLDEN_ANSWERABLE
    assert suite.excluded_by_status(kind) == {
        "deprecated": 1,
        "replaced": 1,
        "review_required": 1,
        "suggested": 2,
    }
    assert len(suite.active(kind)) == golden_count() - 5
    assert suite.excluded_by_status(DatasetType.SECURITY) == {}


def test_suggested_never_returned(tmp_path: Path) -> None:
    suite = suite_with_statuses(tmp_path, ["suggested"] * golden_count())
    kind = DatasetType.GOLDEN_ANSWERABLE
    assert suite.active(kind) == []
    assert all(c.status != "suggested" for c in suite.active(kind))
    assert suite.excluded_by_status(kind) == {"suggested": golden_count()}
