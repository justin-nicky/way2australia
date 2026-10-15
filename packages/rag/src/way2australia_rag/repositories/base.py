"""Storage-independent document repository contract.

Ingestion and retrieval code obtains source documents only through
`DocumentRepository` (Constitution C2). The contract exposes
`KnowledgeDocument` objects and never filesystem paths, so a future
`S3DocumentRepository` can implement it unchanged. The interface is async for
the same reason: network-backed stores need non-blocking I/O.
"""

from typing import Protocol

from pydantic import BaseModel, ConfigDict
from way2australia_core.documents import (
    ALL_LOTE_LANGUAGES,
    AccessScope,
    ApprovalStatus,
    KnowledgeDocument,
    LifecycleStatus,
)


class DocumentQuery(BaseModel):
    """Filter for `DocumentRepository.list_documents`.

    Every field is optional; `None` means "do not filter on this". Filters are
    server-created values and are ANDed together. This object carries no
    storage concepts (no paths, no URIs). Eligibility *policy* (which values
    guest/public may use) is owned by the eligibility module, not by this shape.

    `allowed_access_scopes` and `lote_language` are independent: language
    applicability never widens or implies access.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed_access_scopes: frozenset[AccessScope] | None = None
    approval_status: ApprovalStatus | None = None
    lifecycle_status: LifecycleStatus | None = None
    retrieval_enabled: bool | None = None
    synthetic: bool | None = None
    lote_language: str | None = None

    def matches(self, document: KnowledgeDocument) -> bool:
        """True when `document` satisfies every set filter (the one shared rule).

        A document applies to a language when it is global (`*`) or lists the
        code. Language only narrows; it is independent of access scope.
        """
        scopes = self.allowed_access_scopes
        return (
            (scopes is None or document.access_scope in scopes)
            and self.approval_status in (None, document.approval_status)
            and self.lifecycle_status in (None, document.lifecycle_status)
            and self.retrieval_enabled in (None, document.retrieval_enabled)
            and self.synthetic in (None, document.synthetic)
            and (
                self.lote_language is None
                or ALL_LOTE_LANGUAGES in document.lote_languages
                or self.lote_language in document.lote_languages
            )
        )


class DocumentRepository(Protocol):
    """Read-only access to versioned knowledge documents.

    Implementations: `LocalDocumentRepository` (Phase 1); a future
    `S3DocumentRepository` (Phase 2) must satisfy this same contract without
    changes to `KnowledgeDocument` or ingestion.
    """

    async def get_document(
        self,
        document_id: str,
        version: int | None = None,
    ) -> KnowledgeDocument:
        """Return one document; the latest version when `version` is None.

        Raises `DocumentNotFoundError` if no match exists.
        """
        ...

    async def list_documents(
        self,
        query: DocumentQuery | None = None,
    ) -> list[KnowledgeDocument]:
        """Return documents matching `query` (all when None), in a stable order."""
        ...
