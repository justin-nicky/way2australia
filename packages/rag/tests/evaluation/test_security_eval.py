"""Authorization hard gate tests (Spec 006 R8, R13).

Full in-memory gate on the real seed corpus and suite: fake embedder, no Docker,
no model. Nothing is written outside tmp_path.
"""

import asyncio
import dataclasses
import json
import re
import shutil
import sqlite3
import uuid
from pathlib import Path
from time import perf_counter
from typing import Any

import pytest
from conftest import LIVE_SUITE, REPO_ROOT, live_suite_rows
from qdrant_client import QdrantClient, models
from way2australia_core import AccessContext, Role
from way2australia_rag.evaluation import cli, security_eval
from way2australia_rag.evaluation.errors import (
    EvaluationConfigurationError,
    EvaluationHarnessError,
)
from way2australia_rag.evaluation.models import (
    GoldenCase,
    LoadedSuite,
    SecurityCase,
    SuiteManifest,
)
from way2australia_rag.evaluation.security_corpus import (
    SECURITY_FIXTURE_FILES,
    build_security_repository,
)
from way2australia_rag.evaluation.security_eval import (
    ALL_PATHS,
    DEFERRED_OWNERS,
    FORBIDDEN_VARIANTS,
    PATHS,
    RERANK_PATHS,
    RETRIEVAL_SIDE_ATTACK_TYPES,
    SecurityQuery,
    run_security_evaluation,
    security_document,
    security_gate_chunkers,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    INJECTION_TEXT,
    NON_APPLICABLE_DOCUMENT_ID,
    NON_APPLICABLE_LOTE_CODE,
    SecurityIndex,
    build_security_index,
    delete_security_index,
    is_non_applicable_document,
    require_non_applicable_lote_inactive,
)
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.ingestion.recursive import RecursiveChunker
from way2australia_rag.ingestion.structure import StructureChunker
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.lexical.store import LexicalRow
from way2australia_rag.lexical.tokenizer import query_terms
from way2australia_rag.repositories import (
    DocumentQuery,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    build_sql_access_clause,
    resolve_access,
)
from way2australia_rag.retrieval.applicability import ResolvedLote, resolve_lote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import match_expression
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.strategy import load_retrieval_config
from way2australia_rag.retrieval.text import safe_text

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

SUITE = LIVE_SUITE
TENANT = "way2australia"
RETRIEVAL_CONFIG = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
EVAL_SRC = REPO_ROOT / "packages/rag/src/way2australia_rag/evaluation"
_REGISTRY_LOTE = active_lote_codes(REPO_ROOT)
_RESOLVED_LOTE = resolve_lote(_REGISTRY_LOTE[0], _REGISTRY_LOTE)
assert _RESOLVED_LOTE is not None
ACTIVE_LOTE: ResolvedLote = _RESOLVED_LOTE


_WORK: dict[str, Path] = {}


@pytest.fixture(autouse=True)
def _lexical_work_dir(tmp_path: Path) -> None:
    """Every `build` call writes its lexical file under the test's tmp_path."""
    _WORK["dir"] = tmp_path / "lexical"


def new_base() -> str:
    return f"w2a-sectest-{uuid.uuid4().hex[:8]}"


def guest_access() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id=TENANT))


def seed_repository() -> LocalDocumentRepository:
    return LocalDocumentRepository(LocalRepositoryConfig(REPO_ROOT))


def build(
    queries: list[str],
    security_repository: LocalDocumentRepository,
    client: QdrantClient | None = None,
    base: str | None = None,
    lexical_dir: Path | None = None,
    chunker: HeadingChunker | StructureChunker | RecursiveChunker | None = None,
) -> SecurityIndex:
    return build_security_index(
        client or QdrantClient(":memory:"),
        base or new_base(),
        queries,
        FakeEmbedder(FAKE_VECTOR_SIZE),
        chunker or HeadingChunker(2000),
        seed_repository=seed_repository(),
        security_repository=security_repository,
        tenant_id=TENANT,
        lexical_dir=lexical_dir or _WORK["dir"],
        active_lote_code=ACTIVE_LOTE.code,
    )


def run_gate(
    index: SecurityIndex,
    access: ResolvedAccess,
    queries: list[SecurityQuery],
    deferred: list[dict[str, Any]],
    config: Any,
    paths: tuple[str, ...] | list[str] = PATHS,
) -> Any:
    return run_security_evaluation(
        index,
        access,
        queries,
        deferred,
        config,
        paths,
        active_lote=ACTIVE_LOTE,
    )


def security_result(index: SecurityIndex, report: Any) -> dict[str, Any]:
    return security_document(
        runs=[(index, report)],
        suite=load_suite(REPO_ROOT, SUITE),
        access=guest_access(),
        duration_ms=1.0,
        created_at="2026-01-01T00:00:00+00:00",
        repo_root=REPO_ROOT,
        lote_modes=[None, ACTIVE_LOTE.code],
    )


class SpyIndex(DenseIndex):
    """Records every filter passed to `search`; can drop the filter."""

    def __init__(self, source: DenseIndex, *, drop_filter: bool = False) -> None:
        super().__init__(source._client, source.collection, source.settings)
        self.filters: list[models.Filter] = []
        self._drop = drop_filter

    def search(  # type: ignore[override]
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        self.filters.append(query_filter)
        return super().search(
            vector, models.Filter() if self._drop else query_filter, limit
        )


def spied(
    index: SecurityIndex, *, drop_filter: bool = False
) -> tuple[SecurityIndex, SpyIndex]:
    spy = SpyIndex(index.dense, drop_filter=drop_filter)
    return dataclasses.replace(index, dense=spy), spy


def real_queries() -> tuple[list[SecurityQuery], list[dict[str, Any]]]:
    return select_security_queries(load_suite(REPO_ROOT, SUITE))


@pytest.mark.parametrize(
    "chunker",
    security_gate_chunkers(),
    ids=["heading", "structure", "recursive"],
)
def test_full_gate_passes_on_the_seed_corpus(
    chunker: HeadingChunker | StructureChunker | RecursiveChunker,
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository, chunker=chunker)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert report.passed
    assert report.violations == []
    security = live_suite_rows("security", active_only=True)
    retrieval_side = [
        r for r in security if r["attack_type"] in RETRIEVAL_SIDE_ATTACK_TYPES
    ]
    goldens = len(live_suite_rows("golden_answerable", active_only=True))
    assert report.query_count == len(queries) == len(retrieval_side) + goldens
    assert report.security_case_count == len(retrieval_side)
    assert report.golden_query_count == goldens
    assert {d["case_id"] for d in report.deferred} == {
        r["case_id"]
        for r in security
        if r["attack_type"] not in RETRIEVAL_SIDE_ATTACK_TYPES
    }
    if chunker.name == "heading" and chunker.version == "1":
        assert index.points_per_variant == {
            **{v: len(queries) for v in FORBIDDEN_VARIANTS},
            "staff_canary": len(queries) + 1,
        }
    else:
        assert index.points_per_variant["staff_canary"] >= len(queries) + 1
        assert all(
            index.points_per_variant[v] == len(queries) for v in FORBIDDEN_VARIANTS
        )


def test_sanity_check_holds_for_every_query(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    for query in queries:
        points = index.client.query_points(
            index.collection,
            query=index.embedder.embed_query(query.text),
            using="dense",
            limit=5,
            with_payload=True,
        ).points
        assert points
        best = points[0].score
        winners = [p for p in points if p.score is not None and p.score >= best - 1e-9]
        assert any(
            security_eval.is_forbidden_document(str((p.payload or {})["document_id"]))
            for p in winners
        )
        assert best == pytest.approx(1.0, abs=1e-6)


def test_sanity_check_failure_is_a_harness_error(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    # Remove every forbidden point: the sanity check must refuse, never pass.
    index.client.delete(
        index.collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchAny(
                            any=["fixture_staff_canary"]
                            + [f"forbidden_{v}" for v in FORBIDDEN_VARIANTS]
                        ),
                    )
                ]
            )
        ),
    )
    with pytest.raises(EvaluationHarnessError, match="sanity check"):
        run_gate(index, guest_access(), queries, [], RETRIEVAL_CONFIG)


def test_a_filter_dropping_index_fails_the_gate(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken, _ = spied(index, drop_filter=True)
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    first = report.violations[0]
    assert first["case_id"] == queries[0].case_id
    assert first["document_id"]
    assert first["variant"] != ""


def test_forbidden_documents_are_caught_even_if_check_hit_is_bypassed(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    from way2australia_rag.retrieval import retriever

    monkeypatch.setattr(
        retriever,
        "check_hit",
        lambda payload, access: PointPayload.model_construct(**payload),
    )
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken, _ = spied(index, drop_filter=True)
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    variants = {v["variant"] for v in report.violations}
    assert variants <= {
        *FORBIDDEN_VARIANTS,
        "staff_canary",
        NON_APPLICABLE_LOTE_CODE,
    }
    assert {
        "staff_scope",
        "staff_scope_lote",
        "other_tenant",
        "owned",
        "missing_owner",
    } <= variants
    assert all(v["document_id"] for v in report.violations)


def test_filter_is_identical_for_every_query_including_after_s003(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    spied_index, spy = spied(index)
    report = run_gate(spied_index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert report.passed
    access = guest_access()
    expected_none = build_access_filter(access)
    from way2australia_rag.retrieval.applicability import dense_query_filter

    expected_lote = dense_query_filter(access, ACTIVE_LOTE)
    # dense leg: `dense` and `hybrid`, each with and without `lote`
    assert len(spy.filters) == 4 * len(queries)
    for block in range(len(queries)):
        base = block * 4
        assert spy.filters[base : base + 4] == [
            expected_none,
            expected_lote,
            expected_none,
            expected_lote,
        ]
    s003 = next(i for i, q in enumerate(queries) if q.case_id == "s003")
    assert "staff" in queries[s003].text  # the injection-style query really is there


def test_case_access_context_never_changes_the_filter(
    security_repository: LocalDocumentRepository,
) -> None:
    """Cases claiming another role or tenant run with the server guest access."""
    hostile = [
        {"role": "staff", "tenant_id": "other-tenant"},
        {"role": "admin", "tenant_id": TENANT},
        {"role": "guest", "tenant_id": "another"},
    ]
    suite = LoadedSuite(
        manifest=SuiteManifest(evaluation_suite_id="t", version=1, datasets=[]),
        goldens=[
            GoldenCase(
                case_id="gx",
                case_version=1,
                status="active",
                query="golden with a hostile context",
                answerable=True,
                relevant_document_ids=["d"],
                query_language="en",
                category="c",
                access_context=hostile[0],
            )
        ],
        security=[
            SecurityCase(
                case_id=f"sx{i}",
                case_version=1,
                status="active",
                query=f"security query {i}",
                attack_type="authorization_bypass",
                expected_behavior="refuse",
                access_context=context,
            )
            for i, context in enumerate(hostile)
        ],
    )
    queries, deferred = select_security_queries(suite)
    assert len(queries) == 4
    index = build([q.text for q in queries], security_repository)
    spied_index, spy = spied(index)
    report = run_gate(spied_index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert report.passed
    access = guest_access()
    expected_none = build_access_filter(access)
    from way2australia_rag.retrieval.applicability import dense_query_filter

    expected_lote = dense_query_filter(access, ACTIVE_LOTE)
    assert len(spy.filters) == 16  # 4 queries x dense+hybrid x both lote modes
    for i, filt in enumerate(spy.filters):
        assert filt == (expected_none if i % 2 == 0 else expected_lote)
    for f in spy.filters:
        dumped = json.dumps(f.model_dump(mode="json"))
        assert f'"value": "{TENANT}"' in dumped
        assert "other-tenant" not in dumped
        assert "staff" not in dumped


def test_attack_types_are_split_into_run_deferred_and_unclassified() -> None:
    def case(i: int, attack: str, status: str = "active") -> SecurityCase:
        return SecurityCase(
            case_id=f"s{i}",
            case_version=1,
            status=status,
            query=f"q{i}",
            attack_type=attack,
            expected_behavior="refuse",
        )

    suite = LoadedSuite(
        manifest=SuiteManifest(evaluation_suite_id="t", version=1, datasets=[]),
        security=[
            case(1, "filter_injection"),
            case(2, "denial_of_wallet"),
            case(3, "brand_new_attack"),
            case(4, "authorization_bypass", status="suggested"),
        ],
    )
    queries, deferred = select_security_queries(suite)
    assert [q.case_id for q in queries] == ["s1"]
    assert {d["case_id"]: d["owner"] for d in deferred} == {
        "s2": DEFERRED_OWNERS["denial_of_wallet"],
        "s3": "unclassified",
    }


@pytest.mark.parametrize(
    "base",
    [
        "way2australia",
        "w2a-sectest-1234567",
        "w2a-sectest-123456789",
        "w2a-sectest-1234567g",
        "w2a-sectest-ABCDEF12",
        "xw2a-sectest-12345678",
    ],
)
def test_builder_refuses_a_non_throwaway_base_before_any_write(
    base: str, security_repository: LocalDocumentRepository
) -> None:
    client = QdrantClient(":memory:")
    with pytest.raises(EvaluationConfigurationError, match="collection base"):
        build(["a query"], security_repository, client=client, base=base)
    assert client.get_collections().collections == []


@pytest.mark.parametrize(
    "existing", ["w2a-sectest-12345678-sec-v1", "w2a-sectest-12345678-sec-v1-settings"]
)
def test_builder_refuses_an_existing_collection(
    existing: str, security_repository: LocalDocumentRepository
) -> None:
    client = QdrantClient(":memory:")
    client.create_collection(
        existing,
        vectors_config=models.VectorParams(size=1, distance=models.Distance.COSINE),
    )
    with pytest.raises(EvaluationConfigurationError, match="already exists"):
        build(
            ["a query"], security_repository, client=client, base="w2a-sectest-12345678"
        )
    assert [c.name for c in client.get_collections().collections] == [existing]


def test_builder_refuses_a_real_embedder_identity(
    security_repository: LocalDocumentRepository,
) -> None:
    class Real(FakeEmbedder):
        def __init__(self) -> None:
            super().__init__(FAKE_VECTOR_SIZE)
            self.info = self.info.model_copy(update={"is_fake": False})

    with pytest.raises(EvaluationConfigurationError, match="fake embedder"):
        build_security_index(
            QdrantClient(":memory:"),
            new_base(),
            ["q"],
            Real(),
            HeadingChunker(),
            seed_repository=seed_repository(),
            security_repository=security_repository,
            tenant_id=TENANT,
            lexical_dir=_WORK["dir"],
            active_lote_code=ACTIVE_LOTE.code,
        )


def test_the_security_index_records_a_fake_embedder_and_is_removed(
    security_repository: LocalDocumentRepository,
) -> None:
    index = build(["a query"], security_repository)
    assert index.dense.settings.embedder_is_fake is True
    assert index.dense.index_version == "sec-v1"
    assert len(index.client.get_collections().collections) == 2
    assert index.lexical_path.is_file()
    delete_security_index(index)
    assert index.client.get_collections().collections == []
    assert not index.lexical_path.exists()


def copy_fixtures(tmp_path: Path) -> Path:
    root = tmp_path / "fixtures"
    shutil.copytree(REPO_ROOT / "tests/fixtures/security", root)
    return root


def test_stray_fixture_file_is_refused_before_any_copy(tmp_path: Path) -> None:
    root = copy_fixtures(tmp_path)
    (root / "README.md").write_text("stray", encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(EvaluationConfigurationError, match="README.md"):
        build_security_repository(
            root,
            work,
            schema_source=REPO_ROOT / "knowledge/schemas/document_metadata.schema.json",
        )
    assert list(work.iterdir()) == []


def test_hidden_entries_are_ignored(tmp_path: Path) -> None:
    root = copy_fixtures(tmp_path)
    (root / ".DS_Store").write_bytes(b"\x00")
    work = tmp_path / "work"
    work.mkdir()
    build_security_repository(
        root,
        work,
        schema_source=REPO_ROOT / "knowledge/schemas/document_metadata.schema.json",
    )
    assert sorted(p.name for p in (work / "security_corpus").iterdir()) == sorted(
        SECURITY_FIXTURE_FILES
    )


def test_missing_fixture_is_refused(tmp_path: Path) -> None:
    root = copy_fixtures(tmp_path)
    (root / "staff_only_canary.md").unlink()
    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(EvaluationConfigurationError, match="staff_only_canary.md"):
        build_security_repository(
            root,
            work,
            schema_source=REPO_ROOT / "knowledge/schemas/document_metadata.schema.json",
        )
    assert list(work.iterdir()) == []


def test_real_fixture_folder_builds(
    security_repository: LocalDocumentRepository,
) -> None:
    docs = asyncio.run(security_repository.list_documents(DocumentQuery()))
    assert len(docs) == len(SECURITY_FIXTURE_FILES)


class OddIdStore(DenseIndex):
    """A store that returns an unauthorized point (staff scope) whose
    `document_id` holds quotes, so a message-parsing regex could not read it."""

    odd = "doc'with\"quote'"

    def __init__(self, source: DenseIndex) -> None:
        super().__init__(source._client, source.collection, source.settings)

    def search(  # type: ignore[override]
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        points = super().search(vector, query_filter, limit)
        assert points, "the seed corpus should answer every query"
        first = points[0]
        payload = {**(first.payload or {}), "document_id": self.odd}
        payload["access_scope"] = "staff"
        points[0] = first.model_copy(update={"payload": payload})
        return points


def test_violation_names_the_document_from_the_error_attribute(
    security_repository: LocalDocumentRepository,
) -> None:
    # The forbidden point comes from the store; the real check_hit raises.
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, dense=OddIdStore(index.dense))
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    expected = safe_text(OddIdStore.odd)
    assert report.violations
    assert all(v["document_id"] == expected for v in report.violations)

    document = security_result(broken, report)
    assert document["passed"] is False
    assert document["runs"][0]["violations"]
    assert all(v["document_id"] == expected for v in document["runs"][0]["violations"])

    lines = cli.format_security_summary(document, Path("result.json")).splitlines()
    violation_lines = [line for line in lines if "VIOLATION" in line]
    assert violation_lines
    assert all(f"document {expected}" in line for line in violation_lines)


def test_no_fixture_path_literal_in_library_code() -> None:
    for path in sorted(EVAL_SRC.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if path.name == "cli.py":
            assert 'DEFAULT_FIXTURE_ROOT = "tests/fixtures/security"' in text
            assert text.count("fixtures/security") == 1  # the one default
        else:
            assert "fixtures/security" not in text, path.name


def test_result_document_has_ids_only(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    document = security_result(index, report)
    text = json.dumps(document, ensure_ascii=False)
    assert all(q.text not in text for q in queries)
    assert document["passed"] is True
    assert [e["document_id"] for e in document["excluded_fixtures"]] == [
        "fixture_public_poisoned"
    ]
    assert document["runs"][0]["index"]["embedder_is_fake"] is True


def test_the_whole_gate_finishes_under_ten_seconds(
    security_repository: LocalDocumentRepository,
) -> None:
    started = perf_counter()
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    elapsed = perf_counter() - started
    assert report.passed
    assert elapsed < 10.0, f"gate took {elapsed:.1f}s"


# --- Spec 007 R11: lexical leg and strategies -----------------------------


class DroppedClauseLexical:
    """A lexical store double that ignores the access clause."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.settings = inner.settings
        self.label = inner.label
        self.has_lote_column = inner.has_lote_column

    @property
    def tokenizer(self):
        return self.inner.tokenizer

    def search(
        self, match: str, where: str, params: tuple[Any, ...], limit: int
    ) -> list[LexicalRow]:
        return self.inner.search(match, "1 = 1", (), limit)

    def close(self) -> None:
        self.inner.close()


def test_the_gate_runs_all_three_strategies_on_v2(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    real = security_eval.build_retriever

    def counting(strategy: Strategy, *args: Any) -> Any:
        inner = real(strategy, *args)

        class Counting:
            def retrieve(self, *a: Any, **k: Any) -> Any:
                calls.append(strategy.value)
                assert k["top_k"] == 50
                return inner.retrieve(*a, **k)

        return Counting()

    monkeypatch.setattr(security_eval, "build_retriever", counting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert report.passed
    assert report.strategies == ("dense", "bm25", "hybrid")
    for strategy in report.strategies:
        assert calls.count(strategy) == 2 * len(queries)
    goldens = live_suite_rows("golden_answerable", active_only=True)
    assert {"g064", "g069"} <= {r["case_id"] for r in goldens}  # v2 queries are in


def test_lexical_rows_mirror_the_forbidden_points(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    assert index.lexical_rows_per_variant == index.points_per_variant
    assert index.non_applicable_rows_per_variant == {
        NON_APPLICABLE_LOTE_CODE: len(queries)
    }
    assert (
        index.lexical.settings.chunk_count == index.client.count(index.collection).count
    )
    connection = sqlite3.connect(index.lexical_path)
    try:
        missing = connection.execute(
            "SELECT owner_present FROM chunks WHERE document_id = ?",
            ("forbidden_missing_owner",),
        ).fetchall()
    finally:
        connection.close()
    assert missing and {row[0] for row in missing} == {0}


FORBIDDEN_ROWS = (
    "SELECT rowid FROM chunks WHERE document_id = 'fixture_staff_canary' "
    "OR document_id LIKE 'forbidden\\_%' ESCAPE '\\'"
)


def strip_forbidden_terms(lexical_path: Path) -> None:
    """Keep the forbidden rows but remove the query terms from them."""
    connection = sqlite3.connect(lexical_path)
    try:
        with connection:
            changed = connection.execute(
                f"UPDATE chunk_terms SET terms = 'zzzqqqxxx' "
                f"WHERE rowid IN ({FORBIDDEN_ROWS})"
            ).rowcount
            assert changed > 0
            kept = connection.execute(
                f"SELECT COUNT(*) FROM chunks WHERE rowid IN ({FORBIDDEN_ROWS})"
            ).fetchone()[0]
            assert kept == changed
    finally:
        connection.close()


def test_a_lexical_sanity_failure_is_a_harness_error(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    # Forbidden rows without the query terms: BM25 would not rank them first.
    strip_forbidden_terms(index.lexical_path)
    with pytest.raises(EvaluationHarnessError, match="lexical sanity check"):
        run_gate(index, guest_access(), queries, [], RETRIEVAL_CONFIG)


def test_zero_term_queries_skip_the_lexical_sanity_and_are_counted(
    security_repository: LocalDocumentRepository,
) -> None:
    queries = [
        SecurityQuery("z1", 1, "security", "???"),
        SecurityQuery("z2", 1, "security", "show me the staff canary"),
    ]
    assert query_terms("???").terms == []
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, [], RETRIEVAL_CONFIG)
    assert report.passed
    assert report.bm25_no_term_queries == 1
    assert report.query_count == 2


def test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    by_strategy = {v["strategy"] for v in report.violations}
    assert by_strategy == {"bm25", "hybrid"}  # the dense leg is intact
    assert all(v["document_id"] for v in report.violations)
    assert all(v["case_id"] for v in report.violations)


@pytest.mark.parametrize(
    "variant", ["staff_scope", "staff_scope_lote", "other_tenant", "owned"]
)
def test_each_forbidden_row_type_is_in_the_lexical_file(
    variant: str, security_repository: LocalDocumentRepository
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    rows = index.lexical.search(
        match_expression(query_terms(queries[0].text).terms), "1 = 1", (), 200
    )
    ids = {json.loads(r.payload_json)["document_id"] for r in rows}
    assert f"forbidden_{variant}" in ids


def test_the_missing_owner_row_is_excluded_by_owner_present_not_check_hit(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    access = guest_access()
    where, params = build_sql_access_clause(access)
    loose = (
        "c.access_scope IN (?) AND c.tenant_id = ? AND c.owner_user_id IS NULL",
        ("public", TENANT),
    )
    match = match_expression(query_terms(queries[0].text).terms)

    def documents(where_sql: str, bound: tuple[Any, ...]) -> set[str]:
        rows = index.lexical.search(match, where_sql, bound, 200)
        return {json.loads(r.payload_json)["document_id"] for r in rows}

    assert "forbidden_missing_owner" not in documents(where, params)
    assert "forbidden_missing_owner" in documents(*loose)  # only owner_present stops it
    report = run_gate(index, access, queries, deferred, RETRIEVAL_CONFIG)
    assert not [v for v in report.violations if v["variant"] == "check_hit_failed"]
    assert report.passed


def test_security_result_1_5_has_runs_paths_and_no_text(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    legacy_1_3 = {
        "kind": "security_evaluation",
        "schema_version": "1.3",
        "passed": True,
        "runs": [
            {
                "passed": True,
                "violations": [],
                "paths": list(PATHS),
                "strategies": ["dense", "bm25", "hybrid"],
            }
        ],
    }
    assert legacy_1_3["schema_version"] == "1.3"
    assert "lote_modes" not in legacy_1_3
    for candidate, passed in ((index, True), (broken, False)):
        report = run_gate(
            candidate, guest_access(), queries, deferred, RETRIEVAL_CONFIG
        )
        document = security_result(candidate, report)
        assert document["schema_version"] == "1.6"
        assert document["lote_modes"] == [None, ACTIVE_LOTE.code]
        assert document["passed"] is passed
        run = document["runs"][0]
        assert run["paths"] == list(PATHS)
        assert run["path_details"] == {}  # the five paths run no rerank stage
        assert run["strategies"] == ["dense", "bm25", "hybrid"]
        assert run["bm25_no_term_queries"] == 0
        assert (
            run["index"]["lexical_rows_per_variant"]
            == run["index"]["forbidden_points_per_variant"]
        )
        assert run["index"]["non_applicable_rows_per_variant"] == {
            NON_APPLICABLE_LOTE_CODE: len(queries)
        }
        assert run["authorization_violations"] == report.authorization_violations
        assert run["applicability_violations"] == report.applicability_violations
        assert all(
            v["strategy"] in run["strategies"] and v["path"] in run["paths"]
            for v in run["violations"]
        )
        text = json.dumps(document, ensure_ascii=False)
        assert all(q.text not in text for q in queries)
        assert "forbidden fixture" not in text
        lines = cli.format_security_summary(document, Path("r.json")).splitlines()
        assert "strategies: dense, bm25, hybrid" in lines
        assert f"paths: {', '.join(PATHS)}" in lines


# --- CLI ------------------------------------------------------------------


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "QDRANT_COLLECTION_BASE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("W2A_TENANT_ID", TENANT)


def test_cli_pass_writes_a_result_and_exits_zero(
    clean_env: None, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "out" / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 0
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["kind"] == "security_evaluation"
    assert document["passed"] is True
    out = capsys.readouterr().out
    assert "eval-security: PASS" in out
    assert re.search(r"deferred s001 \(system_prompt_extraction\)", out)
    # never overwritten
    assert (
        cli.main(["security", "--repo-root", str(REPO_ROOT), "--output", str(output)])
        == 2
    )


def test_cli_violation_exits_one_naming_ids_not_text(
    clean_env: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real = cli.build_security_index

    def broken(*args: Any, **kwargs: Any) -> SecurityIndex:
        index = real(*args, **kwargs)
        return dataclasses.replace(index, dense=SpyIndex(index.dense, drop_filter=True))

    monkeypatch.setattr(cli, "build_security_index", broken)
    output = tmp_path / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 1
    out = capsys.readouterr().out
    assert "AUTH VIOLATION path dense" in out and "case s002" in out
    assert "eval-security: FAIL" in out
    assert "forbidden fixture" not in out
    assert json.loads(output.read_text(encoding="utf-8"))["passed"] is False


def test_cli_harness_error_exits_two_and_writes_nothing(
    clean_env: None, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "security.json"
    empty = tmp_path / "no-fixtures"
    empty.mkdir()
    code = cli.main(
        [
            "security",
            "--repo-root",
            str(REPO_ROOT),
            "--output",
            str(output),
            "--fixture-root",
            str(empty),
        ]
    )
    assert code == 2
    assert not output.exists()
    assert "EvaluationConfigurationError" in capsys.readouterr().err


def spy_lexical_path(
    monkeypatch: pytest.MonkeyPatch, paths: list[Path], *, drop_clause: bool = False
) -> None:
    real = cli.build_security_index

    def wrapper(*args: Any, **kwargs: Any) -> SecurityIndex:
        index = real(*args, **kwargs)
        assert index.lexical_path.is_file()
        paths.append(index.lexical_path)
        if drop_clause:
            return dataclasses.replace(
                index, lexical=DroppedClauseLexical(index.lexical)
            )
        return index

    monkeypatch.setattr(cli, "build_security_index", wrapper)


def test_cli_lexical_file_is_removed_after_a_pass(
    clean_env: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paths: list[Path] = []
    spy_lexical_path(monkeypatch, paths)
    output = tmp_path / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 0
    assert len(paths) == 3
    assert all(not path.exists() for path in paths)
    out = capsys.readouterr().out
    assert "strategies: dense, bm25, hybrid" in out
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["schema_version"] == "1.6"
    assert document["lote_modes"] == [None, ACTIVE_LOTE.code]
    assert len(document["runs"]) == 3


def test_cli_clause_less_lexical_store_exits_one_naming_strategies(
    clean_env: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paths: list[Path] = []
    spy_lexical_path(monkeypatch, paths, drop_clause=True)
    output = tmp_path / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 1
    document = json.loads(output.read_text(encoding="utf-8"))
    violations = [v for run in document["runs"] for v in run["violations"]]
    assert {v["strategy"] for v in violations} == {"bm25", "hybrid"}
    assert "eval-security: FAIL" in capsys.readouterr().out
    assert not paths[0].exists()


def test_cli_lexical_file_is_removed_after_a_failed_run(
    clean_env: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    paths: list[Path] = []
    spy_lexical_path(monkeypatch, paths)

    def failing(*args: Any, **kwargs: Any) -> Any:
        raise EvaluationHarnessError("lexical sanity check failed for case 'x'")

    monkeypatch.setattr(cli, "run_security_evaluation", failing)
    output = tmp_path / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 2
    assert not output.exists()
    assert len(paths) == 1
    assert not paths[0].exists()
    assert "EvaluationHarnessError" in capsys.readouterr().err


def test_cli_real_lexical_sanity_failure_exits_two_and_writes_nothing(
    clean_env: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real = cli.build_security_index
    paths: list[Path] = []

    def wrapper(*args: Any, **kwargs: Any) -> SecurityIndex:
        index = real(*args, **kwargs)
        paths.append(index.lexical_path)
        strip_forbidden_terms(index.lexical_path)  # a real, unstubbed failure
        return index

    monkeypatch.setattr(cli, "build_security_index", wrapper)
    output = tmp_path / "security.json"
    code = cli.main(
        ["security", "--repo-root", str(REPO_ROOT), "--output", str(output)]
    )
    assert code == 2
    assert not output.exists()
    assert "lexical sanity check" in capsys.readouterr().err
    assert len(paths) == 1 and not paths[0].exists()


# --- Spec 008 R10: the five gated paths ------------------------------------


def test_every_path_is_gated_for_every_query(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[str] = []
    real = security_eval._retrievers

    def counting(index: SecurityIndex, config: Any, paths: Any) -> Any:
        wrapped = []
        for path, inner in real(index, config, paths):

            class Counting:
                def __init__(self, path: str = path, inner: Any = inner) -> None:
                    self.path, self.inner = path, inner

                def retrieve(self, *a: Any, **k: Any) -> Any:
                    seen.append(self.path)
                    assert k["top_k"] == 50
                    return self.inner.retrieve(*a, **k)

            wrapped.append((path, Counting()))
        return wrapped

    monkeypatch.setattr(security_eval, "_retrievers", counting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert report.passed
    assert PATHS == (
        "dense",
        "bm25",
        "hybrid",
        "hybrid_fallback_open",
        "hybrid_fallback_query",
    )
    assert report.paths == PATHS
    for path in PATHS:
        assert seen.count(path) == 2 * len(queries)


@pytest.mark.parametrize("path", PATHS)
def test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(
    path: str,
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = security_eval._retrievers

    class Injecting:
        def __init__(self, inner: Any) -> None:
            self.inner = inner

        def retrieve(self, *a: Any, **k: Any) -> Any:
            result = self.inner.retrieve(*a, **k)
            if not result.hits:
                return result
            bad = result.hits[0].model_copy(
                update={"document_id": "forbidden_staff_scope"}
            )
            return result.model_copy(update={"hits": [bad, *result.hits]})

    def injecting(index: SecurityIndex, config: Any, paths: Any) -> Any:
        return [
            (name, Injecting(inner) if name == path else inner)
            for name, inner in real(index, config, paths)
        ]

    monkeypatch.setattr(security_eval, "_retrievers", injecting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    assert {v["path"] for v in report.violations} == {path}
    assert all(v["variant"] == "staff_scope" for v in report.violations)
    assert all(
        v["strategy"] == security_eval._path_strategy(path) for v in report.violations
    )


def test_a_dropped_lexical_clause_names_the_four_lexical_paths(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert {v["path"] for v in report.violations} == {
        "bm25",
        "hybrid",
        "hybrid_fallback_open",
        "hybrid_fallback_query",
    }


def test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = security_eval._retrievers

    def not_falling_back(index: SecurityIndex, config: Any, paths: Any) -> Any:
        built = dict(real(index, config, ["dense"]))
        return [(p, built["dense"]) for p in paths if p == "hybrid_fallback_query"]

    monkeypatch.setattr(security_eval, "_retrievers", not_falling_back)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    with pytest.raises(EvaluationHarnessError, match="vacuous"):
        run_gate(
            index,
            guest_access(),
            queries,
            deferred,
            RETRIEVAL_CONFIG,
            ["hybrid_fallback_query"],
        )


def test_a_plain_hybrid_path_that_falls_back_is_a_harness_error(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = security_eval._retrievers

    def falling_back(index: SecurityIndex, config: Any, paths: Any) -> Any:
        # The plain hybrid path, but its dense leg raises RetrievalUnavailableError
        # mid-run, so the retriever serves BM25 as the fallback.
        built = dict(real(index, config, ["hybrid_fallback_query"]))
        return [(p, built["hybrid_fallback_query"]) for p in paths if p == "hybrid"]

    monkeypatch.setattr(security_eval, "_retrievers", falling_back)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    with pytest.raises(EvaluationHarnessError, match="path 'hybrid' fell back"):
        run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, ["hybrid"])


def test_the_bm25_path_is_refused_when_the_standalone_open_fails(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    wrong = dataclasses.replace(index, chunker=HeadingChunker(max_chunk_chars=999))
    with pytest.raises(EvaluationHarnessError, match="standalone open"):
        run_gate(wrong, guest_access(), queries, deferred, RETRIEVAL_CONFIG, ["bm25"])


def test_the_bm25_path_is_built_without_a_dense_index_or_embedder(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, Any, Any]] = []
    real = security_eval.build_retriever

    def spy(
        strategy: Strategy, identity: Any, dense: Any, embedder: Any, *r: Any
    ) -> Any:
        calls.append((strategy.value, dense, embedder))
        return real(strategy, identity, dense, embedder, *r)

    monkeypatch.setattr(security_eval, "build_retriever", spy)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, ["bm25"])
    assert calls == [("bm25", None, None)]


def test_unavailable_dense_is_not_importable_from_the_retrieval_package() -> None:
    import pkgutil

    import way2australia_rag.retrieval as retrieval

    assert hasattr(security_eval, "_UnavailableDense")
    for module in pkgutil.iter_modules(retrieval.__path__):
        text = (Path(retrieval.__path__[0]) / f"{module.name}.py").read_text(
            encoding="utf-8"
        )
        assert "_UnavailableDense" not in text
        assert "security_eval" not in text


class DroppedLoteClauseLexical:
    """Lexical double that ignores the lote portion of the WHERE clause."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.settings = inner.settings
        self.label = inner.label
        self.has_lote_column = inner.has_lote_column

    @property
    def tokenizer(self):
        return self.inner.tokenizer

    def search(
        self, match: str, where: str, params: tuple[Any, ...], limit: int
    ) -> list[LexicalRow]:
        access_where, access_params = build_sql_access_clause(guest_access())
        return self.inner.search(match, access_where, access_params, limit)


def test_zz_active_code_refuses_the_harness() -> None:
    with pytest.raises(EvaluationHarnessError, match="zz"):
        require_non_applicable_lote_inactive(
            [ACTIVE_LOTE.code, NON_APPLICABLE_LOTE_CODE]
        )


def test_access_only_sanity_requires_non_applicable_first(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    index.client.delete(
        index.collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=NON_APPLICABLE_DOCUMENT_ID),
                    )
                ]
            )
        ),
    )
    with pytest.raises(EvaluationHarnessError, match="access-only sanity"):
        run_gate(index, guest_access(), queries, [], RETRIEVAL_CONFIG)


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize(
    "chunker",
    security_gate_chunkers(),
    ids=["heading", "structure", "recursive"],
)
def test_both_lote_modes_on_every_path_and_chunker(
    path: str,
    chunker: HeadingChunker | StructureChunker | RecursiveChunker,
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_lote: list[str | None] = []
    real = security_eval._retrievers

    def counting(index: SecurityIndex, config: Any, paths: Any) -> Any:
        wrapped = []
        for name, inner in real(index, config, paths):

            class Counting:
                def __init__(self, path: str = name, inner: Any = inner) -> None:
                    self.path, self.inner = path, inner

                def retrieve(self, *a: Any, **k: Any) -> Any:
                    if self.path == path:
                        lote = k.get("lote")
                        seen_lote.append(None if lote is None else lote.code)
                    return self.inner.retrieve(*a, **k)

            wrapped.append((name, Counting()))
        return wrapped

    monkeypatch.setattr(security_eval, "_retrievers", counting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository, chunker=chunker)
    report = run_gate(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, [path]
    )
    assert report.passed
    assert seen_lote.count(None) == len(queries)
    assert seen_lote.count(ACTIVE_LOTE.code) == len(queries)


def test_dropped_applicability_filter_reports_applicability_not_authorization(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedLoteClauseLexical(index.lexical))
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    assert report.applicability_violations
    assert not report.authorization_violations
    assert all(v["lote"] == ACTIVE_LOTE.code for v in report.applicability_violations)


def test_dropped_access_filter_still_reports_authorization(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    report = run_gate(broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG)
    assert not report.passed
    assert report.authorization_violations
    assert not report.applicability_violations


# --- Spec 011 R8, R9: the reranked paths -----------------------------------


def test_the_gate_defaults_to_eight_paths_and_the_original_five_are_unchanged() -> None:
    assert PATHS == (
        "dense",
        "bm25",
        "hybrid",
        "hybrid_fallback_open",
        "hybrid_fallback_query",
    )
    assert RERANK_PATHS == (
        "hybrid_rerank",
        "hybrid_rerank_skip_open",
        "hybrid_rerank_skip_query",
    )
    assert ALL_PATHS == (*PATHS, *RERANK_PATHS)
    assert len(ALL_PATHS) == 8
    default = security_eval.run_security_evaluation.__defaults__
    assert default is not None and default[0] == ALL_PATHS


def test_the_security_corpus_has_an_injection_style_forbidden_row(
    security_repository: LocalDocumentRepository,
) -> None:
    assert "injection" in FORBIDDEN_VARIANTS
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    assert index.points_per_variant["injection"] == len(queries)
    points, _ = index.client.scroll(
        index.collection,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value="forbidden_injection"),
                )
            ]
        ),
        limit=1,
        with_payload=True,
    )
    payload = points[0].payload or {}
    assert payload["chunk_text"] == INJECTION_TEXT
    assert payload["access_scope"] == "staff"
    assert "ignore previous instructions" in INJECTION_TEXT


@pytest.mark.parametrize(
    "chunker",
    security_gate_chunkers(),
    ids=["heading", "structure", "recursive"],
)
def test_rerank_paths_pass_over_every_chunker_in_both_lote_modes(
    chunker: HeadingChunker | StructureChunker | RecursiveChunker,
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, list[str | None]] = {path: [] for path in RERANK_PATHS}
    real = security_eval._retrievers

    def counting(index: SecurityIndex, config: Any, paths: Any) -> Any:
        wrapped = []
        for name, inner in real(index, config, paths):

            class Counting:
                def __init__(self, path: str = name, inner: Any = inner) -> None:
                    self.path, self.inner = path, inner

                def retrieve(self, *a: Any, **k: Any) -> Any:
                    lote = k.get("lote")
                    seen[self.path].append(None if lote is None else lote.code)
                    return self.inner.retrieve(*a, **k)

            wrapped.append((name, Counting()))
        return wrapped

    monkeypatch.setattr(security_eval, "_retrievers", counting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository, chunker=chunker)
    report = run_gate(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, RERANK_PATHS
    )
    assert report.passed, report.violations
    for path in RERANK_PATHS:
        assert seen[path].count(None) == len(queries)
        assert seen[path].count(ACTIVE_LOTE.code) == len(queries)
    details = report.path_details
    assert set(details) == set(RERANK_PATHS)
    for detail in details.values():
        assert detail["reranker"]["is_fake"] is True
        assert detail["reranker"]["model_id"] == "fake-reranker"
    assert details["hybrid_rerank"]["skip"] is None
    assert details["hybrid_rerank_skip_open"]["skip"] == {
        "reason": "model_unavailable",
        "stage": "open",
    }
    assert details["hybrid_rerank_skip_query"]["skip"] == {
        "reason": "model_unavailable",
        "stage": "query",
    }


def test_the_rerank_paths_run_the_real_stage_over_hybrid_inside_fallback(
    security_repository: LocalDocumentRepository,
) -> None:
    from way2australia_rag.retrieval.fallback import FallbackRetriever
    from way2australia_rag.retrieval.reranking import RerankingRetriever

    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    built = dict(security_eval._retrievers(index, RETRIEVAL_CONFIG, RERANK_PATHS))
    stages: dict[str, RerankingRetriever] = {}
    for path, retriever in built.items():
        assert isinstance(retriever, FallbackRetriever)
        stage = retriever._primary  # noqa: SLF001
        assert isinstance(stage, RerankingRetriever)
        stages[path] = stage
    assert stages["hybrid_rerank_skip_open"]._open_skip is not None  # noqa: SLF001
    assert stages["hybrid_rerank"]._open_skip is None  # noqa: SLF001


def test_the_fake_reranker_prefers_forbidden_and_injection_text(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    prefer = security_eval._preferring([q.text for q in queries])  # noqa: SLF001
    assert prefer("forbidden fixture")
    assert prefer(INJECTION_TEXT)
    assert prefer(f"{INJECTION_TEXT} extra terms")
    assert prefer(security_eval.lexical_probe_text(queries[0].text, repeats=2))
    assert not prefer("Mock assessments are optional practice sessions.")


def test_a_forbidden_candidate_is_never_returned_even_when_the_reranker_prefers_it(
    security_repository: LocalDocumentRepository,
) -> None:
    """With the access filter dropped in the dense leg, the leg's fail-closed
    check_hit raises before fusion, so forbidden rows never reach the reranker
    while the filters hold; the gate must report that as a violation on
    hybrid_rerank. Separately, on the intact index the fake reranker's
    preference really orders results: a preferred (non-applicable) row is rank 1
    with lote None, so the preference is a committed, observable effect."""
    queries, deferred = real_queries()
    intact = build([q.text for q in queries], security_repository)
    retriever = dict(
        security_eval._retrievers(intact, RETRIEVAL_CONFIG, ["hybrid_rerank"])
    )["hybrid_rerank"]
    for query in queries:
        result = retriever.retrieve(
            query.text,
            guest_access(),
            top_k=RETRIEVAL_CONFIG.rerank.depth,
            lote=None,
        )
        assert result.hits
        assert is_non_applicable_document(result.hits[0].document_id), query.case_id
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken, _ = spied(index, drop_filter=True)
    report = run_gate(
        broken,
        guest_access(),
        queries,
        deferred,
        RETRIEVAL_CONFIG,
        ["hybrid_rerank"],
    )
    assert not report.passed
    assert {v["path"] for v in report.violations} == {"hybrid_rerank"}
    variants = {v["variant"] for v in report.authorization_violations}
    assert "injection" in variants


@pytest.mark.parametrize(
    ("path", "make_fake", "reason", "stage"),
    [
        ("hybrid_rerank_skip_open", "fail_on_load", "model_unavailable", "open"),
        ("hybrid_rerank_skip_query", "fail_on_call", "model_unavailable", "query"),
    ],
)
def test_skip_paths_record_the_expected_skip_for_every_query(
    path: str,
    make_fake: str,
    reason: str,
    stage: str,
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    retriever = dict(security_eval._retrievers(index, RETRIEVAL_CONFIG, [path]))[path]
    for lote in (None, ACTIVE_LOTE):
        for query in queries:
            result = retriever.retrieve(
                query.text,
                guest_access(),
                top_k=RETRIEVAL_CONFIG.fusion.candidate_depth,
                lote=lote,
            )
            assert result.fallback_reason is None  # a skip is never a BM25 fallback
            assert result.rerank is not None and result.rerank.is_fake
            assert result.rerank.skipped_reason == reason
            assert result.rerank.stage == stage
            assert result.hits


def test_the_harness_reranker_failures_use_the_fake_reranker_switches() -> None:
    from way2australia_rag.rerank.errors import RerankerUnavailableError

    one_shot = security_eval.FakeReranker(fail_on_call=1)
    always = security_eval._AlwaysFailingScore()  # noqa: SLF001
    one_shot.load()
    with pytest.raises(RerankerUnavailableError):
        one_shot.score("q", ["a"])
    assert one_shot.score("q", ["a"]).scores  # fail_on_call is one-shot
    for _ in range(3):
        with pytest.raises(RerankerUnavailableError):
            always.score("q", ["a"])
    with pytest.raises(RerankerUnavailableError):
        security_eval.FakeReranker(fail_on_load=True).load()


@pytest.mark.parametrize(
    "path", ["hybrid_rerank_skip_open", "hybrid_rerank_skip_query"]
)
def test_a_skip_path_that_records_no_skip_fails_the_gate(
    path: str,
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = security_eval._retrievers

    def wrong(index: SecurityIndex, config: Any, paths: Any) -> Any:
        # the plain reranking composition under a skip path's name
        built = dict(real(index, config, ["hybrid_rerank"]))
        return [(p, built["hybrid_rerank"]) for p in paths]

    monkeypatch.setattr(security_eval, "_retrievers", wrong)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    with pytest.raises(EvaluationHarnessError, match="vacuous"):
        run_gate(index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, [path])


def test_a_rerank_path_without_a_rerank_stage_is_a_harness_error(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = security_eval._retrievers

    def plain(index: SecurityIndex, config: Any, paths: Any) -> Any:
        built = dict(real(index, config, ["hybrid"]))
        return [(p, built["hybrid"]) for p in paths]

    monkeypatch.setattr(security_eval, "_retrievers", plain)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    with pytest.raises(EvaluationHarnessError, match="no rerank stage"):
        run_gate(
            index,
            guest_access(),
            queries,
            deferred,
            RETRIEVAL_CONFIG,
            ["hybrid_rerank"],
        )


def test_a_rerank_path_that_fell_back_is_a_harness_error(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = security_eval._retrievers

    def falling_back(index: SecurityIndex, config: Any, paths: Any) -> Any:
        built = dict(real(index, config, ["hybrid_fallback_query"]))
        return [(p, built["hybrid_fallback_query"]) for p in paths]

    monkeypatch.setattr(security_eval, "_retrievers", falling_back)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    with pytest.raises(EvaluationHarnessError, match="fell back"):
        run_gate(
            index,
            guest_access(),
            queries,
            deferred,
            RETRIEVAL_CONFIG,
            ["hybrid_rerank"],
        )


def test_a_forbidden_hit_injected_after_the_stage_fails_each_rerank_path(
    security_repository: LocalDocumentRepository, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = security_eval._retrievers

    class Injecting:
        def __init__(self, inner: Any) -> None:
            self.inner = inner

        def retrieve(self, *a: Any, **k: Any) -> Any:
            result = self.inner.retrieve(*a, **k)
            bad = result.hits[0].model_copy(
                update={"document_id": "forbidden_injection"}
            )
            return result.model_copy(update={"hits": [bad, *result.hits]})

    def injecting(index: SecurityIndex, config: Any, paths: Any) -> Any:
        return [(n, Injecting(r)) for n, r in real(index, config, paths)]

    monkeypatch.setattr(security_eval, "_retrievers", injecting)
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, RERANK_PATHS
    )
    assert not report.passed
    assert {v["path"] for v in report.violations} == set(RERANK_PATHS)
    assert {v["variant"] for v in report.violations} == {"injection"}


class _DefectiveStage:
    """Harness-only: a reranking stage whose ordering is defective. The base
    stage's `_order` is replaced; the post-stage membership re-check is real."""

    def __init__(
        self, index: SecurityIndex, mode: str, *, hybrid_ignores_lote: bool = False
    ) -> None:
        from way2australia_rag.retrieval.bm25 import BM25Retriever
        from way2australia_rag.retrieval.fallback import FallbackRetriever
        from way2australia_rag.retrieval.hybrid import HybridRetriever
        from way2australia_rag.retrieval.identity import IndexIdentity
        from way2australia_rag.retrieval.reranking import RerankingRetriever
        from way2australia_rag.retrieval.retriever import DenseRetriever

        identity = IndexIdentity.from_dense(index.dense)
        bm25 = BM25Retriever(identity, index.lexical)
        hybrid: Any = HybridRetriever(
            DenseRetriever(index.dense, index.embedder), bm25, RETRIEVAL_CONFIG.fusion
        )
        if hybrid_ignores_lote:
            inner = hybrid

            class IgnoresLote:
                strategy = inner.strategy

                def retrieve(self, q: Any, access: Any, top_k: int = 5, **_: Any):  # noqa: ANN202
                    return inner.retrieve(q, access, top_k, lote=None)

            hybrid = IgnoresLote()

        class Defective(RerankingRetriever):
            def _order(self, candidates: Any, scores: Any, top_k: int) -> Any:
                ordered = super()._order(candidates, scores, top_k)
                if mode == "duplicate":
                    return [ordered[0], ordered[0], *ordered[1:]]
                if mode == "unknown":
                    other = ordered[0].model_copy(
                        update={"point_id": "00000000-0000-0000-0000-000000000000"}
                    )
                    return [other, *ordered]
                if mode == "altered":
                    return [
                        ordered[0].model_copy(update={"chunk_text": "tampered"}),
                        *ordered[1:],
                    ]
                return ordered  # "plain": defect is in the legs, not the stage

        from way2australia_rag.rerank.fake import FakeReranker

        stage = Defective(
            hybrid, FakeReranker(), RETRIEVAL_CONFIG.fusion.candidate_depth
        )
        self.retriever = FallbackRetriever(stage, bm25, None)

    def retrieve(self, *a: Any, **k: Any) -> Any:
        return self.retriever.retrieve(*a, **k)


@pytest.mark.parametrize("mode", ["duplicate", "unknown", "altered"])
def test_the_post_rerank_membership_recheck_fails_closed_for_a_defective_stage(
    mode: str,
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)

    def defective(i: SecurityIndex, config: Any, paths: Any) -> Any:
        return [(p, _DefectiveStage(i, mode)) for p in paths]

    monkeypatch.setattr(security_eval, "_retrievers", defective)
    report = run_gate(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, ["hybrid_rerank"]
    )
    # the stage raised RetrievalAuthorizationError, recorded as a violation
    # (it is never caught inside the stage or FallbackRetriever)
    assert not report.passed
    assert report.authorization_violations
    assert not report.applicability_violations
    assert {v["variant"] for v in report.authorization_violations} == {
        "check_hit_failed"
    }


def test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote(
    security_repository: LocalDocumentRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hybrid that ignores the lote hands the stage a non-applicable candidate
    that is a member of the pool; only `check_applicable` can stop it."""
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)

    def defective(i: SecurityIndex, config: Any, paths: Any) -> Any:
        return [
            (p, _DefectiveStage(i, "plain", hybrid_ignores_lote=True)) for p in paths
        ]

    monkeypatch.setattr(security_eval, "_retrievers", defective)
    report = run_gate(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG, ["hybrid_rerank"]
    )
    assert not report.passed
    assert report.applicability_violations
    assert not report.authorization_violations
    assert {v["lote"] for v in report.applicability_violations} == {ACTIVE_LOTE.code}


def test_the_summary_prints_the_rerank_path_details(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_gate(
        index,
        guest_access(),
        queries,
        deferred,
        RETRIEVAL_CONFIG,
        RERANK_PATHS,
    )
    document = security_result(index, report)
    assert document["schema_version"] == "1.6"
    run = document["runs"][0]
    assert run["paths"] == list(RERANK_PATHS)
    assert set(run["path_details"]) == set(RERANK_PATHS)
    lines = cli.format_security_summary(document, Path("r.json")).splitlines()
    assert any(
        line.startswith("hybrid_rerank_skip_open: fake reranker")
        and "skip model_unavailable at open" in line
        for line in lines
    )
    assert any(
        line.startswith("hybrid_rerank: fake reranker") and "no skip" in line
        for line in lines
    )
    text = json.dumps(document, ensure_ascii=False)
    assert all(q.text not in text for q in queries)
    assert INJECTION_TEXT not in text


def test_generation_security_checks_pass_on_throwaway_index(
    security_repository: LocalDocumentRepository,
) -> None:
    from way2australia_rag.evaluation.security_eval import (
        run_generation_security_checks,
    )

    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    access = guest_access()
    checks = run_generation_security_checks(
        index,
        access,
        queries,
        RETRIEVAL_CONFIG,
        REPO_ROOT,
        REPO_ROOT / "tests/fixtures/security",
    )
    assert checks["passed"] is True


def test_generation_citation_manipulation_fails_when_validator_is_broken(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from way2australia_core import AccessContext, Role
    from way2australia_rag.evaluation.security_eval import (
        generation_citation_manipulation,
    )
    from way2australia_rag.generation.models import Citation
    from way2australia_rag.retrieval.access import resolve_access

    def broken(_output, blocks):  # noqa: ANN001, ANN202
        return [
            Citation(
                source_id="S1",
                document_id=blocks[0].document_id,
                document_version=1,
                section_id="s",
                title="t",
                source_authority="owner",
                source_url=None,
            )
        ]

    monkeypatch.setattr(
        "way2australia_rag.generation.service.validate_citations", broken
    )
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id=TENANT))
    result = generation_citation_manipulation(REPO_ROOT, access)  # noqa: SLF001
    assert not result["passed"]
