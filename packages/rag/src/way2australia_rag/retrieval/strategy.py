"""Retrieval strategy configuration and factory (Spec 007 R8).

`build_retriever` is the only place a strategy name becomes a retriever.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError

from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.lexical.build import default_lexical_dir, lexical_index_path
from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.retrieval.base import Retriever, Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

DEFAULT_CONFIG_PATH = "config/retrieval.yaml"


class QdrantTimeouts(BaseModel):
    """Qdrant request bounds in whole seconds (Spec 008 R2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    connect_timeout_s: StrictInt = Field(ge=1, le=30)
    query_timeout_s: StrictInt = Field(ge=1, le=30)


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.1"]
    default_strategy: Strategy
    fusion: FusionConfig
    qdrant: QdrantTimeouts


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
        fields = sorted({".".join(str(p) for p in e["loc"]) for e in error.errors()})
        raise RetrievalConfigurationError(
            f"invalid retrieval config '{path.name}': check {', '.join(fields)}"
        ) from None


def build_retriever(
    strategy: Strategy,
    dense_index: DenseIndex,
    embedder: Embedder,
    lexical: LexicalIndex | None,
    config: RetrievalConfig,
) -> Retriever:
    """Map a strategy to its retriever. `bm25` and `hybrid` need `lexical`."""
    try:
        chosen = Strategy(strategy)
    except ValueError:
        raise RetrievalConfigurationError(
            f"unknown retrieval strategy {strategy!r}"
        ) from None
    if chosen == Strategy.DENSE:
        return DenseRetriever(dense_index, embedder)
    if chosen not in (Strategy.BM25, Strategy.HYBRID):
        raise RetrievalConfigurationError(f"unsupported strategy '{chosen.value}'")
    if lexical is None:
        raise RetrievalConfigurationError(
            f"strategy '{chosen.value}' needs the lexical index; "
            "build it with `make index-lexical`."
        )
    bm25 = BM25Retriever(dense_index, lexical)
    if chosen == Strategy.BM25:
        return bm25
    return HybridRetriever(DenseRetriever(dense_index, embedder), bm25, config.fusion)


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
