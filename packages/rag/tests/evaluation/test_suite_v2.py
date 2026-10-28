"""Evaluation Suite `public-eval-v2` tests (Spec 007 T1, R1).

Consistency checks only: counts come from the data under test. The v1 reference
is read from the spec base commit with `git show`; the tests skip when that
commit is not available (for example a shallow clone).
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation import cli
from way2australia_rag.evaluation.validate import validate_evaluation

BASE_COMMIT = "06b1af9"
V1_SUITE = "evaluation/suites/public-eval-v1.json"
V2_SUITE = "evaluation/suites/public-eval-v2.json"
CANDIDATES = "evaluation/candidates/006-candidates.jsonl"
TYPES = {
    "golden_answerable": "golden_public.jsonl",
    "unanswerable_refusal": "unanswerable_public.jsonl",
    "security": "security_public.jsonl",
}
PROMOTED = {f"cand006_ml_00{i}": f"g{63 + i:03d}" for i in range(1, 7)}


def committed(path: str) -> str:
    """File content at the spec base commit (v1 reference)."""
    result = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:{path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"base commit {BASE_COMMIT} not available")
    return result.stdout


def lines(text: str) -> list[str]:
    return [x for x in text.splitlines() if x.strip()]


def read_lines(path: str) -> list[str]:
    return lines((REPO_ROOT / path).read_text(encoding="utf-8"))


def manifest(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def v2_path(kind: str) -> str:
    return f"evaluation/datasets/v2/{TYPES[kind]}"


def v1_path(kind: str) -> str:
    return f"evaluation/datasets/{TYPES[kind]}"


def test_v2_case_count_equals_dataset_rows() -> None:
    v2 = manifest(V2_SUITE)
    rows = sum(len(read_lines(d["path"])) for d in v2["datasets"])
    assert v2["case_count"] == rows
    assert v2["status"] == "active"
    assert v2["version"] == 2
    assert v2["replaces"]["evaluation_suite_id"] == "public-eval-v1"


def test_v2_dataset_counts_follow_v1_plus_promoted() -> None:
    v1_goldens = lines(committed(v1_path("golden_answerable")))
    assert len(read_lines(v2_path("golden_answerable"))) == len(v1_goldens) + len(
        PROMOTED
    )
    for kind in ("unanswerable_refusal", "security"):
        assert len(read_lines(v2_path(kind))) == len(lines(committed(v1_path(kind))))


@pytest.mark.parametrize("kind", list(TYPES))
def test_copied_rows_equal_v1_except_suite_id(kind: str) -> None:
    v1_rows = [json.loads(x) for x in lines(committed(v1_path(kind)))]
    v2_rows = [json.loads(x) for x in read_lines(v2_path(kind))]
    for before, after in zip(v1_rows, v2_rows[: len(v1_rows)], strict=True):
        assert after["evaluation_suite_id"] == "public-eval-v2"
        assert list(after) == list(before)
        expected = dict(before, evaluation_suite_id="public-eval-v2")
        assert after == expected


def test_promoted_goldens_map_from_candidates() -> None:
    candidates = {
        r["candidate_id"]: r
        for r in (json.loads(x) for x in read_lines(CANDIDATES))
        if "candidate_id" in r
    }
    v1_count = len(lines(committed(v1_path("golden_answerable"))))
    goldens = [json.loads(x) for x in read_lines(v2_path("golden_answerable"))]
    new_rows = goldens[v1_count:]
    assert [r["case_id"] for r in new_rows] == list(PROMOTED.values())
    key_order = list(goldens[0])
    for (candidate_id, case_id), row in zip(PROMOTED.items(), new_rows, strict=True):
        proposed = candidates[candidate_id]["proposed_case"]
        assert list(row) == key_order
        assert row["id"] == row["case_id"] == case_id
        assert row["case_version"] == 1
        assert row["status"] == "active"
        assert row["introduced_in_release"] == "seed-v1"
        assert row["evaluation_suite_id"] == "public-eval-v2"
        assert row["answerable"] is True
        for name in (
            "query",
            "relevant_document_ids",
            "expected_facts",
            "query_language",
            "category",
            "access_context",
        ):
            assert row[name] == proposed[name], (case_id, name)
        assert row["query_language"] == "ml"
        review = candidates[candidate_id]["review"]
        assert review["promoted_as"] == {
            "suite_id": "public-eval-v2",
            "case_id": case_id,
        }
        assert candidates[candidate_id]["status"] == "suggested"


@pytest.mark.parametrize("kind", list(TYPES))
def test_v1_dataset_files_are_unchanged(kind: str) -> None:
    assert (REPO_ROOT / v1_path(kind)).read_text(encoding="utf-8") == committed(
        v1_path(kind)
    )


def test_v1_manifest_differs_only_in_status() -> None:
    before = json.loads(committed(V1_SUITE))
    after = manifest(V1_SUITE)
    assert after["status"] == "replaced"
    assert dict(after, status=before["status"]) == before


def test_candidates_differ_only_in_promoted_as() -> None:
    before = [json.loads(x) for x in lines(committed(CANDIDATES))]
    after = [json.loads(x) for x in read_lines(CANDIDATES)]
    assert len(before) == len(after)
    promoted_ids = set(PROMOTED)
    for old, new in zip(before, after, strict=True):
        if old["candidate_id"] in promoted_ids:
            review = dict(new["review"])
            assert review.pop("promoted_as")
            assert dict(new, review=review) == old
            assert new["status"] == "suggested"
        else:
            assert new == old


# --- transcription check on temp copies --------------------------------------


@pytest.fixture
def root(tmp_path: Path) -> Path:
    for name in ("evaluation", "knowledge"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def problems(root: Path) -> list[str]:
    return [str(p) for p in validate_evaluation(root)]


def edit_jsonl(path: Path, change) -> None:  # noqa: ANN001
    rows = [json.loads(x) for x in lines(path.read_text(encoding="utf-8"))]
    change(rows)
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )


def test_clean_copy_has_no_problems(root: Path) -> None:
    assert problems(root) == []


def test_changed_query_is_a_problem_without_text(root: Path) -> None:
    def change(rows: list[dict]) -> None:
        next(r for r in rows if r["case_id"] == "g064")["query"] = "changed"

    edit_jsonl(root / v2_path("golden_answerable"), change)
    found = problems(root)
    assert any("review.promoted_as.query" in p for p in found)
    assert not any("changed" in p for p in found)


def test_changed_relevant_documents_is_a_problem(root: Path) -> None:
    def change(rows: list[dict]) -> None:
        next(r for r in rows if r["case_id"] == "g065")["relevant_document_ids"] = [
            "business_001_overview_scope"
        ]

    edit_jsonl(root / v2_path("golden_answerable"), change)
    assert any("review.promoted_as.relevant_document_ids" in p for p in problems(root))


def test_missing_promoted_case_is_a_problem(root: Path) -> None:
    def change(rows: list[dict]) -> None:
        rows[:] = [r for r in rows if r["case_id"] != "g066"]

    edit_jsonl(root / v2_path("golden_answerable"), change)
    found = problems(root)
    assert any("does not name a case in that suite" in p for p in found)


def test_unknown_suite_is_a_problem(root: Path) -> None:
    def change(rows: list[dict]) -> None:
        rows[0]["review"]["promoted_as"]["suite_id"] = "public-eval-v9"

    edit_jsonl(root / CANDIDATES, change)
    assert any("does not name a known suite" in p for p in problems(root))


# --- defaults and refusals -----------------------------------------------------


def test_cli_default_suite_is_v2() -> None:
    assert cli.DEFAULT_SUITE == V2_SUITE


def test_retrieval_refuses_the_replaced_v1_suite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:  # noqa: ANN001
    monkeypatch.setenv("W2A_TENANT_ID", "way2australia")
    code = cli.main(
        [
            "retrieval",
            "--repo-root",
            str(REPO_ROOT),
            "--suite",
            V1_SUITE,
            "--output",
            str(tmp_path / "out.json"),
        ]
    )
    assert code == 2
    assert "replaced" in capsys.readouterr().err
    assert not (tmp_path / "out.json").exists()


def test_security_refuses_the_replaced_v1_suite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:  # noqa: ANN001
    monkeypatch.setenv("W2A_TENANT_ID", "way2australia")
    code = cli.main(
        [
            "security",
            "--repo-root",
            str(REPO_ROOT),
            "--suite",
            V1_SUITE,
            "--output",
            str(tmp_path / "out.json"),
        ]
    )
    assert code == 2
    assert "replaced" in capsys.readouterr().err
    assert not (tmp_path / "out.json").exists()
