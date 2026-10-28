"""Read-only binding of the query embedder to the Spec 004 dense index.

`DenseIndex` calls only `collection_exists`, `get_collection`, `retrieve`,
`query_points` and `scroll`. It never creates, deletes or modifies anything.
"""

from typing import Any

from qdrant_client import QdrantClient, models

from way2australia_rag.ingestion.embedding import EmbedderInfo
from way2australia_rag.ingestion.errors import IndexSettingsMismatchError
from way2australia_rag.ingestion.settings import IndexSettings, collection_name
from way2australia_rag.ingestion.store import (
    DENSE_VECTOR_NAME,
    SETTINGS_COLLECTION_SUFFIX,
    read_index_settings,
)
from way2australia_rag.retrieval.errors import IndexBindingError

_SCROLL_PAGE = 256

# Retrieval users cannot edit config/ingestion.yaml to fix a binding problem.
_ADVICE = (
    "Re-run ingestion into this index version, or point retrieval at the "
    "matching index_version and collection."
)

# (IndexSettings field, EmbedderInfo field) pairs compared at query time.
_EMBEDDER_FIELDS: tuple[tuple[str, str], ...] = (
    ("embedder_model_id", "model_id"),
    ("embedder_revision", "revision"),
    ("embedder_vector_size", "vector_size"),
    ("embedder_normalize", "normalize"),
    ("embedder_is_fake", "is_fake"),
)


class DenseIndex:
    """A bound, read-only view of one dense index."""

    def __init__(
        self, client: QdrantClient, collection: str, settings: IndexSettings
    ) -> None:
        self._client = client
        self.collection = collection
        self.settings = settings
        self.index_version = settings.index_version

    @classmethod
    def open(
        cls,
        client: QdrantClient,
        collection_base: str,
        index_version: str,
        embedder_info: EmbedderInfo,
    ) -> "DenseIndex":
        collection = collection_name(collection_base, index_version)
        if not client.collection_exists(collection):
            raise IndexBindingError(
                f"collection '{collection}' does not exist. {_ADVICE}"
            )
        if not client.collection_exists(collection + SETTINGS_COLLECTION_SUFFIX):
            raise IndexBindingError(
                f"settings collection for '{collection}' does not exist. {_ADVICE}"
            )
        try:
            recorded = read_index_settings(client, collection)
        except IndexSettingsMismatchError as error:
            fields = ", ".join(error.invalid_fields)
            raise IndexBindingError(
                f"recorded index settings for collection '{collection}' are "
                f"malformed or foreign (invalid fields: {fields}). {_ADVICE}"
            ) from error
        if recorded is None:
            raise IndexBindingError(
                f"no index settings are recorded for collection '{collection}'. "
                f"{_ADVICE}"
            )
        differences: list[str] = []
        if recorded.index_version != index_version:
            differences.append(
                f"index_version: recorded {recorded.index_version!r}, "
                f"wanted {index_version!r}"
            )
        for settings_field, info_field in _EMBEDDER_FIELDS:
            have = getattr(recorded, settings_field)
            want = getattr(embedder_info, info_field)
            if have != want:
                differences.append(
                    f"{settings_field}: recorded {have!r}, wanted {want!r}"
                )
        if differences:
            raise IndexBindingError(
                f"index settings do not match the query embedder for collection "
                f"'{collection}' ({'; '.join(differences)}). {_ADVICE}"
            )
        cls._check_dense_vector(client, collection, embedder_info.vector_size)
        return cls(client, collection, recorded)

    @staticmethod
    def _check_dense_vector(client: QdrantClient, collection: str, size: int) -> None:
        vectors: Any = client.get_collection(collection).config.params.vectors
        params = vectors.get(DENSE_VECTOR_NAME) if isinstance(vectors, dict) else None
        if params is None:
            raise IndexBindingError(
                f"collection '{collection}' has no '{DENSE_VECTOR_NAME}' vector."
            )
        if params.size != size:
            raise IndexBindingError(
                f"'{DENSE_VECTOR_NAME}' vector size: recorded {params.size!r}, "
                f"wanted {size!r} (collection '{collection}'). {_ADVICE}"
            )

    def search(
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        response = self._client.query_points(
            self.collection,
            query=vector,
            using=DENSE_VECTOR_NAME,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return list(response.points)

    def document_count(self, query_filter: models.Filter) -> int:
        """Distinct `document_id`s visible under `query_filter`."""
        seen: set[str] = set()
        offset: Any = None
        while True:
            records, offset = self._client.scroll(
                self.collection,
                scroll_filter=query_filter,
                limit=_SCROLL_PAGE,
                offset=offset,
                with_payload=models.PayloadSelectorInclude(include=["document_id"]),
                with_vectors=False,
            )
            for record in records:
                document_id = (record.payload or {}).get("document_id")
                if document_id is None:
                    raise IndexBindingError(
                        f"a point in collection '{self.collection}' has no "
                        "'document_id'."
                    )
                seen.add(str(document_id))
            if offset is None:
                break
        return len(seen)

    def chunk_identities(self) -> list[tuple[str, str, int, str]]:
        """`(point_id, document_id, document_version, content_hash)` of every point.

        Read-only scroll without a filter and without text; used to bind a
        lexical index to this one (Spec 007 R5).
        """
        identities: list[tuple[str, str, int, str]] = []
        offset: Any = None
        while True:
            records, offset = self._client.scroll(
                self.collection,
                limit=_SCROLL_PAGE,
                offset=offset,
                with_payload=models.PayloadSelectorInclude(
                    include=["document_id", "document_version", "content_hash"]
                ),
                with_vectors=False,
            )
            for record in records:
                payload = record.payload or {}
                try:
                    identities.append(
                        (
                            str(record.id),
                            str(payload["document_id"]),
                            int(payload["document_version"]),
                            str(payload["content_hash"]),
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    raise IndexBindingError(
                        f"a point in collection '{self.collection}' has no "
                        "readable document_id, document_version or content_hash."
                    ) from None
            if offset is None:
                break
        return identities
