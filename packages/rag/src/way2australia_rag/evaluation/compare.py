"""Result comparison and quality gate (Spec 006 R11).

The rule is a constant in code; changing it needs a spec amendment. Hits and MRR
are computed from the per-case rows, never from the rounded aggregates. Flipped
cases, slice drops and latency are reported but never fail the gate.
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from way2australia_rag.evaluation.errors import NotComparableError
from way2australia_rag.evaluation.results import (
    AUTHORITY_VERSIONS,
    CaseRow,
    ComparableRun,
)
from way2australia_rag.retrieval.text import safe_text

HIT_TOLERANCE_CASES = 1
MRR_EPSILON = 1e-9
MAX_LISTED = 10
NEW_BASELINE = "run `make eval-retrieval` on the current system to set a new baseline."
IDENTITY_STEP = (
    "compare runs on the same collection, index_version, embedder and lexical index."
)
FAKE_STEP = (
    "run `make eval-retrieval` with a real embedder (BGE-M3) to produce a "
    "comparable file."
)


def mrr_tolerance(n: int) -> float:
    return 1.0 / n


@dataclass(frozen=True)
class Comparison:
    passed: bool
    hits_base: int
    hits_candidate: int
    mrr_base: float
    mrr_candidate: float
    n: int
    failures: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def _fmt_key(key: tuple[str, int]) -> str:
    return f"{key[0]} v{key[1]}"


def _listed(items: list[str]) -> str:
    shown = ", ".join(items[:MAX_LISTED])
    extra = len(items) - MAX_LISTED
    return f"{shown} and {extra} more" if extra > 0 else shown


def _embedder(run: ComparableRun) -> str:
    return f"{run.info.get('embedder_model_id')}@{run.info.get('embedder_revision')}"


def _lexical_identity(run: ComparableRun) -> tuple[object, object, object] | None:
    lexical = run.info.get("lexical")
    if not isinstance(lexical, dict):
        return None
    return (
        lexical.get("tokenizer_name"),
        lexical.get("tokenizer_version"),
        lexical.get("source_chunk_digest"),
    )


def _lexical_text(identity: tuple[object, object, object] | None) -> str:
    if identity is None:
        return "none"
    name, version, digest = identity
    return f"{name} v{version} digest {digest}"


def _identity_problems(base: ComparableRun, cand: ComparableRun) -> list[str]:
    """Spec 007 R10: unlike systems are refused, unlike strategies are not."""
    problems: list[str] = []
    old_c, new_c = base.info.get("collection"), cand.info.get("collection")
    if old_c is not None and new_c is not None and old_c != new_c:
        problems.append(f"collection changed {old_c} -> {new_c}")
    old_i, new_i = base.info.get("index_version"), cand.info.get("index_version")
    if old_i != new_i:
        problems.append(f"index_version changed {old_i} -> {new_i}")
    if _embedder(base) != _embedder(cand):
        problems.append(f"embedder changed {_embedder(base)} -> {_embedder(cand)}")
    old_l, new_l = _lexical_identity(base), _lexical_identity(cand)
    if old_l is not None and new_l is not None and old_l != new_l:
        problems.append(
            f"lexical index changed {_lexical_text(old_l)} -> {_lexical_text(new_l)}"
        )
    return problems


def _refusals(base: ComparableRun, cand: ComparableRun) -> list[str]:
    problems: list[str] = []
    steps: list[str] = []
    for label, run in (("BASE", base), ("CANDIDATE", cand)):
        if run.embedder_is_fake:
            problems.append(
                f"{label} file '{run.name}' comes from a fake-embedder index"
            )
            steps.append(FAKE_STEP)
    changed = 0
    if base.suite_id != cand.suite_id:
        problems.append(f"suite ID changed {base.suite_id} -> {cand.suite_id}")
        changed += 1
    if base.suite_version != cand.suite_version:
        problems.append(
            f"suite version changed {base.suite_version} -> {cand.suite_version}"
        )
        changed += 1
    if base.top_k != cand.top_k:
        problems.append(f"top_k changed {base.top_k} -> {cand.top_k}")
        changed += 1
    if base.document_count != cand.document_count:
        problems.append(
            f"document count changed {base.document_count} -> {cand.document_count}"
        )
        changed += 1
    only_base = sorted(set(base.cases) - set(cand.cases))
    only_cand = sorted(set(cand.cases) - set(base.cases))
    if only_base or only_cand:
        changed += 1
        base_versions = {k[0]: k[1] for k in only_base}
        cand_versions = {k[0]: k[1] for k in only_cand}
        both = sorted(set(base_versions) & set(cand_versions))
        parts = [f"{c} {base_versions[c]} -> {cand_versions[c]}" for c in both]
        missing = [_fmt_key(k) for k in only_base if k[0] not in both]
        extra = [_fmt_key(k) for k in only_cand if k[0] not in both]
        detail = []
        if parts:
            detail.append(f"case_version changed for {_listed(parts)}")
        if missing:
            detail.append(f"only in BASE: {_listed(missing)}")
        if extra:
            detail.append(f"only in CANDIDATE: {_listed(extra)}")
        problems.append(
            f"case set differs ({len(base.cases)} -> {len(cand.cases)} cases; "
            + "; ".join(detail)
            + ")"
        )
    if changed:
        steps.append(NEW_BASELINE)
    identity = _identity_problems(base, cand)
    if identity:
        problems.extend(identity)
        steps.append(IDENTITY_STEP)
    if not problems:
        return []
    unique_steps = list(dict.fromkeys(steps))
    return [f"not comparable: {'; '.join(problems)}; {' '.join(unique_steps)}"]


def _hits(rows: list[CaseRow]) -> int:
    return sum(1 for r in rows if r.hit)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _metrics(rows: list[CaseRow]) -> tuple[float, float, float]:
    return (
        _hits(rows) / len(rows),
        _mean([r.recall for r in rows]),
        _mean([r.reciprocal_rank for r in rows]),
    )


def _delta_line(
    label: str, base_rows: list[CaseRow], cand_rows: list[CaseRow], k: int
) -> str:
    bh, br, bm = _metrics(base_rows)
    ch, cr, cm = _metrics(cand_rows)
    return (
        f"{label} (n={len(base_rows)}): HitRate@{k} {bh:.4f} -> {ch:.4f} "
        f"({ch - bh:+.4f}), Recall@{k} {br:.4f} -> {cr:.4f} ({cr - br:+.4f}), "
        f"MRR {bm:.4f} -> {cm:.4f} ({cm - bm:+.4f})"
    )


def _slice(
    run: ComparableRun,
    keys: list[tuple[str, int]],
    key_of: Callable[[CaseRow], str],
) -> dict[str, list[tuple[str, int]]]:
    groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for key in keys:
        groups[key_of(run.cases[key])].append(key)
    return groups


def _changed(label: str, old: object, new: object) -> str | None:
    return None if old == new else f"{label}: {old} -> {new}"


def compare(base: ComparableRun, candidate: ComparableRun) -> Comparison:
    """Raise `NotComparableError` for unlike runs; otherwise apply the gate."""
    refusals = _refusals(base, candidate)
    if refusals:
        raise NotComparableError(refusals[0])
    keys = sorted(base.cases)
    n = len(keys)
    if n == 0:
        raise NotComparableError(
            "not comparable: both files hold no cases; run `make eval-retrieval` "
            "on the current system to set a new baseline."
        )
    k = base.top_k
    base_rows = [base.cases[x] for x in keys]
    cand_rows = [candidate.cases[x] for x in keys]
    hits_base, hits_cand = _hits(base_rows), _hits(cand_rows)
    mrr_base = _mean([r.reciprocal_rank for r in base_rows])
    mrr_cand = _mean([r.reciprocal_rank for r in cand_rows])

    failures: list[str] = []
    if hits_cand < hits_base - HIT_TOLERANCE_CASES:
        failures.append(
            f"hits dropped {hits_base} -> {hits_cand} (more than "
            f"{HIT_TOLERANCE_CASES} case)"
        )
    if mrr_base - mrr_cand > mrr_tolerance(n) + MRR_EPSILON:
        failures.append(
            f"MRR dropped {mrr_base:.4f} -> {mrr_cand:.4f} (more than 1/{n} = "
            f"{mrr_tolerance(n):.4f})"
        )

    lines = [
        f"base: {base.name} ({base.kind} {base.schema_version}); "
        f"candidate: {candidate.name} ({candidate.kind} {candidate.schema_version})",
        f"suite: {base.suite_id} v{base.suite_version}, top_k {k}, "
        f"documents {base.document_count}, compared cases {n}",
        _delta_line("overall", base_rows, cand_rows, k),
    ]
    sliced: list[tuple[str, Callable[[CaseRow], str]]] = [
        ("query_language", lambda r: r.query_language),
        ("category", lambda r: r.category),
    ]
    both_v2 = (
        base.schema_version in AUTHORITY_VERSIONS
        and candidate.schema_version in AUTHORITY_VERSIONS
    )
    if both_v2:
        sliced.append(("source_authority", lambda r: r.source_authority or "unknown"))
    for name, key_of in sliced:
        # Slices follow BASE's labels; the same case keys are read from both runs.
        for group, members in sorted(_slice(base, keys, key_of).items()):
            lines.append(
                _delta_line(
                    f"{name} {group}",
                    [base.cases[x] for x in members],
                    [candidate.cases[x] for x in members],
                    k,
                )
            )
    if not both_v2:
        lines.append(
            "note: the source_authority slice was not compared "
            "(it exists only in 2.0 and 2.1 files; both files must be one of them)."
        )
    for label in ("latency_p50", "latency_p95"):
        old, new = base.info.get(label), candidate.info.get(label)
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
            lines.append(
                f"latency {label[8:]} (informational): {old:.1f} ms -> {new:.1f} ms "
                f"({new - old:+.1f} ms)"
            )
    for run in (base, candidate):
        if run.info.get("collection") is None:
            lines.append(
                f"collection not recorded in {run.name}; compared by index_version only"
            )
    for label in ("retrieval_strategy", "device", "git_commit"):
        diff = _changed(label, base.info.get(label), candidate.info.get(label))
        if diff:
            lines.append(f"identity differs, {diff}")
    old_l, new_l = _lexical_identity(base), _lexical_identity(candidate)
    if old_l != new_l:
        lines.append(
            "identity differs, lexical_index: "
            f"{_lexical_text(old_l)} -> {_lexical_text(new_l)}"
        )
    for key in keys:
        old, new = base.cases[key].hit, candidate.cases[key].hit
        if old and not new:
            lines.append(f"WARNING flipped hit->miss: {_fmt_key(key)}")
        elif new and not old:
            lines.append(f"WARNING flipped miss->hit: {_fmt_key(key)}")
    # sorted by case_id, hit->miss before miss->hit is not required
    flips = [x for x in lines if x.startswith("WARNING flipped")]
    rest = [x for x in lines if not x.startswith("WARNING flipped")]
    lines = rest + sorted(flips, key=lambda x: x.split(": ", 1)[1])
    if failures:
        lines.append("eval-compare: FAIL - " + "; ".join(failures))
    else:
        lines.append(
            f"eval-compare: PASS (hits {hits_base} -> {hits_cand}, "
            f"MRR {mrr_base:.4f} -> {mrr_cand:.4f})"
        )
    return Comparison(
        passed=not failures,
        hits_base=hits_base,
        hits_candidate=hits_cand,
        mrr_base=mrr_base,
        mrr_candidate=mrr_cand,
        n=n,
        failures=failures,
        lines=[safe_text(x) for x in lines],
    )
