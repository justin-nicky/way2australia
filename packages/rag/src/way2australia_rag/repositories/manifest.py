"""Knowledge manifest loading and metadata validation.

The manifest (`knowledge/manifest/document_manifest.jsonl`) lists one record per
document version. Records and file frontmatter are validated against the
metadata JSON Schema; the manifest must agree with the frontmatter. Problems
are reported by `document_id` and field name, never by absolute path.
"""

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from way2australia_rag.repositories.errors import (
    DuplicateDocumentError,
    ManifestValidationError,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter

# Manifest-only bookkeeping: not expected to match frontmatter.
MANIFEST_ONLY_FIELDS = frozenset({"path", "sha256", "body_sha256"})


@dataclass(frozen=True)
class ValidationProblem:
    """One actionable validation finding."""

    document_id: str | None
    field: str | None
    reason: str

    def __str__(self) -> str:
        parts = [p for p in (self.document_id, self.field) if p]
        prefix = ": ".join(parts)
        return f"{prefix}: {self.reason}" if prefix else self.reason


@dataclass(frozen=True)
class ManifestEntry:
    """A manifest record. `path` is repository-relative POSIX, never absolute."""

    document_id: str
    document_version: int
    path: str
    record: dict[str, Any]


def describe_error(exc: Exception) -> str:
    """Describe a read/parse failure without leaking absolute filesystem paths."""
    if isinstance(exc, OSError):
        return exc.strerror or type(exc).__name__
    if isinstance(exc, json.JSONDecodeError):
        return f"invalid JSON ({exc.msg} at line {exc.lineno})"
    return type(exc).__name__


def load_schema(schema_path: Path) -> Draft202012Validator:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestValidationError(
            f"cannot load metadata schema: {describe_error(exc)}"
        ) from exc
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ManifestValidationError(
            f"metadata schema is invalid: {exc.message}"
        ) from exc
    return Draft202012Validator(schema)


def schema_problems(
    validator: Draft202012Validator, data: dict[str, Any], document_id: str | None
) -> list[ValidationProblem]:
    """Validate `data` against the metadata schema, one problem per violation."""
    problems: list[ValidationProblem] = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        if error.validator == "required":
            missing = [
                name for name in error.validator_value if name not in error.instance
            ]
            for name in missing:
                problems.append(
                    ValidationProblem(document_id, name, "required field is missing")
                )
        else:
            field = ".".join(str(part) for part in error.path) or None
            problems.append(ValidationProblem(document_id, field, error.message))
    return problems


def _path_problem(document_id: str, path: object) -> ValidationProblem | None:
    if not isinstance(path, str) or not path:
        return ValidationProblem(document_id, "path", "must be a non-empty string")
    posix = PurePosixPath(path)
    if posix.is_absolute() or ".." in posix.parts or "\\" in path:
        return ValidationProblem(
            document_id, "path", "must be a relative path inside the repository"
        )
    return None


def load_manifest(
    manifest_path: Path, validator: Draft202012Validator
) -> list[ManifestEntry]:
    """Load and structurally validate the manifest.

    Raises `ManifestValidationError` for unreadable files, bad JSON lines or
    schema violations (all problems listed), and `DuplicateDocumentError` when
    a `document_id` or `(document_id, document_version)` repeats.
    """
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise ManifestValidationError(
            f"cannot read manifest: {describe_error(exc)}"
        ) from exc

    problems: list[ValidationProblem] = []
    entries: list[ManifestEntry] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                ValidationProblem(None, None, f"line {number}: {describe_error(exc)}")
            )
            continue
        if not isinstance(record, dict):
            problems.append(
                ValidationProblem(
                    None, None, f"line {number}: record must be an object"
                )
            )
            continue
        document_id = record.get("document_id")
        label = document_id if isinstance(document_id, str) else f"line {number}"
        found = schema_problems(validator, record, label)
        for name in ("path", "sha256", "body_sha256"):
            if name not in record:
                found.append(
                    ValidationProblem(label, name, "required field is missing")
                )
        if "path" in record and (p := _path_problem(label, record["path"])):
            found.append(p)
        if found:
            problems.extend(found)
            continue
        entries.append(
            ManifestEntry(
                document_id=record["document_id"],
                document_version=record["document_version"],
                path=record["path"],
                record=record,
            )
        )

    if problems:
        raise ManifestValidationError(
            "manifest has invalid records:\n" + "\n".join(f"  {p}" for p in problems)
        )

    seen_ids: set[str] = set()
    seen_versions: set[tuple[str, int]] = set()
    for entry in entries:
        key = (entry.document_id, entry.document_version)
        if key in seen_versions:
            raise DuplicateDocumentError(*key)
        if entry.document_id in seen_ids:
            raise DuplicateDocumentError(entry.document_id)
        seen_versions.add(key)
        seen_ids.add(entry.document_id)
    return entries


def check_manifest_documents(
    entries: list[ManifestEntry], repo_root: Path, validator: Draft202012Validator
) -> list[ValidationProblem]:
    """Check each entry's file exists, its frontmatter is valid and agrees."""
    problems: list[ValidationProblem] = []
    for entry in entries:
        file_path = repo_root / entry.path
        if not file_path.is_file():
            problems.append(
                ValidationProblem(
                    entry.document_id,
                    "path",
                    f"referenced file does not exist: {entry.path}",
                )
            )
            continue
        try:
            metadata, _body = split_frontmatter(file_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            reason = str(exc) if type(exc) is ValueError else describe_error(exc)
            problems.append(ValidationProblem(entry.document_id, "frontmatter", reason))
            continue
        found = schema_problems(validator, metadata, entry.document_id)
        problems.extend(found)
        if not found:
            problems.extend(compare_manifest_to_metadata(entry, metadata))
    return problems


def compare_manifest_to_metadata(
    entry: ManifestEntry, metadata: dict[str, Any]
) -> list[ValidationProblem]:
    """Report every field where manifest and frontmatter disagree.

    The manifest is a subset of the frontmatter (it omits e.g. `effective_*`),
    so a field only the frontmatter carries is not a mismatch; a non-null
    manifest value the frontmatter lacks is.
    """
    problems: list[ValidationProblem] = []
    fields = (set(entry.record) | set(metadata)) - MANIFEST_ONLY_FIELDS
    for name in sorted(fields):
        in_manifest, in_file = name in entry.record, name in metadata
        if in_manifest and in_file:
            if entry.record[name] != metadata[name]:
                problems.append(
                    ValidationProblem(
                        entry.document_id,
                        name,
                        f"manifest has {entry.record[name]!r} but frontmatter "
                        f"has {metadata[name]!r}",
                    )
                )
        elif in_manifest and entry.record[name] is not None:
            problems.append(
                ValidationProblem(
                    entry.document_id,
                    name,
                    f"manifest has {entry.record[name]!r} but frontmatter omits it",
                )
            )
    return problems


def validate_manifest(
    manifest_path: Path, repo_root: Path, schema_path: Path
) -> list[ValidationProblem]:
    """Full validation: raises on structural/duplicate errors, else returns problems."""
    validator = load_schema(schema_path)
    entries = load_manifest(manifest_path, validator)
    return check_manifest_documents(entries, repo_root, validator)
