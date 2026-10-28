"""Authorization hard gate over a throwaway security index (Spec 006 R8).

Every retrieval-side security case and every active golden query runs through
the production `dense`, `bm25` and `hybrid` retrievers (built by
`build_retriever`) with the one server-resolved `ResolvedAccess` passed in. A
case's own `access_context` is never consulted, and query text never reaches the
filter. A forbidden document in the results, or a `check_hit` failure, is a
violation. Violations name `case_id`, `document_id` and variant, never text.
"""

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from way2australia_rag.evaluation.errors import EvaluationHarnessError
from way2australia_rag.evaluation.models import DatasetType, LoadedSuite
from way2australia_rag.evaluation.security_index import (
    FORBIDDEN_VARIANTS,
    SECURITY_COLLECTION_PREFIX,
    SecurityIndex,
    forbidden_variant,
    is_forbidden_document,
)
from way2australia_rag.ingestion.store import DENSE_VECTOR_NAME
from way2australia_rag.lexical.tokenizer import query_terms
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.bm25 import match_expression
from way2australia_rag.retrieval.errors import RetrievalAuthorizationError
from way2australia_rag.retrieval.fusion import FusionConfig
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
# Fusion settings do not affect what is authorized; the CLI passes the real config.
DEFAULT_RETRIEVAL_CONFIG = RetrievalConfig(
    schema_version="1.0",
    default_strategy=Strategy.DENSE,
    fusion=FusionConfig(
        method="rrf",
        k=60,
        weights={"dense": 1.0, "bm25": 1.0},
        candidate_depth=MAX_TOP_K,
    ),
)
LEXICAL_SANITY_SQL = (
    "SELECT c.document_id FROM chunk_terms "
    "JOIN chunks c ON c.rowid = chunk_terms.rowid "
    "WHERE chunk_terms MATCH ? ORDER BY bm25(chunk_terms) ASC, c.point_id ASC LIMIT 1"
)

__all__ = [
    "DEFERRED_OWNERS",
    "EXCLUDED_FIXTURES",
    "FORBIDDEN_VARIANTS",
    "RETRIEVAL_SIDE_ATTACK_TYPES",
    "SECURITY_COLLECTION_PREFIX",
    "SecurityQuery",
    "SecurityReport",
    "run_security_evaluation",
    "security_document",
    "select_security_queries",
]


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
    strategies: tuple[str, ...] = tuple(s.value for s in STRATEGIES)
    violations: list[dict[str, str]] = field(default_factory=list)
    deferred: list[dict[str, Any]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


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
    retrieval_config: RetrievalConfig = DEFAULT_RETRIEVAL_CONFIG,
    strategies: Sequence[Strategy] = STRATEGIES,
) -> SecurityReport:
    """Run the gate. `queries` must be the ones the index was built for, in order.

    Raises `EvaluationHarnessError` when an unfiltered sanity check (dense, or
    lexical for a query with terms) does not find a forbidden point nearest: the
    gate would otherwise pass vacuously."""
    if tuple(q.text for q in queries) != index.queries:
        raise EvaluationHarnessError(
            "the queries do not match the ones the security index was built for."
        )
    retrievers = [
        (
            strategy,
            build_retriever(
                strategy, index.dense, index.embedder, index.lexical, retrieval_config
            ),
        )
        for strategy in strategies
    ]
    report = SecurityReport(
        deferred=list(deferred), strategies=tuple(s.value for s in strategies)
    )
    sanity = _open_lexical_sanity(index)
    try:
        for query in queries:
            _sanity_check(index, query)
            terms = query_terms(query.text).terms
            if terms:
                _lexical_sanity_check(sanity, query, terms)
            else:
                report.bm25_no_term_queries += 1
            for strategy, retriever in retrievers:
                _gate(report, strategy, retriever, query, access)
            report.query_count += 1
            if query.kind == "security":
                report.security_case_count += 1
            else:
                report.golden_query_count += 1
    finally:
        sanity.close()
    return report


def _gate(
    report: SecurityReport,
    strategy: Strategy,
    retriever: Any,
    query: SecurityQuery,
    access: ResolvedAccess,
) -> None:
    try:
        result = retriever.retrieve(query.text, access, top_k=MAX_TOP_K)
    except RetrievalAuthorizationError as error:
        # The store returned a point the policy forbids; the error carries the
        # hit's document ID.
        document_id = error.document_id
        report.violations.append(
            {
                "case_id": query.case_id,
                "strategy": strategy.value,
                "document_id": safe_text(document_id),
                "variant": (
                    forbidden_variant(document_id)
                    if is_forbidden_document(document_id)
                    else "check_hit_failed"
                ),
                "detail": safe_text(error),
            }
        )
        return
    for hit in result.hits:
        if is_forbidden_document(hit.document_id):
            report.violations.append(
                {
                    "case_id": query.case_id,
                    "strategy": strategy.value,
                    "document_id": hit.document_id,
                    "variant": forbidden_variant(hit.document_id),
                }
            )


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
    top = str((points[0].payload or {}).get("document_id")) if points else ""
    if not is_forbidden_document(top):
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
SECURITY_SCHEMA_VERSION = "1.1"


def security_document(
    *,
    index: SecurityIndex,
    report: SecurityReport,
    suite: LoadedSuite,
    access: ResolvedAccess,
    duration_ms: float,
    created_at: str,
    repo_root: Any,
) -> dict[str, Any]:
    """Result document: IDs, counts and verdicts only. No query or chunk text."""
    commit, dirty = git_state(repo_root)
    return {
        "kind": SECURITY_RESULT_KIND,
        "schema_version": SECURITY_SCHEMA_VERSION,
        "created_at": created_at,
        "git_commit": commit,
        "git_dirty": dirty,
        "passed": report.passed,
        "evaluation_suite_id": suite.manifest.evaluation_suite_id,
        "evaluation_suite_version": suite.manifest.version,
        "access": {
            "role": "guest",
            "tenant_id": access.tenant_id,
            "allowed_access_scopes": sorted(
                str(s) for s in access.policy.allowed_access_scopes
            ),
        },
        "index": {
            "collection": index.collection,
            "index_version": index.dense.index_version,
            "embedder_is_fake": index.dense.settings.embedder_is_fake,
            "seed_document_count": len(index.seed_document_ids),
            "forbidden_points_per_variant": dict(index.points_per_variant),
            "lexical_rows_per_variant": dict(index.lexical_rows_per_variant),
        },
        "query_count": report.query_count,
        "security_cases_run": report.security_case_count,
        "golden_queries_run": report.golden_query_count,
        "strategies": list(report.strategies),
        "bm25_no_term_queries": report.bm25_no_term_queries,
        "violations": report.violations,
        "deferred": report.deferred,
        "excluded_fixtures": EXCLUDED_FIXTURES,
        "duration_ms": round(duration_ms, 1),
    }
