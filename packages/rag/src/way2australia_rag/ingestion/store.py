"""Qdrant index store: collection, companion settings collection, state, writes.

Phase 1 batch ingestion only. Replacing a document deletes its points and then
upserts the new ones; the brief window between the two calls is accepted
(Spec 004 R9). Atomic switching belongs to the Phase 2 release workflow.
The store never deletes a collection.
"""

from collections.abc import Iterable, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from qdrant_client import QdrantClient, models

from way2australia_rag.ingestion.errors import (
    IndexSettingsMismatchError,
    IngestionConfigurationError,
)
from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.ingestion.settings import (
    IndexSettings,
    collection_name,
    compare,
    mismatch_message,
)

DENSE_VECTOR_NAME = "dense"
SETTINGS_COLLECTION_SUFFIX = "-settings"
# Fixed ID of the single point in the companion settings collection.
SETTINGS_POINT_ID = "00000000-0000-0000-0000-000000000001"
KEYWORD_INDEX_FIELDS: tuple[str, ...] = (
    "access_scope",
    "tenant_id",
    "document_id",
    "content_language",
    "lote_languages",
)
_STATE_FIELDS = ["document_id", "document_version", "content_hash"]
_SCROLL_PAGE = 256


class IndexPoint(BaseModel):
    """One point to write: deterministic ID, dense vector and payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    point_id: str
    vector: list[float]
    payload: PointPayload


class IndexedDocument(BaseModel):
    """What the index currently holds for one document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_version: int
    content_hash: str
    point_ids: frozenset[str]


class QdrantIndexStore:
    def __init__(
        self, client: QdrantClient, collection_base: str, index_version: str
    ) -> None:
        self._client = client
        self._index_version = index_version
        self.index_version = index_version
        self.collection = collection_name(collection_base, index_version)
        self.settings_collection = self.collection + SETTINGS_COLLECTION_SUFFIX

    def ensure_collection(self, settings: IndexSettings) -> None:
        """Create or validate the collection per the design's startup table."""
        if settings.index_version != self._index_version:
            raise IngestionConfigurationError(
                "index settings index_version does not match the store's index_version."
            )
        if not self._client.collection_exists(self.collection):
            self._create_collection(settings)
            self._write_settings(settings)
            return
        recorded = self._read_settings()
        if recorded is not None:
            if compare(recorded, settings):
                raise IndexSettingsMismatchError(
                    mismatch_message(self.collection, recorded, settings)
                )
            return
        if self._client.count(self.collection, exact=True).count > 0:
            raise IndexSettingsMismatchError(
                f"collection '{self.collection}' has points but no recorded "
                "index settings (unknown provenance). To build with these "
                "settings, set index_version to a new label in "
                "config/ingestion.yaml; the existing collection is left untouched."
            )
        self._write_settings(settings)

    def read_state(self) -> dict[str, IndexedDocument]:
        """Scroll identity payloads only (no vectors) into per-document state.

        If a document's points disagree on version or hash (a half-written
        state), version 0 and an empty hash are reported so the document
        always differs from its target and is rewritten.
        """
        versions: dict[str, set[int]] = {}
        hashes: dict[str, set[str]] = {}
        ids: dict[str, set[str]] = {}
        offset: Any = None
        while True:
            records, offset = self._client.scroll(
                self.collection,
                limit=_SCROLL_PAGE,
                offset=offset,
                with_payload=models.PayloadSelectorInclude(include=_STATE_FIELDS),
                with_vectors=False,
            )
            for record in records:
                data = record.payload or {}
                document_id = str(data["document_id"])
                versions.setdefault(document_id, set()).add(
                    int(data["document_version"])
                )
                hashes.setdefault(document_id, set()).add(str(data["content_hash"]))
                ids.setdefault(document_id, set()).add(str(record.id))
            if offset is None:
                break
        state: dict[str, IndexedDocument] = {}
        for document_id, point_ids in ids.items():
            consistent = (
                len(versions[document_id]) == 1 and len(hashes[document_id]) == 1
            )
            state[document_id] = IndexedDocument(
                document_version=next(iter(versions[document_id])) if consistent else 0,
                content_hash=next(iter(hashes[document_id])) if consistent else "",
                point_ids=frozenset(point_ids),
            )
        return state

    def replace_document(self, document_id: str, points: Sequence[IndexPoint]) -> None:
        """Delete all of the document's points, then upsert the new ones in one call."""
        self._delete_by_document_ids([document_id])
        if not points:
            return
        self._client.upsert(
            self.collection,
            points=[
                models.PointStruct(
                    id=point.point_id,
                    vector={DENSE_VECTOR_NAME: point.vector},
                    payload=point.payload.model_dump(mode="json"),
                )
                for point in points
            ],
            wait=True,
        )

    def delete_documents(self, document_ids: Iterable[str]) -> None:
        self._delete_by_document_ids(list(document_ids))

    def _delete_by_document_ids(self, document_ids: list[str]) -> None:
        if not document_ids:
            return
        self._client.delete(
            self.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchAny(any=document_ids),
                        )
                    ]
                )
            ),
            wait=True,
        )

    def _create_collection(self, settings: IndexSettings) -> None:
        self._client.create_collection(
            self.collection,
            vectors_config={
                DENSE_VECTOR_NAME: models.VectorParams(
                    size=settings.embedder_vector_size,
                    distance=models.Distance.COSINE,
                )
            },
        )
        for field in KEYWORD_INDEX_FIELDS:
            self._client.create_payload_index(
                self.collection,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

    def _read_settings(self) -> IndexSettings | None:
        if not self._client.collection_exists(self.settings_collection):
            return None
        found = self._client.retrieve(
            self.settings_collection,
            ids=[SETTINGS_POINT_ID],
            with_payload=True,
            with_vectors=False,
        )
        if not found or found[0].payload is None:
            return None
        try:
            return IndexSettings.model_validate(found[0].payload)
        except ValidationError as error:
            # Field names only: never echo the payload.
            fields = sorted({".".join(map(str, e["loc"])) for e in error.errors()})
            raise IndexSettingsMismatchError(
                f"recorded index settings for collection '{self.collection}' are "
                f"malformed or foreign (invalid fields: {', '.join(fields)}); "
                "set index_version to a new label in config/ingestion.yaml. "
                "The existing collection is left untouched."
            ) from error

    def _write_settings(self, settings: IndexSettings) -> None:
        if not self._client.collection_exists(self.settings_collection):
            self._client.create_collection(
                self.settings_collection,
                vectors_config=models.VectorParams(
                    size=1, distance=models.Distance.COSINE
                ),
            )
        self._client.upsert(
            self.settings_collection,
            points=[
                models.PointStruct(
                    id=SETTINGS_POINT_ID,
                    vector=[1.0],
                    payload=settings.model_dump(mode="json"),
                )
            ],
            wait=True,
        )
