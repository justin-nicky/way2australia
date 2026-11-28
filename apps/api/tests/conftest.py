"""Fixtures for the serving tests (helpers: `support.py`)."""

import asyncio
from pathlib import Path
from typing import Any

import pytest
from way2australia_rag.ingestion.cli import build_chunker
from way2australia_rag.ingestion.config import load_ingestion_config
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import (
    DenseIdentity,
    LexicalIdentityInput,
    LexicalIndex,
)
from way2australia_rag.lexical.tokenizer import TOKENIZERS
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.strategy import load_retrieval_config

from .support import REPO_ROOT, CountingGenerator


@pytest.fixture(autouse=True)
def serving_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "W2A_TENANT_ID", "W2A_API_FAKE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "way2australia")


@pytest.fixture
def fake_lexical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A lexical file from the real corpus with the configured fake identity."""
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    collection = collection_name("way2australia", config.index_version)
    model_id, revision = embedder_identity(config, "fake")
    chunker = build_chunker(config, FakeTokenizer())
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    entries = asyncio.run(
        production_entries(repository, chunker, FakeTokenizer(), None)
    )
    directory = tmp_path / "lex"
    retrieval = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    build_lexical_index(
        entries,
        lexical_index_path(directory, collection),
        LexicalIdentityInput(
            collection=collection,
            index_version=config.index_version,
            dense_identity=DenseIdentity(
                collection=collection,
                index_version=config.index_version,
                embedder_model_id=model_id,
                embedder_revision=revision,
            ),
            chunker=chunker.identity,
            hash_contract=HASH_CONTRACT,
        ),
        tokenizer=TOKENIZERS[retrieval.lexical.tokenizer],
    )
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    return directory


@pytest.fixture
def generators(monkeypatch: pytest.MonkeyPatch) -> list[CountingGenerator]:
    """Every generator phase 1 builds (the lifespan's `build_generator`)."""
    built: list[CountingGenerator] = []

    def build(_config: object, _provider: str | None = None) -> CountingGenerator:
        built.append(CountingGenerator())
        return built[-1]

    monkeypatch.setattr("way2australia_api.lifespan.build_generator", build)
    return built


@pytest.fixture
def lexical_handles(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    counts = {"opened": 0, "closed": 0}
    open_ = LexicalIndex.open.__func__  # type: ignore[attr-defined]
    close = LexicalIndex.close

    def counting_open(cls: Any, *args: Any, **kwargs: Any) -> LexicalIndex:
        counts["opened"] += 1
        return open_(cls, *args, **kwargs)

    def counting_close(self: LexicalIndex) -> None:
        counts["closed"] += 1
        close(self)

    monkeypatch.setattr(LexicalIndex, "open", classmethod(counting_open))
    monkeypatch.setattr(LexicalIndex, "close", counting_close)
    return counts
