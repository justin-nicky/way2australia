"""Authorization hard gate over a throwaway security index (Spec 006 R8, Spec 008 R10).

Every retrieval-side security case and every active golden query runs through
five paths: the production `dense`, `bm25` and `hybrid` retrievers (built by
`build_retriever`), and the two `hybrid` fallback paths (`hybrid_fallback_open`,
`hybrid_fallback_query`), with the one server-resolved `ResolvedAccess` passed in. A
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
    FORBIDDEN_VARIANTS,
    SECURITY_COLLECTION_PREFIX,
    SecurityIndex,
    forbidden_variant,
    is_forbidden_document,
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
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.bm25 import BM25Retriever, match_expression
from way2australia_rag.retrieval.errors import (
    FallbackReason,
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
PATHS = (PATH_DENSE, PATH_BM25, PATH_HYBRID, PATH_FALLBACK_OPEN, PATH_FALLBACK_QUERY)
_FALLBACK_PATHS = frozenset({PATH_FALLBACK_OPEN, PATH_FALLBACK_QUERY})
LEXICAL_SANITY_SQL = (
    "SELECT c.document_id FROM chunk_terms "
    "JOIN chunks c ON c.rowid = chunk_terms.rowid "
    "WHERE chunk_terms MATCH ? ORDER BY bm25(chunk_terms) ASC, c.point_id ASC LIMIT 1"
)

__all__ = [
    "DEFERRED_OWNERS",
    "EXCLUDED_FIXTURES",
    "FORBIDDEN_VARIANTS",
    "PATHS",
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
    violations: list[dict[str, str]] = field(default_factory=list)
    deferred: list[dict[str, Any]] = field(default_factory=list)

    @property
    def strategies(self) -> tuple[str, ...]:
        """The distinct strategies the gated paths exercise, in path order."""
        seen: dict[str, None] = {}
        for path in self.paths:
            seen.setdefault(_path_strategy(path), None)
        return tuple(seen)

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
    retrieval_config: RetrievalConfig,
    paths: Sequence[str] = PATHS,
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
    retrievers = _retrievers(index, retrieval_config, paths)
    report = SecurityReport(deferred=list(deferred), paths=tuple(paths))
    sanity = _open_lexical_sanity(index)
    try:
        for query in queries:
            _sanity_check(index, query)
            terms = query_terms(query.text).terms
            if terms:
                _lexical_sanity_check(sanity, query, terms)
            else:
                report.bm25_no_term_queries += 1
            for path, retriever in retrievers:
                _gate(report, path, retriever, query, access)
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
        self, query_text: str, access: ResolvedAccess, top_k: int = 5
    ) -> RetrievalResult:
        raise RetrievalUnavailableError(FallbackReason.QDRANT_UNAVAILABLE)


def _path_strategy(path: str) -> str:
    if path in (PATH_DENSE, PATH_BM25):
        return path
    return Strategy.HYBRID.value


def _retrievers(
    index: SecurityIndex, config: RetrievalConfig, paths: Sequence[str]
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
        else:
            raise EvaluationHarnessError(f"unknown gate path '{path}'.")
        built.append((path, retriever))
    return built


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


def _gate(
    report: SecurityReport,
    path: str,
    retriever: Retriever,
    query: SecurityQuery,
    access: ResolvedAccess,
) -> None:
    try:
        result = retriever.retrieve(query.text, access, top_k=MAX_TOP_K)
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
    except RetrievalAuthorizationError as error:
        # The store returned a point the policy forbids; the error carries the
        # hit's document ID.
        document_id = error.document_id
        report.violations.append(
            {
                "case_id": query.case_id,
                "path": path,
                "strategy": _path_strategy(path),
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
                    "path": path,
                    "strategy": _path_strategy(path),
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
SECURITY_SCHEMA_VERSION = "1.3"


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
        "bm25_no_term_queries": report.bm25_no_term_queries,
        "violations": report.violations,
        "index": {
            "collection": index.collection,
            "index_version": index.dense.index_version,
            "embedder_is_fake": index.dense.settings.embedder_is_fake,
            "seed_document_count": len(index.seed_document_ids),
            "forbidden_points_per_variant": dict(index.points_per_variant),
            "lexical_rows_per_variant": dict(index.lexical_rows_per_variant),
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
        "runs": run_rows,
        "deferred": list(runs[0][1].deferred) if runs else [],
        "excluded_fixtures": EXCLUDED_FIXTURES,
        "duration_ms": round(duration_ms, 1),
    }
