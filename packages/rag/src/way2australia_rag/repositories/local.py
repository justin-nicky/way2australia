"""Local-filesystem `DocumentRepository` (Phase 1).

All path handling lives here; callers receive `KnowledgeDocument` objects only.
The manifest decides which documents exist. A manifest entry is loaded only
when its path lies under one of the configured approved roots, so raw sources,
evaluation files, docs, config, release manifests and security fixtures are
never loaded even if listed. Directory placement grants no authorization: the
access scope comes from validated metadata.
"""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import ValidationError
from way2australia_core.documents import ALL_LOTE_LANGUAGES, KnowledgeDocument

from way2australia_rag.repositories.base import DocumentQuery
from way2australia_rag.repositories.errors import (
    DocumentNotFoundError,
    DocumentValidationError,
    ManifestValidationError,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_content_hash, normalize_body
from way2australia_rag.repositories.manifest import (
    ManifestEntry,
    ValidationProblem,
    check_manifest_documents,
    describe_error,
    load_manifest,
    load_schema,
)

DEFAULT_APPROVED_ROOTS: tuple[str, ...] = (
    "knowledge/public/business",
    "knowledge/public/official",
    "knowledge/public/languages",
)
"""Repository-relative directories that production loading may read."""


@dataclass(frozen=True)
class LocalRepositoryConfig:
    """Explicit configuration; nothing is resolved from the working directory.

    `manifest_path`, `schema_path` and `approved_roots` are relative to
    `repo_root`.
    """

    repo_root: Path
    manifest_path: str = "knowledge/manifest/document_manifest.jsonl"
    schema_path: str = "knowledge/schemas/document_metadata.schema.json"
    approved_roots: tuple[str, ...] = DEFAULT_APPROVED_ROOTS


def under_root(path: str, roots: Sequence[str]) -> bool:
    parts = PurePosixPath(path).parts
    return any(parts[: len(r)] == r for r in (PurePosixPath(x).parts for x in roots))


def _applies_to_language(document: KnowledgeDocument, language: str) -> bool:
    return (
        ALL_LOTE_LANGUAGES in document.lote_languages
        or language in document.lote_languages
    )


def _matches(document: KnowledgeDocument, query: DocumentQuery) -> bool:
    scopes = query.allowed_access_scopes
    return (
        (scopes is None or document.access_scope in scopes)
        and query.approval_status in (None, document.approval_status)
        and query.lifecycle_status in (None, document.lifecycle_status)
        and query.retrieval_enabled in (None, document.retrieval_enabled)
        and query.synthetic in (None, document.synthetic)
        and (
            query.lote_language is None
            or _applies_to_language(document, query.lote_language)
        )
    )


def document_fields(body: str, metadata: dict[str, Any]) -> dict[str, Any]:
    """Model input for one document: known frontmatter fields, content and hash."""
    fields: dict[str, Any] = {
        name: metadata[name]
        for name in KnowledgeDocument.model_fields
        if name in metadata
    }
    fields["content"] = normalize_body(body)
    fields["content_hash"] = compute_content_hash(body, metadata)
    return fields


class LocalDocumentRepository:
    """Reads approved knowledge documents from the local filesystem.

    Documents are loaded and validated once, on first use, and cached. Any
    invalid document fails the whole load with a repository error naming the
    document and field (never an absolute path).
    """

    def __init__(self, config: LocalRepositoryConfig) -> None:
        self._config = config
        self._documents: list[KnowledgeDocument] | None = None
        self._lock = asyncio.Lock()

    async def get_document(
        self, document_id: str, version: int | None = None
    ) -> KnowledgeDocument:
        documents = await self._load()
        matches = [
            d
            for d in documents
            if d.document_id == document_id
            and (version is None or d.document_version == version)
        ]
        if not matches:
            raise DocumentNotFoundError(document_id, version)
        return max(matches, key=lambda d: d.document_version)

    async def list_documents(
        self, query: DocumentQuery | None = None
    ) -> list[KnowledgeDocument]:
        documents = await self._load()
        if query is None:
            return list(documents)
        return [d for d in documents if _matches(d, query)]

    async def _load(self) -> list[KnowledgeDocument]:
        async with self._lock:
            if self._documents is None:
                self._documents = await asyncio.to_thread(self._read_all)
            return self._documents

    def _read_all(self) -> list[KnowledgeDocument]:
        config = self._config
        root = config.repo_root
        validator = load_schema(root / config.schema_path)
        entries = [
            e
            for e in load_manifest(root / config.manifest_path, validator)
            if under_root(e.path, config.approved_roots)
        ]
        problems: list[ValidationProblem] = check_manifest_documents(
            entries, root, validator
        )
        if problems:
            raise ManifestValidationError(
                "documents are invalid:\n" + "\n".join(f"  {p}" for p in problems)
            )
        documents = [self._build(entry) for entry in entries]
        return sorted(documents, key=lambda d: (d.document_id, d.document_version))

    def _build(self, entry: ManifestEntry) -> KnowledgeDocument:
        try:
            text = (self._config.repo_root / entry.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise DocumentValidationError(
                entry.document_id, "content", describe_error(exc)
            ) from exc
        metadata, body = split_frontmatter(text)
        fields = document_fields(body, metadata)
        try:
            return KnowledgeDocument.model_validate(fields)
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(p) for p in first["loc"]) or "document"
            raise DocumentValidationError(
                entry.document_id, field, first["msg"]
            ) from exc
