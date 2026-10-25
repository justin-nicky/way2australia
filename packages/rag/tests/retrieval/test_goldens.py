"""Suite, golden and release reader tests (Spec 005 R8, R11)."""

import hashlib
import json
from pathlib import Path

import pytest
from conftest import REPO_ROOT, live_suite_rows
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.goldens import (
    declared_release_id,
    load_golden_cases,
    load_suite,
)

SUITE = "evaluation/suites/public-eval-v1.json"


def tree_hashes() -> dict[str, str]:
    return {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((REPO_ROOT / "evaluation").rglob("*"))
        if p.is_file()
    }


def test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged() -> None:
    before = tree_hashes()
    suite = load_suite(REPO_ROOT, SUITE)
    cases, excluded = load_golden_cases(REPO_ROOT, suite)
    assert suite.evaluation_suite_id == "public-eval-v1" and suite.version == 1
    assert len(cases) == len(
        live_suite_rows("golden_answerable", active_only=True, suite=SUITE)
    )
    assert excluded == len(live_suite_rows("golden_answerable", suite=SUITE)) - len(
        cases
    )
    assert tree_hashes() == before


def write_suite(
    root: Path, rows: list[dict[str, object]], path: str = "d.jsonl"
) -> str:
    base = {
        "case_version": 1,
        "query": "q",
        "query_language": "en",
        "category": "business",
        "answerable": True,
        "status": "active",
        "relevant_document_ids": ["doc"],
        "extra_new_field": 1,
    }
    (root / "d.jsonl").write_text(
        "\n".join(json.dumps({**base, **row}) for row in rows) + "\n"
    )
    (root / "suite.json").write_text(
        json.dumps(
            {
                "evaluation_suite_id": "s",
                "version": 2,
                "datasets": [
                    {"type": "security", "path": "other.jsonl"},
                    {"type": "golden_answerable", "path": path},
                ],
            }
        )
    )
    return "suite.json"


def test_filtering_in_temporary_suite(tmp_path: Path) -> None:
    suite_file = write_suite(
        tmp_path,
        [
            {"case_id": "ok"},
            {"case_id": "inactive", "status": "retired"},
            {"case_id": "unanswerable", "answerable": False},
            {"case_id": "empty", "relevant_document_ids": []},
        ],
    )
    cases, excluded = load_golden_cases(tmp_path, load_suite(tmp_path, suite_file))
    assert [c.case_id for c in cases] == ["ok"]
    assert excluded == 3


def test_path_escaping_repo_root_refused(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "outside.jsonl").write_text("")
    suite_file = write_suite(root, [{"case_id": "a"}], path="../outside.jsonl")
    with pytest.raises(RetrievalConfigurationError, match="outside"):
        load_suite(root, suite_file)
    with pytest.raises(RetrievalConfigurationError, match="outside"):
        load_suite(root, "../suite.json")


def test_invalid_line_names_file_and_line_only(tmp_path: Path) -> None:
    suite_file = write_suite(tmp_path, [{"case_id": "a"}])
    (tmp_path / "d.jsonl").write_text('{"case_id": "SECRET-QUERY"}\n')
    with pytest.raises(RetrievalConfigurationError, match="line 1") as info:
        load_golden_cases(tmp_path, load_suite(tmp_path, suite_file))
    assert "SECRET-QUERY" not in str(info.value)
    assert str(tmp_path) not in str(info.value)


def test_declared_release() -> None:
    assert declared_release_id(REPO_ROOT, "seed-v1") == "seed-v1"
    for bad in ("nope-v9", "../seed-v1", ""):
        with pytest.raises(RetrievalConfigurationError):
            declared_release_id(REPO_ROOT, bad)


def test_release_id_mismatch_refused(tmp_path: Path) -> None:
    (tmp_path / "knowledge/releases").mkdir(parents=True)
    (tmp_path / "knowledge/releases/seed-v1.json").write_text(
        json.dumps({"knowledge_release_id": "other"})
    )
    with pytest.raises(RetrievalConfigurationError, match="does not declare"):
        declared_release_id(tmp_path, "seed-v1")
