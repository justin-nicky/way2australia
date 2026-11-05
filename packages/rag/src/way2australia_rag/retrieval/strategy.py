"""Retrieval strategy configuration and factory (Spec 007 R8).

`build_retriever` is the only place a strategy name becomes a retriever.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    ValidationError,
    model_validator,
)

from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.lexical.build import default_lexical_dir, lexical_index_path
from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.lexical.tokenizer import TOKENIZERS
from way2australia_rag.retrieval.base import MAX_TOP_K, Retriever, Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

DEFAULT_CONFIG_PATH = "config/retrieval.yaml"


class QdrantTimeouts(BaseModel):
    """Qdrant request bounds in whole seconds (Spec 008 R2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    connect_timeout_s: StrictInt = Field(ge=1, le=30)
    query_timeout_s: StrictInt = Field(ge=1, le=30)


class LexicalConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tokenizer: str = "lexical-v1"

    @model_validator(mode="after")
    def known_tokenizer(self) -> "LexicalConfig":
        if self.tokenizer not in TOKENIZERS:
            raise ValueError(f"unknown lexical tokenizer {self.tokenizer!r}")
        return self


_FLOATING_REVISIONS = frozenset({"main", "latest"})


class RerankConfig(BaseModel):
    """The `rerank` block (Spec 011 R3). Off unless a 1.3 file turns it on."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = False
    provider: Literal["bge", "fake"] = "bge"
    model_id: str = "BAAI/bge-reranker-v2-m3"
    revision: str | None = None
    depth: StrictInt = Field(default=20, ge=1, le=MAX_TOP_K)
    max_length: StrictInt = Field(default=512, ge=32, le=8192)
    batch_size: StrictInt = Field(default=16, ge=1, le=256)

    @model_validator(mode="after")
    def pinned_revision(self) -> "RerankConfig":
        if self.revision is not None:
            cleaned = self.revision.strip()
            if not cleaned or cleaned.lower() in _FLOATING_REVISIONS:
                raise ValueError("rerank.revision must be a pinned commit SHA")
        if self.enabled and self.revision is None:
            raise ValueError("rerank.revision is required when rerank.enabled")
        return self


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.1", "1.2", "1.3"]
    default_strategy: Strategy
    fusion: FusionConfig
    qdrant: QdrantTimeouts
    lexical: LexicalConfig = LexicalConfig()
    rerank: RerankConfig = RerankConfig()

    @model_validator(mode="before")
    @classmethod
    def default_lexical_for_11(cls, data: object) -> object:
        if isinstance(data, dict) and data.get("schema_version") == "1.1":
            if "lexical" not in data:
                return {**data, "lexical": {"tokenizer": "lexical-v1"}}
        return data

    @model_validator(mode="before")
    @classmethod
    def rerank_block_matches_schema(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        version = data.get("schema_version")
        if version == "1.3" and "rerank" not in data:
            raise ValueError("rerank is required in schema 1.3")
        if version in ("1.1", "1.2") and "rerank" in data:
            raise ValueError("rerank needs schema 1.3")
        return data

    @model_validator(mode="after")
    def rerank_depth_within_fusion(self) -> "RetrievalConfig":
        if self.rerank.depth > self.fusion.candidate_depth:
            raise ValueError("rerank.depth must not exceed fusion.candidate_depth")
        return self


def _model_error_text(entry: Mapping[str, Any]) -> str:
    """Our own `rerank.*` ValueError text (model-level validators carry no precise
    field location); empty for every other error."""
    ctx = entry.get("ctx")
    if isinstance(ctx, dict):
        text = str(ctx.get("error", ""))
        if text.startswith("rerank"):
            return text
    return ""


def load_retrieval_config(path: Path) -> RetrievalConfig:
    """Load and validate the config file; any problem is a configuration error."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        # Only the file name: never the absolute path or parser excerpts.
        raise RetrievalConfigurationError(
            f"cannot read retrieval config '{path.name}' ({type(error).__name__})"
        ) from None
    if not isinstance(raw, dict):
        raise RetrievalConfigurationError(
            f"retrieval config '{path.name}' must be a YAML mapping"
        )
    try:
        return RetrievalConfig.model_validate(raw)
    except ValidationError as error:
        fields = sorted(
            {
                _model_error_text(e) or ".".join(str(p) for p in e["loc"])
                for e in error.errors()
            }
        )
        raise RetrievalConfigurationError(
            f"invalid retrieval config '{path.name}': check {', '.join(fields)}"
        ) from None


def build_retriever(
    strategy: Strategy,
    identity: IndexIdentity,
    dense_index: DenseIndex | None,
    embedder: Embedder | None,
    lexical: LexicalIndex | None,
    config: RetrievalConfig,
) -> Retriever:
    """Map a strategy to its retriever. `dense` and `hybrid` need `dense_index`
    and `embedder`; `bm25` and `hybrid` need `lexical`."""
    try:
        chosen = Strategy(strategy)
    except ValueError:
        raise RetrievalConfigurationError(
            f"unknown retrieval strategy {strategy!r}"
        ) from None
    if chosen == Strategy.BM25:
        if lexical is None:
            raise RetrievalConfigurationError(
                "strategy 'bm25' needs the lexical index; "
                "build it with `make index-lexical`."
            )
        return BM25Retriever(identity, lexical)
    if chosen not in (Strategy.DENSE, Strategy.HYBRID):
        raise RetrievalConfigurationError(f"unsupported strategy '{chosen.value}'")
    if dense_index is None or embedder is None:
        raise RetrievalConfigurationError(
            f"strategy '{chosen.value}' needs the dense index and the embedder."
        )
    if chosen == Strategy.DENSE:
        return DenseRetriever(dense_index, embedder)
    if lexical is None:
        raise RetrievalConfigurationError(
            f"strategy '{chosen.value}' needs the lexical index; "
            "build it with `make index-lexical`."
        )
    bm25 = BM25Retriever(identity, lexical)
    hybrid = HybridRetriever(DenseRetriever(dense_index, embedder), bm25, config.fusion)
    return FallbackRetriever(hybrid, bm25, None)


def needs_lexical(strategy: Strategy) -> bool:
    return strategy in (Strategy.BM25, Strategy.HYBRID)


def open_bound_lexical(
    settings: RuntimeSettings, repo_root: Path, dense_index: DenseIndex
) -> LexicalIndex:
    """Open the lexical file for the bound dense index and verify it belongs to it.

    The path is `<lexical_index_dir>/<collection>.sqlite` (the `make index-lexical`
    default). A missing, foreign or stale file raises `LexicalIndexBindingError`
    with rebuild advice, before any query."""
    directory = settings.lexical_index_dir or default_lexical_dir(repo_root)
    if not directory.is_absolute():
        directory = repo_root / directory
    lexical = LexicalIndex.open(
        lexical_index_path(directory, dense_index.collection),
        dense_index.collection,
        dense_index.index_version,
    )
    try:
        lexical.bind_to(dense_index)
    except BaseException:
        lexical.close()
        raise
    return lexical
