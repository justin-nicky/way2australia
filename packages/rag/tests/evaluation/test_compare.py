"""Result comparison and quality gate tests (Spec 006 R11).

Synthetic result files in tmp_path only. The committed 1.0 baseline is read, never
written.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation import cli
from way2australia_rag.evaluation.compare import (
    HIT_TOLERANCE_CASES,
    MRR_EPSILON,
    compare,
    mrr_tolerance,
)
from way2australia_rag.evaluation.errors import NotComparableError
from way2australia_rag.evaluation.results import read_result

SECRET_QUERY = "SECRET-QUERY text"
COMMITTED = (
    REPO_ROOT / "experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json"
)
NEXT_STEP = "`make eval-retrieval`"


def case(i: int, hit: bool = True, rr: float = 1.0, **extra: Any) -> dict[str, Any]:
    row = {
        "case_id": f"g{i:03d}",
        "case_version": 1,
        "query_language": "en" if i % 2 else "mixed",
        "category": "business" if i % 3 else "official",
        "source_authority": "owner_approved" if i % 2 else "naati",
        "ranked_document_ids": [],
        "relevant_document_ids": [],
        "query": SECRET_QUERY,  # must never be echoed
        "hit": hit,
        "recall": 1.0 if hit else 0.0,
        "reciprocal_rank": rr if hit else 0.0,
        "latency_ms": 10.0,
    }
    row.update(extra)
    return row


def doc(n: int = 10, *, v2: bool = True, **over: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema_version": "2.0" if v2 else "1.0",
        "kind": "retrieval_evaluation" if v2 else "retrieval_baseline",
        "git_commit": "abc",
        "evaluation_suite_id": "public-eval-v1",
        "evaluation_suite_version": 1,
        "collection": "c1",
        "index_version": "idx-v1",
        "index_settings": {"embedder_model_id": "m", "embedder_revision": "r1"},
        "top_k": 5,
        "device": "cpu",
        "embedder_is_fake": False,
        "document_count": 13,
        "latency_ms": {"p50": 10.0, "p95": 20.0},
        "cases": [case(i) for i in range(n)],
    }
    document.update(over)
    return document


def write(tmp_path: Path, name: str, document: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def run(tmp_path: Path, base: dict[str, Any], cand: dict[str, Any]):  # noqa: ANN201
    return compare(
        read_result(write(tmp_path, "base.json", base), "BASE"),
        read_result(write(tmp_path, "cand.json", cand), "CANDIDATE"),
    )


def refusal(tmp_path: Path, base: dict[str, Any], cand: dict[str, Any]) -> str:
    with pytest.raises(NotComparableError) as info:
        run(tmp_path, base, cand)
    message = str(info.value)
    assert message.startswith("not comparable:")
    assert SECRET_QUERY not in message
    assert str(tmp_path) not in message
    return message


def test_constants() -> None:
    assert HIT_TOLERANCE_CASES == 1
    assert mrr_tolerance(4) == 0.25


def test_identical_runs_pass_without_warnings(tmp_path: Path) -> None:
    result = run(tmp_path, doc(), doc())
    assert result.passed
    assert not [x for x in result.lines if x.startswith("WARNING")]


def test_pass_at_exactly_one_lost_case_and_fail_at_two(tmp_path: Path) -> None:
    one = doc()
    one["cases"][0] = case(0, hit=False)
    assert run(tmp_path, doc(), one).passed  # MRR drop is exactly 1/10 too
    two = doc()
    two["cases"][0] = case(0, hit=False)
    two["cases"][1] = case(1, hit=False)
    result = run(tmp_path, doc(), two)
    assert not result.passed
    assert "hits dropped 10 -> 8" in result.failures[0]


def test_mrr_boundary(tmp_path: Path) -> None:
    # Hits stay equal; the MRR drop is exactly 1/n, then just above it.
    base = doc()
    cand = doc()
    cand["cases"][0] = case(0, rr=0.5)
    cand["cases"][1] = case(1, rr=0.5)  # total drop 1.0 / 10 = 1/n
    assert run(tmp_path, base, cand).passed
    cand["cases"][2] = case(2, rr=0.99)  # a little more
    result = run(tmp_path, base, cand)
    assert not result.passed
    assert result.hits_base == result.hits_candidate
    assert "MRR dropped" in result.failures[0]


def ranked(ranks: tuple[int, ...]) -> dict[str, Any]:
    return doc(
        len(ranks),
        cases=[case(i, rr=1 / rank) for i, rank in enumerate(ranks)],
    )


def test_mrr_boundary_at_three_cases_exercises_the_epsilon(tmp_path: Path) -> None:
    # Pass: the unrounded drop is one float step above 1/3, so only the epsilon
    # keeps this a pass.
    result = run(tmp_path, ranked((1, 1, 1)), ranked((1, 2, 2)))
    assert result.hits_base == result.hits_candidate == 3
    drop = result.mrr_base - result.mrr_candidate
    assert drop == 0.33333333333333337
    assert drop > mrr_tolerance(3)
    assert drop <= mrr_tolerance(3) + MRR_EPSILON
    assert result.passed
    # Fail: the smallest drop above 1/3 reachable with ranks 1-5 at n=3 (61/180).
    result = run(tmp_path, ranked((1, 2, 4)), ranked((3, 5, 5)))
    assert result.hits_base == result.hits_candidate == 3
    drop = result.mrr_base - result.mrr_candidate
    assert abs(drop - 61 / 180) < 1e-12
    assert drop > mrr_tolerance(3) + MRR_EPSILON
    assert not result.passed
    assert "MRR dropped" in result.failures[0]


def test_flip_warnings_both_directions_sorted(tmp_path: Path) -> None:
    base = doc()
    base["cases"][5] = case(5, hit=False)
    cand = doc()
    cand["cases"][2] = case(2, hit=False)
    result = run(tmp_path, base, cand)
    warnings = [x for x in result.lines if x.startswith("WARNING")]
    assert warnings == [
        "WARNING flipped hit->miss: g002 v1",
        "WARNING flipped miss->hit: g005 v1",
    ]
    assert result.passed


def test_slices_and_latency_and_identity_are_printed(tmp_path: Path) -> None:
    cand = doc(device="mps:0", latency_ms={"p50": 12.0, "p95": 25.0})
    text = "\n".join(run(tmp_path, doc(), cand).lines)
    assert "query_language en" in text and "category business" in text
    assert "source_authority naati" in text
    assert "latency p50 (informational): 10.0 ms -> 12.0 ms" in text
    assert "identity differs, device: cpu -> mps:0" in text


def test_v1_versus_v2_notes_source_authority_not_compared(tmp_path: Path) -> None:
    result = run(tmp_path, doc(v2=False), doc())
    text = "\n".join(result.lines)
    assert result.passed
    assert "source_authority slice was not compared" in text
    assert "source_authority naati" not in text


def test_suite_id_differs(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(evaluation_suite_id="other-suite"))
    assert "suite ID changed public-eval-v1 -> other-suite" in message
    assert NEXT_STEP in message and "new baseline" in message


def test_suite_version_differs(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(evaluation_suite_version=2))
    assert "suite version changed 1 -> 2" in message
    assert NEXT_STEP in message and "new baseline" in message


def test_case_set_missing_and_extra(tmp_path: Path) -> None:
    fewer = doc()
    fewer["cases"].pop()
    message = refusal(tmp_path, doc(), fewer)
    assert "case set differs (10 -> 9 cases" in message
    assert "only in BASE: g009 v1" in message
    assert NEXT_STEP in message
    message = refusal(tmp_path, fewer, doc())
    assert "only in CANDIDATE: g009 v1" in message
    assert "case set differs (9 -> 10 cases" in message
    assert NEXT_STEP in message


def test_case_version_differs(tmp_path: Path) -> None:
    cand = doc()
    cand["cases"][3] = case(3, case_version=2)
    message = refusal(tmp_path, doc(), cand)
    assert "case_version changed for g003 1 -> 2" in message
    assert NEXT_STEP in message


def test_many_differing_cases_are_capped(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(15), doc(2))
    assert "and 3 more" in message


def test_top_k_differs(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(top_k=3))
    assert "top_k changed 5 -> 3" in message and NEXT_STEP in message


def test_document_count_differs(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(document_count=14))
    assert "document count changed 13 -> 14" in message
    assert (
        "run `make eval-retrieval` on the current system to set a new baseline."
        in message
    )


def test_base_fake(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(embedder_is_fake=True), doc())
    assert "BASE file 'base.json' comes from a fake-embedder index" in message
    assert "real embedder" in message and NEXT_STEP in message


def test_candidate_fake(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(embedder_is_fake=True))
    assert "CANDIDATE file 'cand.json' comes from a fake-embedder index" in message
    assert "BASE file" not in message and "real embedder" in message


@pytest.mark.parametrize(
    ("over", "found"),
    [
        ({"kind": "security_evaluation"}, "'security_evaluation'"),
        ({"schema_version": "3.0"}, "'3.0'"),
    ],
)
def test_unknown_kind_or_schema_version(
    tmp_path: Path, over: dict[str, Any], found: str
) -> None:
    message = refusal(tmp_path, doc(**over), doc())
    assert "BASE file 'base.json'" in message and found in message
    assert "make eval-retrieval" in message and "make retrieval-baseline" in message


def test_unreadable_and_malformed_files(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(NotComparableError) as info:
        read_result(tmp_path / "bad.json", "BASE")
    assert "'bad.json'" in str(info.value) and str(tmp_path) not in str(info.value)
    with pytest.raises(NotComparableError):
        read_result(tmp_path / "missing.json", "CANDIDATE")
    broken = doc()
    del broken["cases"][0]["hit"]
    with pytest.raises(NotComparableError, match="malformed"):
        read_result(write(tmp_path, "broken.json", broken), "BASE")


@pytest.mark.parametrize(
    ("label", "version", "second_version"),
    [("2.0 same version", True, 1), ("2.0 other version", True, 2), ("1.0", False, 1)],
)
def test_duplicate_case_id_is_refused(
    tmp_path: Path, label: str, version: bool, second_version: int
) -> None:
    document = doc(3, v2=version)
    document["cases"].append(case(0, case_version=second_version))
    path = write(tmp_path, "dup.json", document)
    with pytest.raises(NotComparableError) as info:
        read_result(path, "BASE")
    message = str(info.value)
    assert message.startswith("not comparable:"), label
    assert "'dup.json'" in message and "g000" in message
    assert "make eval-retrieval" in message
    assert str(tmp_path) not in message
    other = write(tmp_path, "ok.json", doc(3))
    assert cli.main(["compare", "--base", str(path), "--candidate", str(other)]) == 2


def test_several_differences_are_all_named(tmp_path: Path) -> None:
    message = refusal(
        tmp_path,
        doc(embedder_is_fake=True),
        doc(8, top_k=3, document_count=14, evaluation_suite_version=2),
    )
    for part in (
        "fake-embedder",
        "suite version changed 1 -> 2",
        "top_k changed 5 -> 3",
        "document count changed 13 -> 14",
        "case set differs (10 -> 8 cases",
    ):
        assert part in message


def test_committed_baseline_compared_with_itself_passes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run_ = read_result(COMMITTED, "BASE")  # read-only
    assert run_.schema_version == "1.0" and len(run_.cases) == 63
    result = compare(run_, read_result(COMMITTED, "CANDIDATE"))
    assert result.passed
    assert not [x for x in result.lines if x.startswith("WARNING")]
    code = cli.main(
        ["compare", "--base", str(COMMITTED), "--candidate", str(COMMITTED)]
    )
    assert code == 0
    assert "eval-compare: PASS" in capsys.readouterr().out


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = write(tmp_path, "base.json", doc())
    bad = doc()
    for i in (0, 1):
        bad["cases"][i] = case(i, hit=False)
    failing = write(tmp_path, "fail.json", bad)
    assert cli.main(["compare", "--base", str(base), "--candidate", str(failing)]) == 1
    assert "FAIL" in capsys.readouterr().out
    other = write(tmp_path, "other.json", doc(document_count=14))
    assert cli.main(["compare", "--base", str(base), "--candidate", str(other)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("not comparable:") and "13 -> 14" in err
    assert str(tmp_path) not in err and SECRET_QUERY not in err
