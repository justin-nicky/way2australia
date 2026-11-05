"""Result 2.5, eval-compare, eval-continuity and eval-retrieval with reranking
(Spec 011 R6, R7, R9, T3). Fakes and tmp_path only; nothing under experiments/results.
"""

from pathlib import Path
from typing import Any, NoReturn

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation import cli
from way2australia_rag.evaluation.compare import compare
from way2australia_rag.evaluation.continuity import (
    EXIT_OK,
    EXIT_REFUSED,
    compare_continuity,
)
from way2australia_rag.evaluation.errors import NotComparableError
from way2australia_rag.evaluation.results import read_result
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.applicability import ResolvedLote, check_applicable
from way2australia_rag.retrieval.errors import LanguageApplicabilityError
from way2australia_rag.retrieval.models import RerankRecord, RetrievalResult
from way2australia_rag.retrieval.strategy import load_retrieval_config

from .test_compare import doc23, write
from .test_retrieval_eval import RealStub, basic_suite, build, golden, run, suite_of

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)
DEPTH = 5


class Reranked:
    """Wraps a dense retriever: marks every result as reranked, or skipped."""

    strategy = "dense"

    def __init__(self, inner: Any, skip: dict[int, str] | None = None) -> None:
        self.inner = inner
        self.skip = skip or {}
        self.calls = 0

    def retrieve(self, query, access, top_k=5, *, lote=None) -> RetrievalResult:  # noqa: ANN001
        result = self.inner.retrieve(query, access, top_k, lote=lote)
        call, self.calls = self.calls, self.calls + 1
        reason = self.skip.get(call)
        if reason is not None:
            record = RerankRecord(
                model_id="m",
                revision="r" * 40,
                max_length=512,
                is_fake=True,
                device=None,
                depth=DEPTH,
                candidates=0,
                truncated_pairs=0,
                skipped_reason=reason,
                stage="query",
            )
            return result.model_copy(update={"rerank": record})
        hits = [
            h.model_copy(update={"fused_rank": len(result.hits) - h.rank + 1})
            for h in result.hits
        ]
        record = RerankRecord(
            model_id="m",
            revision="r" * 40,
            max_length=512,
            is_fake=True,
            device="fake",
            depth=DEPTH,
            candidates=len(hits),
            truncated_pairs=2 if call % 2 else 0,
        )
        return result.model_copy(
            update={
                "hits": hits,
                "rerank": record,
                "leg_latency_ms": {"rerank": 7.0},
            }
        )


def reranked_run(skip: dict[int, str] | None = None, **over: Any) -> dict[str, Any]:
    index, emb, retriever = build()
    reranker = FakeReranker()
    reranker.load()
    return run(
        index,
        emb,
        Reranked(retriever, skip),
        suite_of([golden(1, ["doc_1"]), golden(2, ["doc_2"])]),
        rerank_requested=True,
        reranker=reranker,
        rerank_depth=DEPTH,
        rerank_load_ms=900.0,
        **over,
    )


def test_result_2_5_keys_with_a_reranker() -> None:
    doc = reranked_run()
    assert doc["schema_version"] == "2.5"
    assert doc["rerank_requested"] is True
    assert doc["rerank"] == {
        "model_id": "fake-reranker",
        "revision": "fake",
        "max_length": 512,
        "is_fake": True,
        "device": "fake",
        "depth": DEPTH,
    }
    assert doc["rerank_skip_counts"] == {} and doc["warmup_rerank_skip"] is None
    assert set(doc["rerank_truncation"]) == {"pairs", "cases"}
    for row in doc["cases"]:
        assert row["served_path"] == "dense+rerank"
        assert set(row["relevant_fused_ranks"]) == set(row["relevant_document_ids"])
        assert row["rerank_top1_score"] is not None
    assert list(doc["latency_ms"]["by_served_path"]) == ["dense+rerank"]
    assert doc["latency_ms"]["legs"]["rerank"] == {"p50": 7.0, "p95": 7.0}
    assert doc["latency_ms"]["rerank_device"] == "fake"


def test_truncation_counts_cover_every_measured_query() -> None:
    doc = reranked_run()
    measured = doc["case_count"] + doc["unanswerable"]["n"]
    assert measured >= 2
    # calls: 0 warm-up, then odd call numbers carry 2 truncated pairs
    pairs = sum(r["rerank_truncated_pairs"] for r in doc["cases"])
    assert doc["rerank_truncation"]["pairs"] >= pairs > 0
    assert 1 <= doc["rerank_truncation"]["cases"] <= measured


def test_skip_counts_by_reason_and_stage_and_path() -> None:
    doc = reranked_run(skip={1: "model_unavailable"})
    assert doc["rerank_skip_counts"] == {"model_unavailable:query": 1}
    paths = {r["served_path"] for r in doc["cases"]}
    assert paths == {"dense+rerank_skipped:model_unavailable", "dense+rerank"}
    skipped = next(r for r in doc["cases"] if "skipped" in r["served_path"])
    assert skipped["rerank_top1_score"] is None
    assert skipped["relevant_fused_ranks"] is None
    assert doc["latency_ms"]["p50"] is None  # two paths


def test_warmup_skip_is_recorded_and_not_counted_as_measured() -> None:
    doc = reranked_run(skip={0: "model_timeout"})
    assert doc["warmup_rerank_skip"] == {"reason": "model_timeout", "stage": "query"}
    assert doc["rerank_skip_counts"] == {}


def test_warm_up_load_joins_warmup_and_never_the_percentiles() -> None:
    doc = reranked_run()
    latency = doc["latency_ms"]
    assert latency["warmup_rerank_load_ms"] == 900.0
    assert latency["warmup_ms"] >= 900.0
    assert latency["p95"] < 900.0


def test_unanswerable_rerank_distributions_are_informational() -> None:
    index, emb, retriever = build()
    from .test_retrieval_eval import suite_with_unanswerable

    reranker = FakeReranker()
    reranker.load()
    doc = run(
        index,
        emb,
        Reranked(retriever),
        suite_with_unanswerable(),
        rerank_requested=True,
        reranker=reranker,
        rerank_depth=DEPTH,
    )
    block = doc["unanswerable"]
    assert block["informational"] is True
    assert set(block["rerank_top1_distribution"]) == {
        "min",
        "p25",
        "median",
        "p75",
        "max",
    }
    assert block["golden_rerank_top1_distribution"]["min"] is not None
    assert all(c["rerank_top1_score"] is not None for c in block["cases"])


def test_reranking_off_has_null_identity_and_no_rerank_unanswerable_keys() -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    assert doc["rerank_requested"] is False and doc["rerank"] is None
    assert doc["rerank_skip_counts"] == {}
    assert doc["rerank_truncation"] == {"pairs": 0, "cases": 0}
    assert "rerank_top1_distribution" not in doc["unanswerable"]
    assert all(r["served_path"] == "dense" for r in doc["cases"])
    assert doc["latency_ms"]["warmup_rerank_load_ms"] is None


def test_a_reranker_without_the_flag_or_depth_is_refused() -> None:
    index, emb, retriever = build()
    with pytest.raises(Exception, match="rerank"):
        run(index, emb, retriever, basic_suite(), reranker=FakeReranker())
    with pytest.raises(Exception, match="depth"):
        run(index, emb, retriever, basic_suite(), rerank_requested=True)


# ---- reading -----------------------------------------------------------------


def with_rerank(depth: int = 20, revision: str = "a" * 40, **over: Any) -> dict:
    return doc23(
        n=5,
        rerank_requested=True,
        rerank={
            "model_id": "BAAI/bge-reranker-v2-m3",
            "revision": revision,
            "max_length": 512,
            "is_fake": False,
            "device": "mps",
            "depth": depth,
        },
        **over,
    )


def test_a_2_4_file_reads_as_not_reranked(tmp_path: Path) -> None:
    older = doc23(n=3, schema_version="2.4")
    del older["rerank_requested"], older["rerank"], older["rerank_skip_counts"]
    run_ = read_result(write(tmp_path, "o.json", older))
    assert run_.info["rerank"] is None and run_.info["rerank_skips"] == 0
    assert run_.info["lote"] is None


def test_a_malformed_2_5_rerank_block_is_refused(tmp_path: Path) -> None:
    bad = with_rerank()
    del bad["rerank"]["depth"]
    with pytest.raises(NotComparableError, match="malformed"):
        read_result(write(tmp_path, "b.json", bad))


# ---- eval-compare --------------------------------------------------------------


def go(tmp_path: Path, base: dict, cand: dict, **flags: bool):  # noqa: ANN201
    return compare(
        read_result(write(tmp_path, "base.json", base), "BASE"),
        read_result(write(tmp_path, "cand.json", cand), "CANDIDATE"),
        **flags,
    )


def test_rerank_off_versus_on_is_refused_and_names_the_flag(tmp_path: Path) -> None:
    with pytest.raises(NotComparableError) as info:
        go(tmp_path, doc23(n=5), with_rerank())
    message = str(info.value)
    assert "rerank changed off -> BAAI/bge-reranker-v2-m3@aaaaaaa depth 20" in message
    assert "--cross-rerank" in message


@pytest.mark.parametrize(
    "other", [with_rerank(depth=50), with_rerank(revision="b" * 40)]
)
def test_rerank_identity_differences_are_refused(tmp_path: Path, other: dict) -> None:
    with pytest.raises(NotComparableError, match="rerank changed"):
        go(tmp_path, with_rerank(), other)


def test_max_length_and_model_differences_are_refused(tmp_path: Path) -> None:
    for key, value in (("max_length", 256), ("model_id", "other/model")):
        other = with_rerank()
        other["rerank"][key] = value
        with pytest.raises(NotComparableError, match="rerank changed"):
            go(tmp_path, with_rerank(), other)


def test_identical_rerank_identity_compares(tmp_path: Path) -> None:
    assert go(tmp_path, with_rerank(), with_rerank()).passed


def test_cross_rerank_prints_lines_and_runs_the_gate(tmp_path: Path) -> None:
    result = go(tmp_path, doc23(n=5), with_rerank(), cross_rerank=True)
    assert result.passed
    assert any(x.startswith("cross-rerank: rerank: off -> ") for x in result.lines)


def test_cross_rerank_relaxes_only_rerank_fields(tmp_path: Path) -> None:
    with pytest.raises(NotComparableError, match="top_k changed"):
        go(tmp_path, doc23(n=5), with_rerank(top_k=3), cross_rerank=True)
    with pytest.raises(NotComparableError, match="index_version changed"):
        go(
            tmp_path,
            doc23(n=5),
            with_rerank(index_version="idx-v9"),
            cross_rerank=True,
        )


def test_flags_combine_and_each_relaxes_its_own_fields(tmp_path: Path) -> None:
    cand = with_rerank(index_version="idx-v2", collection="c2")
    cand["chunker"] = {**cand["chunker"], "name": "recursive"}
    with pytest.raises(NotComparableError, match="rerank changed"):
        go(tmp_path, doc23(n=5), cand, cross_index=True)
    with pytest.raises(NotComparableError, match="index_version changed"):
        go(tmp_path, doc23(n=5), cand, cross_rerank=True)
    result = go(tmp_path, doc23(n=5), cand, cross_index=True, cross_rerank=True)
    assert result.passed
    both = go(
        tmp_path,
        doc23(n=5),
        cand,
        cross_index=True,
        cross_tokenizer=True,
        cross_rerank=True,
    )
    assert both.passed


def test_a_2_4_reference_compares_with_a_2_5_arm_across_index(tmp_path: Path) -> None:
    older = doc23(n=5, schema_version="2.4")
    del older["rerank_requested"], older["rerank"], older["rerank_skip_counts"]
    cand = with_rerank()
    assert go(tmp_path, older, cand, cross_rerank=True).passed


@pytest.mark.parametrize("which", ["base", "cand"])
def test_a_skipped_reranked_run_is_refused_with_the_count(
    tmp_path: Path, which: str
) -> None:
    skipped = with_rerank(rerank_skip_counts={"model_unavailable:open": 4})
    base, cand = (
        (skipped, with_rerank()) if which == "base" else (with_rerank(), skipped)
    )
    with pytest.raises(NotComparableError, match="has 4 reranking-skipped"):
        go(tmp_path, base, cand)
    with pytest.raises(NotComparableError, match="has 4 reranking-skipped"):
        go(tmp_path, base, cand, cross_rerank=True)


def test_compare_cli_accepts_cross_rerank(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = write(tmp_path, "b.json", doc23(n=5))
    cand = write(tmp_path, "c.json", with_rerank())
    args = ["compare", "--base", str(base), "--candidate", str(cand)]
    assert cli.main(args) == 2
    assert cli.main([*args, "--cross-rerank"]) == 0
    assert "cross-rerank" in capsys.readouterr().out


# ---- eval-continuity (D-C) -----------------------------------------------------


def test_continuity_refuses_a_rerank_difference(tmp_path: Path) -> None:
    code, lines = compare_continuity(
        write(tmp_path, "b.json", doc23(n=3)), write(tmp_path, "c.json", with_rerank())
    )
    assert code == EXIT_REFUSED and "rerank changed off ->" in lines[0]


def test_continuity_passes_off_against_a_2_4_fixture(tmp_path: Path) -> None:
    older = doc23(n=3, schema_version="2.4")
    del older["rerank_requested"], older["rerank"], older["rerank_skip_counts"]
    code, _lines = compare_continuity(
        write(tmp_path, "b.json", older), write(tmp_path, "c.json", doc23(n=3))
    )
    assert code == EXIT_OK


def test_continuity_refuses_a_skipped_reranked_file(tmp_path: Path) -> None:
    skipped = with_rerank(rerank_skip_counts={"model_timeout:query": 2})
    code, lines = compare_continuity(
        write(tmp_path, "b.json", with_rerank()), write(tmp_path, "c.json", skipped)
    )
    assert code == EXIT_REFUSED and "2 reranking-skipped" in lines[0]


# ---- eval-retrieval CLI --------------------------------------------------------


def test_cli_refuses_a_fake_reranker_before_any_qdrant_contact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    text = (REPO_ROOT / "config/retrieval.yaml").read_text(encoding="utf-8")
    fake = tmp_path / "retrieval.yaml"
    fake.write_text(text.replace("provider: bge", "provider: fake"), encoding="utf-8")
    assert load_retrieval_config(fake).rerank.provider == "fake"

    def no_qdrant(_settings: object) -> NoReturn:
        raise AssertionError("Qdrant must not be contacted")

    code = cli.main(
        [
            "retrieval",
            "--repo-root",
            str(REPO_ROOT),
            "--rerank",
            "--retrieval-config",
            str(fake),
            "--output",
            str(tmp_path / "x.json"),
        ],
        client_factory=no_qdrant,
        embedder_factory=lambda _c, _p: RealStub(),
    )
    assert code == 2
    assert "fake reranker" in capsys.readouterr().err
    assert not (tmp_path / "x.json").exists()


def test_cli_rerank_flags_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        cli.main(["retrieval", "--rerank", "--no-rerank"])


# ---- configs and the applicability field read -----------------------------------


def test_depth50_config_differs_only_in_rerank_depth() -> None:
    committed = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    arm = load_retrieval_config(
        REPO_ROOT / "experiments/configs/rerank/retrieval-depth50.yaml"
    )
    assert arm.rerank.depth == 50
    assert committed.model_copy(
        update={"rerank": committed.rerank.model_copy(update={"depth": 50})}
    ) == arm.model_copy(
        update={
            "rerank": arm.rerank.model_copy(
                update={"enabled": committed.rerank.enabled}
            )
        }
    )


class _FieldSpy:
    """Records every attribute `check_applicable` reads."""

    def __init__(self, lote_languages: list[str]) -> None:
        object.__setattr__(self, "reads", set())
        object.__setattr__(
            self, "_values", {"lote_languages": lote_languages, "document_id": "d"}
        )

    def __getattr__(self, name: str) -> Any:
        self.reads.add(name)  # type: ignore[attr-defined]
        return self._values[name]  # type: ignore[attr-defined]


@pytest.mark.parametrize("languages", [["*"], ["ml"], ["en"], ["ml", "ta"]])
def test_check_applicable_reads_only_the_two_fields_the_stage_builds(
    languages: list[str],
) -> None:
    spy = _FieldSpy(languages)
    try:
        check_applicable(spy, ResolvedLote(code="ml"))  # type: ignore[arg-type]
    except LanguageApplicabilityError:
        pass
    assert spy.reads <= {"document_id", "lote_languages"}  # type: ignore[attr-defined]
