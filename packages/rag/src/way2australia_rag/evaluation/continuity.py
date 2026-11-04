"""Golden-case continuity between two retrieval result files (Spec 010 R10).

Unlike ``eval-compare``, suite ID/version, ``lote``, case-set differences and
``git_commit`` are reported but do not refuse the run. Identity fields that
must match refuse with exit 2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from way2australia_rag.evaluation.compare import _chunker_text
from way2australia_rag.evaluation.results import read_result

EXIT_OK = 0
EXIT_DIFF = 1
EXIT_REFUSED = 2


def _lote_label(value: object) -> str:
    return "none" if value is None else str(value)


def _fmt_key(key: tuple[str, int]) -> str:
    return f"{key[0]} v{key[1]}"


def _load_raw(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _identity_refusals(base: dict[str, Any], cand: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for field in ("collection", "index_version", "top_k"):
        old, new = base.get(field), cand.get(field)
        if old != new:
            problems.append(f"{field} changed {old!r} -> {new!r}")
    if _embedder_pair_from_doc(base) != _embedder_pair_from_doc(cand):
        problems.append("embedder pair differs")
    if base.get("chunker") != cand.get("chunker"):
        problems.append(
            f"chunker changed {_chunker_text(base.get('chunker'))} -> "
            f"{_chunker_text(cand.get('chunker'))}"
        )
    if base.get("lexical_index") != cand.get("lexical_index"):
        problems.append("lexical identity differs")
    if base.get("retrieval_strategy") != cand.get("retrieval_strategy"):
        problems.append(
            f"served strategy changed {base.get('retrieval_strategy')!r} -> "
            f"{cand.get('retrieval_strategy')!r}"
        )
    return problems


def _embedder_pair_from_doc(document: dict[str, Any]) -> tuple[object, object]:
    settings = document.get("index_settings")
    if isinstance(settings, dict):
        return settings.get("embedder_model_id"), settings.get("embedder_revision")
    return document.get("embedder_model_id"), document.get("embedder_revision")


def _info_lines(base: dict[str, Any], cand: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for label, field in (
        ("suite", "evaluation_suite_id"),
        ("suite version", "evaluation_suite_version"),
    ):
        old, new = base.get(field), cand.get(field)
        if old != new:
            lines.append(f"{label}: {old} -> {new}")
    old_lote, new_lote = base.get("lote"), cand.get("lote")
    if old_lote != new_lote:
        lines.append(f"lote: {_lote_label(old_lote)} -> {_lote_label(new_lote)}")
    if base.get("git_commit") != cand.get("git_commit"):
        lines.append(
            f"git_commit: {base.get('git_commit')!r} -> {cand.get('git_commit')!r}"
        )
    return lines


def _case_keys(document: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    cases = document.get("cases")
    if not isinstance(cases, list):
        return {}
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for row in cases:
        if not isinstance(row, dict):
            continue
        case_id = row.get("case_id")
        version = row.get("case_version")
        if isinstance(case_id, str) and isinstance(version, int):
            out[(case_id, version)] = row
    return out


def compare_continuity(base_path: Path, candidate_path: Path) -> tuple[int, list[str]]:
    """Return exit code and output lines."""
    lines: list[str] = []
    try:
        base_run = read_result(base_path, "BASE")
        cand_run = read_result(candidate_path, "CANDIDATE")
    except Exception as error:  # noqa: BLE001 - message only
        return EXIT_REFUSED, [f"ERROR: {error}"]

    base = _load_raw(base_path)
    cand = _load_raw(candidate_path)
    refusals = _identity_refusals(base, cand)
    if refusals:
        return EXIT_REFUSED, [
            "not comparable: " + "; ".join(refusals),
            "compare runs on the same collection, index_version, embedder, "
            "lexical index, served strategy and top_k.",
        ]

    lines.extend(_info_lines(base, cand))
    base_keys = set(base_run.cases)
    cand_keys = set(cand_run.cases)
    shared = sorted(base_keys & cand_keys)
    only_base = sorted(base_keys - cand_keys)
    only_cand = sorted(cand_keys - base_keys)
    lines.append(f"shared goldens: {len(shared)}")
    if only_base:
        lines.append(f"only in BASE: {', '.join(_fmt_key(k) for k in only_base)}")
    if only_cand:
        lines.append(f"only in CANDIDATE: {', '.join(_fmt_key(k) for k in only_cand)}")

    diffs: list[str] = []
    for key in shared:
        brow = base_run.cases[key]
        crow = cand_run.cases[key]
        raw_b = _case_keys(base)[key]
        raw_c = _case_keys(cand)[key]
        ranked_b = raw_b.get("ranked_document_ids")
        ranked_c = raw_c.get("ranked_document_ids")
        if (
            brow.hit != crow.hit
            or brow.reciprocal_rank != crow.reciprocal_rank
            or ranked_b != ranked_c
        ):
            diffs.append(
                f"{_fmt_key(key)}: hit {brow.hit} -> {crow.hit}, "
                f"reciprocal_rank {brow.reciprocal_rank} -> {crow.reciprocal_rank}, "
                f"ranked_document_ids {ranked_b!r} -> {ranked_c!r}"
            )
    lines.extend(diffs)
    if diffs:
        return EXIT_DIFF, lines
    if lines:
        lines.append("continuity: no shared-case differences")
    else:
        lines.append("continuity: identical on shared goldens")
    return EXIT_OK, lines


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print(
            "usage: python -m way2australia_rag.evaluation.continuity "
            "<base.json> <candidate.json>",
            file=sys.stderr,
        )
        return EXIT_REFUSED
    code, lines = compare_continuity(Path(args[0]), Path(args[1]))
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
