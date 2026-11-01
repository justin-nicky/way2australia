"""Retrieval evaluation runner (Spec 006 R4, R5, R6, R7; Spec 007 R9).

Every case is retrieved with the one server-resolved `ResolvedAccess` passed in;
a case's own `access_context` is never consulted. Read-only on Qdrant, on
`evaluation/` and on `knowledge/`. The result document holds no query text,
chunk text, absolute paths or secrets. The CLI is the only writer.
"""

from collections import Counter
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
    UnanswerableCase,
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
from way2australia_rag.ingestion.settings import IndexSettings
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.metrics import (
    dedupe_documents,
    hit_rate_at_k,
    percentile,
    random_hit_rate,
    recall_at_k,
    reciprocal_rank,
)
from way2australia_rag.retrieval.models import LexicalIdentity, RetrievalResult
from way2australia_rag.retrieval.strategy import QdrantTimeouts

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


def require_real_index(identity: IndexIdentity) -> None:
    if identity.embedder_is_fake:
        raise EvaluationConfigurationError(
            "the index was built with the fake embedder; eval-retrieval refuses it "
            '(use `make retrieval-baseline BASELINE_ARGS="--embedder fake '
            '--allow-fake"` for plumbing checks).'
        )


def _require_settings_if_dense_served(
    index_settings: IndexSettings | None, served: set[str]
) -> None:
    """A run served by `dense` or `hybrid` reached Qdrant, so it must record the
    full index settings; only `bm25` (standalone or a hybrid open-time fallback)
    may have none (Spec 008 R8, T3 review F2)."""
    if index_settings is None and served - {Strategy.BM25.value}:
        raise EvaluationConfigurationError(
            "index_settings is required unless every case is served by 'bm25' "
            f"(served: {', '.join(sorted(served))}); a run that reached Qdrant "
            "records the index settings."
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
    results: Sequence[tuple[UnanswerableCase, RetrievalResult]],
    golden_top1: Sequence[float | None],
    score_kind: str | None,
) -> dict[str, Any]:
    """Top-1 score per active unanswerable case. Latency is not recorded, so
    p50/p95 of the golden run stay comparable with 1.0. No pass or fail.

    `score_kind` is `None` when the measured cases mixed score kinds: scores of
    different kinds are not comparable, so both distributions are then `null`."""
    rows: list[dict[str, Any]] = []
    for case, result in results:
        score = round(result.hits[0].score, 4) if result.hits else None
        rows.append(
            {
                "case_id": case.case_id,
                "case_version": case.case_version,
                "top1_score": score,
            }
        )
    mixed = score_kind is None
    return {
        "status": UNANSWERABLE_STATUS,
        "owner": UNANSWERABLE_OWNER,
        "n": len(rows),
        "served_strategies": sorted({r.strategy for _c, r in results}),
        "score_kind": score_kind,
        "top1_score": (
            None if mixed else score_distribution([r["top1_score"] for r in rows])
        ),
        "golden_top1_score": None if mixed else score_distribution(golden_top1),
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
) -> dict[str, dict[str, int | None] | None] | None:
    if result.strategy == Strategy.DENSE.value:
        return None
    legs = document_leg_ranks(result)
    ranks_by_leg: dict[str, dict[str, int | None] | None] = {
        leg: {doc: ranks.get(doc) for doc in sorted(relevant)}
        for leg, ranks in legs.items()
    }
    if result.fallback_reason is not None:
        ranks_by_leg = {"dense": None, **ranks_by_leg}  # the dense leg never ran
    return ranks_by_leg


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


def _path_label(result: RetrievalResult) -> str:
    """The served path of one result: `<served>` or `<served>+fallback:<reason>`."""
    if result.fallback_reason is None:
        return result.strategy
    return f"{result.strategy}+fallback:{result.fallback_reason}"


def _latency_by_path(
    results: Sequence[RetrievalResult], latencies: Sequence[float]
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[float]] = {}
    for result, value in zip(results, latencies, strict=True):
        groups.setdefault(_path_label(result), []).append(value)
    return {
        label: {
            "p50": round(percentile(values, 50), 3),
            "p95": round(percentile(values, 95), 3),
            "n": len(values),
        }
        for label, values in sorted(groups.items())
    }


def _single(values: set[str]) -> str | None:
    return next(iter(values)) if len(values) == 1 else None


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
    identity: IndexIdentity,
    document_count: int,
    embedder: Embedder | None,
    index_settings: IndexSettings | None = None,
    access: ResolvedAccess,
    suite: LoadedSuite,
    release_id: str,
    top_k: int,
    authorities: Mapping[str, str],
    registry_languages: Sequence[str],
    repo_root: Path,
    fusion: FusionConfig | None = None,
    qdrant_timeouts: QdrantTimeouts | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Run the active golden cases, then the active unanswerable cases, and return
    the 2.2 result document. `fusion` is required when `hybrid` is requested and
    recorded when any case was served by `hybrid`. `qdrant_timeouts` is recorded
    as given (`None` for `bm25`).

    Unanswerable cases contribute their top-1 score only; their latency is
    excluded from the p50/p95 figures.
    """
    require_active_suite(suite)
    if embedder is not None:  # `bm25` builds none
        require_real_embedder(embedder)
    require_real_index(identity)
    cases = active_golden_cases(suite)
    if not cases:
        raise EvaluationConfigurationError("no active golden cases to run.")
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
    _require_settings_if_dense_served(index_settings, {warm_up.strategy})
    # A real BgeM3Embedder reports no device until the model has loaded.
    device = embedder.device if embedder is not None else None

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
                "served_strategy": result.strategy,
                "fallback_reason": result.fallback_reason,
            }
        )
        section_rows.append(
            {
                "ranked_section_ids": dedupe_sections(result.hits),
                "relevant_section_ids": list(case.relevant_section_ids),
            }
        )

    latencies = [r["latency_ms"] for r in rows]
    unanswerable_results = [
        (case, retriever.retrieve(case.query, access, top_k))
        for case in suite.active(DatasetType.UNANSWERABLE_REFUSAL)
    ]
    measured = [*results, *(r for _c, r in unanswerable_results)]
    served = {r.strategy for r in measured}
    _require_settings_if_dense_served(index_settings, served)
    kinds = {r.score_kind for r in measured}
    score_kind = _single(kinds)
    unanswerable = unanswerable_report(
        suite,
        unanswerable_results,
        [r["top1_score"] for r in rows],
        score_kind,
    )
    for result in measured:
        if result.lexical is not None:
            lexical_identity = lexical_identity or result.lexical
    reasons = Counter(r.fallback_reason for r in measured if r.fallback_reason)
    fallback_counts = dict(sorted(reasons.items()))
    by_path = _latency_by_path(results, latencies)
    single_path = len(by_path) == 1
    truncated = (
        None
        if served == {Strategy.DENSE.value}
        else sum(1 for r in rows if r["query_terms_truncated"])
    )
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
        "collection": identity.collection,
        "index_version": identity.index_version,
        # null when the run never reached Qdrant (`bm25`)
        "index_settings": (
            index_settings.model_dump(mode="json") if index_settings else None
        ),
        "requested_strategy": strategy.value,
        "served_strategies": sorted(served),
        # null when more than one strategy served: no single one describes the run
        "retrieval_strategy": _single(served),
        "score_kind": score_kind,
        "fallback_counts": fallback_counts,
        "warmup_fallback_reason": warm_up.fallback_reason,
        "qdrant_timeouts": (
            qdrant_timeouts.model_dump(mode="json") if qdrant_timeouts else None
        ),
        "dense_identity": identity.model_dump(mode="json"),
        "fusion": (_fusion_report(fusion) if Strategy.HYBRID.value in served else None),
        "lexical_index": _lexical_report(lexical_identity),
        "truncated_query_count": truncated,
        "top_k": top_k,
        "device": device,
        "embedder_is_fake": identity.embedder_is_fake,
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
            "p50": round(percentile(latencies, 50), 3) if single_path else None,
            "p95": round(percentile(latencies, 95), 3) if single_path else None,
            "by_served_path": by_path,
            "warmup_ms": round(warmup_ms, 3),
            "measured_cases": len(rows),
            "legs": _leg_latency(results),
        },
        "cases": rows,
        "notes": _notes(suite, top_k=top_k, document_count=document_count, n=len(rows)),
    }
