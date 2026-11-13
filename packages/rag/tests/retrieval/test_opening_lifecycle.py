"""`open_retrieval` lifecycle and depth rules (Spec 013 R1, R2; Spec 008 F4,
Spec 011 F3): no leaked client or lexical file on any failed open, an idempotent
`close()`, one standalone helper and the early `top_k` refusal."""

from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval import opening
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import load_retrieval_config

from .test_cli import ingest
from .test_fallback import client_at, closed_port
from .test_opening import fake_lexical  # noqa: F401  (fixture)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)


class CountingClient:
    """Delegates to a real in-memory client and counts `close` calls."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class Factory:
    def __init__(self, client: Any) -> None:
        self.client = client
        self.calls = 0

    def __call__(self, _settings: object) -> Any:
        self.calls += 1
        return self.client


class CountingReranker(FakeReranker):
    def __init__(self, *, fail: Exception | None = None) -> None:
        super().__init__()
        self.fail = fail

    def load(self) -> None:
        if self.fail is not None:
            raise self.fail
        super().load()


class RerankerFactory:
    def __init__(self, reranker: FakeReranker | None = None) -> None:
        self.reranker = reranker or CountingReranker()
        self.calls = 0

    def __call__(self, _config: Any, _provider: str | None = None) -> FakeReranker:
        self.calls += 1
        return self.reranker


@pytest.fixture
def lexical_closes(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """One entry per `LexicalIndex.close` call."""
    calls: list[int] = []
    original = LexicalIndex.close

    def counting(self: LexicalIndex) -> None:
        calls.append(1)
        original(self)

    monkeypatch.setattr(LexicalIndex, "close", counting)
    return calls


@pytest.fixture
def ingested() -> CountingClient:
    inner = QdrantClient(":memory:")
    ingest(inner)
    return CountingClient(inner)


def open_with(
    strategy: Strategy,
    factory: Any,
    *,
    rerank: bool = False,
    reranker_factory: Any = None,
    top_k: int | None = None,
    settings: Any = None,
) -> Any:
    retrieval = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    extra: dict[str, Any] = {}
    if reranker_factory is not None:
        extra["reranker_factory"] = reranker_factory
    return open_retrieval(
        strategy,
        settings=settings or load_runtime_settings(RetrievalConfigurationError),
        ingestion_config=load_ingestion_config(REPO_ROOT / "config/ingestion.yaml"),
        retrieval_config=retrieval,
        provider="fake",
        repo_root=REPO_ROOT,
        client_factory=factory,
        rerank=rerank,
        top_k=top_k,
        **extra,
    )


# --- a failure at each step closes what the call opened ----------------------


def test_dense_open_failure_closes_the_client(
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
) -> None:
    empty = CountingClient(QdrantClient(":memory:"))  # collection is absent
    with pytest.raises(Exception):  # noqa: B017, PT011 - the class is not the point
        open_with(Strategy.HYBRID, Factory(empty))
    assert empty.close_calls == 1
    assert lexical_closes == []


def test_lexical_bind_failure_closes_the_client(
    ingested: CountingClient,
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "no-lexical"
    missing.mkdir()
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(missing))
    with pytest.raises(Exception):  # noqa: B017, PT011
        open_with(Strategy.HYBRID, Factory(ingested))
    assert ingested.close_calls == 1
    assert lexical_closes == []


def test_reranker_load_failure_closes_client_and_lexical(
    ingested: CountingClient,
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
) -> None:
    broken = CountingReranker(fail=ValueError("corrupt cache"))
    with pytest.raises(ValueError, match="corrupt cache"):
        open_with(
            Strategy.HYBRID,
            Factory(ingested),
            rerank=True,
            reranker_factory=RerankerFactory(broken),
        )
    assert ingested.close_calls == 1
    assert lexical_closes == [1]


def test_build_retriever_failure_closes_client_and_lexical(
    ingested: CountingClient,
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("build failed")

    monkeypatch.setattr(opening, "build_retriever", boom)
    with pytest.raises(RuntimeError, match="build failed"):
        open_with(Strategy.HYBRID, Factory(ingested))
    assert ingested.close_calls == 1
    assert lexical_closes == [1]


def test_dense_strategy_failure_closes_the_client(
    fake_lexical: Path,  # noqa: F811
) -> None:
    empty = CountingClient(QdrantClient(":memory:"))
    with pytest.raises(Exception):  # noqa: B017, PT011
        open_with(Strategy.DENSE, Factory(empty))
    assert empty.close_calls == 1


def test_open_time_fallback_closes_the_failed_client_once(
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
) -> None:
    holder: list[CountingClient] = []

    def factory(settings: object) -> CountingClient:
        client = CountingClient(client_at(closed_port())(settings))
        holder.append(client)
        return client

    opened = open_with(Strategy.HYBRID, factory)
    try:
        assert holder[0].close_calls == 1
        assert opened.client is None and opened.lexical is not None
    finally:
        opened.close()
    assert holder[0].close_calls == 1
    assert lexical_closes == [1]


# --- close() ----------------------------------------------------------------


def test_close_closes_lexical_then_client_and_is_idempotent(
    ingested: CountingClient,
    fake_lexical: Path,  # noqa: F811
    lexical_closes: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    lexical_close = LexicalIndex.close
    client_close = CountingClient.close

    def note_lexical(self: LexicalIndex) -> None:
        order.append("lexical")
        lexical_close(self)

    def note_client(self: CountingClient) -> None:
        order.append("client")
        client_close(self)

    monkeypatch.setattr(LexicalIndex, "close", note_lexical)
    monkeypatch.setattr(CountingClient, "close", note_client)
    opened = open_with(Strategy.HYBRID, Factory(ingested))
    assert opened.client is ingested
    opened.close()
    opened.close()
    assert ingested.close_calls == 1
    assert lexical_closes == [1]
    assert order == ["lexical", "client"]
    assert opened.lexical is None and opened.client is None


# --- top_k against rerank.depth ---------------------------------------------


def test_top_k_above_depth_is_refused_before_any_reranker_or_client(
    ingested: CountingClient,
    fake_lexical: Path,  # noqa: F811
) -> None:
    depth = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml").rerank.depth
    reranker_factory = RerankerFactory()
    factory = Factory(ingested)
    with pytest.raises(RetrievalConfigurationError, match="rerank.depth"):
        open_with(
            Strategy.HYBRID,
            factory,
            rerank=True,
            reranker_factory=reranker_factory,
            top_k=depth + 1,
        )
    assert reranker_factory.calls == 0
    assert reranker_factory.reranker.load_calls == 0
    assert factory.calls == 0


def test_top_k_at_depth_opens_and_top_k_without_rerank_is_not_checked(
    fake_lexical: Path,  # noqa: F811
) -> None:
    """`close()` closes the client, so each open gets its own."""
    depth = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml").rerank.depth
    reranker_factory = RerankerFactory()

    def indexed() -> CountingClient:
        inner = QdrantClient(":memory:")
        ingest(inner)
        return CountingClient(inner)

    at_depth = open_with(
        Strategy.HYBRID,
        Factory(indexed()),
        rerank=True,
        reranker_factory=reranker_factory,
        top_k=depth,
    )
    at_depth.close()
    assert reranker_factory.calls == 1
    without = open_with(Strategy.HYBRID, Factory(indexed()), top_k=depth + 10)
    without.close()


# --- one standalone helper --------------------------------------------------


def test_bm25_and_the_open_time_fallback_share_one_standalone_helper(
    fake_lexical: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    original = opening._open_standalone  # noqa: SLF001

    def spy(**kwargs: Any) -> Any:
        calls.append(1)
        return original(**kwargs)

    monkeypatch.setattr(opening, "_open_standalone", spy)
    bm25 = open_with(Strategy.BM25, None)
    bm25.close()
    fallback = open_with(Strategy.HYBRID, client_at(closed_port()))
    fallback.close()
    assert calls == [1, 1]
