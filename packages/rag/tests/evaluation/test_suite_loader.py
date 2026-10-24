"""Governed suite loader tests (Spec 006 R1, R3)."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from conftest import REPO_ROOT, live_suite_rows
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import DatasetType
from way2australia_rag.evaluation.suite import (
    declared_release_id,
    load_suite,
    read_manifest,
)

SUITE = "evaluation/suites/public-eval-v1.json"


def tree_hashes() -> dict[str, str]:
    return {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((REPO_ROOT / "evaluation").rglob("*"))
        if p.is_file()
    }


def copy_suite(tmp_path: Path) -> Path:
    shutil.copytree(REPO_ROOT / "evaluation", tmp_path / "evaluation")
    return tmp_path


def test_real_suite_loads_every_declared_case_and_is_read_only() -> None:
    before = tree_hashes()
    suite = load_suite(REPO_ROOT, SUITE)
    assert suite.manifest.evaluation_suite_id == "public-eval-v1"
    counts = (
        len(live_suite_rows("golden_answerable")),
        len(live_suite_rows("unanswerable_refusal")),
        len(live_suite_rows("security")),
    )
    assert (len(suite.goldens), len(suite.unanswerable), len(suite.security)) == counts
    assert suite.manifest.case_count == sum(counts)
    assert tree_hashes() == before


def test_unknown_dataset_type_refused(tmp_path: Path) -> None:
    root = copy_suite(tmp_path)
    path = root / SUITE
    raw = json.loads(path.read_text())
    raw["datasets"][0]["type"] = "mystery"
    path.write_text(json.dumps(raw))
    with pytest.raises(EvaluationConfigurationError, match="unknown dataset type"):
        load_suite(root, SUITE)


def test_escaping_path_refused(tmp_path: Path) -> None:
    root = copy_suite(tmp_path)
    path = root / SUITE
    raw = json.loads(path.read_text())
    raw["datasets"][1]["path"] = "../outside.jsonl"
    path.write_text(json.dumps(raw))
    with pytest.raises(EvaluationConfigurationError, match="outside"):
        load_suite(root, SUITE)
    with pytest.raises(EvaluationConfigurationError, match="outside"):
        read_manifest(root, "../suite.json")


def test_malformed_line_names_file_and_line_only(tmp_path: Path) -> None:
    root = copy_suite(tmp_path)
    (root / "evaluation/datasets/security_public.jsonl").write_text(
        '{"case_id": "SECRET-QUERY"}\n'
    )
    with pytest.raises(EvaluationConfigurationError, match="line 1") as info:
        load_suite(root, SUITE)
    message = str(info.value)
    assert "security_public.jsonl" in message
    assert "SECRET-QUERY" not in message and str(root) not in message


def test_access_context_is_loaded_but_ignored() -> None:
    suite = load_suite(REPO_ROOT, SUITE)
    assert all(c.access_context for c in suite.goldens)
    # Retrieval-facing models expose no field derived from it.
    assert not any(
        "access" in f
        for f in type(suite.goldens[0]).model_fields
        if f != "access_context"
    )


def test_extra_fields_tolerated(tmp_path: Path) -> None:
    root = copy_suite(tmp_path)
    path = root / "evaluation/datasets/unanswerable_public.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    rows[0]["brand_new_field"] = {"a": 1}
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    suite = load_suite(root, SUITE)
    assert len(suite.unanswerable) == len(live_suite_rows("unanswerable_refusal"))


def test_declared_release_id() -> None:
    assert declared_release_id(REPO_ROOT, "seed-v1") == "seed-v1"
    for bad in ("nope-v9", "../seed-v1", ""):
        with pytest.raises(EvaluationConfigurationError):
            declared_release_id(REPO_ROOT, bad)


def test_dataset_types_loaded_by_type() -> None:
    suite = load_suite(REPO_ROOT, SUITE)
    for kind in DatasetType:
        expected = live_suite_rows(kind.value, active_only=True)
        assert len(suite.active(kind)) == len(expected), kind
