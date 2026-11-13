"""Generation evaluation runner (Spec 012 R9).

Runs goldens and unanswerable cases through `AnswerService`, writes a
`generation_evaluation` result (schema 1.0). Phase 1 estimates cost with zero
generator calls; phase 2 generates. Read-only on `knowledge/`; fake runs need
`--allow-fake` and write only under `experiments/results/tmp/`.
"""

from __future__ import annotations

import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    CaseBase,
    DatasetType,
    GoldenCase,
    LoadedSuite,
    UnanswerableCase,
)
from way2australia_rag.evaluation.retrieval_eval import (
    active_golden_cases,
    require_active_suite,
)
from way2australia_rag.evaluation.slices import SMALL_SAMPLE_THRESHOLD
from way2australia_rag.generation.base import Generator, GeneratorInfo
from way2australia_rag.generation.config import GenerationConfig, PricingConfig
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.models import (
    AnswerReason,
    AnswerResponse,
    AnswerStatus,
)
from way2australia_rag.generation.prompts import PromptVersion, render_prompt
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import Retriever
from way2australia_rag.retrieval.baseline import git_state
from way2australia_rag.retrieval.metrics import percentile
from way2australia_rag.retrieval.text import safe_text
from way2australia_rag.script_mix import script_mix

GENERATION_KIND = "generation_evaluation"
GENERATION_SCHEMA_VERSION = "1.1"


@dataclass(frozen=True)
class SelectedCases:
    goldens: tuple[GoldenCase, ...]
    unanswerables: tuple[UnanswerableCase, ...]
    selection: dict[str, Any]


@dataclass(frozen=True)
class CostEstimate:
    case_count: int
    prompt_chars: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float | None


def active_unanswerable_cases(suite: LoadedSuite) -> list[UnanswerableCase]:
    cases = suite.active(DatasetType.UNANSWERABLE_REFUSAL)
    for case in cases:
        if case.answerable:
            raise EvaluationConfigurationError(
                f"active unanswerable case '{case.case_id}' is marked answerable; "
                "run `make validate-evaluation`."
            )
    return cases


def select_cases(
    suite: LoadedSuite,
    *,
    limit: int | None,
    all_cases: bool,
) -> SelectedCases:
    """Proportional `--limit` selection; at least one unanswerable when limit ≥ 2."""
    goldens = active_golden_cases(suite)
    unanswerables = active_unanswerable_cases(suite)
    total_g, total_u = len(goldens), len(unanswerables)
    if all_cases:
        return SelectedCases(
            tuple(goldens),
            tuple(unanswerables),
            {
                "mode": "all",
                "limit": None,
                "golden_selected": total_g,
                "unanswerable_selected": total_u,
                "golden_total": total_g,
                "unanswerable_total": total_u,
            },
        )
    if limit is None:
        raise EvaluationConfigurationError(
            "a real generator run needs exactly one of --limit N or --all."
        )
    if limit < 1:
        raise EvaluationConfigurationError("--limit must be at least 1.")
    if not goldens and not unanswerables:
        raise EvaluationConfigurationError("no active cases to evaluate.")
    cap = total_g + total_u
    n = min(limit, cap)
    if n >= cap:
        picked_g, picked_u = goldens, unanswerables
    else:
        g_take = round(n * total_g / (total_g + total_u)) if (total_g + total_u) else 0
        u_take = n - g_take
        if n >= 2 and u_take == 0 and unanswerables:
            u_take = 1
            g_take = n - 1
        if n >= 2 and g_take == 0 and goldens:
            g_take = 1
            u_take = n - 1
        picked_g, picked_u = goldens[:g_take], unanswerables[:u_take]
    return SelectedCases(
        tuple(picked_g),
        tuple(picked_u),
        {
            "mode": "limit",
            "limit": limit,
            "golden_selected": len(picked_g),
            "unanswerable_selected": len(picked_u),
            "golden_total": total_g,
            "unanswerable_total": total_u,
        },
    )


def apply_pricing_overrides(
    config: GenerationConfig,
    *,
    input_per_mtok: float | None,
    output_per_mtok: float | None,
    source: Literal["config", "cli"] = "config",
) -> tuple[GenerationConfig, dict[str, Any]]:
    pricing = config.pricing
    applied: dict[str, Any] = {
        "input_per_mtok": pricing.input_per_mtok,
        "output_per_mtok": pricing.output_per_mtok,
        "input_source": "config",
        "output_source": "config",
    }
    if input_per_mtok is not None:
        pricing = pricing.model_copy(update={"input_per_mtok": input_per_mtok})
        applied["input_per_mtok"] = input_per_mtok
        applied["input_source"] = source
    if output_per_mtok is not None:
        pricing = pricing.model_copy(update={"output_per_mtok": output_per_mtok})
        applied["output_per_mtok"] = output_per_mtok
        applied["output_source"] = source
    updated = config.model_copy(update={"pricing": pricing})
    return updated, applied


def require_real_generator_pricing(
    generator: Generator, pricing: PricingConfig, *, allow_null: bool = False
) -> None:
    if generator.info.is_fake:
        return
    if allow_null:
        return
    missing = []
    if pricing.input_per_mtok is None:
        missing.append("pricing.input_per_mtok")
    if pricing.output_per_mtok is None:
        missing.append("pricing.output_per_mtok")
    if missing:
        raise EvaluationConfigurationError(
            "a real generator run needs token prices in config/generation.yaml or "
            f"pass --price-input and --price-output (missing: {', '.join(missing)})."
        )


def _prompt_chars_for_case(
    retriever: Retriever,
    builder: ContextBuilder,
    prompt: PromptVersion,
    case: CaseBase,
    access: ResolvedAccess,
    top_k: int,
    lote: ResolvedLote | None,
) -> int:
    result = retriever.retrieve(case.query, access, top_k, lote=lote)
    blocks, _ = builder.build(result.hits)
    if not blocks:
        return len(prompt.system_text)
    rendered = render_prompt(prompt, blocks, case.query)
    return len(rendered.system) + len(rendered.user)


def estimate_cost(
    *,
    selected: SelectedCases,
    retriever: Retriever,
    builder: ContextBuilder,
    prompt: PromptVersion,
    access: ResolvedAccess,
    config: GenerationConfig,
    top_k: int,
    lote: ResolvedLote | None,
) -> CostEstimate:
    cases = [*selected.goldens, *selected.unanswerables]
    prompt_chars = 0
    for case in cases:
        prompt_chars += _prompt_chars_for_case(
            retriever, builder, prompt, case, access, top_k, lote
        )
    est = config.estimate
    in_tok = int(prompt_chars / est.chars_per_token)
    out_tok = est.assumed_output_tokens * len(cases)
    cost = None
    pricing = config.pricing
    if pricing.input_per_mtok is not None and pricing.output_per_mtok is not None:
        cost = (
            in_tok * pricing.input_per_mtok + out_tok * pricing.output_per_mtok
        ) / 1_000_000
    return CostEstimate(
        case_count=len(cases),
        prompt_chars=prompt_chars,
        estimated_input_tokens=in_tok,
        estimated_output_tokens=out_tok,
        estimated_cost_usd=round(cost, 6) if cost is not None else None,
    )


def print_cost_estimate(estimate: CostEstimate, pricing: PricingConfig) -> None:
    lines = [
        f"cases: {estimate.case_count}",
        f"rendered prompt characters: {estimate.prompt_chars}",
        f"estimated input tokens: {estimate.estimated_input_tokens}",
        f"estimated output tokens: {estimate.estimated_output_tokens}",
    ]
    if estimate.estimated_cost_usd is not None:
        lines.append(f"estimated cost (USD): {estimate.estimated_cost_usd:.6f}")
    else:
        lines.append(
            "estimated cost: n/a (set pricing.input_per_mtok and "
            "pricing.output_per_mtok or pass --price-input / --price-output)"
        )
    if pricing.input_per_mtok is not None:
        lines.append(f"price input (USD/Mtok): {pricing.input_per_mtok}")
    if pricing.output_per_mtok is not None:
        lines.append(f"price output (USD/Mtok): {pricing.output_per_mtok}")
    print("\n".join(safe_text(line) for line in lines))


def require_confirmation(*, yes: bool) -> None:
    if yes:
        return
    if not sys.stdin.isatty():
        raise EvaluationConfigurationError(
            "refusing a real generator run without a TTY; pass --yes to confirm."
        )
    try:
        answer = input("Proceed with generation? [y/N] ").strip().lower()
    except EOFError as error:
        raise EvaluationConfigurationError(
            "refusing a real generator run without confirmation."
        ) from error
    if answer not in {"y", "yes"}:
        raise EvaluationConfigurationError("generation run cancelled.")


def _actual_cost_usd(
    usage_in: int, usage_out: int, pricing: PricingConfig
) -> float | None:
    if pricing.input_per_mtok is None or pricing.output_per_mtok is None:
        return None
    return round(
        (usage_in * pricing.input_per_mtok + usage_out * pricing.output_per_mtok)
        / 1_000_000,
        6,
    )


def _cited_document_ids(response: AnswerResponse) -> list[str]:
    return [c.document_id for c in response.citations]


def _precision_recall(
    cited: set[str], relevant: set[str]
) -> tuple[float | None, float | None]:
    if not cited:
        return (0.0 if relevant else None, 0.0 if relevant else None)
    if not relevant:
        return (0.0, None)
    hit = len(cited & relevant)
    return hit / len(cited), hit / len(relevant)


def _facts_matched(answer: str | None, facts: Sequence[str]) -> tuple[int, int]:
    if not facts or answer is None:
        return 0, len(facts)
    lowered = answer.casefold()
    matched = sum(1 for fact in facts if fact.casefold() in lowered)
    return matched, len(facts)


def _case_kind(case: CaseBase) -> str:
    return (
        "golden_answerable" if isinstance(case, GoldenCase) else "unanswerable_refusal"
    )


def _row_from_response(
    case: CaseBase,
    response: AnswerResponse,
    *,
    first_request: bool,
    relevant_document_ids: list[str] | None,
    expected_facts: list[str],
) -> dict[str, Any]:
    cited = _cited_document_ids(response)
    relevant = set(relevant_document_ids or [])
    prec, rec = (
        _precision_recall(set(cited), relevant)
        if isinstance(case, GoldenCase) and response.status == AnswerStatus.ANSWERED
        else (None, None)
    )
    matched, total = _facts_matched(
        response.answer,
        expected_facts if isinstance(case, GoldenCase) else [],
    )
    usage = response.usage
    return {
        "case_id": case.case_id,
        "case_version": case.case_version,
        "kind": _case_kind(case),
        "query_language": getattr(case, "query_language", "en"),
        "status": response.status.value,
        "reason": response.reason.value if response.reason else None,
        "sub_reason": response.sub_reason,
        "answer": safe_text(response.answer) if response.answer else None,
        "cited_document_ids": cited,
        "relevant_document_ids": sorted(relevant),
        "citation_precision": prec,
        "citation_recall": rec,
        "expected_facts_matched": matched,
        "expected_facts_total": total,
        "answer_script_mix": script_mix(response.answer or ""),
        "usage": usage.model_dump() if usage else None,
        "latency_ms": dict(response.latency_ms),
        "served_retrieval_path": response.identity.retrieval.get("strategy"),
        "response_model": response.identity.response_model,
        "first_request": first_request,
    }


def _is_refusal(response: AnswerResponse) -> bool:
    return (
        response.status == AnswerStatus.INSUFFICIENT_EVIDENCE
        and response.reason is not None
    )


def _aggregate_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    goldens = [r for r in rows if r["kind"] == "golden_answerable"]
    unanswerables = [r for r in rows if r["kind"] == "unanswerable_refusal"]
    answered = [r for r in goldens if r["status"] == AnswerStatus.ANSWERED.value]
    refusals = [r for r in unanswerables if _is_refusal_status(r)]
    evidence_only = [r for r in rows if r["status"] == AnswerStatus.EVIDENCE_ONLY.value]
    output_invalid = [
        r
        for r in rows
        if r["status"] == AnswerStatus.INSUFFICIENT_EVIDENCE.value
        and r["reason"] == AnswerReason.OUTPUT_INVALID.value
    ]
    citation_invalid = [
        r
        for r in rows
        if r["status"] == AnswerStatus.INSUFFICIENT_EVIDENCE.value
        and r["reason"] == AnswerReason.CITATION_INVALID.value
    ]
    generator_unavailable = [
        r
        for r in rows
        if r["status"] == AnswerStatus.EVIDENCE_ONLY.value
        and r["reason"] == AnswerReason.GENERATOR_UNAVAILABLE.value
    ]
    n_cases = len(rows)
    n_goldens = len(goldens)
    n_unanswerables = len(unanswerables)
    return {
        "golden_count": n_goldens,
        "unanswerable_count": n_unanswerables,
        "answered_count": len(answered),
        "refusal_count": len(refusals),
        "evidence_only_count": len(evidence_only),
        "output_invalid_count": len(output_invalid),
        "citation_invalid_count": len(citation_invalid),
        "citation_invalid_rate": len(citation_invalid) / n_cases if n_cases else None,
        "generator_unavailable_count": len(generator_unavailable),
        "answer_rate": len(answered) / n_goldens if n_goldens else None,
        "answer_rate_small_sample": n_goldens < SMALL_SAMPLE_THRESHOLD,
        "refusal_rate": len(refusals) / n_unanswerables if n_unanswerables else None,
        "refusal_rate_small_sample": n_unanswerables < SMALL_SAMPLE_THRESHOLD,
        "cases_run": n_cases,
        "cases_run_small_sample": n_cases < SMALL_SAMPLE_THRESHOLD,
    }


def _is_refusal_status(row: dict[str, Any]) -> bool:
    return (
        row["kind"] == "unanswerable_refusal"
        and row["status"] == AnswerStatus.INSUFFICIENT_EVIDENCE.value
        and row["reason"] is not None
    )


def _subreason_counts(rows: Sequence[dict[str, Any]], *, reason: str) -> dict[str, Any]:
    picked = [r for r in rows if r["reason"] == reason and r["sub_reason"]]
    counts: Counter[str] = Counter(str(r["sub_reason"]) for r in picked)
    by_reason: dict[str, list[str]] = {}
    for row in picked:
        key = str(row["sub_reason"])
        by_reason.setdefault(key, []).append(row["case_id"])
    return {
        "count": len(picked),
        "by_sub_reason": dict(sorted(counts.items())),
        "case_ids_by_sub_reason": {k: sorted(v) for k, v in sorted(by_reason.items())},
    }


def _latency_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    stages = ("retrieval_ms", "context_ms", "generation_ms", "total_ms")
    out: dict[str, Any] = {}
    for stage in stages:
        values = [
            float(r["latency_ms"][stage]) for r in rows if stage in r["latency_ms"]
        ]
        out[stage] = {
            "p50": round(percentile(values, 50), 3) if values else None,
            "p95": round(percentile(values, 95), 3) if values else None,
            "n": len(values),
        }
    return out


def _token_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    ins: list[int] = []
    outs: list[int] = []
    for row in rows:
        usage = row.get("usage")
        if not isinstance(usage, dict):
            continue
        if usage.get("input_tokens") is not None:
            ins.append(int(usage["input_tokens"]))
        if usage.get("output_tokens") is not None:
            outs.append(int(usage["output_tokens"]))
    return {
        "input_total": sum(ins),
        "output_total": sum(outs),
        "input_mean": round(sum(ins) / len(ins), 3) if ins else None,
        "output_mean": round(sum(outs) / len(outs), 3) if outs else None,
        "cases_with_usage": len(ins),
    }


def _facts_coverage(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    golden_rows = [r for r in rows if r["kind"] == "golden_answerable"]
    matched = sum(r["expected_facts_matched"] for r in golden_rows)
    total = sum(r["expected_facts_total"] for r in golden_rows)
    overall = matched / total if total else None
    by_lang: dict[str, dict[str, Any]] = {}
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in golden_rows:
        groups.setdefault(str(row["query_language"]), []).append(row)
    for key in sorted(groups):
        chunk = groups[key]
        m = sum(r["expected_facts_matched"] for r in chunk)
        t = sum(r["expected_facts_total"] for r in chunk)
        n = len(chunk)
        by_lang[key] = {
            "matched": m,
            "total": t,
            "coverage": m / t if t else None,
            "n": n,
            "small_sample": n < SMALL_SAMPLE_THRESHOLD,
        }
    return {
        "overall": overall,
        "matched": matched,
        "total": total,
        "informational": True,
        "by_query_language": by_lang,
    }


def _script_mix_counts(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        mix = row.get("answer_script_mix") or "none"
        counts[str(mix)] += 1
    return dict(sorted(counts.items()))


def check_thresholds(
    metrics: dict[str, Any],
    *,
    min_answer_rate: float | None,
    min_refusal_rate: float | None,
) -> list[str]:
    problems: list[str] = []
    ar = metrics.get("answer_rate")
    if min_answer_rate is not None and ar is not None and ar < min_answer_rate:
        problems.append(
            f"answer rate {ar:.4f} below --min-answer-rate {min_answer_rate}"
        )
    rr = metrics.get("refusal_rate")
    if min_refusal_rate is not None and rr is not None and rr < min_refusal_rate:
        problems.append(
            f"refusal rate {rr:.4f} below --min-refusal-rate {min_refusal_rate}"
        )
    return problems


def default_generation_output_path(
    repo_root: Path, index_version: str, now: datetime, *, tmp: bool
) -> Path:
    stamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    base = repo_root / "experiments" / "results"
    if tmp:
        base = base / "tmp"
    return base / f"generation-evaluation-{index_version}-{stamp}.json"


def format_generation_summary(document: dict[str, Any], shown: Path) -> str:
    m = document["metrics"]
    sid = document["evaluation_suite_id"]
    sver = document["evaluation_suite_version"]
    lines = [
        f"suite: {sid} v{sver}",
        (
            f"cases: {document['case_selection']['golden_selected']} golden, "
            f"{document['case_selection']['unanswerable_selected']} unanswerable "
            f"({document['case_selection']['mode']})"
        ),
        f"answer rate (goldens): {m['answer_rate']}",
        f"refusal rate (unanswerable): {m['refusal_rate']}",
        f"citation_invalid: {m['citation_invalid_count']}",
        f"evidence_only: {m['evidence_only_count']}",
        f"output_invalid: {m['output_invalid_count']}",
    ]
    gu = document["generator_unavailable"]
    if gu["count"]:
        lines.append(
            "generator_unavailable: "
            + ", ".join(f"{k}={v}" for k, v in sorted(gu["by_sub_reason"].items()))
        )
        for sub, ids in gu["case_ids_by_sub_reason"].items():
            lines.append(f"  {sub}: {', '.join(ids)}")
    models = document.get("response_models") or []
    if models:
        lines.append(f"response models: {', '.join(models)}")
    tok = document["tokens"]
    lines.append(
        f"tokens: in {tok['input_total']} out {tok['output_total']} "
        f"(mean in {tok['input_mean']}, out {tok['output_mean']})"
    )
    cost = document.get("actual_cost_usd")
    if cost is not None:
        lines.append(f"actual cost (USD): {cost:.6f}")
    latency = document["latency_ms"]
    lines.append(
        f"latency p50 total {latency['total_ms']['p50']} ms, "
        f"generation {latency['generation_ms']['p50']} ms"
    )
    lines.append(f"result: {shown}")
    return "\n".join(safe_text(line) for line in lines)


def run_generation_evaluation(
    *,
    retriever: Retriever,
    generator: Generator,
    service: AnswerService,
    suite: LoadedSuite,
    selected: SelectedCases,
    access: ResolvedAccess,
    release_id: str,
    top_k: int,
    lote: ResolvedLote | None,
    config: GenerationConfig,
    prompt: PromptVersion,
    generator_info: GeneratorInfo,
    pricing_applied: dict[str, Any],
    retrieval_identity: dict[str, Any],
    ingestion_config: dict[str, str],
    repo_root: Path,
    min_answer_rate: float | None,
    min_refusal_rate: float | None,
    estimated_cost_usd: float | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    require_active_suite(suite)
    cases: list[CaseBase] = [*selected.goldens, *selected.unanswerables]
    rows: list[dict[str, Any]] = []
    first = True
    for case in cases:
        response = service.answer(case.query, access, top_k, lote=lote)
        relevant = case.relevant_document_ids if isinstance(case, GoldenCase) else []
        facts = case.expected_facts if isinstance(case, GoldenCase) else []
        rows.append(
            _row_from_response(
                case,
                response,
                first_request=first,
                relevant_document_ids=relevant,
                expected_facts=facts,
            )
        )
        first = False
    metrics = _aggregate_metrics(rows)
    status_counts = {
        "golden_answerable": Counter(
            r["status"] for r in rows if r["kind"] == "golden_answerable"
        ),
        "unanswerable_refusal": Counter(
            r["status"] for r in rows if r["kind"] == "unanswerable_refusal"
        ),
    }
    citation_invalid = _subreason_counts(
        rows, reason=AnswerReason.CITATION_INVALID.value
    )
    n_cases = len(rows)
    citation_invalid["rate"] = citation_invalid["count"] / n_cases if n_cases else None
    citation_invalid["small_sample"] = n_cases < SMALL_SAMPLE_THRESHOLD
    generator_unavailable = _subreason_counts(
        rows, reason=AnswerReason.GENERATOR_UNAVAILABLE.value
    )
    answered_golden = [
        r
        for r in rows
        if r["kind"] == "golden_answerable" and r["citation_precision"] is not None
    ]
    precisions = [float(r["citation_precision"]) for r in answered_golden]
    recalls = [
        float(r["citation_recall"])
        for r in answered_golden
        if r["citation_recall"] is not None
    ]
    commit, dirty = git_state(repo_root)
    tokens = _token_summary(rows)
    pricing = config.pricing
    actual_cost = _actual_cost_usd(
        tokens["input_total"], tokens["output_total"], pricing
    )
    manifest = suite.manifest
    return {
        "kind": GENERATION_KIND,
        "schema_version": GENERATION_SCHEMA_VERSION,
        "created_at": clock().astimezone(UTC).isoformat(),
        "git_commit": commit,
        "git_dirty": dirty,
        "evaluation_suite_id": manifest.evaluation_suite_id,
        "evaluation_suite_version": manifest.version,
        "declared_knowledge_release_id": release_id,
        "case_selection": selected.selection,
        "prompt": prompt.identity.model_dump(),
        "generator": generator_info.model_dump(),
        "response_models": sorted(
            {str(r["response_model"]) for r in rows if r.get("response_model")}
        ),
        "pricing_applied": pricing_applied,
        "retrieval_identity": retrieval_identity,
        "ingestion_config": ingestion_config,
        "thresholds": {
            "min_answer_rate": min_answer_rate,
            "min_refusal_rate": min_refusal_rate,
        },
        "status_counts_by_kind": {k: dict(v) for k, v in status_counts.items()},
        "metrics": metrics,
        "citation_invalid": citation_invalid,
        "generator_unavailable": generator_unavailable,
        "citation_precision_mean": (
            round(sum(precisions) / len(precisions), 4) if precisions else None
        ),
        "citation_recall_mean": round(sum(recalls) / len(recalls), 4)
        if recalls
        else None,
        "expected_facts_coverage": _facts_coverage(rows),
        "answer_script_mix": _script_mix_counts(rows),
        "latency_ms": _latency_summary(rows),
        "tokens": tokens,
        "estimated_cost_usd": estimated_cost_usd,
        "actual_cost_usd": actual_cost,
        "small_sample_threshold": SMALL_SAMPLE_THRESHOLD,
        "cases": rows,
        "lote": lote.code if lote is not None else None,
        "top_k": top_k,
        "generator_is_fake": generator_info.is_fake,
    }
