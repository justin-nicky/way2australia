"""Authorization hard gate over a throwaway security index (Spec 006 R8, Spec 008 R10).

Every retrieval-side security case and every active golden query runs through
eight paths: the production `dense`, `bm25` and `hybrid` retrievers (built by
`build_retriever`), the two `hybrid` fallback paths (`hybrid_fallback_open`,
`hybrid_fallback_query`), and the three reranked paths of Spec 011
(`hybrid_rerank`, `hybrid_rerank_skip_open`, `hybrid_rerank_skip_query`, built by
`build_retriever` with a `FakeReranker`), with the one server-resolved
`ResolvedAccess` passed in. A
case's own `access_context` is never consulted, and query text never reaches the
filter. A forbidden document in the results, or a `check_hit` failure, is a
violation. Violations name `case_id`, `document_id` and variant, never text.
"""

import asyncio
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from way2australia_rag.evaluation.errors import EvaluationHarnessError
from way2australia_rag.evaluation.models import DatasetType, LoadedSuite
from way2australia_rag.evaluation.security_index import (
    FORBIDDEN_SENTINEL,
    FORBIDDEN_VARIANTS,
    INJECTION_TEXT,
    NON_APPLICABLE_VARIANT,
    SECURITY_COLLECTION_PREFIX,
    SecurityIndex,
    forbidden_variant,
    is_forbidden_document,
    is_non_applicable_document,
    lexical_probe_text,
)
from way2australia_rag.ingestion.chunking import Chunker, HeadingChunker
from way2australia_rag.ingestion.recursive import RecursiveChunker
from way2australia_rag.ingestion.store import DENSE_VECTOR_NAME
from way2australia_rag.ingestion.structure import StructureChunker
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.lexical.build import production_entries
from way2australia_rag.lexical.store import LexicalIndex, LexicalIndexBindingError
from way2australia_rag.lexical.tokenizer import query_terms
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.rerank.errors import (
    RerankSkipReason,
    classify_reranker_error,
)
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.access import ResolvedAccess, build_sql_access_clause
from way2australia_rag.retrieval.applicability import ResolvedLote, dense_query_filter
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.bm25 import BM25Retriever, match_expression
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    LanguageApplicabilityError,
    RetrievalAuthorizationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.retriever import MAX_TOP_K
from way2australia_rag.retrieval.strategy import RetrievalConfig, build_retriever
from way2australia_rag.retrieval.text import safe_text

RETRIEVAL_SIDE_ATTACK_TYPES = frozenset(
    {
        "authorization_bypass",
        "filter_injection",
        "paid_content_exfiltration",
        "context_exfiltration",
        "privacy_exfiltration",
    }
)
DEFERRED_OWNERS = {
    "system_prompt_extraction": "roadmap-12",
    "ungrounded_generation": "roadmap-10",
    "citation_manipulation": "roadmap-10",
    "indirect_prompt_injection": "roadmap-12",
    "denial_of_wallet": "roadmap-12",
}
UNCLASSIFIED_OWNER = "unclassified"
EXCLUDED_FIXTURES = [
    {
        "document_id": "fixture_public_poisoned",
        "reason": (
            "public scope: the access filter correctly allows it; ingestion "
            "eligibility keeps it out of production. It belongs to the "
            "prompt-injection tests (roadmap 12), not the authorization gate."
        ),
    }
]
SANITY_LIMIT = 5
STRATEGIES = (Strategy.DENSE, Strategy.BM25, Strategy.HYBRID)
PATH_DENSE = "dense"
PATH_BM25 = "bm25"
PATH_HYBRID = "hybrid"
PATH_FALLBACK_OPEN = "hybrid_fallback_open"
PATH_FALLBACK_QUERY = "hybrid_fallback_query"
PATH_RERANK = "hybrid_rerank"
PATH_RERANK_SKIP_OPEN = "hybrid_rerank_skip_open"
PATH_RERANK_SKIP_QUERY = "hybrid_rerank_skip_query"
# The five Spec 006 to 008 paths. Their results are unchanged by Spec 011.
PATHS = (PATH_DENSE, PATH_BM25, PATH_HYBRID, PATH_FALLBACK_OPEN, PATH_FALLBACK_QUERY)
RERANK_PATHS = (PATH_RERANK, PATH_RERANK_SKIP_OPEN, PATH_RERANK_SKIP_QUERY)
# What `make eval-security` runs.
ALL_PATHS = (*PATHS, *RERANK_PATHS)
_FALLBACK_PATHS = frozenset({PATH_FALLBACK_OPEN, PATH_FALLBACK_QUERY})
# The (reason, stage) a skip path must record, or the gate would be vacuous.
_EXPECTED_SKIP: dict[str, tuple[str, str] | None] = {
    PATH_RERANK: None,
    PATH_RERANK_SKIP_OPEN: (RerankSkipReason.MODEL_UNAVAILABLE.value, "open"),
    PATH_RERANK_SKIP_QUERY: (RerankSkipReason.MODEL_UNAVAILABLE.value, "query"),
}
LEXICAL_SANITY_SQL = (
    "SELECT c.document_id FROM chunk_terms "
    "JOIN chunks c ON c.rowid = chunk_terms.rowid "
    "WHERE chunk_terms MATCH ? ORDER BY bm25(chunk_terms) ASC, c.point_id ASC LIMIT 1"
)
LEXICAL_ACCESS_SANITY_SQL = (
    "SELECT c.document_id FROM chunk_terms "
    "JOIN chunks c ON c.rowid = chunk_terms.rowid "
    "WHERE chunk_terms MATCH ? AND ({access_where}) "
    "ORDER BY bm25(chunk_terms) ASC, c.point_id ASC LIMIT 1"
)

__all__ = [
    "ALL_PATHS",
    "DEFERRED_OWNERS",
    "EXCLUDED_FIXTURES",
    "FORBIDDEN_VARIANTS",
    "PATHS",
    "RERANK_PATHS",
    "RETRIEVAL_SIDE_ATTACK_TYPES",
    "SECURITY_COLLECTION_PREFIX",
    "SecurityQuery",
    "SecurityReport",
    "run_security_evaluation",
    "security_document",
    "security_gate_chunkers",
    "security_run_record",
    "select_security_queries",
]


def security_gate_chunkers() -> tuple[Chunker, ...]:
    """The three chunkers exercised by ``make eval-security`` (Spec 009 R9)."""
    tokenizer = FakeTokenizer()
    return (
        HeadingChunker(2000),
        StructureChunker(
            max_chunk_tokens=64,
            context_prefix="title_and_headings",
            tokenizer=tokenizer,
        ),
        RecursiveChunker(
            # 32 + title refuses official_003 on the seed corpus (T3 prefix rule);
            # 48 keeps several chunks per document and ingests all 13 documents.
            target_tokens=48,
            overlap_tokens=4,
            context_prefix="title",
            tokenizer=tokenizer,
        ),
    )


@dataclass(frozen=True)
class SecurityQuery:
    case_id: str
    case_version: int
    kind: str  # "security" or "golden"
    text: str


@dataclass
class SecurityReport:
    query_count: int = 0
    security_case_count: int = 0
    golden_query_count: int = 0
    bm25_no_term_queries: int = 0
    paths: tuple[str, ...] = PATHS
    # Rerank paths only: the fake reranker identity and the skip seen (R8).
    path_details: dict[str, dict[str, Any]] = field(default_factory=dict)
    authorization_violations: list[dict[str, str]] = field(default_factory=list)
    applicability_violations: list[dict[str, str]] = field(default_factory=list)
    deferred: list[dict[str, Any]] = field(default_factory=list)

    @property
    def strategies(self) -> tuple[str, ...]:
        """The distinct strategies the gated paths exercise, in path order."""
        seen: dict[str, None] = {}
        for path in self.paths:
            seen.setdefault(_path_strategy(path), None)
        return tuple(seen)

    @property
    def violations(self) -> list[dict[str, str]]:
        return [*self.authorization_violations, *self.applicability_violations]

    @property
    def passed(self) -> bool:
        return not self.authorization_violations and not self.applicability_violations


def select_security_queries(
    suite: LoadedSuite,
) -> tuple[list[SecurityQuery], list[dict[str, Any]]]:
    """Retrieval-side security cases, then active goldens; plus the deferred list."""
    queries: list[SecurityQuery] = []
    deferred: list[dict[str, Any]] = []
    for case in suite.active(DatasetType.SECURITY):
        if case.attack_type in RETRIEVAL_SIDE_ATTACK_TYPES:
            queries.append(
                SecurityQuery(case.case_id, case.case_version, "security", case.query)
            )
        else:
            deferred.append(
                {
                    "case_id": case.case_id,
                    "case_version": case.case_version,
                    "attack_type": case.attack_type,
                    "owner": DEFERRED_OWNERS.get(case.attack_type, UNCLASSIFIED_OWNER),
                }
            )
    for golden in suite.active(DatasetType.GOLDEN_ANSWERABLE):
        queries.append(
            SecurityQuery(golden.case_id, golden.case_version, "golden", golden.query)
        )
    return queries, deferred


def run_security_evaluation(
    index: SecurityIndex,
    access: ResolvedAccess,
    queries: Sequence[SecurityQuery],
    deferred: Sequence[dict[str, Any]],
    retrieval_config: RetrievalConfig,
    paths: Sequence[str] = ALL_PATHS,
    *,
    active_lote: ResolvedLote,
) -> SecurityReport:
    """Run the gate. `queries` must be the ones the index was built for, in order.

    Raises `EvaluationHarnessError` when an unfiltered sanity check (dense, or
    lexical for a query with terms) does not find a forbidden point nearest: the
    gate would otherwise pass vacuously. `retrieval_config` has no built-in
    default: the caller passes the settings from `config/retrieval.yaml`."""
    if tuple(q.text for q in queries) != index.queries:
        raise EvaluationHarnessError(
            "the queries do not match the ones the security index was built for."
        )
    if active_lote.code != index.active_lote_code:
        raise EvaluationHarnessError(
            "the active lote code does not match the one the security index was "
            "built for."
        )
    retrievers = _retrievers(index, retrieval_config, paths)
    report = SecurityReport(deferred=list(deferred), paths=tuple(paths))
    sanity = _open_lexical_sanity(index)
    access_where, access_params = build_sql_access_clause(access)
    try:
        for query in queries:
            _sanity_check(index, query)
            _access_sanity_check(index, query, access)
            terms = query_terms(query.text).terms
            if terms:
                _lexical_sanity_check(sanity, query, terms)
                _access_lexical_sanity_check(
                    sanity, query, terms, access_where, access_params
                )
            else:
                report.bm25_no_term_queries += 1
            for path, retriever in retrievers:
                top_k = _path_top_k(path, retrieval_config)
                _gate(report, path, retriever, query, access, lote=None, top_k=top_k)
                _gate(
                    report,
                    path,
                    retriever,
                    query,
                    access,
                    lote=active_lote,
                    top_k=top_k,
                )
            report.query_count += 1
            if query.kind == "security":
                report.security_case_count += 1
            else:
                report.golden_query_count += 1
    finally:
        sanity.close()
    return report


class _UnavailableDense:
    """Harness-only dense leg that is always unavailable (Spec 008 R10).

    Constructed only by this gate, for the `hybrid_fallback_query` path. No flag,
    environment variable or config value reaches it."""

    strategy = Strategy.DENSE

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = 5,
        *,
        lote: object = None,
    ) -> RetrievalResult:
        raise RetrievalUnavailableError(FallbackReason.QDRANT_UNAVAILABLE)


class _AlwaysFailingScore(FakeReranker):
    """Harness-only reranker whose every `score` call fails as unavailable.

    `FakeReranker.fail_on_call` fails one numbered call; resetting the counter
    before each call makes it fail every call. Constructed only by this gate."""

    def __init__(self) -> None:
        super().__init__(fail_on_call=1)

    def score(self, query: str, texts: Sequence[str]) -> Any:
        self.score_calls = 0
        return super().score(query, texts)


def _rerank_config(config: RetrievalConfig) -> RetrievalConfig:
    """The gate asks the stage for every candidate the legs fetch (the widest
    pool the re-check must cover), not only the committed `rerank.depth`."""
    depth = config.fusion.candidate_depth
    return config.model_copy(
        update={"rerank": config.rerank.model_copy(update={"depth": depth})}
    )


def _path_top_k(path: str, config: RetrievalConfig) -> int:
    if path in RERANK_PATHS:
        return min(MAX_TOP_K, _rerank_config(config).rerank.depth)
    return MAX_TOP_K


def _preferring(queries: Sequence[str]) -> Any:
    """What the gate's fake reranker puts first: every forbidden, non-applicable
    and injection-style text (the worst case for a stage that trusts scores)."""
    probes = {
        text
        for q in queries
        for repeats in (2, 3)
        if (text := lexical_probe_text(q, repeats=repeats))
    }

    def prefer(text: str) -> bool:
        return FORBIDDEN_SENTINEL in text or INJECTION_TEXT in text or text in probes

    return prefer


def _path_strategy(path: str) -> str:
    if path in (PATH_DENSE, PATH_BM25):
        return path
    return Strategy.HYBRID.value


def _retrievers(
    index: SecurityIndex,
    config: RetrievalConfig,
    paths: Sequence[str],
) -> list[tuple[str, Retriever]]:
    """One retriever per gated path, all over the one throwaway index."""
    identity = IndexIdentity.from_dense(index.dense)
    built: list[tuple[str, Retriever]] = []
    for path in paths:
        retriever: Retriever
        if path == PATH_DENSE:
            retriever = build_retriever(
                Strategy.DENSE,
                identity,
                index.dense,
                index.embedder,
                index.lexical,
                config,
            )
        elif path == PATH_BM25:
            _check_standalone_open(index, identity)
            # The production standalone shape: no dense index, no embedder.
            retriever = build_retriever(
                Strategy.BM25, identity, None, None, index.lexical, config
            )
        elif path == PATH_HYBRID:
            retriever = build_retriever(
                Strategy.HYBRID,
                identity,
                index.dense,
                index.embedder,
                index.lexical,
                config,
            )
        elif path == PATH_FALLBACK_OPEN:
            retriever = FallbackRetriever(
                None,
                BM25Retriever(identity, index.lexical),
                FallbackReason.QDRANT_UNAVAILABLE,
            )
        elif path == PATH_FALLBACK_QUERY:
            bm25 = BM25Retriever(identity, index.lexical)
            retriever = FallbackRetriever(
                HybridRetriever(_UnavailableDense(), bm25, config.fusion), bm25, None
            )
        elif path in RERANK_PATHS:
            retriever = _rerank_retriever(path, index, identity, config)
        else:
            raise EvaluationHarnessError(f"unknown gate path '{path}'.")
        built.append((path, retriever))
    return built


def _rerank_retriever(
    path: str,
    index: SecurityIndex,
    identity: IndexIdentity,
    config: RetrievalConfig,
) -> Retriever:
    """The production composition (`build_retriever` with a reranker) over the
    throwaway index, with a `FakeReranker`. The open-time load happens here, as
    in `open_retrieval`: an eligible failure becomes the sticky open-stage skip."""
    reranker: FakeReranker
    open_skip: RerankSkipReason | None = None
    if path == PATH_RERANK:
        reranker = FakeReranker(prefer=_preferring(index.queries))
    elif path == PATH_RERANK_SKIP_OPEN:
        reranker = FakeReranker(fail_on_load=True)
    else:
        reranker = _AlwaysFailingScore()
    try:
        reranker.load()
    except Exception as error:  # noqa: BLE001 - classified; anything else re-raised
        mapped = classify_reranker_error(error)
        if mapped is None:
            raise
        open_skip = mapped.reason
    return build_retriever(
        Strategy.HYBRID,
        identity,
        index.dense,
        index.embedder,
        index.lexical,
        _rerank_config(config),
        reranker,
        open_skip,
    )


def _check_standalone_open(index: SecurityIndex, identity: IndexIdentity) -> None:
    """The production standalone open on the throwaway file: identity against the
    throwaway collection, then freshness of the seed chunks.

    `verify_fresh` cannot run as is: the file also holds the synthetic forbidden
    rows, which no repository document produces. So freshness is checked as
    "every chunk the seed repository and chunker produce is in the file, with the
    same version and hash". No Qdrant client and no embedder are used."""
    lexical = LexicalIndex.open(
        index.lexical_path, identity.collection, identity.index_version
    )
    try:
        lexical.check_identity(identity, index.chunker.identity, HASH_CONTRACT)
        tokenizer = FakeTokenizer()
        entries = asyncio.run(
            production_entries(index.seed_repository, index.chunker, tokenizer, None)
        )
        in_file = lexical.chunk_identities()
        missing = [
            point
            for point, payload in entries
            if (
                point,
                str(payload["document_id"]),
                int(payload["document_version"]),
                str(payload["content_hash"]),
            )
            not in in_file
        ]
    except LexicalIndexBindingError as error:
        raise EvaluationHarnessError(
            f"the security lexical file fails the standalone open: {safe_text(error)}"
        ) from None
    finally:
        lexical.close()
    if missing:
        raise EvaluationHarnessError(
            f"the security lexical file is stale against the seed repository "
            f"({len(missing)} chunk(s) missing)."
        )


def _lote_label(lote: ResolvedLote | None) -> str:
    return lote.code if lote is not None else "none"


def _gate(
    report: SecurityReport,
    path: str,
    retriever: Retriever,
    query: SecurityQuery,
    access: ResolvedAccess,
    *,
    lote: ResolvedLote | None,
    top_k: int = MAX_TOP_K,
) -> None:
    try:
        result = retriever.retrieve(query.text, access, top_k=top_k, lote=lote)
        if path in _FALLBACK_PATHS and (
            result.fallback_reason != FallbackReason.QDRANT_UNAVAILABLE.value
            or result.strategy != Strategy.BM25.value
        ):
            # A fallback path that did not fall back would gate nothing.
            raise EvaluationHarnessError(
                f"path '{path}' did not serve BM25 as the fallback for case "
                f"'{query.case_id}', so the gate would be vacuous."
            )
        if path not in _FALLBACK_PATHS and result.fallback_reason is not None:
            # A plain path that fell back gated a different strategy than named.
            raise EvaluationHarnessError(
                f"path '{path}' fell back ({result.fallback_reason}) for case "
                f"'{query.case_id}', so it did not gate the strategy it names."
            )
        if path in RERANK_PATHS:
            _check_rerank_path(report, path, result, query)
    except RetrievalAuthorizationError as error:
        document_id = error.document_id
        report.authorization_violations.append(
            _violation_row(
                query,
                path,
                document_id,
                lote,
                variant=(
                    forbidden_variant(document_id)
                    if is_forbidden_document(document_id)
                    else "check_hit_failed"
                ),
                detail=safe_text(error),
            )
        )
        return
    except LanguageApplicabilityError as error:
        report.applicability_violations.append(
            _violation_row(
                query,
                path,
                error.document_id,
                lote,
                variant=NON_APPLICABLE_VARIANT,
                detail=safe_text(error),
            )
        )
        return
    for hit in result.hits:
        if is_forbidden_document(hit.document_id):
            report.authorization_violations.append(
                _violation_row(
                    query,
                    path,
                    hit.document_id,
                    lote,
                    variant=forbidden_variant(hit.document_id),
                )
            )
        elif lote is not None and is_non_applicable_document(hit.document_id):
            report.applicability_violations.append(
                _violation_row(
                    query,
                    path,
                    hit.document_id,
                    lote,
                    variant=NON_APPLICABLE_VARIANT,
                )
            )


def _check_rerank_path(
    report: SecurityReport, path: str, result: RetrievalResult, query: SecurityQuery
) -> None:
    """A reranked path must show the stage it names: the reranker identity, and
    for a skip path exactly the expected reason and stage. Otherwise the gate
    would pass without exercising the path it claims to."""
    record = result.rerank
    if record is None:
        raise EvaluationHarnessError(
            f"path '{path}' recorded no rerank stage for case '{query.case_id}', "
            "so the gate would be vacuous."
        )
    expected = _EXPECTED_SKIP[path]
    seen = (
        None
        if record.skipped_reason is None
        else (record.skipped_reason, str(record.stage))
    )
    if seen != expected:
        raise EvaluationHarnessError(
            f"path '{path}' recorded skip {seen} instead of {expected} for case "
            f"'{query.case_id}', so the gate would be vacuous."
        )
    detail = {
        "reranker": {
            "model_id": record.model_id,
            "revision": record.revision,
            "max_length": record.max_length,
            "is_fake": record.is_fake,
        },
        "depth": record.depth,
        "skip": (None if seen is None else {"reason": seen[0], "stage": seen[1]}),
    }
    if report.path_details.setdefault(path, detail) != detail:
        raise EvaluationHarnessError(
            f"path '{path}' changed its rerank record between queries."
        )


def _violation_row(
    query: SecurityQuery,
    path: str,
    document_id: str,
    lote: ResolvedLote | None,
    *,
    variant: str,
    detail: str | None = None,
) -> dict[str, str]:
    row = {
        "case_id": query.case_id,
        "path": path,
        "strategy": _path_strategy(path),
        "lote": _lote_label(lote),
        "document_id": safe_text(document_id),
        "variant": variant,
    }
    if detail is not None:
        row["detail"] = detail
    return row


def _sanity_check(index: SecurityIndex, query: SecurityQuery) -> None:
    """Unfiltered, the nearest point must be forbidden, or the gate proves nothing."""
    vector = index.embedder.embed_query(query.text)
    points = index.client.query_points(
        index.collection,
        query=vector,
        using=DENSE_VECTOR_NAME,
        limit=SANITY_LIMIT,
        with_payload=True,
        with_vectors=False,
    ).points
    if not points:
        raise EvaluationHarnessError(
            f"sanity check failed for case '{query.case_id}': the nearest "
            "unfiltered point is not a forbidden fixture, so the gate would be vacuous."
        )
    best = points[0].score
    winners = [p for p in points if p.score is not None and p.score >= best - 1e-9]
    if not any(
        is_forbidden_document(str((p.payload or {}).get("document_id")))
        for p in winners
    ):
        raise EvaluationHarnessError(
            f"sanity check failed for case '{query.case_id}': the nearest "
            "unfiltered point is not a forbidden fixture, so the gate would be vacuous."
        )


def _open_lexical_sanity(index: SecurityIndex) -> sqlite3.Connection:
    """A harness-only read-only connection for the unfiltered lexical check."""
    try:
        connection = sqlite3.connect(
            f"file:{quote(str(index.lexical_path))}?mode=ro", uri=True
        )
    except sqlite3.Error:
        raise EvaluationHarnessError(
            "cannot open the security lexical file for the sanity check."
        ) from None
    connection.execute("PRAGMA query_only = ON")
    return connection


def _access_sanity_check(
    index: SecurityIndex, query: SecurityQuery, access: ResolvedAccess
) -> None:
    """With the access filter alone, the nearest point must be non-applicable."""
    vector = index.embedder.embed_query(query.text)
    points = index.client.query_points(
        index.collection,
        query=vector,
        using=DENSE_VECTOR_NAME,
        query_filter=dense_query_filter(access, None),
        limit=1,
        with_payload=True,
        with_vectors=False,
    ).points
    top = str((points[0].payload or {}).get("document_id")) if points else ""
    if not is_non_applicable_document(top):
        raise EvaluationHarnessError(
            f"access-only sanity check failed for case '{query.case_id}': the "
            "nearest filtered point is not a non-applicable fixture, so the gate "
            "would be vacuous."
        )


def _access_lexical_sanity_check(
    connection: sqlite3.Connection,
    query: SecurityQuery,
    terms: list[str],
    access_where: str,
    access_params: tuple[Any, ...],
) -> None:
    """With the access clause alone, the best BM25 row must be non-applicable."""
    sql = LEXICAL_ACCESS_SANITY_SQL.format(access_where=access_where)
    row = connection.execute(sql, (match_expression(terms), *access_params)).fetchone()
    top = str(row[0]) if row else ""
    if not is_non_applicable_document(top):
        raise EvaluationHarnessError(
            f"lexical access-only sanity check failed for case '{query.case_id}': "
            "the best filtered row is not a non-applicable fixture, so the gate "
            "would be vacuous."
        )


def _lexical_sanity_check(
    connection: sqlite3.Connection, query: SecurityQuery, terms: list[str]
) -> None:
    """Unfiltered, the best BM25 row must be forbidden (harness-only SQL: no
    access clause on purpose)."""
    row = connection.execute(LEXICAL_SANITY_SQL, (match_expression(terms),)).fetchone()
    top = str(row[0]) if row else ""
    if not is_forbidden_document(top):
        raise EvaluationHarnessError(
            f"lexical sanity check failed for case '{query.case_id}': the best "
            "unfiltered row is not a forbidden fixture, so the gate would be vacuous."
        )


SECURITY_RESULT_KIND = "security_evaluation"
SECURITY_SCHEMA_VERSION = "1.5"


def security_run_record(index: SecurityIndex, report: SecurityReport) -> dict[str, Any]:
    """One chunker's gate outcome (the 1.2 per-run fields under ``runs``)."""
    return {
        "chunker": index.chunker.identity.model_dump(mode="json"),
        "passed": report.passed,
        "query_count": report.query_count,
        "security_cases_run": report.security_case_count,
        "golden_queries_run": report.golden_query_count,
        "paths": list(report.paths),
        "strategies": list(report.strategies),
        "path_details": {
            path: report.path_details[path]
            for path in report.paths
            if path in report.path_details
        },
        "bm25_no_term_queries": report.bm25_no_term_queries,
        "violations": report.violations,
        "authorization_violations": report.authorization_violations,
        "applicability_violations": report.applicability_violations,
        "index": {
            "collection": index.collection,
            "index_version": index.dense.index_version,
            "embedder_is_fake": index.dense.settings.embedder_is_fake,
            "seed_document_count": len(index.seed_document_ids),
            "forbidden_points_per_variant": dict(index.points_per_variant),
            "lexical_rows_per_variant": dict(index.lexical_rows_per_variant),
            "non_applicable_rows_per_variant": dict(
                index.non_applicable_rows_per_variant
            ),
        },
    }


def security_document(
    *,
    runs: Sequence[tuple[SecurityIndex, SecurityReport]],
    suite: LoadedSuite,
    access: ResolvedAccess,
    duration_ms: float,
    created_at: str,
    repo_root: Any,
    lote_modes: Sequence[str | None],
) -> dict[str, Any]:
    """Result document: IDs, counts and verdicts only. No query or chunk text."""
    commit, dirty = git_state(repo_root)
    run_rows = [security_run_record(index, report) for index, report in runs]
    return {
        "kind": SECURITY_RESULT_KIND,
        "schema_version": SECURITY_SCHEMA_VERSION,
        "created_at": created_at,
        "git_commit": commit,
        "git_dirty": dirty,
        "passed": all(row["passed"] for row in run_rows),
        "evaluation_suite_id": suite.manifest.evaluation_suite_id,
        "evaluation_suite_version": suite.manifest.version,
        "access": {
            "role": "guest",
            "tenant_id": access.tenant_id,
            "allowed_access_scopes": sorted(
                str(s) for s in access.policy.allowed_access_scopes
            ),
        },
        "lote_modes": list(lote_modes),
        "runs": run_rows,
        "deferred": list(runs[0][1].deferred) if runs else [],
        "excluded_fixtures": EXCLUDED_FIXTURES,
        "duration_ms": round(duration_ms, 1),
    }
