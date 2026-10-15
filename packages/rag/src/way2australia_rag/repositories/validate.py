"""`make validate-knowledge`: validate the production knowledge corpus.

Thin entry point over the repository and manifest modules. It collects every
problem it can find (document ID, field, reason), prints one line each plus a
summary count, and exits 0 when valid or 1 on any problem. Messages carry
repository-relative paths only, never absolute ones.
"""

import argparse
import asyncio
import sys
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

from pydantic import ValidationError
from way2australia_core.documents import (
    AccessScope,
    ApprovalStatus,
    KnowledgeDocument,
    LifecycleStatus,
)

from way2australia_rag.repositories.base import DocumentQuery
from way2australia_rag.repositories.eligibility import (
    GUEST_PUBLIC_POLICY,
    list_eligible_documents,
)
from way2australia_rag.repositories.errors import (
    DocumentRepositoryError,
    DuplicateDocumentError,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.local import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
    document_fields,
    under_root,
)
from way2australia_rag.repositories.manifest import (
    ManifestEntry,
    ValidationProblem,
    check_manifest_documents,
    describe_error,
    load_manifest,
    load_schema,
)


def _error_problems(exc: DocumentRepositoryError) -> list[ValidationProblem]:
    """Turn a repository error into problems (one per listed line when multiline)."""
    if isinstance(exc, DuplicateDocumentError):
        return [
            ValidationProblem(
                exc.document_id, "document_id", _duplicate_reason(exc.version)
            )
        ]
    lines = [line.strip() for line in str(exc).splitlines() if line.strip()]
    if len(lines) > 1:
        return [ValidationProblem(None, None, line) for line in lines[1:]]
    return [ValidationProblem(None, None, lines[0] if lines else type(exc).__name__)]


def _duplicate_reason(version: int | None) -> str:
    if version is None:
        return "document_id appears more than once in the manifest"
    return f"(document_id, document_version) {version} appears more than once"


def _model_problems(entry: ManifestEntry, repo_root: Path) -> list[ValidationProblem]:
    """Validate the Pydantic model, listing every model error."""
    document_id = entry.document_id
    try:
        text = (repo_root / entry.path).read_text(encoding="utf-8")
        metadata, body = split_frontmatter(text)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        reason = str(exc) if type(exc) is ValueError else describe_error(exc)
        return [ValidationProblem(document_id, "frontmatter", reason)]
    problems: list[ValidationProblem] = []
    try:
        KnowledgeDocument.model_validate(document_fields(body, metadata))
    except ValidationError as exc:
        for error in exc.errors():
            field = ".".join(str(p) for p in error["loc"]) or "document"
            problems.append(ValidationProblem(document_id, field, error["msg"]))
    return problems


def _unlisted_files(
    config: LocalRepositoryConfig, listed_paths: set[str]
) -> list[ValidationProblem]:
    problems: list[ValidationProblem] = []
    for root in config.approved_roots:
        base = config.repo_root / root
        if not base.is_dir():
            continue
        for file_path in sorted(base.rglob("*.md")):
            rel = PurePosixPath(file_path.relative_to(config.repo_root).as_posix())
            if str(rel) not in listed_paths:
                problems.append(
                    ValidationProblem(
                        str(rel),
                        "path",
                        "markdown file under an approved root is not listed in the "
                        "manifest, so it will not be loaded",
                    )
                )
    return problems


def _corpus_problems(config: LocalRepositoryConfig) -> list[ValidationProblem]:
    """Check the loaded production corpus is safe for guest/public retrieval.

    Any document that retrieval could pick up (active and retrieval-enabled) must
    be public, approved and not synthetic. The eligible set is then re-derived
    through the guest/public policy as a second check.
    """
    repository = LocalDocumentRepository(config)
    candidates = asyncio.run(
        repository.list_documents(
            DocumentQuery(
                lifecycle_status=LifecycleStatus.ACTIVE, retrieval_enabled=True
            )
        )
    )
    problems: list[ValidationProblem] = []
    for doc in candidates:
        if doc.synthetic:
            problems.append(
                ValidationProblem(
                    doc.document_id, "synthetic", "synthetic document is retrievable"
                )
            )
        if doc.approval_status is not ApprovalStatus.APPROVED:
            problems.append(
                ValidationProblem(
                    doc.document_id,
                    "approval_status",
                    f"retrievable document is {doc.approval_status.value}, "
                    "not approved",
                )
            )
        if doc.access_scope is not AccessScope.PUBLIC:
            problems.append(
                ValidationProblem(
                    doc.document_id,
                    "access_scope",
                    f"production public corpus holds a {doc.access_scope.value} "
                    "document, not public",
                )
            )
    eligible = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    for doc in eligible:
        if (
            doc.synthetic
            or doc.approval_status is not ApprovalStatus.APPROVED
            or doc.access_scope is not AccessScope.PUBLIC
        ):
            problems.append(
                ValidationProblem(
                    doc.document_id,
                    "eligibility",
                    "eligible document is synthetic, not approved or not public",
                )
            )
    return problems


def validate_knowledge(config: LocalRepositoryConfig) -> list[ValidationProblem]:
    """Return every problem found in the corpus described by `config`."""
    root = config.repo_root
    try:
        validator = load_schema(root / config.schema_path)
        all_entries = load_manifest(root / config.manifest_path, validator)
    except DocumentRepositoryError as exc:
        return _error_problems(exc)

    problems: list[ValidationProblem] = []
    entries: list[ManifestEntry] = []
    for entry in all_entries:
        if under_root(entry.path, config.approved_roots):
            entries.append(entry)
        else:
            problems.append(
                ValidationProblem(
                    entry.document_id,
                    "path",
                    f"{entry.path} is outside the approved production roots and "
                    "will not be loaded",
                )
            )
    problems.extend(_unlisted_files(config, {e.path for e in all_entries}))

    document_problems = check_manifest_documents(entries, root, validator)
    problems.extend(document_problems)
    broken = {p.document_id for p in document_problems}
    for entry in entries:
        if entry.document_id not in broken:
            problems.extend(_model_problems(entry, root))

    if not problems:
        try:
            problems.extend(_corpus_problems(config))
        except DocumentRepositoryError as exc:
            problems.extend(_error_problems(exc))
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate-knowledge",
        description="Validate the production knowledge corpus.",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="repository root"
    )
    args = parser.parse_args(argv)
    config = LocalRepositoryConfig(repo_root=args.repo_root.resolve())
    problems = validate_knowledge(config)
    for problem in problems:
        print(f"ERROR {problem}")
    if problems:
        print(f"validate-knowledge: FAILED with {len(problems)} problem(s)")
        return 1
    print("validate-knowledge: OK, 0 problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
