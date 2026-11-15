"""Lexical store under serving: tokenizer refusal, shared connection, close once
(Spec 013 R2, R3, R7; Spec 010 T5)."""

import asyncio
import sqlite3
import threading
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from lexical_support import identity, open_lexical, payload
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.cli import build_chunker
from way2australia_rag.ingestion.config import (
    RuntimeSettings,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.lexical import store as lexical_store
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import (
    DenseIdentity,
    LexicalIdentityInput,
    LexicalIndex,
    LexicalIndexBindingError,
)
from way2australia_rag.lexical.store import _read_only_connection as open_readonly
from way2australia_rag.lexical.tokenizer import TOKENIZERS
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import load_retrieval_config

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

RETRIEVAL = REPO_ROOT / "config/retrieval.yaml"
INGESTION = REPO_ROOT / "config/ingestion.yaml"


class _TracingLock:
    """A lock that reports when a second acquire finds it already held."""

    def __init__(self) -> None:
        self._inner = threading.Lock()
        self.waiting = threading.Event()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        if self._inner.locked():
            self.waiting.set()
        return self._inner.acquire(blocking, timeout)

    def release(self) -> None:
        self._inner.release()

    def __enter__(self) -> "_TracingLock":
        self.acquire()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()


class _Guard:
    """Stands in for the read-only connection so a test can count closes and
    hold a query inside `execute`."""

    def __init__(self, inner: sqlite3.Connection) -> None:
        self._inner = inner
        self.block = False
        self.entered = threading.Event()
        self.release = threading.Event()
        self.in_execute = False
        self.close_calls = 0
        self.closed_during_execute = False

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        if not self.block:
            return self._inner.execute(*args, **kwargs)
        self.in_execute = True
        self.entered.set()
        try:
            assert self.release.wait(timeout=1)
            return self._inner.execute(*args, **kwargs)
        finally:
            self.in_execute = False

    def close(self) -> None:
        if self.in_execute:
            self.closed_during_execute = True
        self.close_calls += 1
        self._inner.close()


class CountingClient:
    def __init__(self, inner: QdrantClient) -> None:
        self._inner = inner
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        self._inner.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def guard_opens(monkeypatch: pytest.MonkeyPatch) -> list[_Guard]:
    opened: list[_Guard] = []

    def wrapping(path: Path) -> _Guard:
        guard = _Guard(open_readonly(path))
        opened.append(guard)
        return guard

    monkeypatch.setattr(lexical_store, "_read_only_connection", wrapping)
    return opened


def pub(doc: str, text: str) -> dict[str, Any]:
    return payload(
        doc,
        text,
        language_scope="global",
        lote_languages=["*"],
        content_language="en",
        title=f"T {doc}",
        knowledge_domain="d",
        source_authority="business_policy",
        source_type="faq",
        source_url=None,
        section_id="s",
        chunk_position=0,
    )


def guest() -> Any:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def stable(result: RetrievalResult) -> dict[str, Any]:
    data = result.model_dump()
    data.pop("latency_ms", None)
    data.pop("leg_latency_ms", None)
    return data


def retriever_for(lexical: LexicalIndex) -> BM25Retriever:
    info = FakeEmbedder().info
    return BM25Retriever(
        IndexIdentity(
            collection=lexical.settings.collection,
            index_version=lexical.settings.index_version,
            embedder_model_id=info.model_id,
            embedder_revision=info.revision,
            embedder_is_fake=info.is_fake,
            source="lexical_file",
        ),
        lexical,
    )


def synthetic_file(tmp_path: Path) -> Path:
    target = tmp_path / "lex.sqlite"
    build_lexical_index(
        [
            ("p1", pub("doc_a", "coaching coaching coaching sessions")),
            ("p2", pub("doc_b", "mock tests and materials")),
            ("p3", pub("doc_c", "coaching and more words about other things here")),
        ],
        target,
        identity(),
    )
    return target


def prepare_v1_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A lexical-v1 file whose identity matches `config/ingestion.yaml`."""
    config = load_ingestion_config(INGESTION)
    collection = collection_name("way2australia", config.index_version)
    model_id, revision = embedder_identity(config, "fake")
    chunker = build_chunker(config, FakeTokenizer())
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    entries = asyncio.run(
        production_entries(repository, chunker, FakeTokenizer(), None)
    )
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
        tokenizer=TOKENIZERS["lexical-v1"],
    )
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "W2A_TENANT_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "way2australia")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    monkeypatch.chdir(tmp_path)
    return directory


def assert_tokenizer_refusal(message: str, directory: Path) -> None:
    assert "make index-lexical" in message
    assert "lexical-v1" in message and "lexical-v2" in message
    assert "tokenizer" in message
    assert str(directory) not in message
    assert "/" not in message


def test_standalone_refuses_lexical_v1_under_lexical_v2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare_v1_file(tmp_path, monkeypatch)
    guards = guard_opens(monkeypatch)
    retrieval = load_retrieval_config(RETRIEVAL)
    assert retrieval.lexical.tokenizer == "lexical-v2"
    with pytest.raises(LexicalIndexBindingError) as caught:
        open_retrieval(
            Strategy.BM25,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=load_ingestion_config(INGESTION),
            retrieval_config=retrieval,
            provider="fake",
            repo_root=REPO_ROOT,
        )
    assert_tokenizer_refusal(str(caught.value), directory)
    assert [guard.close_calls for guard in guards] == [1]


def test_bound_path_refuses_lexical_v1_under_lexical_v2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare_v1_file(tmp_path, monkeypatch)
    client = QdrantClient(":memory:")

    def ingest_factory(_settings: RuntimeSettings) -> QdrantClient:
        return client

    assert (
        ingestion_cli.main(
            ["--repo-root", str(REPO_ROOT), "--embedder", "fake"],
            client_factory=ingest_factory,
        )
        == 0
    )
    guards = guard_opens(monkeypatch)
    counting = CountingClient(client)

    def open_factory(_settings: RuntimeSettings) -> QdrantClient:
        return counting  # type: ignore[return-value]

    retrieval = load_retrieval_config(RETRIEVAL)
    assert retrieval.lexical.tokenizer == "lexical-v2"
    with pytest.raises(LexicalIndexBindingError) as caught:
        open_retrieval(
            Strategy.HYBRID,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=load_ingestion_config(INGESTION),
            retrieval_config=retrieval,
            provider="fake",
            repo_root=REPO_ROOT,
            client_factory=open_factory,
        )
    assert_tokenizer_refusal(str(caught.value), directory)
    assert [guard.close_calls for guard in guards] == [1]
    assert counting.close_calls == 1


def test_eight_threads_match_serial_bm25(tmp_path: Path) -> None:
    lexical = open_lexical(synthetic_file(tmp_path))
    retriever = retriever_for(lexical)
    access = guest()
    try:
        serial = retriever.retrieve("coaching", access, 5)
        assert serial.hits
        expected = stable(serial)
        barrier = threading.Barrier(8)
        found: list[tuple[str, Any]] = [("missing", None)] * 8

        def worker(index: int) -> None:
            try:
                barrier.wait(timeout=1)
                result = retriever.retrieve("coaching", access, 5)
                found[index] = ("ok", stable(result))
            except BaseException as exc:  # noqa: BLE001 - reported below
                found[index] = ("err", exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=1)
        assert all(not thread.is_alive() for thread in threads)
        assert found == [("ok", expected)] * 8
    finally:
        lexical.close()


def test_close_while_querying_closes_the_connection_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = synthetic_file(tmp_path)
    guards = guard_opens(monkeypatch)
    lexical = open_lexical(target)
    guard = guards[0]
    lexical._lock = _TracingLock()  # type: ignore[assignment]
    retriever = retriever_for(lexical)
    access = guest()
    serial = retriever.retrieve("coaching", access, 5)
    assert serial.hits
    guard.block = True
    results: list[RetrievalResult] = []
    errors: list[BaseException] = []

    def query() -> None:
        try:
            results.append(retriever.retrieve("coaching", access, 5))
        except BaseException as exc:  # noqa: BLE001 - reported below
            errors.append(exc)

    query_thread = threading.Thread(target=query)
    close_thread = threading.Thread(target=lexical.close)
    started_close = False
    query_thread.start()
    try:
        assert guard.entered.wait(timeout=1)
        close_thread.start()
        started_close = True
        assert lexical._lock.waiting.wait(timeout=1)  # type: ignore[attr-defined]
        assert guard.close_calls == 0
        guard.release.set()
    finally:
        guard.release.set()
        query_thread.join(timeout=1)
        if started_close:
            close_thread.join(timeout=1)
    assert not query_thread.is_alive()
    assert not close_thread.is_alive()
    assert errors == []
    assert [result.hits for result in results] == [serial.hits]
    assert guard.closed_during_execute is False
    assert guard.close_calls == 1
    lexical.close()
    assert guard.close_calls == 1
