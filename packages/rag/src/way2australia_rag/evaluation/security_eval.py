"""Authorization hard gate over a throwaway security index (Spec 006 R8).

Every retrieval-side security case and every active golden query runs through
`DenseRetriever` with the one server-resolved `ResolvedAccess` passed in. A
case's own `access_context` is never consulted, and query text never reaches the
filter. A forbidden document in the results, or a `check_hit` failure, is a
violation. Violations name `case_id`, `document_id` and variant, never text.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

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
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.errors import RetrievalAuthorizationError
from way2australia_rag.retrieval.retriever import MAX_TOP_K, DenseRetriever
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
_HIT_DOCUMENT = re.compile(r"hit for document '([^']*)'")

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
) -> SecurityReport:
    """Run the gate. `queries` must be the ones the index was built for, in order.

    Raises `EvaluationHarnessError` when the unfiltered sanity check does not find
    a forbidden point nearest (the gate would otherwise pass vacuously)."""
    if tuple(q.text for q in queries) != index.queries:
        raise EvaluationHarnessError(
            "the queries do not match the ones the security index was built for."
        )
    retriever = DenseRetriever(index.dense, index.embedder)
    report = SecurityReport(deferred=list(deferred))
    for query in queries:
        _sanity_check(index, query)
        try:
            result = retriever.retrieve(query.text, access, top_k=MAX_TOP_K)
        except RetrievalAuthorizationError as error:
            # The store returned a point the policy forbids. The message names the
            # document ID and field names only (never text).
            named = _HIT_DOCUMENT.search(str(error))
            document_id = named.group(1) if named else ""
            report.violations.append(
                {
                    "case_id": query.case_id,
                    "document_id": safe_text(document_id),
                    "variant": (
                        forbidden_variant(document_id)
                        if is_forbidden_document(document_id)
                        else "check_hit_failed"
                    ),
                    "detail": safe_text(error),
                }
            )
        else:
            for hit in result.hits:
                if is_forbidden_document(hit.document_id):
                    report.violations.append(
                        {
                            "case_id": query.case_id,
                            "document_id": hit.document_id,
                            "variant": forbidden_variant(hit.document_id),
                        }
                    )
        report.query_count += 1
        if query.kind == "security":
            report.security_case_count += 1
        else:
            report.golden_query_count += 1
    return report


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


SECURITY_RESULT_KIND = "security_evaluation"
SECURITY_SCHEMA_VERSION = "1.0"


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
        },
        "query_count": report.query_count,
        "security_cases_run": report.security_case_count,
        "golden_queries_run": report.golden_query_count,
        "violations": report.violations,
        "deferred": report.deferred,
        "excluded_fixtures": EXCLUDED_FIXTURES,
        "duration_ms": round(duration_ms, 1),
    }
