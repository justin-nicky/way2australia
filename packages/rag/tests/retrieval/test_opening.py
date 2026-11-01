"""`open_retrieval` for `bm25` and its two CLIs: no embedder, no Qdrant client,
no model (Spec 008 R5)."""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT, manifest_document_count
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.cli import build_chunker
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import DenseIdentity, LexicalIdentityInput
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval import cli as retrieve_cli
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import load_retrieval_config

BGE_M3_MODULE = "way2australia_rag.ingestion.bge_m3"


class Raises:
    """A factory that must never be called."""

    calls = 0

    def __call__(self, *_args: Any, **_kwargs: Any) -> Any:
        type(self).calls += 1
        raise AssertionError("must not be called on the bm25 path")


@pytest.fixture
def fake_lexical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A lexical file built from the real corpus with the configured fake identity."""
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    collection = collection_name("way2australia", config.index_version)
    model_id, revision = embedder_identity(config, "fake")
    chunker = build_chunker(config)
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    entries = asyncio.run(production_entries(repository, chunker))
    directory = tmp_path / "lex"
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
            chunker_name=chunker.name,
            chunker_version=chunker.version,
            chunker_max_chunk_chars=chunker.max_chunk_chars,
            hash_contract=HASH_CONTRACT,
        ),
    )
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "W2A_TENANT_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "way2australia")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    monkeypatch.chdir(tmp_path)
    return directory


def block_model_stack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)  # type: ignore[arg-type]
    monkeypatch.delitem(sys.modules, BGE_M3_MODULE, raising=False)


def test_open_retrieval_bm25_builds_no_embedder_and_no_client(
    fake_lexical: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    block_model_stack(monkeypatch)
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    settings = load_runtime_settings(RetrievalConfigurationError)
    opened = open_retrieval(
        Strategy.BM25,
        settings=settings,
        ingestion_config=config,
        retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
        provider="fake",
        repo_root=REPO_ROOT,
        client_factory=Raises(),
        embedder_factory=Raises(),
    )
    try:
        access = resolve_access(
            AccessContext(role=Role.GUEST, tenant_id="way2australia")
        )
        assert opened.embedder is None and opened.index_settings is None
        assert opened.identity.source == "lexical_file"
        assert opened.document_count(access) == manifest_document_count()
        result = opened.retriever.retrieve("Is coaching compulsory?", access, 5)
        assert result.hits and result.strategy == "bm25"
    finally:
        opened.close()
    assert Raises.calls == 0
    assert BGE_M3_MODULE not in sys.modules


def test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model(
    fake_lexical: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    block_model_stack(monkeypatch)
    code = retrieve_cli.main(
        [
            "Is coaching compulsory?",
            "--repo-root",
            str(REPO_ROOT),
            "--embedder",
            "fake",
            "--strategy",
            "bm25",
        ],
        client_factory=Raises(),
    )
    out = capsys.readouterr()
    assert code == 0, out.err
    assert "strategy=bm25" in out.out
    assert BGE_M3_MODULE not in sys.modules


def test_bm25_path_imports_neither_the_model_adapter_nor_the_model_stack() -> None:
    """In a fresh interpreter, importing the opening module loads no BGE-M3 code
    (the adapter is imported only inside `build_embedder`'s provider branch)."""
    code = (
        "import sys\n"
        "import way2australia_rag.retrieval.opening\n"
        "import way2australia_rag.retrieval.cli\n"
        f"assert {BGE_M3_MODULE!r} not in sys.modules\n"
        "heavy = {'torch', 'sentence_transformers', 'transformers'}\n"
        "assert not heavy & set(sys.modules), heavy & set(sys.modules)\n"
    )
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stderr
