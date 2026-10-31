"""Deterministic point identity (Spec 004 R9)."""

import uuid

from way2australia_rag.ingestion.config import IngestionConfig
from way2australia_rag.ingestion.embedding import FakeEmbedder

# Fixed UUID namespace for ingestion point IDs. Generated once (uuid4) during
# Spec 004 T5 and never changed: changing it changes every point ID and would
# make every document look half-restored. Pinned by a unit test.
INGESTION_NAMESPACE = uuid.UUID("533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2")

_SEPARATOR = "\x1f"  # ASCII unit separator: joins fields unambiguously


def point_id(document_id: str, section_id: str, position: int) -> str:
    """UUIDv5 of document ID, section ID and chunk position."""
    name = _SEPARATOR.join((document_id, section_id, str(position)))
    return str(uuid.uuid5(INGESTION_NAMESPACE, name))


def embedder_identity(config: IngestionConfig, provider: str) -> tuple[str, str]:
    """Model ID and revision the dense index is (to be) built with. The model is
    never loaded."""
    if provider == "fake":
        info = FakeEmbedder(config.embedder.fake_vector_size).info
        return info.model_id, info.revision
    return config.embedder.model_id, config.embedder.revision
