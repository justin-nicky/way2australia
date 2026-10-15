"""Production retrieval-eligibility policy (R8, R9).

A stored document is not automatically eligible for production RAG ingestion.
`EligibilityPolicy` is the single explicit place that decides eligibility:

    approval_status == approved
    AND lifecycle_status == active
    AND retrieval_enabled
    AND NOT synthetic
    AND access_scope in policy.allowed_access_scopes

The allowed access scopes are server-owned input. They come from the caller's
trusted server-side role mapping (Phase 1: `guest` -> `public`), never from a
user request, a document, or an LLM. Eligibility is never inferred from the
directory a document lives in, and language metadata (`lote_languages`,
`content_language`) never influences it: language only narrows which eligible
documents apply, it cannot widen access.
"""

from dataclasses import dataclass

from way2australia_core.documents import (
    ALL_LOTE_LANGUAGES,
    AccessScope,
    ApprovalStatus,
    KnowledgeDocument,
    LifecycleStatus,
)

from way2australia_rag.repositories.base import DocumentQuery, DocumentRepository


@dataclass(frozen=True, slots=True)
class EligibilityPolicy:
    """Which documents may reach production retrieval for one server-chosen role."""

    allowed_access_scopes: frozenset[AccessScope]

    def __post_init__(self) -> None:
        if not self.allowed_access_scopes:
            raise ValueError("allowed_access_scopes must not be empty")

    def is_eligible(self, document: KnowledgeDocument) -> bool:
        return (
            document.approval_status is ApprovalStatus.APPROVED
            and document.lifecycle_status is LifecycleStatus.ACTIVE
            and document.retrieval_enabled
            and not document.synthetic
            and document.access_scope in self.allowed_access_scopes
        )

    def query(self, lote_language: str | None = None) -> DocumentQuery:
        """Repository filter equivalent to this policy.

        `lote_language` only narrows applicability; it never changes the
        access scopes.
        """
        return DocumentQuery(
            allowed_access_scopes=self.allowed_access_scopes,
            approval_status=ApprovalStatus.APPROVED,
            lifecycle_status=LifecycleStatus.ACTIVE,
            retrieval_enabled=True,
            synthetic=False,
            lote_language=lote_language,
        )


GUEST_PUBLIC_POLICY = EligibilityPolicy(frozenset({AccessScope.PUBLIC}))
"""Phase 1 policy: the `guest` role may retrieve `public` knowledge only."""


async def list_eligible_documents(
    repository: DocumentRepository,
    policy: EligibilityPolicy,
    lote_language: str | None = None,
) -> list[KnowledgeDocument]:
    """List documents eligible under `policy`, optionally for one CCL language.

    The policy filter is pushed to the repository and then re-applied to the
    result, so a repository that ignores part of the query still cannot leak an
    ineligible document.
    """
    documents = await repository.list_documents(policy.query(lote_language))
    return [
        d
        for d in documents
        if policy.is_eligible(d)
        and (
            lote_language is None
            or ALL_LOTE_LANGUAGES in d.lote_languages
            or lote_language in d.lote_languages
        )
    ]
