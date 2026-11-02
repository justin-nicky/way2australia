"""Build chunkers and chunker identity from ingestion config (Spec 009 R5)."""

from __future__ import annotations

from way2australia_rag.ingestion.chunking import (
    Chunker,
    ChunkerIdentity,
    HeadingChunker,
)
from way2australia_rag.ingestion.config import (
    EmbedderConfig,
    HeadingChunkerSpec,
    IngestionConfig,
    RecursiveChunkerSpec,
    StructureChunkerSpec,
)
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.recursive import RecursiveChunker
from way2australia_rag.ingestion.structure import StructureChunker
from way2australia_rag.ingestion.tokenization import (
    FAKE_TOKENIZER_MODEL_ID,
    FAKE_TOKENIZER_REVISION,
    ChunkTokenizer,
    build_tokenizer,
    embedder_for_run,
)


def tokenizer_ref_from_embedder(embedder: EmbedderConfig) -> str:
    if embedder.provider == "fake":
        return f"{FAKE_TOKENIZER_MODEL_ID}@{FAKE_TOKENIZER_REVISION}"
    return f"{embedder.model_id}@{embedder.revision}"


def _sorted_params(params: dict[str, str | int | bool]) -> dict[str, str | int | bool]:
    return dict(sorted(params.items()))


def chunker_params_from_spec(
    spec: HeadingChunkerSpec | StructureChunkerSpec | RecursiveChunkerSpec,
) -> dict[str, str | int | bool]:
    if isinstance(spec, HeadingChunkerSpec):
        return {"max_chunk_chars": spec.max_chunk_chars}
    if isinstance(spec, StructureChunkerSpec):
        return {
            "context_prefix": spec.context_prefix,
            "max_chunk_tokens": spec.max_chunk_tokens,
        }
    return {
        "context_prefix": spec.context_prefix,
        "overlap_tokens": spec.overlap_tokens,
        "target_tokens": spec.target_tokens,
    }


def chunker_identity(config: IngestionConfig) -> ChunkerIdentity:
    """Chunker identity from the config file's embedder; no tokenizer file load."""
    return chunker_identity_for_run(config, config.embedder.provider)


def chunker_identity_for_run(config: IngestionConfig, provider: str) -> ChunkerIdentity:
    """Expected chunker identity for a run's embedder override; no tokenizer load."""
    spec = config.chunker
    embedder = embedder_for_run(config.embedder, provider)
    if spec.name == "heading":
        tokenizer = None
    else:
        tokenizer = tokenizer_ref_from_embedder(embedder)
    return ChunkerIdentity(
        name=spec.name,
        version=spec.version,
        params=_sorted_params(chunker_params_from_spec(spec)),
        tokenizer=tokenizer,
    )


def chunk_token_cap(config: IngestionConfig) -> int | None:
    spec = config.chunker
    if isinstance(spec, HeadingChunkerSpec):
        return None
    if isinstance(spec, StructureChunkerSpec):
        return spec.max_chunk_tokens
    assert isinstance(spec, RecursiveChunkerSpec)
    return spec.target_tokens


def build_chunker(config: IngestionConfig, tokenizer: ChunkTokenizer) -> Chunker:
    spec = config.chunker
    if isinstance(spec, HeadingChunkerSpec):
        chunker = HeadingChunker(spec.max_chunk_chars)
        if (chunker.name, chunker.version) != (spec.name, spec.version):
            raise IngestionConfigurationError(
                f"unsupported chunker '{spec.name}' version '{spec.version}'."
            )
        return chunker
    if isinstance(spec, StructureChunkerSpec):
        return StructureChunker(
            max_chunk_tokens=spec.max_chunk_tokens,
            context_prefix=spec.context_prefix,
            tokenizer=tokenizer,
        )
    assert isinstance(spec, RecursiveChunkerSpec)
    return RecursiveChunker(
        target_tokens=spec.target_tokens,
        overlap_tokens=spec.overlap_tokens,
        context_prefix=spec.context_prefix,
        tokenizer=tokenizer,
    )


def build_chunker_from_config(config: IngestionConfig) -> Chunker:
    """Build a chunker using the config file's embedder for tokenizer identity."""
    return build_chunker(config, build_tokenizer(config.embedder))
