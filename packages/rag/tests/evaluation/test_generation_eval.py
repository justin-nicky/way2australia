"""Generation evaluation runner and CLI (Spec 012 R9, R10)."""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from conftest import LIVE_SUITE, REPO_ROOT
from generation.support import FakeRetriever, generation_config, hit, retrieval_result
from way2australia_core import AccessContext, Role
from way2australia_rag.evaluation import cli, generation_eval
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    DatasetType,
    GoldenCase,
    LoadedSuite,
    SuiteManifest,
    UnanswerableCase,
)
from way2australia_rag.evaluation.slices import SMALL_SAMPLE_THRESHOLD
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.generation.base import GeneratorOutput, GeneratorUsage
from way2australia_rag.generation.config import PricingConfig
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.errors import UnavailableReason
from way2australia_rag.generation.fake import FakeGenerator, FakeMode, default_fake_info
from way2australia_rag.generation.models import AnswerReason, AnswerStatus
from way2australia_rag.generation.prompts import PromptRegistry, RenderedPrompt
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import DEFAULT_TOP_K, Strategy
from way2australia_rag.retrieval.models import RetrievalResult, RetrievedChunk

from .test_cli import index_factory


def _fake_embedder(_c, _p):  # noqa: ANN001, ANN202
    return FakeEmbedder(64)


def _factory() -> object:
    return index_factory(FakeEmbedder(64))


def generation_run(factory, *extra: str) -> int:  # noqa: ANN001, ANN201
    return cli.main(
        ["generation", "--repo-root", str(REPO_ROOT), *extra],
        client_factory=factory,
        embedder_factory=_fake_embedder,
    )


pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)


def test_select_cases_limit_keeps_at_least_one_unanswerable() -> None:
    suite = load_suite(REPO_ROOT, LIVE_SUITE)
    goldens = len(suite.active(DatasetType.GOLDEN_ANSWERABLE))
    unans = len(suite.active(DatasetType.UNANSWERABLE_REFUSAL))
    assert goldens >= 2 and unans >= 1
    picked = generation_eval.select_cases(suite, limit=4, all_cases=False)
    assert picked.selection["unanswerable_selected"] >= 1
    assert (
        picked.selection["golden_selected"] + picked.selection["unanswerable_selected"]
        <= 4
    )


def test_no_tty_without_yes_raises() -> None:
    with pytest.raises(EvaluationConfigurationError, match="TTY"):
        generation_eval.require_confirmation(yes=False)


def test_min_threshold_exit_logic() -> None:
    problems = generation_eval.check_thresholds(
        {"answer_rate": 0.5, "refusal_rate": 0.5},
        min_answer_rate=0.9,
        min_refusal_rate=0.8,
    )
    assert len(problems) == 2


def test_fake_cli_writes_tmp_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "gen.json"
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "fake",
        "--allow-fake",
        "--limit",
        "3",
        "--output",
        str(out),
    )
    assert code == 0 and out.is_file()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["kind"] == "generation_evaluation"
    assert doc["schema_version"] == "1.1"
    assert doc["generator_is_fake"] is True
    assert len(doc["cases"]) == 3


def _config_copy(tmp_path: Path, **changes: object) -> Path:
    """Committed generation config with nulls put back (T6 filled them)."""
    import yaml

    raw = yaml.safe_load((REPO_ROOT / "config/generation.yaml").read_text())
    if "pricing" in changes:
        raw["pricing"] = changes["pricing"]
    if "anthropic_model_id" in changes:
        raw["anthropic"]["model_id"] = changes["anthropic_model_id"]
    path = tmp_path / "generation-copy.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


def test_bedrock_without_pricing_exits_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class StubBedrock:
        info = FakeGenerator().info
        calls = 0

        def close(self) -> None:
            return None

    def build(*_a, **_k):  # noqa: ANN202
        stub = StubBedrock()
        stub.info = stub.info.model_copy(
            update={"is_fake": False, "provider": "bedrock"}
        )
        return stub

    monkeypatch.setattr("way2australia_rag.evaluation.cli.build_generator", build)
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "bedrock",
        "--model-id",
        "anthropic.claude-test",
        "--limit",
        "2",
        "--yes",
        "--generation-config",
        str(
            _config_copy(
                tmp_path, pricing={"input_per_mtok": None, "output_per_mtok": None}
            )
        ),
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "pricing.input_per_mtok" in err


def test_recording_fake_has_zero_calls_before_yes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    built: list[FakeGenerator] = []

    def build(*_a, **_k):  # noqa: ANN202
        generator = FakeGenerator()
        generator.info = generator.info.model_copy(
            update={"is_fake": False, "provider": "bedrock"}
        )
        built.append(generator)
        return generator

    monkeypatch.setattr("way2australia_rag.evaluation.cli.build_generator", build)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "bedrock",
        "--model-id",
        "anthropic.claude-test",
        "--limit",
        "2",
        "--price-input",
        "1",
        "--price-output",
        "2",
    )
    assert code == 2
    assert built and built[0].calls == 0
    assert "estimated input tokens" in capsys.readouterr().out


_INSUFFICIENT = AnswerStatus.INSUFFICIENT_EVIDENCE
_CITATION_INVALID = AnswerReason.CITATION_INVALID
_OUTPUT_INVALID = AnswerReason.OUTPUT_INVALID
_MODEL_DECLINED = AnswerReason.MODEL_DECLINED
_EVIDENCE_ONLY = AnswerStatus.EVIDENCE_ONLY
_UNAVAILABLE = AnswerReason.GENERATOR_UNAVAILABLE

# One row per FakeMode. UNAVAILABLE is repeated once per UnavailableReason,
# including deadline. NON_ELIGIBLE has no status: the service lets it propagate.
_DEFECT_ROWS: list[
    tuple[
        FakeMode,
        UnavailableReason | None,
        AnswerStatus | None,
        AnswerReason | None,
        str | None,
    ]
] = [
    (FakeMode.OK, None, AnswerStatus.ANSWERED, None, None),
    (FakeMode.UNKNOWN_ID, None, _INSUFFICIENT, _CITATION_INVALID, "unknown_id"),
    (
        FakeMode.MARKER_MISMATCH,
        None,
        _INSUFFICIENT,
        _CITATION_INVALID,
        "marker_mismatch",
    ),
    (FakeMode.DUPLICATE_ID, None, _INSUFFICIENT, _CITATION_INVALID, "duplicate_id"),
    (FakeMode.EMPTY_CITATIONS, None, _INSUFFICIENT, _CITATION_INVALID, "no_citation"),
    (FakeMode.MODEL_URL, None, _INSUFFICIENT, _CITATION_INVALID, "model_url"),
    (FakeMode.DECLINE, None, _INSUFFICIENT, _MODEL_DECLINED, None),
    (FakeMode.REFUSAL, None, _INSUFFICIENT, _MODEL_DECLINED, None),
    (FakeMode.MALFORMED_JSON, None, _INSUFFICIENT, _OUTPUT_INVALID, "json"),
    (FakeMode.SCHEMA_MISMATCH, None, _INSUFFICIENT, _OUTPUT_INVALID, "schema"),
    (FakeMode.MAX_TOKENS, None, _INSUFFICIENT, _OUTPUT_INVALID, "max_tokens"),
    *[
        (FakeMode.UNAVAILABLE, reason, _EVIDENCE_ONLY, _UNAVAILABLE, reason.value)
        for reason in UnavailableReason
    ],
    (FakeMode.NON_ELIGIBLE, None, None, None, None),
]


def test_defect_matrix_lists_every_mode_and_outage_reason() -> None:
    """A shorter table (round 2 covered six rows) must not satisfy this gate."""
    modes = {row[0] for row in _DEFECT_ROWS}
    unavailable = {row[1] for row in _DEFECT_ROWS if row[0] is FakeMode.UNAVAILABLE}
    declined = {row[0] for row in _DEFECT_ROWS if row[3] is _MODEL_DECLINED}
    assert modes == set(FakeMode)
    assert unavailable == set(UnavailableReason)
    assert declined == {FakeMode.DECLINE, FakeMode.REFUSAL}
    assert len(_DEFECT_ROWS) == len(FakeMode) + len(UnavailableReason) - 1
    assert len(_DEFECT_ROWS) != len(FakeMode)
    assert len(_DEFECT_ROWS) != 6


@pytest.mark.parametrize(
    ("mode", "unavailable", "status", "reason", "sub_reason"),
    _DEFECT_ROWS,
    ids=[
        f"{mode.value}-{unavailable.value}" if unavailable is not None else mode.value
        for mode, unavailable, *_rest in _DEFECT_ROWS
    ],
)
def test_fake_defect_status_reason_subreason(
    mode: FakeMode,
    unavailable: UnavailableReason | None,
    status: AnswerStatus | None,
    reason: AnswerReason | None,
    sub_reason: str | None,
) -> None:
    config = generation_config()
    prompt = PromptRegistry(REPO_ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    generator = FakeGenerator(
        mode,
        unavailable=unavailable or UnavailableReason.CONNECTION,
    )
    service = AnswerService(
        FakeRetriever([hit(1, "Coaching is optional.")]),
        ContextBuilder(config.context),
        prompt,
        generator,
        config,
    )
    if mode is FakeMode.NON_ELIGIBLE:
        with pytest.raises(RuntimeError, match="non-eligible"):
            service.answer("Is coaching compulsory?", access)
        return
    response = service.answer("Is coaching compulsory?", access)
    assert (response.status, response.reason, response.sub_reason) == (
        status,
        reason,
        sub_reason,
    )
    if reason is _MODEL_DECLINED:
        assert response.reason is _MODEL_DECLINED
        assert response.sub_reason is None
        assert response.reason is not AnswerReason.NO_EVIDENCE
    if mode is FakeMode.UNAVAILABLE:
        assert unavailable is not None
        wrong = (
            "deadline" if unavailable is UnavailableReason.CONNECTION else "connection"
        )
        assert response.sub_reason == unavailable.value
        assert response.sub_reason != wrong


def test_every_active_unanswerable_refuses_on_fake_decline() -> None:
    suite = load_suite(REPO_ROOT, LIVE_SUITE)
    unanswerables = generation_eval.active_unanswerable_cases(suite)
    assert unanswerables
    config = generation_config()
    prompt = PromptRegistry(REPO_ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    service = AnswerService(
        FakeRetriever([hit(1, "noise")]),
        ContextBuilder(config.context),
        prompt,
        FakeGenerator(FakeMode.DECLINE),
        config,
    )
    for case in unanswerables:
        response = service.answer(case.query, access)
        assert response.status == AnswerStatus.INSUFFICIENT_EVIDENCE
        assert response.reason is AnswerReason.MODEL_DECLINED
        assert response.sub_reason is None
        assert response.reason is not AnswerReason.NO_EVIDENCE


def test_unanswerable_with_no_evidence_refuses_before_generator() -> None:
    config = generation_config()
    prompt = PromptRegistry(REPO_ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    generator = FakeGenerator(FakeMode.DECLINE)
    service = AnswerService(
        FakeRetriever([]),
        ContextBuilder(config.context),
        prompt,
        generator,
        config,
    )
    case = UnanswerableCase(
        case_id="u",
        case_version=1,
        status="active",
        query="secret",
        answerable=False,
        expected_behavior="refuse",
        query_language="en",
    )
    response = service.answer(case.query, access)
    assert response.status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert response.reason == AnswerReason.NO_EVIDENCE
    assert generator.calls == 0


def test_cli_min_thresholds_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "gen.json"
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "fake",
        "--allow-fake",
        "--limit",
        "3",
        "--output",
        str(out),
        "--min-answer-rate",
        "1.1",
    )
    assert code == 1
    assert "GATE" in capsys.readouterr().err


def test_cli_all_and_price_overrides_recorded(tmp_path: Path) -> None:
    out = tmp_path / "all.json"
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "fake",
        "--allow-fake",
        "--all",
        "--output",
        str(out),
        "--price-input",
        "3.5",
        "--price-output",
        "4.5",
    )
    assert code == 0 and out.is_file()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["case_selection"]["mode"] == "all"
    assert doc["pricing_applied"]["input_source"] == "cli"
    assert doc["pricing_applied"]["input_per_mtok"] == 3.5
    assert doc["pricing_applied"]["output_per_mtok"] == 4.5


def test_fake_cli_default_output_under_experiments_tmp(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "fake",
        "--allow-fake",
        "--limit",
        "2",
    )
    assert code == 0
    assert "result: experiments/results/tmp/" in capsys.readouterr().out


def test_bedrock_yes_skips_tty_confirmation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class StubBedrock(FakeGenerator):
        def close(self) -> None:
            return None

    def build(*_a, **_k):  # noqa: ANN202
        generator = StubBedrock()
        generator.info = generator.info.model_copy(
            update={"is_fake": False, "provider": "bedrock", "model_id": "m"}
        )
        return generator

    monkeypatch.setattr("way2australia_rag.evaluation.cli.build_generator", build)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "bedrock",
        "--model-id",
        "anthropic.claude-test",
        "--limit",
        "2",
        "--yes",
        "--price-input",
        "1",
        "--price-output",
        "2",
        "--output",
        str(tmp_path / "bedrock.json"),
    )
    assert code == 0
    assert "estimated input tokens" in capsys.readouterr().out
    doc = json.loads((tmp_path / "bedrock.json").read_text(encoding="utf-8"))
    assert doc["estimated_cost_usd"] is not None


_INPUT_TOKENS = 100
_OUTPUT_TOKENS = 40
_PRICE_IN = 3.0
_PRICE_OUT = 15.0
# Answer paths that return GeneratorOutput (not an exception, not the pre-gate):
# 3 answered + 5 citation_invalid + 1 model decline.
_CASES_WITH_USAGE = 9
_BOOST_TICKS = 10
_ML_QUERY = "ml-part"


class _StepClock:
    """Integer seconds. Each step is 1, so millisecond deltas stay exact."""

    def __init__(self) -> None:
        self._n = 0

    def __call__(self) -> float:
        self._n += 1
        return float(self._n)


@dataclass(frozen=True)
class _Plan:
    mode: FakeMode
    unavailable: UnavailableReason | None = None
    answer: str | None = None
    citations: tuple[str, ...] = ()


class _ScriptedGenerator:
    """One mode per question. OK answers are fixed so facts and citations are known."""

    def __init__(self, plan: dict[str, _Plan], clock: _StepClock) -> None:
        self._plan = plan
        self._clock = clock
        self.info = default_fake_info()
        self.calls = 0

    def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
        self.calls += 1
        query = _question_text(prompt.user)
        spec = self._plan[query]
        if query == _ML_QUERY:
            for _ in range(_BOOST_TICKS):
                self._clock()
        if spec.answer is not None:
            return GeneratorOutput(
                answerable=True,
                answer=spec.answer,
                citations=list(spec.citations),
                usage=_fixed_usage(),
                stop_reason="end_turn",
            )
        fake = FakeGenerator(
            spec.mode,
            unavailable=spec.unavailable or UnavailableReason.CONNECTION,
        )
        output = fake.generate(prompt)
        return output.model_copy(update={"usage": _fixed_usage()})

    def close(self) -> None:
        return None


class _QueryRetriever:
    strategy = Strategy.HYBRID

    def __init__(
        self, hits: list[RetrievedChunk], empty_queries: frozenset[str]
    ) -> None:
        self._hits = hits
        self._empty = empty_queries

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
        *,
        lote: ResolvedLote | None = None,
    ) -> RetrievalResult:
        del access, top_k, lote
        hits = [] if query_text in self._empty else self._hits
        return retrieval_result(hits)


def _fixed_usage() -> GeneratorUsage:
    return GeneratorUsage(
        input_tokens=_INPUT_TOKENS,
        output_tokens=_OUTPUT_TOKENS,
        attempts=1,
    )


def _question_text(user: str) -> str:
    start = user.rindex("<question>") + len("<question>")
    return user[start : user.rindex("</question>")]


def _golden(
    case_id: str,
    query: str,
    *,
    language: str,
    relevant: list[str],
    facts: list[str],
) -> GoldenCase:
    return GoldenCase(
        case_id=case_id,
        case_version=1,
        status="active",
        query=query,
        answerable=True,
        relevant_document_ids=relevant,
        expected_facts=facts,
        query_language=language,
        category="crafted",
    )


def _unanswerable(case_id: str, query: str) -> UnanswerableCase:
    return UnanswerableCase(
        case_id=case_id,
        case_version=1,
        status="active",
        query=query,
        answerable=False,
        expected_behavior="refuse",
        query_language="en",
    )


def _exact(actual: object, expected: object, wrong: object) -> None:
    """The expected value, and a plausible wrong one that must not match."""
    assert actual == expected
    assert actual != wrong


def test_crafted_suite_metrics_are_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hand-counted mini-suite: every status and sub-reason, exact aggregates.

    Clock: each ``perf_counter`` call advances 1.000 s, so a stage spanning
    N calls is N × 1000 ms. A case with evidence takes six service calls
    (retrieval 1, context 1, generation 1, total 5). ``no_evidence`` returns
    before generation (four calls: total 3, generation 0). ``ml-part`` ticks
    the same clock ten extra times inside ``generate``, so its generation
    span is 11 and its total span is 15.

    Usage is 100/40 on the nine outputs that return (3 answered, 5 citation
    failures, 1 decline). Exceptions and the pre-gate contribute no usage.
    Cost is (900 × 3 + 360 × 15) / 1_000_000 = 0.0081.
    """
    hits = [
        hit(1, "Coaching is optional.", document_id="doc_1"),
        hit(2, "The fee is 100.", document_id="doc_2"),
    ]
    goldens = [
        _golden(
            "g_en",
            "en-full",
            language="en",
            relevant=["doc_1"],
            facts=["alpha fact"],
        ),
        _golden(
            "g_en_part",
            "en-part",
            language="en",
            relevant=["doc_1", "doc_missing"],
            facts=["alpha fact", "beta fact"],
        ),
        _golden(
            "g_unknown", "cite-unknown", language="en", relevant=["doc_1"], facts=[]
        ),
        _golden("g_marker", "cite-marker", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_dup", "cite-dup", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_empty", "cite-empty", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_url", "cite-url", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_json", "out-json", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_schema", "out-schema", language="en", relevant=["doc_1"], facts=[]),
        _golden("g_max", "out-maxtok", language="en", relevant=["doc_1"], facts=[]),
        _golden(
            "g_ml",
            _ML_QUERY,
            language="ml",
            relevant=["doc_1", "doc_2"],
            facts=["നിരക്ക്", "ഇല്ലാത്തത്"],
        ),
    ]
    unanswerables = [
        _unanswerable("u_decline", "decline-please"),
        _unanswerable("u_refusal", "refusal-please"),
        _unanswerable("u_none", "no-evidence"),
        _unanswerable("u_connection", "outage-connection"),
        _unanswerable("u_timeout", "outage-timeout"),
        _unanswerable("u_throttled", "outage-throttled"),
        _unanswerable("u_server", "outage-server"),
        _unanswerable("u_deadline", "outage-deadline"),
    ]
    plan = {
        "en-full": _Plan(
            FakeMode.OK,
            answer="alpha fact is stated [S1]",
            citations=("S1",),
        ),
        "en-part": _Plan(
            FakeMode.OK,
            answer="alpha fact only [S1][S2]",
            citations=("S1", "S2"),
        ),
        "cite-unknown": _Plan(FakeMode.UNKNOWN_ID),
        "cite-marker": _Plan(FakeMode.MARKER_MISMATCH),
        "cite-dup": _Plan(FakeMode.DUPLICATE_ID),
        "cite-empty": _Plan(FakeMode.EMPTY_CITATIONS),
        "cite-url": _Plan(FakeMode.MODEL_URL),
        "out-json": _Plan(FakeMode.MALFORMED_JSON),
        "out-schema": _Plan(FakeMode.SCHEMA_MISMATCH),
        "out-maxtok": _Plan(FakeMode.MAX_TOKENS),
        _ML_QUERY: _Plan(
            FakeMode.OK,
            answer="നിരക്ക് [S1]",
            citations=("S1",),
        ),
        "decline-please": _Plan(FakeMode.DECLINE),
        "refusal-please": _Plan(FakeMode.REFUSAL),
        "outage-connection": _Plan(FakeMode.UNAVAILABLE, UnavailableReason.CONNECTION),
        "outage-timeout": _Plan(FakeMode.UNAVAILABLE, UnavailableReason.TIMEOUT),
        "outage-throttled": _Plan(FakeMode.UNAVAILABLE, UnavailableReason.THROTTLED),
        "outage-server": _Plan(FakeMode.UNAVAILABLE, UnavailableReason.SERVER_ERROR),
        "outage-deadline": _Plan(FakeMode.UNAVAILABLE, UnavailableReason.DEADLINE),
    }
    suite = LoadedSuite(
        manifest=SuiteManifest(
            evaluation_suite_id="crafted-012",
            version=1,
            status="active",
            datasets=[],
        ),
        goldens=goldens,
        unanswerable=unanswerables,
    )
    selected = generation_eval.SelectedCases(
        tuple(goldens),
        tuple(unanswerables),
        {
            "mode": "all",
            "limit": None,
            "golden_selected": len(goldens),
            "unanswerable_selected": len(unanswerables),
            "golden_total": len(goldens),
            "unanswerable_total": len(unanswerables),
        },
    )
    config = generation_config().model_copy(
        update={
            "pricing": PricingConfig(
                input_per_mtok=_PRICE_IN,
                output_per_mtok=_PRICE_OUT,
            )
        }
    )
    prompt = PromptRegistry(REPO_ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    clock = _StepClock()
    monkeypatch.setattr(
        "way2australia_rag.generation.service.time.perf_counter",
        clock,
    )
    generator = _ScriptedGenerator(plan, clock)
    retriever = _QueryRetriever(hits, frozenset({"no-evidence"}))
    service = AnswerService(
        retriever,
        ContextBuilder(config.context),
        prompt,
        generator,
        config,
    )
    doc = generation_eval.run_generation_evaluation(
        retriever=retriever,
        generator=generator,
        service=service,
        suite=suite,
        selected=selected,
        access=access,
        release_id="rel-crafted",
        top_k=DEFAULT_TOP_K,
        lote=None,
        config=config,
        prompt=prompt,
        generator_info=generator.info,
        pricing_applied={
            "input_per_mtok": _PRICE_IN,
            "output_per_mtok": _PRICE_OUT,
            "input_source": "test",
        },
        retrieval_identity={"strategy": "hybrid"},
        ingestion_config={"chunker": "test"},
        repo_root=REPO_ROOT,
        min_answer_rate=None,
        min_refusal_rate=None,
        estimated_cost_usd=0.5,
    )
    shown = tmp_path / "generation-evaluation-crafted.json"
    shown.write_text(json.dumps(doc), encoding="utf-8")
    assert shown.is_relative_to(tmp_path)
    reloaded = json.loads(shown.read_text(encoding="utf-8"))

    n_cases = 19
    _exact(generator.calls, n_cases - 1, n_cases)
    _exact(doc["metrics"]["cases_run"], n_cases, n_cases - 1)
    _exact(doc["metrics"]["golden_count"], 11, 10)
    _exact(doc["metrics"]["unanswerable_count"], 8, 7)
    _exact(doc["metrics"]["answered_count"], 3, 8)
    _exact(doc["metrics"]["answer_rate"], 3 / 11, 8 / 11)
    _exact(doc["metrics"]["refusal_count"], 3, 8)
    _exact(doc["metrics"]["refusal_rate"], 3 / 8, 1.0)
    _exact(doc["metrics"]["refusal_rate"], 3 / 8, 2 / 8)
    _exact(doc["metrics"]["evidence_only_count"], 5, 0)
    _exact(doc["metrics"]["output_invalid_count"], 3, 0)
    _exact(doc["metrics"]["citation_invalid_count"], 5, 4)
    _exact(doc["metrics"]["citation_invalid_rate"], 5 / n_cases, 5 / 11)
    _exact(doc["metrics"]["generator_unavailable_count"], 5, 4)
    assert doc["metrics"]["answer_rate_small_sample"] is False
    assert doc["metrics"]["refusal_rate_small_sample"] is True
    assert doc["metrics"]["cases_run_small_sample"] is False
    assert doc["metrics"]["answer_rate_small_sample"] is not True
    assert doc["small_sample_threshold"] == SMALL_SAMPLE_THRESHOLD

    citation_ids = {
        "duplicate_id": ["g_dup"],
        "marker_mismatch": ["g_marker"],
        "model_url": ["g_url"],
        "no_citation": ["g_empty"],
        "unknown_id": ["g_unknown"],
    }
    assert doc["citation_invalid"] == {
        "count": 5,
        "by_sub_reason": {key: 1 for key in citation_ids},
        "case_ids_by_sub_reason": citation_ids,
        "rate": 5 / n_cases,
        "small_sample": False,
    }
    assert doc["citation_invalid"]["count"] != 6
    assert doc["citation_invalid"]["case_ids_by_sub_reason"]["unknown_id"] != ["g_url"]

    outage_ids = {
        "connection": ["u_connection"],
        "deadline": ["u_deadline"],
        "server_error": ["u_server"],
        "throttled": ["u_throttled"],
        "timeout": ["u_timeout"],
    }
    assert doc["generator_unavailable"] == {
        "count": 5,
        "by_sub_reason": {key: 1 for key in outage_ids},
        "case_ids_by_sub_reason": outage_ids,
    }
    assert doc["generator_unavailable"]["case_ids_by_sub_reason"]["deadline"] != [
        "u_timeout"
    ]
    assert "deadline" in doc["generator_unavailable"]["by_sub_reason"]

    by_id = {row["case_id"]: row for row in doc["cases"]}
    assert len(by_id) == n_cases
    assert (by_id["g_en"]["citation_precision"], by_id["g_en"]["citation_recall"]) == (
        1.0,
        1.0,
    )
    assert (
        by_id["g_en_part"]["citation_precision"],
        by_id["g_en_part"]["citation_recall"],
    ) == (0.5, 0.5)
    assert (by_id["g_ml"]["citation_precision"], by_id["g_ml"]["citation_recall"]) == (
        1.0,
        0.5,
    )
    assert by_id["g_unknown"]["citation_precision"] is None
    assert by_id["g_unknown"]["citation_recall"] is None
    _exact(doc["citation_precision_mean"], 0.8333, 1.0)
    _exact(doc["citation_recall_mean"], 0.6667, 1.0)
    assert (
        by_id["g_en"]["expected_facts_matched"],
        by_id["g_en"]["expected_facts_total"],
    ) == (
        1,
        1,
    )
    assert (
        by_id["g_en_part"]["expected_facts_matched"],
        by_id["g_en_part"]["expected_facts_total"],
    ) == (1, 2)
    assert (
        by_id["g_ml"]["expected_facts_matched"],
        by_id["g_ml"]["expected_facts_total"],
    ) == (
        1,
        2,
    )
    assert doc["expected_facts_coverage"] == {
        "overall": 0.6,
        "matched": 3,
        "total": 5,
        "informational": True,
        "by_query_language": {
            "en": {
                "matched": 2,
                "total": 3,
                "coverage": 2 / 3,
                "n": 10,
                "small_sample": False,
            },
            "ml": {
                "matched": 1,
                "total": 2,
                "coverage": 0.5,
                "n": 1,
                "small_sample": True,
            },
        },
    }
    assert doc["expected_facts_coverage"]["informational"] is not False
    assert doc["expected_facts_coverage"]["by_query_language"]["en"]["matched"] != 3
    assert (
        doc["expected_facts_coverage"]["by_query_language"]["ml"]["small_sample"]
        is not False
    )

    output_map = {
        row["sub_reason"]: row["case_id"]
        for row in doc["cases"]
        if row["reason"] == AnswerReason.OUTPUT_INVALID.value
    }
    assert output_map == {
        "json": "g_json",
        "schema": "g_schema",
        "max_tokens": "g_max",
    }
    assert output_map["max_tokens"] != "g_json"
    assert by_id["u_decline"]["reason"] == AnswerReason.MODEL_DECLINED.value
    assert by_id["u_refusal"]["reason"] == AnswerReason.MODEL_DECLINED.value
    assert by_id["u_refusal"]["sub_reason"] is None
    assert by_id["u_none"]["status"] == AnswerStatus.INSUFFICIENT_EVIDENCE.value
    assert by_id["u_none"]["reason"] == AnswerReason.NO_EVIDENCE.value
    assert by_id["u_deadline"]["status"] == AnswerStatus.EVIDENCE_ONLY.value
    assert by_id["u_deadline"]["sub_reason"] == "deadline"
    assert by_id["g_en"]["first_request"] is True
    assert by_id["g_ml"]["first_request"] is False
    assert {row["status"] for row in doc["cases"]} == {
        AnswerStatus.ANSWERED.value,
        AnswerStatus.INSUFFICIENT_EVIDENCE.value,
        AnswerStatus.EVIDENCE_ONLY.value,
    }

    assert doc["answer_script_mix"] == {"latin": 2, "latin+malayalam": 1, "none": 16}
    assert doc["answer_script_mix"] != {"latin": 2, "malayalam": 1, "none": 16}
    assert doc["answer_script_mix"]["none"] != n_cases

    usual = {
        "retrieval_ms": 1000.0,
        "context_ms": 1000.0,
        "generation_ms": 1000.0,
        "total_ms": 5000.0,
    }
    boosted = {
        "retrieval_ms": 1000.0,
        "context_ms": 1000.0,
        "generation_ms": 11000.0,
        "total_ms": 15000.0,
    }
    pre_gate = {
        "retrieval_ms": 1000.0,
        "context_ms": 1000.0,
        "generation_ms": 0.0,
        "total_ms": 3000.0,
    }
    assert by_id["g_en"]["latency_ms"] == usual
    assert by_id["u_deadline"]["latency_ms"] == usual
    assert by_id["g_ml"]["latency_ms"] == boosted
    assert by_id["u_none"]["latency_ms"] == pre_gate
    assert by_id["u_none"]["latency_ms"] != usual
    assert doc["latency_ms"] == {
        "retrieval_ms": {"p50": 1000.0, "p95": 1000.0, "n": n_cases},
        "context_ms": {"p50": 1000.0, "p95": 1000.0, "n": n_cases},
        "generation_ms": {"p50": 1000.0, "p95": 11000.0, "n": n_cases},
        "total_ms": {"p50": 5000.0, "p95": 15000.0, "n": n_cases},
    }
    assert doc["latency_ms"]["total_ms"]["p95"] != 5000.0
    assert doc["latency_ms"]["generation_ms"]["n"] != n_cases - 1

    input_total = _INPUT_TOKENS * _CASES_WITH_USAGE
    output_total = _OUTPUT_TOKENS * _CASES_WITH_USAGE
    assert doc["tokens"] == {
        "input_total": input_total,
        "output_total": output_total,
        "input_mean": float(_INPUT_TOKENS),
        "output_mean": float(_OUTPUT_TOKENS),
        "cases_with_usage": _CASES_WITH_USAGE,
    }
    assert doc["tokens"]["cases_with_usage"] != n_cases
    assert doc["tokens"]["input_total"] != 0
    _exact(doc["actual_cost_usd"], 0.0081, None)
    _exact(doc["estimated_cost_usd"], 0.5, None)
    assert doc["status_counts_by_kind"] == {
        "golden_answerable": {"answered": 3, "insufficient_evidence": 8},
        "unanswerable_refusal": {"evidence_only": 5, "insufficient_evidence": 3},
    }

    assert reloaded["metrics"]["answer_rate"] == 3 / 11
    assert reloaded["metrics"]["refusal_rate"] == 3 / 8
    assert reloaded["citation_invalid"]["case_ids_by_sub_reason"] == citation_ids
    assert reloaded["generator_unavailable"]["case_ids_by_sub_reason"] == outage_ids
    assert reloaded["actual_cost_usd"] == 0.0081
    assert reloaded["latency_ms"]["total_ms"]["p95"] == 15000.0


def test_run_generation_evaluation_metrics_shape(tmp_path: Path) -> None:
    out = tmp_path / "metrics.json"
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "fake",
        "--allow-fake",
        "--limit",
        "6",
        "--output",
        str(out),
    )
    assert code == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    metrics = doc["metrics"]
    assert "answer_rate" in metrics and "refusal_rate" in metrics
    assert "answer_rate_small_sample" in metrics
    assert "refusal_rate_small_sample" in metrics
    assert metrics["answer_rate_small_sample"] == (
        metrics["golden_count"] < SMALL_SAMPLE_THRESHOLD
    )
    assert "citation_invalid_rate" in metrics
    assert "rate" in doc["citation_invalid"]
    assert "small_sample" in doc["citation_invalid"]
    assert doc["expected_facts_coverage"]["informational"] is True
    assert "by_query_language" in doc["expected_facts_coverage"]
    assert "answer_script_mix" in doc
    assert "latency_ms" in doc and "tokens" in doc
    assert doc["estimated_cost_usd"] is None
    case = doc["cases"][0]
    assert {"latency_ms", "citation_precision", "answer_script_mix"} <= set(case)


def test_prompt_chars_uses_system_text_when_no_blocks() -> None:
    config = generation_config()
    prompt = PromptRegistry(REPO_ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    case = UnanswerableCase(
        case_id="empty",
        case_version=1,
        status="active",
        query="nothing here",
        answerable=False,
        expected_behavior="refuse",
        query_language="en",
    )
    chars = generation_eval._prompt_chars_for_case(
        FakeRetriever([]),
        ContextBuilder(config.context),
        prompt,
        case,
        access,
        DEFAULT_TOP_K,
        None,
    )
    assert chars == len(prompt.system_text)


def test_result_1_1_records_response_models(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class Named(FakeGenerator):
        def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
            return (
                super()
                .generate(prompt)
                .model_copy(update={"response_model": "claude-test-1"})
            )

    monkeypatch.setattr(
        "way2australia_rag.evaluation.cli.build_generator", lambda *_a, **_k: Named()
    )
    out = tmp_path / "named.json"
    code = generation_run(
        _factory(),
        "--embedder", "fake", "--strategy", "dense", "--no-rerank",
        "--generator", "fake", "--allow-fake", "--limit", "3",
        "--output", str(out),
    )  # fmt: skip
    assert code == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema_version"] == "1.1"
    assert doc["response_models"] == ["claude-test-1"]
    called = [c for c in doc["cases"] if c["response_model"]]
    assert called and all(c["response_model"] == "claude-test-1" for c in called)
    assert "response models: claude-test-1" in capsys.readouterr().out


def test_fake_result_has_no_response_models(tmp_path: Path) -> None:
    out = tmp_path / "fake.json"
    assert (
        generation_run(
            _factory(),
            "--embedder",
            "fake",
            "--strategy",
            "dense",
            "--no-rerank",
            "--generator",
            "fake",
            "--allow-fake",
            "--limit",
            "2",
            "--output",
            str(out),
        )  # fmt: skip
        == 0
    )
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["response_models"] == []
    assert all("response_model" in c for c in doc["cases"])


def test_cli_anthropic_without_a_model_id_exits_two(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """`--generator anthropic` is accepted; with no model ID the run stops with
    exit 2 naming `--model-id`, before any generator call."""
    calls: list[object] = []
    monkeypatch.setattr(
        "way2australia_rag.generation.anthropic_api.AnthropicGenerator.generate",
        lambda *a, **k: calls.append(a),
    )
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--generator",
        "anthropic",
        "--limit",
        "1",
        "--output",
        str(tmp_path / "a.json"),
        "--generation-config",
        str(_config_copy(tmp_path, anthropic_model_id=None)),
    )
    assert code == 2
    assert "--model-id" in capsys.readouterr().err
    assert calls == []


def test_cli_without_a_generator_flag_builds_the_configured_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """T6: no `--generator`, no price flags: the file's default and pricing apply
    (stub SDK; the run stops at the confirmation, so nothing is generated)."""
    import sys
    from types import SimpleNamespace

    import yaml
    from way2australia_rag.generation.build import build_generator as real_build

    raw = yaml.safe_load((REPO_ROOT / "config/generation.yaml").read_text())
    default = raw["default_generator"]
    assert default is not None
    if default != "anthropic":
        pytest.skip("the committed default is not anthropic; the stub covers anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_CUSTOM_HEADERS", raising=False)
    stub = SimpleNamespace(close=lambda: None)
    monkeypatch.setitem(
        sys.modules, "anthropic", SimpleNamespace(Anthropic=lambda **_: stub)
    )
    built: list[object] = []

    def spy(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        generator = real_build(*args, **kwargs)
        built.append(generator)
        return generator

    monkeypatch.setattr("way2australia_rag.evaluation.cli.build_generator", spy)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    code = generation_run(
        _factory(),
        "--embedder",
        "fake",
        "--strategy",
        "dense",
        "--no-rerank",
        "--limit",
        "2",
        "--output",
        str(tmp_path / "a.json"),
    )
    assert code == 2  # no --yes and no terminal: stops at the confirmation
    assert len(built) == 1
    info = built[0].info  # type: ignore[attr-defined]
    assert info.provider == default and info.model_id == raw[default]["model_id"]
    assert info.is_fake is False
    assert "estimated input tokens" in capsys.readouterr().out
