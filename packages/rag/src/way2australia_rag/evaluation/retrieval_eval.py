"""Retrieval evaluation runner (Spec 006 R4, R5, R6, R7).

Every case is retrieved with the one server-resolved `ResolvedAccess` passed in;
a case's own `access_context` is never consulted. Read-only on Qdrant, on
`evaluation/` and on `knowledge/`. The result document holds no query text,
chunk text, absolute paths or secrets. The CLI is the only writer.
"""

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    CaseStatus,
    DatasetType,
    GoldenCase,
    LoadedSuite,
)
from way2australia_rag.evaluation.results import RESULT_KIND, SCHEMA_VERSION
from way2australia_rag.evaluation.sections import (
    dedupe_sections,
    section_report,
)
from way2australia_rag.evaluation.slices import (
    SMALL_SAMPLE_THRESHOLD,
    absent_query_languages,
    aggregate,
    slice_by,
    source_authority_key,
)
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.retrieval.access import ResolvedAccess, build_access_filter
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.metrics import (
    dedupe_documents,
    hit_rate_at_k,
    percentile,
    random_hit_rate,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.retriever import DenseRetriever

RETRIEVAL_STRATEGY = "dense"
OVERLAP_CASES = ("g004", "u001")


def active_golden_cases(suite: LoadedSuite) -> list[GoldenCase]:
    """Active goldens in dataset order. An active golden must be answerable and
    have relevant documents: `validate-evaluation` enforces it, and a quality run
    never silently drops one."""
    cases: list[GoldenCase] = suite.active(DatasetType.GOLDEN_ANSWERABLE)
    for case in cases:
        if not case.answerable or not case.relevant_document_ids:
            raise EvaluationConfigurationError(
                f"active golden case '{case.case_id}' is not answerable or has no "
                "relevant_document_ids; run `make validate-evaluation`."
            )
    return cases


def require_active_suite(suite: LoadedSuite) -> None:
    status = suite.manifest.status
    if status != CaseStatus.ACTIVE.value:
        raise EvaluationConfigurationError(
            f"suite '{suite.manifest.evaluation_suite_id}' has status "
            f"'{status}'; only an active suite is evaluated."
        )


def require_real_embedder(embedder: Embedder) -> None:
    if embedder.info.is_fake:
        raise EvaluationConfigurationError(
            "the configured embedder is fake; eval-retrieval measures quality and "
            "never runs on a fake embedder (use `make retrieval-baseline "
            'BASELINE_ARGS="--embedder fake --allow-fake"` for plumbing checks).'
        )


def require_real_index(index: DenseIndex) -> None:
    if index.settings.embedder_is_fake:
        raise EvaluationConfigurationError(
            "the index was built with the fake embedder; eval-retrieval refuses it "
            '(use `make retrieval-baseline BASELINE_ARGS="--embedder fake '
            '--allow-fake"` for plumbing checks).'
        )


def _notes(suite: LoadedSuite, *, top_k: int, document_count: int, n: int) -> list[str]:
    notes = [
        f"Top-{top_k} over {document_count} indexed documents is optimistic; compare "
        f"HitRate@{top_k} with the random expectation "
        f"min(1, {top_k}/{document_count}).",
        f"min(1, {top_k}/{document_count}) understates the random rate for cases "
        "with several relevant documents.",
        f"One case equals 1/{n} of HitRate ({1 / n:.3f}).",
        "Every document is a single chunk, so section-level and document-level "
        "results coincide.",
        "The index was not verified against the declared release's document snapshot.",
        "Model load and the warm-up query are excluded from p50/p95.",
    ]
    active_golden = {c.case_id for c in suite.active(DatasetType.GOLDEN_ANSWERABLE)}
    active_unanswerable = {
        c.case_id for c in suite.active(DatasetType.UNANSWERABLE_REFUSAL)
    }
    golden_id, unanswerable_id = OVERLAP_CASES
    if golden_id in active_golden and unanswerable_id in active_unanswerable:
        notes.append(
            f"{golden_id} overlaps unanswerable {unanswerable_id} and stays a "
            "counted miss until a human resolves it."
        )
    return notes


def run_retrieval_evaluation(
    *,
    retriever: DenseRetriever,
    index: DenseIndex,
    embedder: Embedder,
    access: ResolvedAccess,
    suite: LoadedSuite,
    release_id: str,
    top_k: int,
    authorities: Mapping[str, str],
    registry_languages: Sequence[str],
    repo_root: Path,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Run the active golden cases and return the 2.0 result document."""
    require_active_suite(suite)
    require_real_embedder(embedder)
    require_real_index(index)
    cases = active_golden_cases(suite)
    if not cases:
        raise EvaluationConfigurationError("no active golden cases to run.")
    document_count = index.document_count(build_access_filter(access))
    if document_count < 1:
        raise EvaluationConfigurationError(
            "no documents are visible under the access filter."
        )

    started = perf_counter()
    retriever.retrieve(cases[0].query, access, top_k)  # unmeasured warm-up
    warmup_ms = (perf_counter() - started) * 1000.0
    # A real BgeM3Embedder reports no device until the model has loaded.
    device = embedder.device

    rows: list[dict[str, Any]] = []
    section_rows: list[dict[str, Any]] = []
    for case in cases:
        result = retriever.retrieve(case.query, access, top_k)
        ranked = dedupe_documents(result.hits)
        relevant = set(case.relevant_document_ids)
        top1 = round(result.hits[0].score, 4) if result.hits else None
        rows.append(
            {
                "case_id": case.case_id,
                "case_version": case.case_version,
                "query_language": case.query_language,
                "category": case.category,
                "source_authority": source_authority_key(
                    case.relevant_document_ids, authorities
                ),
                "ranked_document_ids": ranked,
                "relevant_document_ids": sorted(relevant),
                "hit": hit_rate_at_k(ranked, relevant, top_k) == 1.0,
                "recall": recall_at_k(ranked, relevant, top_k),
                "reciprocal_rank": reciprocal_rank(ranked, relevant),
                "top1_score": top1,
                "latency_ms": round(result.latency_ms, 3),
            }
        )
        section_rows.append(
            {
                "ranked_section_ids": dedupe_sections(result.hits),
                "relevant_section_ids": list(case.relevant_section_ids),
            }
        )

    latencies = [r["latency_ms"] for r in rows]
    settings = index.settings
    commit, dirty = git_state(repo_root)
    manifest = suite.manifest
    types = (
        DatasetType.GOLDEN_ANSWERABLE,
        DatasetType.UNANSWERABLE_REFUSAL,
        DatasetType.SECURITY,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": RESULT_KIND,
        "created_at": clock().astimezone(UTC).isoformat(),
        "git_commit": commit,
        "git_dirty": dirty,
        "evaluation_suite_id": manifest.evaluation_suite_id,
        "evaluation_suite_version": manifest.version,
        "evaluation_suite": {
            "status": manifest.status,
            "cases_by_type": {t.value: len(suite.cases(t)) for t in types},
            "excluded_by_status": {t.value: suite.excluded_by_status(t) for t in types},
        },
        "declared_knowledge_release_id": release_id,
        "release_snapshot_verified": False,
        "collection": index.collection,
        "index_version": index.index_version,
        "index_settings": settings.model_dump(mode="json"),
        "retrieval_strategy": RETRIEVAL_STRATEGY,
        "top_k": top_k,
        "device": device,
        "embedder_is_fake": settings.embedder_is_fake,
        "case_count": len(rows),
        "excluded_case_count": len(suite.goldens) - len(rows),
        "document_count": document_count,
        "random_hit_rate_at_k": round(random_hit_rate(top_k, document_count), 4),
        "random_hit_rate_formula": f"min(1, {top_k}/{document_count})",
        "metrics": {
            "overall": aggregate(rows, top_k),
            "by_query_language": slice_by(rows, "query_language", top_k),
            "by_category": slice_by(rows, "category", top_k),
            "by_source_authority": slice_by(rows, "source_authority", top_k),
        },
        "absent_query_languages": absent_query_languages(
            registry_languages, [r["query_language"] for r in rows]
        ),
        "small_sample_threshold": SMALL_SAMPLE_THRESHOLD,
        "section_level": section_report(section_rows, top_k),
        "latency_ms": {
            "p50": round(percentile(latencies, 50), 3),
            "p95": round(percentile(latencies, 95), 3),
            "warmup_ms": round(warmup_ms, 3),
            "measured_cases": len(rows),
        },
        "cases": rows,
        "notes": _notes(suite, top_k=top_k, document_count=document_count, n=len(rows)),
    }
