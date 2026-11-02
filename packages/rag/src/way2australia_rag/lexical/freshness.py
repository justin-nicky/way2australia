"""Per-document freshness of a lexical file (Spec 009 R6)."""

import asyncio

from way2australia_rag.ingestion.chunking import ChunkerIdentity
from way2australia_rag.lexical.store import (
    REBUILD_ADVICE,
    LexicalIndex,
    LexicalIndexBindingError,
)
from way2australia_rag.repositories import GUEST_PUBLIC_POLICY, DocumentRepository
from way2australia_rag.repositories.eligibility import list_eligible_documents


def verify_fresh(
    lexical: LexicalIndex,
    repository: DocumentRepository,
    chunker_identity: ChunkerIdentity,
) -> None:
    """Return when the file matches the repository; else `LexicalIndexBindingError`."""
    recorded_identity = lexical.settings.chunker_identity()
    if recorded_identity != chunker_identity:
        raise LexicalIndexBindingError(
            f"lexical index '{lexical.label}' chunker identity does not match "
            f"the configured chunker (chunker_name: recorded "
            f"{recorded_identity.name!r}, wanted {chunker_identity.name!r}). "
            f"{REBUILD_ADVICE}"
        )

    expected = asyncio.run(_eligible_document_versions(repository))
    recorded = lexical.document_versions()
    if expected == recorded:
        return
    expected_by_id = {
        document_id: (version, content_hash)
        for document_id, version, content_hash in expected
    }
    recorded_by_id = {
        document_id: (version, content_hash)
        for document_id, version, content_hash in recorded
    }
    only_repository = len(set(expected_by_id) - set(recorded_by_id))
    only_file = len(set(recorded_by_id) - set(expected_by_id))
    changed = sum(
        1
        for document_id in set(expected_by_id) & set(recorded_by_id)
        if expected_by_id[document_id] != recorded_by_id[document_id]
    )
    raise LexicalIndexBindingError(
        f"lexical index '{lexical.label}' is stale against the document "
        f"repository (documents only in the repository: {only_repository}; "
        f"only in the lexical index: {only_file}; with changed version or hash: "
        f"{changed}). {REBUILD_ADVICE}"
    )


async def _eligible_document_versions(
    repository: DocumentRepository,
) -> set[tuple[str, int, str]]:
    documents = await list_eligible_documents(repository, GUEST_PUBLIC_POLICY)
    return {
        (document.document_id, document.document_version, document.content_hash)
        for document in documents
    }
