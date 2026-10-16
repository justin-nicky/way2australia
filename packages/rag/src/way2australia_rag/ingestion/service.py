"""Ingestion service: align the index with eligible documents (Spec 004 R1, R10, R11).

Target state comes only from `list_eligible_documents`; anything indexed that is
not in the target is deleted. A changed document is embedded first and only then
replaced, so an embedding failure leaves its old points untouched. Each document
is handled in its own try/except; failures are reported and the run continues.
Reports and logs carry document IDs and exception class names, never document
text or filesystem paths.
"""

import logging
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict
from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.ingestion.chunking import Chunk, Chunker
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.ingestion.errors import IngestionError, OptionalDependencyError
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import build_payload
from way2australia_rag.ingestion.settings import build_index_settings
from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
from way2australia_rag.repositories import (
    DocumentRepository,
    EligibilityPolicy,
    list_eligible_documents,
)

logger = logging.getLogger(__name__)


class DocumentFailure(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    reason: str


class RunReport(BaseModel):
    """Outcome of one run. IDs and labels only; no paths, no document text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    index_version: str
    collection: str
    embedder_model_id: str
    embedder_is_fake: bool
    added: list[str]
    updated: list[str]
    unchanged: list[str]
    deleted: list[str]
    failures: list[DocumentFailure]


def _reason(error: Exception) -> str:
    # IngestionError messages are path-free by contract; for anything else
    # (client or model errors) only the class name is safe to report.
    if isinstance(error, IngestionError):
        return f"{type(error).__name__}: {error}"
    return type(error).__name__


class IngestionService:
    def __init__(
        self,
        repository: DocumentRepository,
        policy: EligibilityPolicy,
        chunker: Chunker,
        embedder: Embedder,
        store: QdrantIndexStore,
        batch_size: int,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self._repository = repository
        self._policy = policy
        self._chunker = chunker
        self._embedder = embedder
        self._store = store
        self._batch_size = batch_size

    async def run(self) -> RunReport:
        settings = build_index_settings(
            self._store.index_version, self._embedder.info, self._chunker
        )
        self._store.ensure_collection(settings)
        logger.info("ingestion: collection '%s' ready", self._store.collection)
        target = await list_eligible_documents(self._repository, self._policy)
        state = self._store.read_state()
        logger.info(
            "ingestion: %d eligible document(s), %d indexed document(s)",
            len(target),
            len(state),
        )
        target_ids = {d.document_id for d in target}

        added: list[str] = []
        updated: list[str] = []
        unchanged: list[str] = []
        deleted: list[str] = []
        failures: list[DocumentFailure] = []

        stale = sorted(set(state) - target_ids)
        if stale:
            try:
                self._store.delete_documents(stale)
                deleted = stale
            except Exception as error:  # noqa: BLE001 - reported, run continues
                logger.warning("delete failed for %d document(s)", len(stale))
                failures.extend(
                    DocumentFailure(document_id=i, reason=_reason(error)) for i in stale
                )

        for document in sorted(target, key=lambda d: d.document_id):
            document_id = document.document_id
            chunks = self._chunker.chunk(document)
            expected = {point_id(document_id, c.section_id, c.position) for c in chunks}
            indexed = state.get(document_id)
            if indexed is None:
                category = added
            elif (
                indexed.content_hash != document.content_hash
                or indexed.document_version != document.document_version
                or set(indexed.point_ids) != expected
            ):
                category = updated
            else:
                unchanged.append(document_id)
                continue
            try:
                points = self._embed(document, chunks)
                self._store.replace_document(document_id, points)
            except OptionalDependencyError:
                raise  # a missing group affects every document: refuse the run
            except Exception as error:  # noqa: BLE001 - reported, run continues
                logger.warning(
                    "ingestion failed for %s: %s", document_id, type(error).__name__
                )
                failures.append(
                    DocumentFailure(document_id=document_id, reason=_reason(error))
                )
                continue
            category.append(document_id)

        logger.info(
            "ingestion: added %d, updated %d, unchanged %d, deleted %d, failed %d",
            len(added),
            len(updated),
            len(unchanged),
            len(deleted),
            len(failures),
        )
        return RunReport(
            index_version=self._store.index_version,
            collection=self._store.collection,
            embedder_model_id=self._embedder.info.model_id,
            embedder_is_fake=self._embedder.info.is_fake,
            added=added,
            updated=updated,
            unchanged=unchanged,
            deleted=deleted,
            failures=failures,
        )

    def _embed(
        self, document: KnowledgeDocument, chunks: Sequence[Chunk]
    ) -> list[IndexPoint]:
        vectors: list[list[float]] = []
        for start in range(0, len(chunks), self._batch_size):
            batch = chunks[start : start + self._batch_size]
            result = self._embedder.embed_documents([c.text for c in batch])
            if len(result) != len(batch):
                raise IngestionError("embedder returned a wrong number of vectors")
            vectors.extend(result)
        return [
            IndexPoint(
                point_id=point_id(document.document_id, c.section_id, c.position),
                vector=vector,
                payload=build_payload(document, c),
            )
            for c, vector in zip(chunks, vectors, strict=True)
        ]
