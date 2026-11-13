"""Evaluation Suite `public-eval-v4` tests (Spec 012 T6, R12).

Consistency checks only. The v3 reference is pinned by SHA-256 so the tests need no
git history.
"""

import hashlib
import json
from typing import Any

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation import cli

V3_SUITE = "evaluation/suites/public-eval-v3.json"
V4_SUITE = "evaluation/suites/public-eval-v4.json"
CANDIDATES = "evaluation/candidates/012-candidates.jsonl"
FILES = {
    "golden_answerable": "golden_public.jsonl",
    "unanswerable_refusal": "unanswerable_public.jsonl",
    "security": "security_public.jsonl",
}
V3_HASHES = {
    "golden_public.jsonl": "63d61e108ca3549e71a26eddee4a6755d30ba7d3578fdd861fa253ee319bca6a",  # noqa: E501
    "unanswerable_public.jsonl": "70f6df38d6c828bf9cfdf154f54de2b1eee149330fadf551a41d62b706a2b06e",  # noqa: E501
    "security_public.jsonl": "659da65cfbcf2116a6f9f05a41e0e0a8c1037433e90d7645a8e53c202232da80",  # noqa: E501
}
NEW_IDS = {"golden_answerable": ["g088"], "unanswerable_refusal": ["u016", "u017"]}


def rows(path: str) -> list[dict[str, Any]]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    return [json.loads(x) for x in text.splitlines() if x.strip()]


def manifest(path: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_cli_default_suite_is_v4() -> None:
    assert cli.DEFAULT_SUITE == V4_SUITE


def test_v4_manifest_counts_and_lineage() -> None:
    v4 = manifest(V4_SUITE)
    assert v4["status"] == "active" and v4["version"] == 4
    assert v4["replaces"] == {"evaluation_suite_id": "public-eval-v3", "version": 3}
    assert v4["case_count"] == sum(len(rows(d["path"])) for d in v4["datasets"])
    assert [d["type"] for d in v4["datasets"]] == list(FILES)


@pytest.mark.parametrize("name", list(V3_HASHES))
def test_v3_dataset_files_match_their_committed_hashes(name: str) -> None:
    data = (REPO_ROOT / "evaluation/datasets/v3" / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == V3_HASHES[name]


def test_v3_manifest_differs_from_v4_lineage_only_in_status() -> None:
    v3 = manifest(V3_SUITE)
    assert v3["status"] == "replaced"
    assert v3["evaluation_suite_id"] == "public-eval-v3" and v3["version"] == 3


@pytest.mark.parametrize("kind", list(FILES))
def test_v3_rows_equal_their_v4_copy_except_suite_id(kind: str) -> None:
    before = rows(f"evaluation/datasets/v3/{FILES[kind]}")
    after = rows(f"evaluation/datasets/v4/{FILES[kind]}")
    assert len(after) == len(before) + len(NEW_IDS.get(kind, []))
    for old, new in zip(before, after[: len(before)], strict=True):
        assert list(new) == list(old)
        assert new == dict(old, evaluation_suite_id="public-eval-v4")
    assert [r["case_id"] for r in after[len(before) :]] == NEW_IDS.get(kind, [])
    assert all(r["evaluation_suite_id"] == "public-eval-v4" for r in after)


def test_candidate_decisions_and_promotions() -> None:
    by_id = {
        r["case_id"]: r
        for kind in FILES
        for r in rows(f"evaluation/datasets/v4/{FILES[kind]}")
    }
    promoted = {}
    for row in rows(CANDIDATES):
        review = row["review"]
        assert row["status"] == "suggested"
        assert review["reviewed_on"]
        if review["decision"] == "rejected":
            assert review["promoted_as"] is None and review["notes"]
            continue
        assert review["decision"] in {"approved", "approved_with_changes"}
        assert review["promoted_as"]["suite_id"] == "public-eval-v4"
        promoted[row["candidate_id"]] = review["promoted_as"]["case_id"]
        case = by_id[review["promoted_as"]["case_id"]]
        assert case["query"] == row["proposed_case"]["query"]
    assert promoted == {
        "cand012_en_001": "g088",
        "cand012_en_003": "u016",
        "cand012_ml_002": "u017",
    }
