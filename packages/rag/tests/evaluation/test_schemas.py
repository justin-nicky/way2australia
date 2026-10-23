"""Evaluation schema tests (Spec 006 R2)."""

import copy
import json
from typing import Any

import pytest
from conftest import REPO_ROOT
from jsonschema import Draft202012Validator
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.schemas import load_schemas

SCHEMA_DIR = REPO_ROOT / "evaluation/schemas"

BASE: dict[str, Any] = {
    "case_id": "x1",
    "case_version": 1,
    "status": "active",
    "introduced_in_release": "seed-v1",
    "evaluation_suite_id": "s",
    "query": "q",
}
GOLDEN = {
    **BASE,
    "answerable": True,
    "relevant_document_ids": ["d"],
    "query_language": "en",
    "category": "c",
}
UNANSWERABLE = {**BASE, "answerable": False, "expected_behavior": "b"}
SECURITY = {**BASE, "attack_type": "a", "expected_behavior": "b"}
REQUIRED = {
    "golden_answerable": (
        GOLDEN,
        ["query", "answerable", "relevant_document_ids", "query_language", "category"],
    ),
    "unanswerable_refusal": (
        UNANSWERABLE,
        ["query", "answerable", "expected_behavior"],
    ),
    "security": (SECURITY, ["query", "attack_type", "expected_behavior"]),
}


@pytest.mark.parametrize("name", sorted(p.name for p in SCHEMA_DIR.glob("*.json")))
def test_schema_files_are_valid_draft_2020_12(name: str) -> None:
    Draft202012Validator.check_schema(json.loads((SCHEMA_DIR / name).read_text()))


def test_valid_rows_pass() -> None:
    schemas = load_schemas(REPO_ROOT)
    for name, (row, _) in REQUIRED.items():
        assert not list(schemas.case_type(name).iter_errors(row))


@pytest.mark.parametrize(
    ("name", "field"),
    [(n, f) for n, (_, fields) in REQUIRED.items() for f in fields],
)
def test_per_type_required_field_enforced(name: str, field: str) -> None:
    row = copy.deepcopy(REQUIRED[name][0])
    del row[field]
    assert list(load_schemas(REPO_ROOT).case_type(name).iter_errors(row))


def test_existing_schema_is_referenced_not_copied() -> None:
    types = json.loads((SCHEMA_DIR / "evaluation_case_types.schema.json").read_text())
    for name in REQUIRED:
        assert types["$defs"][name]["allOf"][0] == {
            "$ref": "evaluation_case.schema.json"
        }
    # the status enum is enforced through the referenced schema
    row = {**GOLDEN, "status": "retired"}
    assert list(load_schemas(REPO_ROOT).case_type("golden_answerable").iter_errors(row))


def test_missing_schema_is_configuration_error(tmp_path) -> None:  # noqa: ANN001
    (tmp_path / "evaluation/schemas").mkdir(parents=True)
    with pytest.raises(EvaluationConfigurationError):
        load_schemas(tmp_path)
