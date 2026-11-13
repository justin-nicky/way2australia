"""Evaluation Suite `public-eval-v3` tests (Spec 010 T1, R1).

Consistency checks only: counts come from the data under test, except R1's stated
slice minimums. The v2 reference is pinned by SHA-256 so the tests need no git
history.
"""

import asyncio
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation.schemas import load_schemas
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.eligibility import (
    GUEST_PUBLIC_POLICY,
    list_eligible_documents,
)

V2_SUITE = "evaluation/suites/public-eval-v2.json"
V3_SUITE = "evaluation/suites/public-eval-v3.json"
CANDIDATES = "evaluation/candidates/010-candidates.jsonl"
FILES = {
    "golden_answerable": "golden_public.jsonl",
    "unanswerable_refusal": "unanswerable_public.jsonl",
    "security": "security_public.jsonl",
}
V2_HASHES = {
    "golden_public.jsonl": "17e01a1ecc3c26f13c319f42fd101db9b456b143b0eac4fef62c342673f68745",  # noqa: E501
    "unanswerable_public.jsonl": "504b81079b0bf39c4e1f0b17231d749087c1a71a07e3cb148fb9e92f521092b3",  # noqa: E501
    "security_public.jsonl": "356c163e9595c92772e0d07ceb60a1ccf9e5562ba817f64861c9d95fdfee779e",  # noqa: E501
}
V2_MANIFEST_ACTIVE: dict[str, Any] = {
    "evaluation_suite_id": "public-eval-v2",
    "version": 2,
    "status": "active",
    "introduced_in_release": "seed-v1",
    "datasets": [
        {
            "type": kind,
            "path": f"evaluation/datasets/v2/{name}",
        }
        for kind, name in FILES.items()
    ],
    "case_count": 91,
    "replaces": {"evaluation_suite_id": "public-eval-v1", "version": 1},
    "notes": "Spec 007 suite. Every public-eval-v1 case is carried over unchanged "
    "except evaluation_suite_id, plus six owner-approved pure-Malayalam goldens "
    "(g064-g069) promoted from cand006_ml_001 to cand006_ml_006. g004 and u001 "
    "stay as in v1 (owner decision keep_both). Cases are versioned and "
    "human-governed.",
}


def rows(path: str) -> list[dict[str, Any]]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    return [json.loads(x) for x in text.splitlines() if x.strip()]


def v2_rows(kind: str) -> list[dict[str, Any]]:
    return rows(f"evaluation/datasets/v2/{FILES[kind]}")


def v3_rows(kind: str) -> list[dict[str, Any]]:
    return rows(f"evaluation/datasets/v3/{FILES[kind]}")


def manifest(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def candidates() -> list[dict[str, Any]]:
    return rows(CANDIDATES)


def test_v3_manifest_counts_and_lineage() -> None:
    v3 = manifest(V3_SUITE)
    # replaced by v4 (Spec 012)
    assert v3["status"] == "replaced" and v3["version"] == 3
    assert v3["replaces"] == {"evaluation_suite_id": "public-eval-v2", "version": 2}
    assert v3["case_count"] == sum(len(rows(d["path"])) for d in v3["datasets"])
    assert [d["type"] for d in v3["datasets"]] == list(FILES)


@pytest.mark.parametrize("kind", list(FILES))
def test_v2_rows_equal_their_v3_copy_except_suite_id(kind: str) -> None:
    before, after = v2_rows(kind), v3_rows(kind)
    assert len(after) >= len(before)
    for old, new in zip(before, after[: len(before)], strict=True):
        assert new["evaluation_suite_id"] == "public-eval-v3"
        assert list(new) == list(old)
        assert new == dict(old, evaluation_suite_id="public-eval-v3")


@pytest.mark.parametrize("name", list(V2_HASHES))
def test_v2_dataset_files_match_their_committed_hashes(name: str) -> None:
    data = (REPO_ROOT / "evaluation/datasets/v2" / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == V2_HASHES[name]


def test_v2_manifest_differs_only_in_status() -> None:
    after = manifest(V2_SUITE)
    assert after["status"] == "replaced"
    assert dict(after, status="active") == V2_MANIFEST_ACTIVE


def test_every_candidate_is_promoted_with_a_recorded_approval() -> None:
    by_id = {r["case_id"]: r for kind in FILES for r in v3_rows(kind)}
    seen = set()
    for row in candidates():
        review = row["review"]
        assert row["status"] == "suggested"
        assert review["decision"] in {"approved", "approved_with_changes"}
        assert review["reviewed_on"]
        promoted = review["promoted_as"]
        assert promoted["suite_id"] == "public-eval-v3"
        case = by_id[promoted["case_id"]]
        assert promoted["case_id"] not in seen
        seen.add(promoted["case_id"])
        proposed = row["proposed_case"]
        assert case["status"] == "active" and case["case_version"] == 1
        assert case["introduced_in_release"] == "seed-v1"
        assert case["query"] == proposed["query"]
        assert case["query_language"] == proposed["query_language"]
        if proposed["answerable"]:
            assert case["category"] == proposed["category"] == "multilingual"
            assert case["relevant_document_ids"] == proposed["relevant_document_ids"]
            assert case["expected_facts"] == proposed["expected_facts"]
        else:
            assert case["expected_behavior"] == proposed["expected_behavior"]


def test_new_goldens_follow_candidate_order_without_id_gaps() -> None:
    goldens = v3_rows("golden_answerable")
    new = goldens[len(v2_rows("golden_answerable")) :]
    ids = [r["case_id"] for r in new]
    assert ids == [f"g{70 + i:03d}" for i in range(len(new))]
    promoted = [
        r["review"]["promoted_as"]["case_id"]
        for r in candidates()
        if r["proposed_case"]["answerable"]
    ]
    assert promoted == ids


def test_slice_minimums() -> None:
    goldens = v3_rows("golden_answerable")
    assert sum(r["query_language"] == "ml" for r in goldens) >= 12
    assert sum(r["query_language"] == "mixed" for r in goldens) >= 12
    refusals = v3_rows("unanswerable_refusal")
    assert sum(r.get("query_language") == "ml" for r in refusals) >= 3


def test_every_relevant_document_is_eligible() -> None:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    eligible = {
        d.document_id
        for d in asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    }
    for row in v3_rows("golden_answerable"):
        assert set(row["relevant_document_ids"]) <= eligible, row["case_id"]


def test_real_evaluation_assets_validate() -> None:
    assert validate_evaluation(REPO_ROOT) == []


# --- candidate_row schema: golden or unanswerable proposed_case ----------------


def candidate_row(answerable: bool) -> dict[str, Any]:
    wanted = [r for r in candidates() if r["proposed_case"]["answerable"] is answerable]
    return copy.deepcopy(wanted[0])


def errors(row: dict[str, Any]) -> list[Any]:
    return list(load_schemas(REPO_ROOT).candidate_row().iter_errors(row))


def test_schema_accepts_both_shapes() -> None:
    assert errors(candidate_row(True)) == []
    assert errors(candidate_row(False)) == []


def test_schema_still_accepts_the_spec_006_rows() -> None:
    for row in rows("evaluation/candidates/006-candidates.jsonl"):
        assert errors(row) == []


def test_schema_rejects_a_golden_without_documents() -> None:
    row = candidate_row(True)
    del row["proposed_case"]["relevant_document_ids"]
    assert errors(row)


def test_schema_rejects_an_unanswerable_without_a_language() -> None:
    row = candidate_row(False)
    del row["proposed_case"]["query_language"]
    assert errors(row)


def test_schema_rejects_an_unanswerable_without_expected_behavior() -> None:
    row = candidate_row(False)
    del row["proposed_case"]["expected_behavior"]
    assert errors(row)


def test_schema_rejects_a_row_matching_neither_shape() -> None:
    row = candidate_row(True)
    row["proposed_case"]["answerable"] = "maybe"
    assert errors(row)


# --- unanswerable promotion check on a temporary copy ---------------------------


@pytest.fixture
def root(tmp_path: Path) -> Path:
    import shutil

    for name in ("evaluation", "knowledge"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def edit_jsonl(path: Path, change) -> None:  # noqa: ANN001
    data = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
    change(data)
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in data) + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("field", ["query", "expected_behavior", "query_language"])
def test_changed_unanswerable_field_is_a_problem_without_text(
    root: Path, field: str
) -> None:
    def change(data: list[dict]) -> None:
        next(r for r in data if r["case_id"] == "u013")[field] = "changed"

    edit_jsonl(root / "evaluation/datasets/v3/unanswerable_public.jsonl", change)
    found = [str(p) for p in validate_evaluation(root)]
    assert any(f"review.promoted_as.{field}" in p for p in found)
    assert not any("changed" in p for p in found)
