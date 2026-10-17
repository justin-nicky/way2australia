"""Index settings recorded with an index, and the mismatch comparison (Spec 004 R7).

`batch_size` and `max_length` are deliberately not index settings: they do not
change the vectors an embedder produces, so a change to them never requires a
new index.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.ingestion.embedding import EmbedderInfo
from way2australia_rag.repositories.hashing import HASH_CONTRACT

SETTINGS_SCHEMA_VERSION = "1.0"


class IndexSettings(BaseModel):
    """Settings an index was built with. `hash_contract` is recorded, never compared."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"] = SETTINGS_SCHEMA_VERSION
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_vector_size: int
    embedder_normalize: bool
    embedder_is_fake: bool
    chunker_name: str
    chunker_version: str
    chunker_max_chunk_chars: int
    hash_contract: str


_IGNORED_FIELDS = frozenset({"hash_contract"})


def build_index_settings(
    index_version: str,
    embedder: EmbedderInfo,
    chunker: Chunker,
    hash_contract: str = HASH_CONTRACT,
) -> IndexSettings:
    return IndexSettings(
        index_version=index_version,
        embedder_model_id=embedder.model_id,
        embedder_revision=embedder.revision,
        embedder_vector_size=embedder.vector_size,
        embedder_normalize=embedder.normalize,
        embedder_is_fake=embedder.is_fake,
        chunker_name=chunker.name,
        chunker_version=chunker.version,
        chunker_max_chunk_chars=chunker.max_chunk_chars,
        hash_contract=hash_contract,
    )


def compare(recorded: IndexSettings, wanted: IndexSettings) -> list[str]:
    """Names of fields that differ, ignoring `hash_contract`. Empty means compatible."""
    return [
        name
        for name in IndexSettings.model_fields
        if name not in _IGNORED_FIELDS
        and getattr(recorded, name) != getattr(wanted, name)
    ]


def mismatch_message(
    collection: str, recorded: IndexSettings, wanted: IndexSettings
) -> str:
    """Refusal text listing each differing field; points to a new index_version."""
    differences = compare(recorded, wanted)
    details = "; ".join(
        f"{name}: recorded {getattr(recorded, name)!r}, "
        f"wanted {getattr(wanted, name)!r}"
        for name in differences
    )
    return (
        f"index settings mismatch for collection '{collection}' ({details}). "
        "To build with these settings, set index_version to a new label in "
        "config/ingestion.yaml; the existing collection is left untouched."
    )


def collection_name(collection_base: str, index_version: str) -> str:
    """The single derivation of the collection name: `<base>-<index_version>`."""
    return f"{collection_base}-{index_version}"
