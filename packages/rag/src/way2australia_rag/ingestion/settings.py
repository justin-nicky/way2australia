"""Index settings recorded with an index, and the mismatch comparison (Spec 004 R7).

`batch_size` and `max_length` are deliberately not index settings: they are
run-time embedder options, not properties of the stored vectors. `batch_size`
does not change vectors. `max_length` could change vectors if inputs exceeded
the model limit and were truncated; Spec 009 refuses oversize chunks before
embedding (truncation guard), so production chunks always embed in full.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from way2australia_rag.ingestion.chunking import Chunker, ChunkerIdentity
from way2australia_rag.ingestion.embedding import EmbedderInfo
from way2australia_rag.repositories.hashing import HASH_CONTRACT

SETTINGS_SCHEMA_VERSION = "1.1"
_LEGACY_SCHEMA_VERSION = "1.0"

_IGNORED_FIELDS = frozenset({"hash_contract", "schema_version"})


class IndexSettings(BaseModel):
    """Settings an index was built with. `hash_contract` is recorded, never compared."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.1"] = SETTINGS_SCHEMA_VERSION
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_vector_size: int
    embedder_normalize: bool
    embedder_is_fake: bool
    chunker_name: str
    chunker_version: str
    chunker_params: dict[str, str | int | bool]
    chunker_tokenizer: str | None
    hash_contract: str

    @classmethod
    def from_stored(cls, payload: dict[str, Any]) -> "IndexSettings":
        """Upgrade schema 1.0 in memory; stored 1.0 payloads are never rewritten."""
        data = dict(payload)
        if data.get("schema_version") == _LEGACY_SCHEMA_VERSION:
            data["schema_version"] = SETTINGS_SCHEMA_VERSION
            data["chunker_params"] = {
                "max_chunk_chars": data.pop("chunker_max_chunk_chars")
            }
            data["chunker_tokenizer"] = None
        return cls.model_validate(data)

    def chunker_identity(self) -> ChunkerIdentity:
        return ChunkerIdentity(
            name=self.chunker_name,
            version=self.chunker_version,
            params=dict(sorted(self.chunker_params.items())),
            tokenizer=self.chunker_tokenizer,
        )


def build_index_settings(
    index_version: str,
    embedder: EmbedderInfo,
    chunker: Chunker,
    hash_contract: str = HASH_CONTRACT,
) -> IndexSettings:
    identity = chunker.identity
    return IndexSettings(
        index_version=index_version,
        embedder_model_id=embedder.model_id,
        embedder_revision=embedder.revision,
        embedder_vector_size=embedder.vector_size,
        embedder_normalize=embedder.normalize,
        embedder_is_fake=embedder.is_fake,
        chunker_name=identity.name,
        chunker_version=identity.version,
        chunker_params=dict(sorted(identity.params.items())),
        chunker_tokenizer=identity.tokenizer,
        hash_contract=hash_contract,
    )


def compare(recorded: IndexSettings, wanted: IndexSettings) -> list[str]:
    """Names of fields that differ, ignoring `hash_contract` and `schema_version`."""
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
