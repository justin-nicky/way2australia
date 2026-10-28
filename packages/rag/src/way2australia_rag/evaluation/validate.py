"""All checks behind `make validate-evaluation` (Spec 006 R2, R14).

Collects every problem, then the caller decides the exit code: no problems is
0, problems is 1. Configuration errors (a missing schema, an unreadable suite
or dataset, an invalid knowledge corpus) are raised as
`EvaluationConfigurationError` and mean exit 2.

Relevant documents are checked only through the document repository and the
guest/public eligibility policy, never through file paths. Nothing is written.
Messages carry repository-relative file names and line numbers, never absolute
paths or case text.
"""

import asyncio
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.schemas import EvaluationSchemas, load_schemas
from way2australia_rag.evaluation.suite import inside, read_json
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentQuery,
    DocumentRepository,
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.retrieval.text import safe_text

SUITES_DIR = "evaluation/suites"
CANDIDATES_DIR = "evaluation/candidates"
DEFAULT_LANGUAGE = "en"
OWNER_REVIEW = "owner_review"
GOLDEN_TYPE = "golden_answerable"
PROMOTED_FIELDS = ("query", "relevant_document_ids", "expected_facts", "query_language")


@dataclass(frozen=True)
class EvaluationProblem:
    file: str
    line: int | None
    case_id: str | None
    field: str | None
    reason: str

    def __str__(self) -> str:
        where = self.file if self.line is None else f"{self.file}:{self.line}"
        parts = [where]
        if self.case_id:
            parts.append(self.case_id)
        head = " ".join(parts)
        field = f" {self.field}" if self.field else ""
        return safe_text(f"{head}{field}: {self.reason}")


def _schema_problems(
    validator: Draft202012Validator,
    instance: Any,
    *,
    file: str,
    line: int | None,
    case_id: str | None,
    prefix: str = "",
) -> list[EvaluationProblem]:
    """One problem per schema violation; the reason never echoes the value."""
    seen: set[tuple[str, str]] = set()
    problems: list[EvaluationProblem] = []
    for error in validator.iter_errors(instance):
        field, reason = _describe(error)
        key = (field, reason)
        if key in seen:
            continue
        seen.add(key)
        problems.append(
            EvaluationProblem(file, line, case_id, f"{prefix}{field}".strip(), reason)
        )
    return sorted(problems, key=lambda p: (p.field or "", p.reason))


def _describe(error: ValidationError) -> tuple[str, str]:
    path = ".".join(str(p) for p in error.absolute_path)
    kind = error.validator
    if kind == "required" and isinstance(error.validator_value, list):
        instance = error.instance if isinstance(error.instance, dict) else {}
        missing = [n for n in error.validator_value if n not in instance]
        name = missing[0] if missing else ""
        field = f"{path}.{name}" if path else name
        return field, "missing required field"
    reasons = {
        "enum": "value is not one of the allowed values",
        "const": "value is not the required constant",
        "type": "wrong type",
        "minLength": "must not be empty",
        "minItems": "must not be empty",
        "minimum": "value is below the allowed minimum",
    }
    return path or "(row)", reasons.get(str(kind), "invalid value")


def _read_rows(
    path: Path, relative: str
) -> tuple[list[tuple[int, Any]], list[EvaluationProblem], int]:
    """Parsed (line, row) pairs, malformed-line problems and the non-blank count."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise EvaluationConfigurationError(f"cannot read '{path.name}'.") from error
    rows: list[tuple[int, Any]] = []
    problems: list[EvaluationProblem] = []
    count = 0
    for number, text in enumerate(lines, start=1):
        if not text.strip():
            continue
        count += 1
        try:
            rows.append((number, json.loads(text)))
        except ValueError:
            problems.append(
                EvaluationProblem(
                    relative, number, None, None, "line is not valid JSON"
                )
            )
    return rows, problems, count


def _row_id(row: Any) -> str | None:
    if isinstance(row, dict):
        value = row.get("case_id") or row.get("candidate_id")
        return value if isinstance(value, str) else None
    return None


def _document_ids(
    repository: DocumentRepository,
) -> tuple[set[str], set[str]]:
    """(all document IDs, IDs eligible under the guest/public policy)."""

    async def collect() -> tuple[set[str], set[str]]:
        every = await repository.list_documents(DocumentQuery())
        eligible = await list_eligible_documents(repository, GUEST_PUBLIC_POLICY)
        return {d.document_id for d in every}, {d.document_id for d in eligible}

    try:
        return asyncio.run(collect())
    except DocumentRepositoryError as error:
        raise EvaluationConfigurationError(
            "the knowledge corpus is invalid; run `make validate-knowledge`."
        ) from error


def _document_problems(
    ids: Any,
    known: set[str],
    eligible: set[str],
    *,
    file: str,
    line: int,
    case_id: str | None,
    field: str,
) -> Iterator[EvaluationProblem]:
    if not isinstance(ids, list):
        return
    for document_id in ids:
        if not isinstance(document_id, str):
            continue
        if document_id not in known:
            yield EvaluationProblem(
                file, line, case_id, field, f"unknown document '{document_id}'"
            )
        elif document_id not in eligible:
            yield EvaluationProblem(
                file,
                line,
                case_id,
                field,
                f"document '{document_id}' not eligible for guest/public",
            )


def _suite_paths(repo_root: Path) -> list[Path]:
    directory = repo_root / SUITES_DIR
    paths = sorted(directory.glob("*.json")) if directory.is_dir() else []
    if not paths:
        raise EvaluationConfigurationError("no evaluation suite manifest found.")
    return paths


def _validate_suite(
    repo_root: Path,
    suite_path: Path,
    schemas: EvaluationSchemas,
    known: set[str],
    eligible: set[str],
    case_ids_by_suite: dict[str, set[str]],
    cases_by_suite: dict[str, dict[str, dict[str, Any]]],
) -> list[EvaluationProblem]:
    relative = suite_path.relative_to(repo_root).as_posix()
    manifest = read_json(suite_path)
    if not isinstance(manifest, dict):
        raise EvaluationConfigurationError(f"'{suite_path.name}' is not an object.")
    problems = _schema_problems(
        schemas.suite(), manifest, file=relative, line=None, case_id=None
    )
    suite_id = manifest.get("evaluation_suite_id")
    datasets = manifest.get("datasets")
    if not isinstance(datasets, list):
        return problems

    seen_paths: set[str] = set()
    seen_case_ids: dict[str, str] = {}
    case_rows: dict[str, dict[str, Any]] = {}
    case_lines = 0
    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue
        kind, dataset_path = dataset.get("type"), dataset.get("path")
        if not isinstance(dataset_path, str) or not dataset_path:
            continue
        if dataset_path in seen_paths:
            problems.append(
                EvaluationProblem(
                    relative, None, None, "datasets", "dataset path listed twice"
                )
            )
            continue
        seen_paths.add(dataset_path)
        path = inside(repo_root, dataset_path)  # escaping path -> configuration error
        if path.is_relative_to((repo_root / CANDIDATES_DIR).resolve()):
            problems.append(
                EvaluationProblem(
                    relative,
                    None,
                    None,
                    "datasets",
                    "suite references a candidates file; candidates are never cases",
                )
            )
            continue
        if kind not in {"golden_answerable", "unanswerable_refusal", "security"}:
            continue  # reported by the suite schema
        rows, row_problems, count = _read_rows(path, dataset_path)
        problems.extend(row_problems)
        case_lines += count
        validator = schemas.case_type(kind)
        for number, row in rows:
            case_id = _row_id(row)
            if not isinstance(row, dict):
                problems.append(
                    EvaluationProblem(
                        dataset_path, number, None, None, "line is not an object"
                    )
                )
                continue
            problems.extend(
                _schema_problems(
                    validator, row, file=dataset_path, line=number, case_id=case_id
                )
            )
            if case_id is not None:
                if case_id in seen_case_ids:
                    problems.append(
                        EvaluationProblem(
                            dataset_path,
                            number,
                            case_id,
                            "case_id",
                            f"duplicate of a case in {seen_case_ids[case_id]}",
                        )
                    )
                else:
                    seen_case_ids[case_id] = dataset_path
                    case_rows[case_id] = row
            row_suite = row.get("evaluation_suite_id")
            if (
                isinstance(row_suite, str)
                and row_suite
                and isinstance(suite_id, str)
                and row_suite != suite_id
            ):
                problems.append(
                    EvaluationProblem(
                        dataset_path,
                        number,
                        case_id,
                        "evaluation_suite_id",
                        "does not match the suite manifest",
                    )
                )
            if kind == GOLDEN_TYPE:
                problems.extend(
                    _document_problems(
                        row.get("relevant_document_ids"),
                        known,
                        eligible,
                        file=dataset_path,
                        line=number,
                        case_id=case_id,
                        field="relevant_document_ids",
                    )
                )
    count_declared = manifest.get("case_count")
    if (
        isinstance(count_declared, int)
        and not isinstance(count_declared, bool)
        and count_declared != case_lines
    ):
        problems.append(
            EvaluationProblem(
                relative,
                None,
                None,
                "case_count",
                f"declares {count_declared} cases but the datasets hold {case_lines}",
            )
        )
    if isinstance(suite_id, str) and suite_id:
        case_ids_by_suite[suite_id] = set(seen_case_ids)
        cases_by_suite[suite_id] = case_rows
    return problems


def _validate_candidates(
    repo_root: Path,
    schemas: EvaluationSchemas,
    known: set[str],
    eligible: set[str],
    case_ids_by_suite: dict[str, set[str]],
    cases_by_suite: dict[str, dict[str, dict[str, Any]]],
) -> list[EvaluationProblem]:
    directory = repo_root / CANDIDATES_DIR
    if not directory.is_dir():
        return []
    problems: list[EvaluationProblem] = []
    seen_ids: set[str] = set()
    row_validator = schemas.candidate_row()
    for path in sorted(directory.glob("*.jsonl")):
        relative = path.relative_to(repo_root).as_posix()
        rows, row_problems, _ = _read_rows(path, relative)
        problems.extend(row_problems)
        for number, row in rows:
            candidate_id = _row_id(row)
            if not isinstance(row, dict):
                problems.append(
                    EvaluationProblem(
                        relative, number, None, None, "line is not an object"
                    )
                )
                continue
            problems.extend(
                _schema_problems(
                    row_validator, row, file=relative, line=number, case_id=candidate_id
                )
            )
            if candidate_id is not None:
                if candidate_id in seen_ids:
                    problems.append(
                        EvaluationProblem(
                            relative, number, candidate_id, "candidate_id", "duplicate"
                        )
                    )
                seen_ids.add(candidate_id)
            problems.extend(
                _candidate_rules(
                    row,
                    relative,
                    number,
                    candidate_id,
                    known,
                    eligible,
                    case_ids_by_suite,
                    cases_by_suite,
                )
            )
    return problems


def _candidate_rules(
    row: dict[str, Any],
    relative: str,
    number: int,
    candidate_id: str | None,
    known: set[str],
    eligible: set[str],
    case_ids_by_suite: dict[str, set[str]],
    cases_by_suite: dict[str, dict[str, dict[str, Any]]],
) -> Iterator[EvaluationProblem]:
    def problem(field: str, reason: str) -> EvaluationProblem:
        return EvaluationProblem(relative, number, candidate_id, field, reason)

    target = row.get("target_suite_id")
    if isinstance(target, str) and target and target not in case_ids_by_suite:
        yield problem("target_suite_id", "does not name a known suite")
    targets = row.get("target_case_ids")
    if isinstance(target, str) and isinstance(targets, list):
        for case_id in targets:
            if isinstance(case_id, str) and case_id not in case_ids_by_suite.get(
                target, set()
            ):
                yield problem("target_case_ids", f"unknown case '{case_id}'")
    proposed = row.get("proposed_case")
    if not isinstance(proposed, dict):
        return
    yield from _promotion_problems(row, proposed, problem, cases_by_suite)
    yield from _document_problems(
        proposed.get("relevant_document_ids"),
        known,
        eligible,
        file=relative,
        line=number,
        case_id=candidate_id,
        field="proposed_case.relevant_document_ids",
    )
    language = proposed.get("query_language")
    if isinstance(language, str) and language and language != DEFAULT_LANGUAGE:
        if row.get("needs_fluent_speaker_review") is not True:
            yield problem(
                "needs_fluent_speaker_review",
                "must be true for a candidate query not in the default language",
            )
        reviews = row.get("requires_review")
        if not isinstance(reviews, list) or OWNER_REVIEW not in reviews:
            yield problem(
                "requires_review",
                f"must include '{OWNER_REVIEW}' for a candidate query not in the "
                "default language",
            )


def _promotion_problems(
    row: dict[str, Any],
    proposed: dict[str, Any],
    problem: Any,
    cases_by_suite: dict[str, dict[str, dict[str, Any]]],
) -> Iterator[EvaluationProblem]:
    """`review.promoted_as` must name a loaded suite and case that transcribe the
    candidate. Messages carry field names only, never case text."""
    review = row.get("review")
    promoted = review.get("promoted_as") if isinstance(review, dict) else None
    if promoted is None:
        return
    field = "review.promoted_as"
    if not isinstance(promoted, dict):
        yield problem(field, "must be an object with suite_id and case_id")
        return
    suite_id, case_id = promoted.get("suite_id"), promoted.get("case_id")
    if not isinstance(suite_id, str) or suite_id not in cases_by_suite:
        yield problem(field, "does not name a known suite")
        return
    case = cases_by_suite[suite_id].get(case_id) if isinstance(case_id, str) else None
    if case is None:
        yield problem(field, "does not name a case in that suite")
        return
    for name in PROMOTED_FIELDS:
        if case.get(name) != proposed.get(name):
            yield problem(f"{field}.{name}", "differs from the promoted case")


def validate_evaluation(
    repo_root: Path, repository: DocumentRepository | None = None
) -> list[EvaluationProblem]:
    """Every problem found in the evaluation assets under `repo_root`.

    `repository` is injectable for tests; by default the production corpus is
    read through `LocalDocumentRepository`.
    """
    root = repo_root.resolve()
    schemas = load_schemas(root)
    repo = repository or LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))
    known, eligible = _document_ids(repo)
    problems: list[EvaluationProblem] = []
    case_ids_by_suite: dict[str, set[str]] = {}
    cases_by_suite: dict[str, dict[str, dict[str, Any]]] = {}
    for suite_path in _suite_paths(root):
        problems.extend(
            _validate_suite(
                root,
                suite_path,
                schemas,
                known,
                eligible,
                case_ids_by_suite,
                cases_by_suite,
            )
        )
    problems.extend(
        _validate_candidates(
            root, schemas, known, eligible, case_ids_by_suite, cases_by_suite
        )
    )
    return problems
