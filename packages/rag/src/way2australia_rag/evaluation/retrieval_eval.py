"""Retrieval evaluation runner (Spec 006 R4, R5, R6, R7; Spec 007 R9).

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
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.metrics import (
    dedupe_documents,
    hit_rate_at_k,
    percentile,
    random_hit_rate,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.models import LexicalIdentity, RetrievalResult

OVERLAP_CASES = ("g004", "u001")
UNANSWERABLE_STATUS = "not_evaluable_before_generation"
UNANSWERABLE_OWNER = "roadmap-10"


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


def score_distribution(scores: Sequence[float | None]) -> dict[str, float | None]:
    """min, p50, p95, max of the top-1 scores (nearest rank); None when empty.

    Informational only: it has no threshold and is never answerability (R10)."""
    values = [s for s in scores if s is not None]
    if not values:
        return {"min": None, "p50": None, "p95": None, "max": None}
    return {
        "min": round(min(values), 4),
        "p50": round(percentile(values, 50), 4),
        "p95": round(percentile(values, 95), 4),
        "max": round(max(values), 4),
    }


def unanswerable_report(
    suite: LoadedSuite,
    retriever: Retriever,
    access: ResolvedAccess,
    top_k: int,
    golden_top1: Sequence[float | None],
    score_kind: str = "dense_cosine",
) -> dict[str, Any]:
    """Top-1 score per active unanswerable case. Latency is not recorded, so
    p50/p95 of the golden run stay comparable with 1.0. No pass or fail."""
    rows: list[dict[str, Any]] = []
    for case in suite.active(DatasetType.UNANSWERABLE_REFUSAL):
        result = retriever.retrieve(case.query, access, top_k)
        score = round(result.hits[0].score, 4) if result.hits else None
        rows.append(
            {
                "case_id": case.case_id,
                "case_version": case.case_version,
                "top1_score": score,
            }
        )
    return {
        "status": UNANSWERABLE_STATUS,
        "owner": UNANSWERABLE_OWNER,
        "n": len(rows),
        "score_kind": score_kind,
        "top1_score": score_distribution([r["top1_score"] for r in rows]),
        "golden_top1_score": score_distribution(golden_top1),
        "cases": rows,
    }


def document_leg_ranks(result: RetrievalResult) -> dict[str, dict[str, int]]:
    """Per leg, the document rank (after dedupe, at candidate depth) of every
    document the leg returned. A hybrid result carries each leg's deduped
    ranking; a single-leg `bm25` run reports its own document ranks."""
    if result.leg_document_ranks is not None:
        return {
            leg: {doc: position for position, doc in enumerate(ranked, 1)}
            for leg, ranked in result.leg_document_ranks.items()
        }
    ranked = dedupe_documents(result.hits)
    return {result.strategy: {doc: position for position, doc in enumerate(ranked, 1)}}


def _leg_ranks_for(
    result: RetrievalResult, relevant: set[str]
) -> dict[str, dict[str, int | None]] | None:
    if result.strategy == Strategy.DENSE.value:
        return None
    legs = document_leg_ranks(result)
    return {
        leg: {doc: ranks.get(doc) for doc in sorted(relevant)}
        for leg, ranks in legs.items()
    }


def _lexical_report(identity: LexicalIdentity | None) -> dict[str, Any] | None:
    if identity is None:
        return None
    return {
        "label": identity.label,
        "tokenizer_name": identity.tokenizer_name,
        "tokenizer_version": identity.tokenizer_version,
        "source_chunk_digest": identity.source_chunk_digest,
        "chunk_count": identity.chunk_count,
    }


def _fusion_report(fusion: FusionConfig | None) -> dict[str, Any] | None:
    if fusion is None:
        return None
    return {
        "method": fusion.method,
        "k": fusion.k,
        "weights": dict(fusion.weights),
        "candidate_depth": fusion.candidate_depth,
    }


def _leg_latency(results: Sequence[RetrievalResult]) -> dict[str, Any] | None:
    legs: dict[str, list[float]] = {}
    for result in results:
        for leg, value in (result.leg_latency_ms or {}).items():
            legs.setdefault(leg, []).append(value)
    if not legs:
        return None
    return {
        leg: {
            "p50": round(percentile(values, 50), 3),
            "p95": round(percentile(values, 95), 3),
        }
        for leg, values in sorted(legs.items())
    }


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
            f"{golden_id} overlaps unanswerable {unanswerable_id}; "
            "both are active cases."
        )
    return notes


def run_retrieval_evaluation(
    *,
    retriever: Retriever,
    index: DenseIndex,
    embedder: Embedder,
    access: ResolvedAccess,
    suite: LoadedSuite,
    release_id: str,
    top_k: int,
    authorities: Mapping[str, str],
    registry_languages: Sequence[str],
    repo_root: Path,
    fusion: FusionConfig | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Run the active golden cases, then the active unanswerable cases, and return
    the 2.1 result document. `fusion` is required for (and only recorded by) the
    `hybrid` strategy.

    Unanswerable cases contribute their top-1 score only; their latency is
    excluded from the p50/p95 figures.
    """
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

    strategy = Strategy(retriever.strategy)
    if strategy == Strategy.HYBRID and fusion is None:
        raise EvaluationConfigurationError(
            "the hybrid strategy needs its fusion config."
        )
    started = perf_counter()
    warm_up = retriever.retrieve(cases[0].query, access, top_k)  # unmeasured
    warmup_ms = (perf_counter() - started) * 1000.0
    # A real BgeM3Embedder reports no device until the model has loaded.
    device = embedder.device

    lexical_identity = warm_up.lexical
    rows: list[dict[str, Any]] = []
    results: list[RetrievalResult] = []
    section_rows: list[dict[str, Any]] = []
    for case in cases:
        result = retriever.retrieve(case.query, access, top_k)
        results.append(result)
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
                "query_terms_truncated": result.query_terms_truncated,
                "leg_ranks": _leg_ranks_for(result, relevant),
            }
        )
        section_rows.append(
            {
                "ranked_section_ids": dedupe_sections(result.hits),
                "relevant_section_ids": list(case.relevant_section_ids),
            }
        )

    latencies = [r["latency_ms"] for r in rows]
    unanswerable = unanswerable_report(
        suite,
        retriever,
        access,
        top_k,
        [r["top1_score"] for r in rows],
        warm_up.score_kind,
    )
    truncated = (
        None
        if strategy == Strategy.DENSE
        else sum(1 for r in rows if r["query_terms_truncated"])
    )
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
        "retrieval_strategy": strategy.value,
        "score_kind": warm_up.score_kind,
        "fusion": _fusion_report(fusion) if strategy == Strategy.HYBRID else None,
        "lexical_index": _lexical_report(lexical_identity),
        "truncated_query_count": truncated,
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
        "unanswerable": unanswerable,
        "latency_ms": {
            "p50": round(percentile(latencies, 50), 3),
            "p95": round(percentile(latencies, 95), 3),
            "warmup_ms": round(warmup_ms, 3),
            "measured_cases": len(rows),
            "legs": _leg_latency(results),
        },
        "cases": rows,
        "notes": _notes(suite, top_k=top_k, document_count=document_count, n=len(rows)),
    }
