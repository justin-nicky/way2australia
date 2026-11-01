"""Index identity: what a dense index and its lexical file are built for
(Spec 008 R3).

`expected` comes from configuration only. It never builds an embedder, never
loads a model and never contacts Qdrant.
"""

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

from way2australia_rag.ingestion.config import IngestionConfig, RuntimeSettings
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import IndexSettings, collection_name


class _DenseLike(Protocol):  # DenseIndex satisfies it
    collection: str
    settings: IndexSettings


class IndexIdentity(BaseModel):
    """The identity of one dense index, from Qdrant or from configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    collection: str
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_is_fake: bool
    source: Literal["qdrant", "lexical_file"]

    @classmethod
    def from_settings(cls, collection: str, settings: IndexSettings) -> "IndexIdentity":
        """From the settings recorded in the dense index (source `qdrant`)."""
        return cls(
            collection=collection,
            index_version=settings.index_version,
            embedder_model_id=settings.embedder_model_id,
            embedder_revision=settings.embedder_revision,
            embedder_is_fake=settings.embedder_is_fake,
            source="qdrant",
        )

    @classmethod
    def from_dense(cls, index: _DenseLike) -> "IndexIdentity":
        return cls.from_settings(index.collection, index.settings)

    @classmethod
    def expected(
        cls, config: IngestionConfig, settings: RuntimeSettings, provider: str
    ) -> "IndexIdentity":
        """From configuration only (source `lexical_file`)."""
        model_id, revision = embedder_identity(config, provider)
        return cls(
            collection=collection_name(settings.collection_base, config.index_version),
            index_version=config.index_version,
            embedder_model_id=model_id,
            embedder_revision=revision,
            embedder_is_fake=provider == "fake",
            source="lexical_file",
        )
