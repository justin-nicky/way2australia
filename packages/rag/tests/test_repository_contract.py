import asyncio
import inspect
from typing import Any

import pytest
from pydantic import ValidationError
from way2australia_core.documents import AccessScope, KnowledgeDocument
from way2australia_rag.repositories import (
    DocumentNotFoundError,
    DocumentQuery,
    DocumentRepository,
    DocumentRepositoryError,
    DocumentValidationError,
    DuplicateDocumentError,
    ManifestValidationError,
)


def make_document(**overrides: Any) -> KnowledgeDocument:
    fields: dict[str, Any] = {
        "document_id": "doc_a",
        "document_version": 1,
        "title": "Doc A",
        "tenant_id": "way2australia",
        "knowledge_domain": "official_exam_rules",
        "access_scope": "public",
        "owner_user_id": None,
        "content_language": "en",
        "language_scope": "global",
        "lote_languages": ["*"],
        "source_authority": "naati",
        "source_type": "official_external_summary",
        "source_url": None,
        "approval_status": "approved",
        "lifecycle_status": "active",
        "last_reviewed_at": None,
        "introduced_in_release": "seed-v1",
        "effective_from": None,
        "effective_to": None,
        "retrieval_enabled": True,
        "synthetic": False,
        "content_hash": "a" * 64,
        "content": "text",
    }
    fields.update(overrides)
    return KnowledgeDocument.model_validate(fields)


class InMemoryDocumentRepository:
    """Satisfies `DocumentRepository` with no local files.

    The filtering here is test scaffolding for the query shape only; it is not
    the production eligibility policy (Spec 002 T6).
    """

    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self._documents = documents

    async def get_document(
        self, document_id: str, version: int | None = None
    ) -> KnowledgeDocument:
        matches = [d for d in self._documents if d.document_id == document_id]
        if version is not None:
            matches = [d for d in matches if d.document_version == version]
        if not matches:
            raise DocumentNotFoundError(document_id, version)
        return max(matches, key=lambda d: d.document_version)

    async def list_documents(
        self, query: DocumentQuery | None = None
    ) -> list[KnowledgeDocument]:
        query = query or DocumentQuery()
        scopes = query.allowed_access_scopes
        return [
            d
            for d in self._documents
            if (scopes is None or d.access_scope in scopes)
            and (query.approval_status in (None, d.approval_status))
            and (query.lifecycle_status in (None, d.lifecycle_status))
            and (query.retrieval_enabled in (None, d.retrieval_enabled))
            and (query.synthetic in (None, d.synthetic))
        ]


def use_repository(repository: DocumentRepository) -> DocumentRepository:
    # Pyright checks the structural fit of the fake at this call site.
    return repository


def test_in_memory_repository_satisfies_protocol() -> None:
    repository = use_repository(InMemoryDocumentRepository([make_document()]))

    assert asyncio.run(repository.get_document("doc_a")).document_id == "doc_a"
    assert len(asyncio.run(repository.list_documents())) == 1


def test_get_document_returns_latest_or_requested_version() -> None:
    repository = InMemoryDocumentRepository(
        [make_document(), make_document(document_version=2)]
    )

    assert asyncio.run(repository.get_document("doc_a")).document_version == 2
    assert asyncio.run(repository.get_document("doc_a", 1)).document_version == 1


def test_get_document_missing_raises_not_found() -> None:
    repository = InMemoryDocumentRepository([make_document()])

    with pytest.raises(DocumentNotFoundError) as exc_info:
        asyncio.run(repository.get_document("doc_a", 9))
    assert exc_info.value.document_id == "doc_a"
    assert "version 9" in str(exc_info.value)


def test_list_documents_applies_query_filters() -> None:
    repository = InMemoryDocumentRepository(
        [
            make_document(),
            make_document(document_id="doc_staff", access_scope="staff"),
        ]
    )
    query = DocumentQuery(allowed_access_scopes=frozenset({AccessScope.PUBLIC}))

    result = asyncio.run(repository.list_documents(query))

    assert [d.document_id for d in result] == ["doc_a"]


def test_protocol_methods_are_async() -> None:
    assert inspect.iscoroutinefunction(DocumentRepository.get_document)
    assert inspect.iscoroutinefunction(DocumentRepository.list_documents)


def test_document_query_defaults_to_no_filters() -> None:
    assert all(value is None for value in DocumentQuery().model_dump().values())


def test_document_query_has_no_filesystem_concepts() -> None:
    fields = set(DocumentQuery.model_fields)

    assert not {"path", "root", "uri", "file"} & fields
    with pytest.raises(ValidationError):
        DocumentQuery.model_validate({"path": "/tmp/x"})


def test_document_query_is_immutable() -> None:
    query = DocumentQuery()

    with pytest.raises(ValidationError):
        query.retrieval_enabled = True


def test_errors_share_base_class() -> None:
    errors = [
        DocumentNotFoundError("d"),
        DuplicateDocumentError("d", 1),
        DocumentValidationError("d", "access_scope", "bad"),
        ManifestValidationError("bad", "d", "sha256"),
    ]

    assert all(isinstance(e, DocumentRepositoryError) for e in errors)


def test_error_messages_name_document_and_field() -> None:
    assert str(DuplicateDocumentError("d", 2)) == "Duplicate document: d version 2"
    assert (
        str(DocumentValidationError("d", "access_scope", "bad"))
        == "d: access_scope: bad"
    )
    assert str(ManifestValidationError("mismatch", "d", "sha256")) == (
        "d: sha256: mismatch"
    )
    assert str(ManifestValidationError("empty manifest")) == "empty manifest"


def test_query_matches_is_the_single_language_and_scope_rule() -> None:
    global_doc = make_document()
    ml_doc = make_document(
        language_scope="language_specific", lote_languages=["ml"], content_language="ml"
    )
    staff_doc = make_document(access_scope="staff")

    assert DocumentQuery().matches(staff_doc)
    assert DocumentQuery(lote_language="xx").matches(global_doc)
    assert not DocumentQuery(lote_language="xx").matches(ml_doc)
    assert DocumentQuery(lote_language="ml").matches(ml_doc)
    scopes = frozenset({AccessScope.PUBLIC})
    assert not DocumentQuery(allowed_access_scopes=scopes, lote_language="*").matches(
        staff_doc
    )
