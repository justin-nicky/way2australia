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
    FORMAT_RULE_ADVICE,
    HIT_TOLERANCE_CASES,
    MRR_EPSILON,
    compare,
    mrr_tolerance,
)
from way2australia_rag.evaluation.errors import NotComparableError
from way2australia_rag.evaluation.results import SCHEMA_VERSION, read_result

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


def test_lote_difference_is_refused(tmp_path: Path) -> None:
    base = doc23(n=5, lote=None)
    cand = doc23(n=5, lote="ml")
    message = refusal(tmp_path, base, cand)
    assert "lote changed none -> ml" in message


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


# --- Spec 007 R10: identity rules across strategies ---------------------------

LEXICAL = {
    "label": "c1.sqlite",
    "tokenizer_name": "lexical-v1",
    "tokenizer_version": "1",
    "source_chunk_digest": "d" * 64,
    "chunk_count": 13,
}
COMMITTED_V2 = (
    REPO_ROOT / "experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json"
)


def doc21(strategy: str = "hybrid", **over: Any) -> dict[str, Any]:
    lexical = None if strategy == "dense" else dict(LEXICAL)
    return doc(
        schema_version="2.1",
        retrieval_strategy=strategy,
        lexical_index=lexical,
        **over,
    )


def test_committed_1_0_versus_2_0_passes_with_identity_rules() -> None:
    base = read_result(COMMITTED, "BASE")
    result = compare(base, read_result(COMMITTED_V2, "CANDIDATE"))
    assert result.passed
    differs = [x for x in result.lines if "identity differs" in x]
    assert all("git_commit" in x or "device" in x for x in differs)


def test_dense_versus_hybrid_passes_with_identity_lines(tmp_path: Path) -> None:
    result = run(tmp_path, doc21("dense"), doc21("hybrid"))
    text = "\n".join(result.lines)
    assert result.passed
    assert "identity differs, retrieval_strategy: dense -> hybrid" in text
    assert "identity differs, lexical_index: none -> lexical-v1 v1 digest" in text


def test_dense_versus_bm25_is_not_refused(tmp_path: Path) -> None:
    assert run(tmp_path, doc21("dense"), doc21("bm25")).passed
    assert run(tmp_path, doc(), doc21("bm25")).passed  # 2.0 dense vs 2.1 bm25


def test_collection_difference_names_both(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(collection="w2a-a"), doc(collection="w2a-b"))
    assert "collection changed w2a-a -> w2a-b" in message
    assert "same collection, index_version, embedder and lexical index" in message


@pytest.mark.parametrize("missing", ["absent", "null"])
def test_missing_collection_compares_by_index_version(
    tmp_path: Path, missing: str
) -> None:
    base = doc()
    if missing == "absent":
        del base["collection"]
    else:
        base["collection"] = None
    result = run(tmp_path, base, doc(collection="other"))
    text = "\n".join(result.lines)
    assert result.passed
    assert (
        "collection not recorded in base.json; compared by index_version only" in text
    )
    assert "cand.json; compared" not in text
    message = refusal(tmp_path, base, doc(collection="other", index_version="idx-v2"))
    assert "index_version changed idx-v1 -> idx-v2" in message


def test_index_version_difference_is_refused(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(index_version="idx-v2"))
    assert "index_version changed idx-v1 -> idx-v2" in message


@pytest.mark.parametrize(
    ("field", "value"), [("embedder_model_id", "m2"), ("embedder_revision", "r2")]
)
def test_embedder_difference_is_refused(tmp_path: Path, field: str, value: str) -> None:
    settings = {"embedder_model_id": "m", "embedder_revision": "r1", field: value}
    message = refusal(tmp_path, doc(), doc(index_settings=settings))
    assert "embedder changed m@r1 -> " in message and value in message


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("source_chunk_digest", "e" * 64),
        ("tokenizer_name", "lexical-v2"),
        ("tokenizer_version", "2"),
    ],
)
def test_lexical_identity_difference_is_refused(
    tmp_path: Path, key: str, value: str
) -> None:
    other = doc21("bm25")
    other["lexical_index"] = {**LEXICAL, key: value}
    message = refusal(tmp_path, doc21("hybrid"), other)
    if key == "tokenizer_name":
        assert "lexical tokenizer changed" in message
    else:
        assert "lexical" in message and value in message


def test_tokenizer_change_refused_without_cross_tokenizer(tmp_path: Path) -> None:
    other = doc21("bm25")
    other["lexical_index"] = {
        **LEXICAL,
        "tokenizer_name": "lexical-v2",
        "tokenizer_version": "2",
    }
    message = refusal(tmp_path, doc21("hybrid"), other)
    assert "lexical tokenizer changed" in message
    assert "--cross-tokenizer" in message


def test_tokenizer_change_accepted_with_cross_tokenizer(tmp_path: Path) -> None:
    other = doc21("bm25")
    other["lexical_index"] = {
        **LEXICAL,
        "tokenizer_name": "lexical-v2",
        "tokenizer_version": "2",
    }
    result = compare(
        read_result(write(tmp_path, "base.json", doc21("hybrid")), "BASE"),
        read_result(write(tmp_path, "cand.json", other), "CANDIDATE"),
        cross_tokenizer=True,
    )
    assert result.passed
    assert any("cross-tokenizer:" in line for line in result.lines)


def test_cross_tokenizer_still_refuses_digest_mismatch(tmp_path: Path) -> None:
    other = doc21("bm25")
    other["lexical_index"] = {
        **LEXICAL,
        "tokenizer_name": "lexical-v2",
        "tokenizer_version": "2",
        "source_chunk_digest": "e" * 64,
    }
    with pytest.raises(NotComparableError) as info:
        compare(
            read_result(write(tmp_path, "base.json", doc21("hybrid")), "BASE"),
            read_result(write(tmp_path, "cand.json", other), "CANDIDATE"),
            cross_tokenizer=True,
        )
    assert "source_chunk_digest" in str(info.value)


def test_lexical_label_difference_alone_is_not_refused(tmp_path: Path) -> None:
    other = doc21("bm25")
    other["lexical_index"] = {**LEXICAL, "label": "renamed.sqlite", "chunk_count": 13}
    assert run(tmp_path, doc21("hybrid"), other).passed


def test_identity_refusals_join_existing_ones(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc(), doc(top_k=3, collection="x"))
    assert "top_k changed 5 -> 3" in message
    assert "collection changed c1 -> x" in message


def test_embedder_pair_is_compared_not_the_joined_string(tmp_path: Path) -> None:
    left = doc(index_settings={"embedder_model_id": "a@b", "embedder_revision": "c"})
    right = doc(index_settings={"embedder_model_id": "a", "embedder_revision": "b@c"})
    message = refusal(tmp_path, left, right)
    assert "embedder changed a@b@c -> a@b@c" in message


@pytest.mark.parametrize("strategy", ["bm25", "hybrid"])
@pytest.mark.parametrize("lexical", [None, "text", ["x"]])
def test_lexical_run_without_a_lexical_object_is_refused(
    tmp_path: Path, strategy: str, lexical: object
) -> None:
    broken = doc21(strategy)
    broken["lexical_index"] = lexical
    message = refusal(tmp_path, doc21("hybrid"), broken)
    assert f"is a {strategy} run without a lexical_index object" in message
    message = refusal(tmp_path, broken, doc21("hybrid"))
    assert "without a lexical_index object" in message


# --- Spec 008 R9: 2.2 files, served strategy -----------------------------------

COMMITTED_BM25 = (
    REPO_ROOT / "experiments/results/retrieval-evaluation-idx-v1-20261028T123109Z.json"
)


def doc22(
    served: str = "bm25",
    *,
    requested: str | None = None,
    reason: str | None = None,
    standalone: bool = True,
    n: int = 10,
    **over: Any,
) -> dict[str, Any]:
    """A 2.2 file. `standalone` drops `index_settings` (Qdrant never reached) and
    leaves the embedder pair in `dense_identity`."""
    path = served if reason is None else f"{served}+fallback:{reason}"
    cases = [case(i, served_strategy=served, fallback_reason=reason) for i in range(n)]
    document = doc(
        n,
        schema_version="2.2",
        requested_strategy=requested or served,
        served_strategies=[served],
        retrieval_strategy=served,
        fallback_counts={reason: n} if reason else {},
        dense_identity={
            "collection": "c1",
            "index_version": "idx-v1",
            "embedder_model_id": "m",
            "embedder_revision": "r1",
            "embedder_is_fake": False,
            "source": "lexical_file" if standalone else "qdrant",
        },
        lexical_index=None if served == "dense" else dict(LEXICAL),
        latency_ms={
            "p50": 3.0,
            "p95": 4.0,
            "by_served_path": {path: {"p50": 3.0, "p95": 4.0, "n": n}},
        },
        cases=cases,
    )
    if standalone:
        document["index_settings"] = None
    document.update(over)
    return document


def test_standalone_bm25_2_2_versus_2_1_bm25_is_accepted_and_gated(
    tmp_path: Path,
) -> None:
    result = run(tmp_path, doc21("bm25"), doc22("bm25"))
    assert result.passed and result.n == 10
    worse = doc22("bm25")
    worse["cases"] = [case(i, hit=i > 2) for i in range(10)]
    for row in worse["cases"]:
        row["served_strategy"] = "bm25"
    assert not run(tmp_path, doc21("bm25"), worse).passed


def test_embedder_pair_comes_from_dense_identity_when_settings_are_null(
    tmp_path: Path,
) -> None:
    path = write(tmp_path, "c.json", doc22("bm25"))
    run_ = read_result(path)
    assert run_.info["embedder_model_id"] == "m"
    assert run_.info["embedder_revision"] == "r1"
    other = doc22("bm25")
    other["dense_identity"]["embedder_revision"] = "r2"
    message = refusal(tmp_path, doc21("bm25"), other)
    assert "embedder changed m@r1 -> m@r2" in message


def test_fallback_only_2_2_file_compares_with_a_labelled_latency(
    tmp_path: Path,
) -> None:
    result = run(
        tmp_path,
        doc21("bm25"),
        doc22("bm25", requested="hybrid", reason="qdrant_unavailable"),
    )
    text = "\n".join(result.lines)
    assert result.passed
    assert "candidate includes failed dense attempt: qdrant_unavailable" in text
    assert "requested hybrid and was served by bm25" in text


def test_mixed_2_2_file_is_refused_with_counts(tmp_path: Path) -> None:
    mixed = doc22("hybrid", standalone=False)
    mixed["served_strategies"] = ["bm25", "hybrid"]
    for row in mixed["cases"][:3]:
        row["served_strategy"] = "bm25"
    message = refusal(tmp_path, doc21("hybrid"), mixed)
    assert (
        "mixes served strategies (golden cases bm25: 3, hybrid: 7; "
        "served_strategies: bm25, hybrid)"
    ) in message
    assert "re-run when the system is stable" in message


def test_2_2_file_with_only_unanswerable_cases_served_differently_is_refused(
    tmp_path: Path,
) -> None:
    mixed = doc22("bm25")
    mixed["served_strategies"] = ["bm25", "hybrid"]
    path = write(tmp_path, "mixed.json", mixed)
    with pytest.raises(NotComparableError) as error:
        read_result(path)
    message = str(error.value)
    assert "golden cases bm25: 10" in message
    assert "served_strategies: bm25, hybrid" in message
    base = write(tmp_path, "base.json", doc21("bm25"))
    args = ["compare", "--base", str(base), "--candidate", str(path)]
    assert cli.main(args) == 2


def test_case_row_disagreeing_with_served_strategies_is_refused(
    tmp_path: Path,
) -> None:
    bad = doc22("bm25")
    bad["cases"][0]["served_strategy"] = "hybrid"
    assert "mixes served strategies" in refusal(tmp_path, doc21("bm25"), bad)


def test_2_2_bm25_without_a_lexical_object_is_refused(tmp_path: Path) -> None:
    path = write(tmp_path, "c.json", doc22("bm25", lexical_index=None))
    with pytest.raises(NotComparableError, match="without a lexical_index object"):
        read_result(path)


def test_2_1_versus_2_2_dense_reads_both(tmp_path: Path) -> None:
    result = run(tmp_path, doc21("dense"), doc22("dense", standalone=False))
    assert result.passed
    assert "source_authority slice was not compared" not in "\n".join(result.lines)


def test_committed_spec_007_bm25_reads_and_compares_with_standalone_2_2(
    tmp_path: Path,
) -> None:
    base = read_result(COMMITTED_BM25, "BASE")
    assert base.schema_version == "2.1" and base.info["retrieval_strategy"] == "bm25"
    cand = doc22(
        "bm25",
        n=len(base.cases),
        document_count=base.document_count,
        evaluation_suite_id=base.suite_id,
        evaluation_suite_version=base.suite_version,
        top_k=base.top_k,
        collection=base.info["collection"],
        index_version=base.info["index_version"],
        lexical_index=base.info["lexical"],
        dense_identity={
            "collection": base.info["collection"],
            "index_version": base.info["index_version"],
            "embedder_model_id": base.info["embedder_model_id"],
            "embedder_revision": base.info["embedder_revision"],
            "embedder_is_fake": False,
            "source": "lexical_file",
        },
    )
    cand["cases"] = [
        {
            **case(0),
            "case_id": key[0],
            "case_version": key[1],
            "hit": row.hit,
            "recall": row.recall,
            "reciprocal_rank": row.reciprocal_rank,
            "query_language": row.query_language,
            "category": row.category,
            "source_authority": row.source_authority,
            "served_strategy": "bm25",
        }
        for key, row in base.cases.items()
    ]
    result = compare(base, read_result(write(tmp_path, "c.json", cand), "CANDIDATE"))
    assert result.passed and result.hits_base == result.hits_candidate


# --- Spec 009 R8: cross-index compare and format 2.3 -------------------------


def doc23(**over: Any) -> dict[str, Any]:
    n = over.pop("n", 10)
    document = doc22("hybrid", standalone=False, n=n)
    document.update(
        {
            "schema_version": SCHEMA_VERSION,
            "metric_unit": "distinct_documents",
            "retrieval_depth": 50,
            "chunk_stats": {
                "chunk_count": 13,
                "document_count": 13,
                "max_chunks_per_document": 1,
                "required_depth": 5,
            },
            "chunker": {
                "name": "heading",
                "version": "1",
                "params": {"max_chunk_chars": 2000},
                "tokenizer": None,
            },
            "ingestion_config": {
                "path": "config/ingestion.yaml",
                "sha256": "a" * 64,
            },
        }
    )
    document.update(over)
    return document


def run_cross(
    tmp_path: Path, base: dict[str, Any], cand: dict[str, Any], *, cross_index: bool
):  # noqa: ANN201
    return compare(
        read_result(write(tmp_path, "base.json", base), "BASE"),
        read_result(write(tmp_path, "cand.json", cand), "CANDIDATE"),
        cross_index=cross_index,
    )


def test_2_3_against_2_2_one_chunk_passes_without_cross_index(tmp_path: Path) -> None:
    legacy = doc22("hybrid", standalone=False, n=13)
    legacy["document_count"] = 13
    legacy["lexical_index"] = {**LEXICAL, "chunk_count": 13}
    modern = doc23(
        n=13,
        evaluation_suite_id=legacy["evaluation_suite_id"],
        evaluation_suite_version=legacy["evaluation_suite_version"],
        document_count=13,
        lexical_index=legacy["lexical_index"],
    )
    assert run_cross(tmp_path, legacy, modern, cross_index=False).passed


def test_2_3_multi_chunk_against_2_2_is_refused(tmp_path: Path) -> None:
    legacy = doc22("hybrid", standalone=False, n=13)
    legacy["lexical_index"] = {**LEXICAL, "chunk_count": 13}
    modern = doc23(
        chunk_stats={
            "chunk_count": 20,
            "document_count": 10,
            "max_chunks_per_document": 2,
            "required_depth": 9,
        }
    )
    message = refusal(tmp_path, legacy, modern)
    assert FORMAT_RULE_ADVICE in message


def test_cross_index_allows_lexical_digest_and_chunk_count(tmp_path: Path) -> None:
    base = doc23()
    cand = doc23()
    cand["lexical_index"] = {
        **LEXICAL,
        "source_chunk_digest": "e" * 64,
        "chunk_count": 99,
    }
    result = run_cross(tmp_path, base, cand, cross_index=True)
    assert result.passed


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("collection", "way2australia-idx-v2"),
        ("index_version", "idx-v2"),
    ],
)
def test_cross_index_allows_index_fields(
    tmp_path: Path, field: str, value: str
) -> None:
    base = doc23()
    cand = doc23(**{field: value})
    cand["chunker"] = {
        "name": "recursive",
        "version": "1",
        "params": {"target_tokens": 128},
        "tokenizer": "bge-m3@5617a9f",
    }
    cand["ingestion_config"] = {
        "path": "experiments/configs/chunking/recursive-128.yaml",
        "sha256": "b" * 64,
    }
    result = run_cross(tmp_path, base, cand, cross_index=True)
    assert result.passed
    text = "\n".join(result.lines)
    assert "cross-index: chunker:" in text


def test_cross_index_with_2_2_side_is_refused(tmp_path: Path) -> None:
    with pytest.raises(NotComparableError) as info:
        run_cross(tmp_path, doc22("hybrid"), doc23(), cross_index=True)
    assert "cross-index comparison requires result 2.3 on both sides" in str(info.value)


def test_2_3_chunker_difference_refused_without_cross_index(tmp_path: Path) -> None:
    message = refusal(
        tmp_path,
        doc23(),
        doc23(
            chunker={
                "name": "recursive",
                "version": "1",
                "params": {
                    "context_prefix": "title",
                    "overlap_tokens": 4,
                    "target_tokens": 32,
                },
                "tokenizer": "fake-tokenizer@0",
            }
        ),
    )
    assert "chunker changed heading 1 -> recursive 1" in message


def test_index_version_difference_refused_without_cross_index(tmp_path: Path) -> None:
    message = refusal(tmp_path, doc23(), doc23(index_version="idx-v2"))
    assert "index_version changed idx-v1 -> idx-v2" in message


def test_make_eval_compare_cross_index_prints_chunker(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base_path = write(tmp_path, "base.json", doc23())
    cand_path = write(
        tmp_path,
        "cand.json",
        doc23(
            index_version="idx-v2",
            chunker={
                "name": "recursive",
                "version": "1",
                "params": {"target_tokens": 128},
                "tokenizer": "bge-m3@5617a9f",
            },
        ),
    )
    code = cli.main(
        [
            "compare",
            "--base",
            str(base_path),
            "--candidate",
            str(cand_path),
            "--cross-index",
        ]
    )
    assert code == 0
    assert "cross-index: chunker:" in capsys.readouterr().out
