"""Continuity command tests (Spec 010 R10)."""

import json
import subprocess
from pathlib import Path
from typing import Any

from conftest import REPO_ROOT
from way2australia_rag.evaluation.continuity import (
    EXIT_DIFF,
    EXIT_OK,
    EXIT_REFUSED,
    compare_continuity,
)

from .test_compare import LEXICAL, doc23, write


def _base(**over: Any) -> dict[str, Any]:
    row = {
        "case_id": "g001",
        "case_version": 1,
        "query_language": "en",
        "category": "business",
        "source_authority": "owner_approved",
        "ranked_document_ids": ["b001"],
        "relevant_document_ids": ["b001"],
        "hit": True,
        "recall": 1.0,
        "reciprocal_rank": 1.0,
        "latency_ms": 1.0,
        "served_strategy": "hybrid",
        "fallback_reason": None,
        "query_terms_truncated": False,
        "leg_ranks": None,
        "script_mix": "latin",
    }
    document = doc23(
        n=1,
        cases=[row],
        lote="ml",
        git_commit="aaa",
        evaluation_suite_id="public-eval-v2",
        evaluation_suite_version=2,
        lexical_index=dict(LEXICAL),
    )
    document.update(over)
    return document


def test_equal_runs_exit_zero(tmp_path: Path) -> None:
    base = _base()
    cand = _base(
        lote=None,
        git_commit="bbb",
        evaluation_suite_id="public-eval-v3",
        evaluation_suite_version=3,
    )
    code, lines = compare_continuity(
        write(tmp_path, "b.json", base), write(tmp_path, "c.json", cand)
    )
    assert code == EXIT_OK
    assert any("suite:" in line for line in lines)
    assert any("lote:" in line for line in lines)


def test_committed_fixtures_equal(tmp_path: Path) -> None:
    fixtures = REPO_ROOT / "packages/rag/tests/evaluation/fixtures"
    code, _lines = compare_continuity(
        fixtures / "continuity_base.json",
        fixtures / "continuity_candidate_equal.json",
    )
    assert code == EXIT_OK


def test_differing_hit_exits_one(tmp_path: Path) -> None:
    base = _base()
    cand = _base(lote=None, git_commit="bbb")
    cand["cases"][0]["hit"] = False
    cand["cases"][0]["reciprocal_rank"] = 0.0
    code, lines = compare_continuity(
        write(tmp_path, "b.json", base), write(tmp_path, "c.json", cand)
    )
    assert code == EXIT_DIFF
    assert any("g001" in line for line in lines)


def test_only_in_one_file_is_reported(tmp_path: Path) -> None:
    base = _base()
    cand = _base(lote=None, git_commit="bbb")
    extra = dict(cand["cases"][0])
    extra.update(
        case_id="g999",
        ranked_document_ids=[],
        hit=False,
        reciprocal_rank=0.0,
    )
    cand["cases"].append(extra)
    code, _lines = compare_continuity(
        write(tmp_path, "b.json", base), write(tmp_path, "c.json", cand)
    )
    assert code == EXIT_OK


def test_identity_mismatch_exits_two(tmp_path: Path) -> None:
    base = _base()
    cand = _base(lote=None, git_commit="bbb", top_k=3)
    code, lines = compare_continuity(
        write(tmp_path, "b.json", base), write(tmp_path, "c.json", cand)
    )
    assert code == EXIT_REFUSED
    assert any("top_k" in line for line in lines)


def test_unreadable_file_exits_two(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code, _lines = compare_continuity(bad, write(tmp_path, "b.json", _base()))
    assert code == EXIT_REFUSED


def test_make_eval_continuity_surfaces_exit_one_on_diff(tmp_path: Path) -> None:
    fixtures = REPO_ROOT / "packages/rag/tests/evaluation/fixtures"
    base_path = fixtures / "continuity_base.json"
    cand = json.loads((fixtures / "continuity_candidate_equal.json").read_text())
    cand["cases"][0]["hit"] = False
    cand_path = write(tmp_path, "cand.json", cand)
    done = subprocess.run(  # noqa: S603
        [
            "make",
            "-C",
            str(REPO_ROOT),
            f"BASE={base_path}",
            f"CANDIDATE={cand_path}",
            "eval-continuity",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert "eval-continuity: exit 1" in done.stderr
    assert done.returncode != EXIT_OK
