"""Ingestion config 1.1, index settings and lexical identity (Spec 009 T3)."""

import asyncio
import json
import shutil
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from conftest import REPO_ROOT, KeepOpenClient
from lexical_support import COLLECTION, VERSION, repository
from lexical_support import identity as lexical_identity_input
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.chunker_build import (
    build_chunker,
    build_chunker_from_config,
    chunker_identity,
    chunker_identity_for_run,
)
from way2australia_rag.ingestion.chunking import ChunkerIdentity, HeadingChunker
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.settings import (
    IndexSettings,
    build_index_settings,
    collection_name,
)
from way2australia_rag.ingestion.store import QdrantIndexStore
from way2australia_rag.ingestion.tokenization import (
    FAKE_TOKENIZER_MODEL_ID,
    FAKE_TOKENIZER_REVISION,
    FakeTokenizer,
    build_tokenizer,
)
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.cli import main as lexical_cli_main
from way2australia_rag.lexical.freshness import verify_fresh
from way2australia_rag.lexical.store import (
    DenseIdentity,
    LexicalIdentityInput,
    LexicalIndex,
    LexicalIndexBindingError,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval import cli as retrieve_cli
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.retriever import DenseRetriever
from way2australia_rag.retrieval.strategy import load_retrieval_config

CONFIG = REPO_ROOT / "config/ingestion.yaml"
RECURSIVE = REPO_ROOT / "experiments/configs/chunking/recursive-128.yaml"
HEADING_COPY = REPO_ROOT / "experiments/configs/chunking/heading-idx-v1.yaml"
HEADING_BASELINE = (
    Path(__file__).resolve().parent / "fixtures" / "heading-idx-v1-ingestion.yaml"
)
RETRIEVAL = REPO_ROOT / "config/retrieval.yaml"
BGE_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "bge_m3"


@pytest.fixture(autouse=True)
def bge_tokenizer_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(
        repo_id: str, filename: str, *, revision: str, local_files_only: bool = False
    ) -> str:
        return str(BGE_FIXTURE_DIR / filename)

    monkeypatch.setattr("huggingface_hub.hf_hub_download", fake_download)


def test_heading_idx_v1_yaml_matches_pre_promotion_baseline() -> None:
    assert HEADING_COPY.read_bytes() == HEADING_BASELINE.read_bytes()


def test_recursive_embedder_block_matches_production() -> None:
    recursive = yaml.safe_load(RECURSIVE.read_text(encoding="utf-8"))
    baseline = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert recursive["embedder"] == baseline["embedder"]


def test_clis_load_recursive_config() -> None:
    for module in (
        "way2australia_rag.ingestion.cli",
        "way2australia_rag.lexical.cli",
        "way2australia_rag.retrieval.cli",
        "way2australia_rag.evaluation.cli",
    ):
        __import__(module)
    load_ingestion_config(RECURSIVE)


def test_schema_1_0_still_loads_heading() -> None:
    config = load_ingestion_config(HEADING_COPY)
    assert config.schema_version == "1.0"
    assert config.chunker.name == "heading"


def test_schema_1_1_loads_recursive_arm() -> None:
    config = load_ingestion_config(RECURSIVE)
    assert config.schema_version == "1.1"
    assert config.chunker.name == "recursive"
    assert config.index_version == "idx-v2"


def test_unknown_chunker_refused(tmp_path: Path) -> None:
    raw = yaml.safe_load(RECURSIVE.read_text(encoding="utf-8"))
    raw["chunker"]["name"] = "semantic"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(IngestionConfigurationError):
        load_ingestion_config(path)


def _structure_config(tmp_path: Path) -> Path:
    raw = yaml.safe_load(RECURSIVE.read_text(encoding="utf-8"))
    raw["chunker"] = {
        "name": "structure",
        "version": "1",
        "max_chunk_tokens": 64,
        "context_prefix": "title_and_headings",
    }
    path = tmp_path / "structure.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


@pytest.mark.parametrize("path", [HEADING_COPY, RECURSIVE])
def test_chunker_identity_matches_built_chunker(path: Path) -> None:
    config = load_ingestion_config(path)
    built = build_chunker(config, build_tokenizer(config.embedder))
    assert chunker_identity(config) == built.identity
    assert chunker_identity(config) == build_chunker_from_config(config).identity


def test_chunker_identity_matches_for_structure(tmp_path: Path) -> None:
    config = load_ingestion_config(_structure_config(tmp_path))
    built = build_chunker(config, build_tokenizer(config.embedder))
    assert chunker_identity(config) == built.identity


def test_chunker_identity_for_run_uses_selected_embedder() -> None:
    config = load_ingestion_config(RECURSIVE)
    fake = build_chunker(config, FakeTokenizer())
    assert chunker_identity_for_run(config, "fake") == fake.identity
    assert chunker_identity_for_run(config, "fake").tokenizer == (
        f"{FAKE_TOKENIZER_MODEL_ID}@{FAKE_TOKENIZER_REVISION}"
    )
    assert chunker_identity(config).tokenizer != fake.identity.tokenizer


def test_index_settings_1_0_upgrades_in_memory() -> None:
    legacy = {
        "schema_version": "1.0",
        "index_version": "idx-v1",
        "embedder_model_id": "fake-hash-embedder",
        "embedder_revision": "1",
        "embedder_vector_size": 64,
        "embedder_normalize": True,
        "embedder_is_fake": True,
        "chunker_name": "heading",
        "chunker_version": "1",
        "chunker_max_chunk_chars": 2000,
        "hash_contract": "content-hash-v1",
    }
    upgraded = IndexSettings.from_stored(legacy)
    wanted = build_index_settings("idx-v1", FakeEmbedder().info, HeadingChunker())
    assert upgraded.model_dump(exclude={"schema_version", "hash_contract"}) == (
        wanted.model_dump(exclude={"schema_version", "hash_contract"})
    )


def test_lexical_1_0_fixture_refused(tmp_path: Path) -> None:
    target = tmp_path / "legacy.sqlite"
    build_lexical_index([], target, lexical_identity_input())
    connection = sqlite3.connect(target)
    row = connection.execute(
        "SELECT value FROM settings WHERE key = 'lexical_settings'"
    ).fetchone()
    settings = json.loads(row[0])
    settings["schema_version"] = "1.0"
    settings["chunker_max_chunk_chars"] = 2000
    settings.pop("chunker_params", None)
    settings.pop("chunker_tokenizer", None)
    connection.execute(
        "UPDATE settings SET value = ? WHERE key = 'lexical_settings'",
        (json.dumps(settings),),
    )
    connection.commit()
    connection.close()
    with pytest.raises(LexicalIndexBindingError, match="lexical settings 1.0"):
        LexicalIndex.open(target, COLLECTION, VERSION)


def test_rebuild_lexical_1_1_preserves_digest(tmp_path: Path) -> None:
    repo = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    chunker = build_chunker_from_config(load_ingestion_config(CONFIG))
    entries = asyncio.run(production_entries(repo, chunker, FakeTokenizer(), None))
    target = tmp_path / "lex.sqlite"
    build_lexical_index(entries, target, lexical_identity_input())
    before = LexicalIndex.open(target, COLLECTION, VERSION).settings
    build_lexical_index(entries, target, lexical_identity_input())
    after = json.loads(
        sqlite3.connect(target)
        .execute("SELECT value FROM settings WHERE key = 'lexical_settings'")
        .fetchone()[0]
    )
    assert after["schema_version"] == "1.2"
    assert after["source_chunk_digest"] == before.source_chunk_digest
    assert after["chunk_count"] == before.chunk_count


def test_verify_fresh_refuses_added_document(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    full_knowledge = tmp_path / "full"
    shutil.copytree(REPO_ROOT / "knowledge", full_knowledge)
    shutil.copytree(full_knowledge, repo_root / "knowledge")
    manifest = repo_root / "knowledge/manifest/document_manifest.jsonl"
    removed_line = manifest.read_text(encoding="utf-8").splitlines()[0]
    removed_id = json.loads(removed_line)["document_id"]
    kept_lines = manifest.read_text(encoding="utf-8").splitlines()[1:]
    manifest.write_text("\n".join(kept_lines) + "\n")
    repo = LocalDocumentRepository(LocalRepositoryConfig(repo_root=repo_root))
    chunker = HeadingChunker()
    entries = asyncio.run(production_entries(repo, chunker, FakeTokenizer(), None))
    target = tmp_path / "lex.sqlite"
    build_lexical_index(entries, target, lexical_identity_input())
    shutil.rmtree(repo_root / "knowledge")
    shutil.copytree(full_knowledge, repo_root / "knowledge")
    repo = LocalDocumentRepository(LocalRepositoryConfig(repo_root=repo_root))
    lexical = LexicalIndex.open(target, COLLECTION, VERSION)
    try:
        with pytest.raises(LexicalIndexBindingError) as caught:
            verify_fresh(lexical, repo, chunker.identity)
        message = str(caught.value)
        assert "documents only in the repository: 1" in message
        assert removed_id  # referenced so the scenario stays tied to a real document
    finally:
        lexical.close()


def test_verify_fresh_refuses_chunker_name_mismatch(tmp_path: Path) -> None:
    build_lexical_index([], tmp_path / "lex.sqlite", lexical_identity_input())
    lexical = LexicalIndex.open(tmp_path / "lex.sqlite", COLLECTION, VERSION)
    other = ChunkerIdentity(
        name="recursive", version="1", params={"target_tokens": 32}, tokenizer="x@y"
    )
    with pytest.raises(LexicalIndexBindingError, match="chunker_name"):
        verify_fresh(lexical, repository(), other)


def test_open_retrieval_bm25_without_tokenizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = load_ingestion_config(CONFIG)
    collection = collection_name("way2australia", config.index_version)
    model_id, revision = embedder_identity(config, "fake")
    chunker = build_chunker(config, FakeTokenizer())
    repo = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    entries = asyncio.run(production_entries(repo, chunker, FakeTokenizer(), None))
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
            chunker=chunker.identity,
            hash_contract=HASH_CONTRACT,
        ),
    )
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "way2australia")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    monkeypatch.chdir(tmp_path)
    with patch(
        "way2australia_rag.ingestion.tokenization.build_tokenizer",
        side_effect=AssertionError("must not load tokenizer on bm25 open"),
    ):
        opened = open_retrieval(
            Strategy.BM25,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=config,
            retrieval_config=load_retrieval_config(RETRIEVAL),
            provider="fake",
            repo_root=REPO_ROOT,
        )
        opened.close()


def test_lexical_cli_recursive_fake_embedder_records_built_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = "w2a-t009-fake-rec"
    config = load_ingestion_config(RECURSIVE)
    collection = collection_name(base, config.index_version)
    target = tmp_path / f"{collection}.sqlite"
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", base)
    assert (
        lexical_cli_main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "--config",
                str(RECURSIVE),
                "--embedder",
                "fake",
                "--output",
                str(target),
            ]
        )
        == 0
    )
    built = build_chunker(config, FakeTokenizer())
    lexical = LexicalIndex.open(target, collection, config.index_version)
    try:
        assert lexical.settings.chunker_tokenizer == (
            f"{FAKE_TOKENIZER_MODEL_ID}@{FAKE_TOKENIZER_REVISION}"
        )
        assert lexical.settings.chunker_identity() == built.identity
    finally:
        lexical.close()
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    with patch(
        "way2australia_rag.ingestion.tokenization.build_tokenizer",
        side_effect=AssertionError("must not load tokenizer on bm25 open"),
    ):
        opened = open_retrieval(
            Strategy.BM25,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=config,
            retrieval_config=load_retrieval_config(RETRIEVAL),
            provider="fake",
            repo_root=REPO_ROOT,
        )
        opened.close()


def test_open_hybrid_paths_without_tokenizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = load_ingestion_config(CONFIG)
    base = "w2a-t009-hybrid-fallback"
    collection = collection_name(base, config.index_version)
    client = QdrantClient(":memory:")
    embedder = FakeEmbedder(config.embedder.fake_vector_size)
    chunker = build_chunker(config, FakeTokenizer())
    store = QdrantIndexStore(client, base, config.index_version)
    service = IngestionService(
        LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT)),
        GUEST_PUBLIC_POLICY,
        chunker,
        embedder,
        store,
        config.embedder.batch_size,
        FakeTokenizer(),
        None,
    )
    assert not asyncio.run(service.run()).failures
    entries = asyncio.run(
        production_entries(
            LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT)),
            chunker,
            FakeTokenizer(),
            None,
        )
    )
    build_lexical_index(
        entries,
        lexical_index_path(tmp_path, collection),
        LexicalIdentityInput(
            collection=collection,
            index_version=config.index_version,
            dense_identity=DenseIdentity(
                collection=collection,
                index_version=config.index_version,
                embedder_model_id=embedder.info.model_id,
                embedder_revision=embedder.info.revision,
            ),
            chunker=chunker.identity,
            hash_contract=HASH_CONTRACT,
        ),
    )
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", base)
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
    tokenizer_patch = patch(
        "way2australia_rag.ingestion.tokenization.build_tokenizer",
        side_effect=AssertionError("must not load tokenizer on retrieval open"),
    )

    def client_factory(_settings: object) -> QdrantClient:
        # `close()` closes the client (Spec 013 R2); the test opens it twice.
        return KeepOpenClient(client)  # type: ignore[return-value]

    with tokenizer_patch:
        opened = open_retrieval(
            Strategy.HYBRID,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=config,
            retrieval_config=load_retrieval_config(RETRIEVAL),
            provider="fake",
            repo_root=REPO_ROOT,
            client_factory=client_factory,
        )
        try:
            calls = {"n": 0}
            original = DenseRetriever.retrieve

            def flaky_dense(
                self: DenseRetriever,
                query_text: str,
                access: ResolvedAccess,
                top_k: int = 5,
                *,
                lote: ResolvedLote | None = None,
            ) -> RetrievalResult:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RetrievalUnavailableError(FallbackReason.QDRANT_TIMEOUT)
                return original(self, query_text, access, top_k, lote=lote)

            monkeypatch.setattr(DenseRetriever, "retrieve", flaky_dense)
            result = opened.retriever.retrieve("Is coaching compulsory?", access, 5)
            assert result.strategy == "bm25"
            assert result.fallback_reason == "qdrant_timeout"
        finally:
            opened.close()

    with tokenizer_patch:
        assert (
            retrieve_cli.main(
                [
                    "Is coaching compulsory?",
                    "--repo-root",
                    str(REPO_ROOT),
                    "--embedder",
                    "fake",
                    "--no-rerank",
                    "--strategy",
                    "hybrid",
                ],
                client_factory=client_factory,
            )
            == 0
        )
