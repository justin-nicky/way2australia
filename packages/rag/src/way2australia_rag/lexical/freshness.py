"""Freshness of a lexical file against the document repository (Spec 008 R4).

Recomputes the chunk digest from the same eligible documents, chunker and point
IDs that `make index-lexical` writes, and compares it with the digest recorded
in the file. Messages carry counts only, never text.

Cost: every call reads, parses, chunks and hashes every eligible document.
Revisit for a large corpus (D060).
"""

import asyncio

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.lexical.build import _identity, production_entries
from way2australia_rag.lexical.store import (
    REBUILD_ADVICE,
    LexicalIndex,
    LexicalIndexBindingError,
    chunk_set_difference,
    source_chunk_digest,
)
from way2australia_rag.repositories import DocumentRepository


def verify_fresh(
    lexical: LexicalIndex, repository: DocumentRepository, chunker: Chunker
) -> None:
    """Return when the file matches the repository; else `LexicalIndexBindingError`."""
    entries = asyncio.run(production_entries(repository, chunker))
    identities = {_identity(point, payload) for point, payload in entries}
    if source_chunk_digest(identities) == lexical.settings.source_chunk_digest:
        return
    diff = chunk_set_difference(identities, lexical.chunk_identities())
    raise LexicalIndexBindingError(
        f"lexical index '{lexical.label}' is stale against the document "
        f"repository (chunks only in the repository: {diff.only_expected}; "
        f"only in the lexical index: {diff.only_mine}; with different "
        f"document_version or content_hash: {diff.changed}). {REBUILD_ADVICE}"
    )
