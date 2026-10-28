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
from conftest import REPO_ROOT, live_suite_rows
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
    DEFERRED_OWNERS,
    FORBIDDEN_VARIANTS,
    RETRIEVAL_SIDE_ATTACK_TYPES,
    SecurityQuery,
    run_security_evaluation,
    security_document,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    SecurityIndex,
    build_security_index,
    delete_security_index,
)
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.payload import PointPayload
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
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import match_expression
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.strategy import load_retrieval_config
from way2australia_rag.retrieval.text import safe_text

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

SUITE = "evaluation/suites/public-eval-v2.json"
TENANT = "way2australia"
RETRIEVAL_CONFIG = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
EVAL_SRC = REPO_ROOT / "packages/rag/src/way2australia_rag/evaluation"


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
) -> SecurityIndex:
    return build_security_index(
        client or QdrantClient(":memory:"),
        base or new_base(),
        queries,
        FakeEmbedder(FAKE_VECTOR_SIZE),
        HeadingChunker(),
        seed_repository=seed_repository(),
        security_repository=security_repository,
        tenant_id=TENANT,
        lexical_dir=lexical_dir or _WORK["dir"],
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


def test_full_gate_passes_on_the_seed_corpus(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_security_evaluation(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
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
    assert index.points_per_variant == {
        **{v: len(queries) for v in FORBIDDEN_VARIANTS},
        "staff_canary": len(queries) + 1,
    }


def test_sanity_check_holds_for_every_query(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    for query in queries:
        top = index.client.query_points(
            index.collection,
            query=index.embedder.embed_query(query.text),
            using="dense",
            limit=5,
            with_payload=True,
        ).points[0]
        assert security_eval.is_forbidden_document(
            str((top.payload or {})["document_id"])
        )
        assert top.score == pytest.approx(1.0, abs=1e-6)


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
        run_security_evaluation(index, guest_access(), queries, [], RETRIEVAL_CONFIG)


def test_a_filter_dropping_index_fails_the_gate(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken, _ = spied(index, drop_filter=True)
    report = run_security_evaluation(
        broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
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
    report = run_security_evaluation(
        broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert not report.passed
    variants = {v["variant"] for v in report.violations}
    assert variants <= {*FORBIDDEN_VARIANTS, "staff_canary"}
    assert {"staff_scope", "other_tenant", "owned", "missing_owner"} <= variants
    assert all(v["document_id"] for v in report.violations)


def test_filter_is_identical_for_every_query_including_after_s003(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    spied_index, spy = spied(index)
    report = run_security_evaluation(
        spied_index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert report.passed
    expected = build_access_filter(guest_access())
    # the dense leg runs twice per query: `dense`, then inside `hybrid`
    assert len(spy.filters) == 2 * len(queries)
    assert all(f == expected for f in spy.filters)
    s003 = next(i for i, q in enumerate(queries) if q.case_id == "s003")
    assert "staff" in queries[s003].text  # the injection-style query really is there
    assert all(f == spy.filters[0] for f in spy.filters[2 * s003 :])


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
    report = run_security_evaluation(
        spied_index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert report.passed
    expected = build_access_filter(guest_access())
    assert len(spy.filters) == 8  # 4 queries x (dense + the hybrid dense leg)
    assert all(f == expected for f in spy.filters)
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
    report = run_security_evaluation(
        broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert not report.passed
    expected = safe_text(OddIdStore.odd)
    assert report.violations
    assert all(v["document_id"] == expected for v in report.violations)

    document = security_document(
        index=broken,
        report=report,
        suite=load_suite(REPO_ROOT, SUITE),
        access=guest_access(),
        duration_ms=1.0,
        created_at="2026-01-01T00:00:00+00:00",
        repo_root=REPO_ROOT,
    )
    assert document["passed"] is False
    assert document["violations"]
    assert all(v["document_id"] == expected for v in document["violations"])

    lines = cli.format_security_summary(document, Path("result.json")).splitlines()
    violation_lines = [line for line in lines if line.startswith("VIOLATION")]
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
    report = run_security_evaluation(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    document = security_document(
        index=index,
        report=report,
        suite=load_suite(REPO_ROOT, SUITE),
        access=guest_access(),
        duration_ms=1.0,
        created_at="2026-01-01T00:00:00+00:00",
        repo_root=REPO_ROOT,
    )
    text = json.dumps(document, ensure_ascii=False)
    assert all(q.text not in text for q in queries)
    assert document["passed"] is True
    assert [e["document_id"] for e in document["excluded_fixtures"]] == [
        "fixture_public_poisoned"
    ]
    assert document["index"]["embedder_is_fake"] is True


def test_the_whole_gate_finishes_under_ten_seconds(
    security_repository: LocalDocumentRepository,
) -> None:
    started = perf_counter()
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    report = run_security_evaluation(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
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
    report = run_security_evaluation(
        index, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert report.passed
    assert report.strategies == ("dense", "bm25", "hybrid")
    for strategy in report.strategies:
        assert calls.count(strategy) == len(queries)
    goldens = live_suite_rows("golden_answerable", active_only=True)
    assert {"g064", "g069"} <= {r["case_id"] for r in goldens}  # v2 queries are in


def test_lexical_rows_mirror_the_forbidden_points(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, _ = real_queries()
    index = build([q.text for q in queries], security_repository)
    assert index.lexical_rows_per_variant == index.points_per_variant
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
        run_security_evaluation(index, guest_access(), queries, [], RETRIEVAL_CONFIG)


def test_zero_term_queries_skip_the_lexical_sanity_and_are_counted(
    security_repository: LocalDocumentRepository,
) -> None:
    queries = [
        SecurityQuery("z1", 1, "security", "???"),
        SecurityQuery("z2", 1, "security", "show me the staff canary"),
    ]
    assert query_terms("???").terms == []
    index = build([q.text for q in queries], security_repository)
    report = run_security_evaluation(
        index, guest_access(), queries, [], RETRIEVAL_CONFIG
    )
    assert report.passed
    assert report.bm25_no_term_queries == 1
    assert report.query_count == 2


def test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    report = run_security_evaluation(
        broken, guest_access(), queries, deferred, RETRIEVAL_CONFIG
    )
    assert not report.passed
    by_strategy = {v["strategy"] for v in report.violations}
    assert by_strategy == {"bm25", "hybrid"}  # the dense leg is intact
    assert all(v["document_id"] for v in report.violations)
    assert all(v["case_id"] for v in report.violations)


@pytest.mark.parametrize("variant", ["staff_scope", "other_tenant", "owned"])
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
    report = run_security_evaluation(index, access, queries, deferred, RETRIEVAL_CONFIG)
    assert not [v for v in report.violations if v["variant"] == "check_hit_failed"]
    assert report.passed


def test_security_result_1_1_has_strategies_and_no_text(
    security_repository: LocalDocumentRepository,
) -> None:
    queries, deferred = real_queries()
    index = build([q.text for q in queries], security_repository)
    broken = dataclasses.replace(index, lexical=DroppedClauseLexical(index.lexical))
    for candidate, passed in ((index, True), (broken, False)):
        report = run_security_evaluation(
            candidate, guest_access(), queries, deferred, RETRIEVAL_CONFIG
        )
        document = security_document(
            index=candidate,
            report=report,
            suite=load_suite(REPO_ROOT, SUITE),
            access=guest_access(),
            duration_ms=1.0,
            created_at="2026-01-01T00:00:00+00:00",
            repo_root=REPO_ROOT,
        )
        assert document["schema_version"] == "1.1"
        assert document["passed"] is passed
        assert document["strategies"] == ["dense", "bm25", "hybrid"]
        assert document["bm25_no_term_queries"] == 0
        assert (
            document["index"]["lexical_rows_per_variant"]
            == (document["index"]["forbidden_points_per_variant"])
        )
        assert all(
            v["strategy"] in document["strategies"] for v in document["violations"]
        )
        text = json.dumps(document, ensure_ascii=False)
        assert all(q.text not in text for q in queries)
        assert "forbidden fixture" not in text
        lines = cli.format_security_summary(document, Path("r.json")).splitlines()
        assert "strategies: dense, bm25, hybrid" in lines


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
    assert "VIOLATION case s002" in out
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
    assert len(paths) == 1
    assert not paths[0].exists() and not paths[0].parent.exists()
    assert "strategies: dense, bm25, hybrid" in capsys.readouterr().out
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "1.1"


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
    assert {v["strategy"] for v in document["violations"]} == {"bm25", "hybrid"}
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
    assert not paths[0].exists() and not paths[0].parent.exists()
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
