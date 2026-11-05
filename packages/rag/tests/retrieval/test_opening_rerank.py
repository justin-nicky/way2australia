"""Reranking wiring: `open_retrieval` and `make retrieve` (Spec 011 R3, R4, R5)."""

from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.rerank.errors import RerankerUnavailableError, RerankSkipReason
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval import cli
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import (
    RetrievalConfig,
    load_retrieval_config,
)

from .test_cli import Factory, ingest
from .test_fallback import client_at, closed_port
from .test_opening import fake_lexical  # noqa: F401  (fixture)

QUERY = "Is coaching compulsory?"


class RecordingFactory:
    """A reranker factory that records its calls and hands out one fake."""

    def __init__(self, reranker: FakeReranker | None = None) -> None:
        self.reranker = reranker or FakeReranker()
        self.calls = 0

    def __call__(self, config: Any, provider: str | None = None) -> FakeReranker:
        self.calls += 1
        return self.reranker


class MustNotBuild:
    calls = 0

    def __call__(self, *_a: Any, **_k: Any) -> Any:
        type(self).calls += 1
        raise AssertionError("no reranker may be built")


def retrieval_config(*, enabled: bool = False) -> RetrievalConfig:
    config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    rerank = config.rerank.model_copy(update={"enabled": enabled})
    return config.model_copy(update={"rerank": rerank})


def access() -> Any:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def open_with(
    strategy: Strategy,
    client: Any,
    *,
    rerank: bool,
    factory: Any,
    enabled: bool = False,
) -> Any:
    return open_retrieval(
        strategy,
        settings=load_runtime_settings(RetrievalConfigurationError),
        ingestion_config=load_ingestion_config(REPO_ROOT / "config/ingestion.yaml"),
        retrieval_config=retrieval_config(enabled=enabled),
        provider="fake",
        repo_root=REPO_ROOT,
        client_factory=client,
        rerank=rerank,
        reranker_factory=factory,
    )


@pytest.fixture
def memory_client(fake_lexical: Path) -> Factory:  # noqa: F811
    client = QdrantClient(":memory:")
    ingest(client)
    return Factory(client)


def test_committed_config_has_reranking_off() -> None:
    config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    assert config.rerank.enabled is False


@pytest.mark.parametrize("strategy", [Strategy.DENSE, Strategy.BM25])
def test_rerank_with_another_strategy_is_refused_before_anything_opens(
    strategy: Strategy,
) -> None:
    factory = RecordingFactory()
    with pytest.raises(RetrievalConfigurationError, match="hybrid strategy only"):
        open_with(strategy, MustNotBuild(), rerank=True, factory=factory)
    assert factory.calls == 0


@pytest.mark.parametrize(
    ("rerank", "enabled"),
    [(False, False), (False, True)],
    ids=["config-off", "no-rerank"],
)
def test_reranking_off_never_builds_or_loads_a_reranker(
    memory_client: Factory, rerank: bool, enabled: bool
) -> None:
    broken = RecordingFactory(FakeReranker(fail_on_load=True))
    opened = open_with(
        Strategy.HYBRID, memory_client, rerank=rerank, factory=broken, enabled=enabled
    )
    try:
        result = opened.retriever.retrieve(QUERY, access(), 5)
        assert opened.reranker is None and result.rerank is None
        assert result.score_kind == "rrf"
    finally:
        opened.close()
    assert broken.calls == 0 and broken.reranker.load_calls == 0


def test_reranking_on_builds_and_loads_once_and_reranks(
    memory_client: Factory,
) -> None:
    factory = RecordingFactory()
    opened = open_with(Strategy.HYBRID, memory_client, rerank=True, factory=factory)
    try:
        for _ in range(2):
            result = opened.retriever.retrieve(QUERY, access(), 5)
            assert result.rerank is not None and result.rerank.skipped_reason is None
            assert result.score_kind == "cross_encoder"
            assert all(h.fused_rank is not None for h in result.hits)
        assert opened.reranker is factory.reranker
    finally:
        opened.close()
    assert factory.calls == 1 and factory.reranker.load_calls == 1


def test_open_time_load_outage_is_a_sticky_skip_with_the_pre_spec_hits(
    memory_client: Factory,
) -> None:
    factory = RecordingFactory(FakeReranker(fail_on_load=True))
    opened = open_with(Strategy.HYBRID, memory_client, rerank=True, factory=factory)
    plain = open_with(
        Strategy.HYBRID, memory_client, rerank=False, factory=MustNotBuild()
    )
    try:
        expected = plain.retriever.retrieve(QUERY, access(), 5)
        assert expected.rerank is None
        for _ in range(3):
            result = opened.retriever.retrieve(QUERY, access(), 5)
            assert result.hits == expected.hits and result.score_kind == "rrf"
            assert result.rerank is not None
            assert (result.rerank.skipped_reason, result.rerank.stage) == (
                RerankSkipReason.MODEL_UNAVAILABLE.value,
                "open",
            )
    finally:
        opened.close()
        plain.close()
    assert factory.reranker.load_calls == 1  # never retried


def test_offline_not_cached_at_load_is_a_configuration_error_not_a_skip(
    memory_client: Factory,
) -> None:
    class Offline(FakeReranker):
        def load(self) -> None:
            raise RetrievalConfigurationError(
                "weights are not cached; run `make setup-bge-m3`"
            )

    with pytest.raises(RetrievalConfigurationError, match="make setup-bge-m3"):
        open_with(
            Strategy.HYBRID,
            memory_client,
            rerank=True,
            factory=RecordingFactory(Offline()),
        )


def test_other_load_errors_propagate(memory_client: Factory) -> None:
    class Broken(FakeReranker):
        def load(self) -> None:
            raise ValueError("corrupt cache")

    with pytest.raises(ValueError, match="corrupt cache"):
        open_with(
            Strategy.HYBRID,
            memory_client,
            rerank=True,
            factory=RecordingFactory(Broken()),
        )


def test_dense_outage_at_open_serves_bm25_without_loading_the_reranker(
    fake_lexical: Path,  # noqa: F811
) -> None:
    factory = RecordingFactory()
    opened = open_with(
        Strategy.HYBRID, client_at(closed_port()), rerank=True, factory=factory
    )
    try:
        result = opened.retriever.retrieve(QUERY, access(), 5)
        assert result.strategy == "bm25" and result.rerank is None
        assert result.fallback_reason == "qdrant_unavailable"
    finally:
        opened.close()
    assert factory.reranker.load_calls == 0 and factory.reranker.score_calls == 0


# --- CLI ---------------------------------------------------------------------


def run(factory: Factory, *extra: str) -> int:
    return cli.main(
        [QUERY, "--repo-root", str(REPO_ROOT), "--embedder", "fake", *extra],
        client_factory=factory,
    )


def test_cli_prints_rerank_off_by_default(
    memory_client: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(memory_client) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[-1] == "rerank: off"


def test_cli_rerank_line_with_the_fake_reranker(
    memory_client: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    assert run(memory_client, "--rerank", "--reranker", "fake") == 0
    out = capsys.readouterr().out
    assert (
        f"rerank: {config.rerank.model_id}@{(config.rerank.revision or '')[:7]} "
        f"depth {config.rerank.depth}"
    ) in out
    assert "score_kind" not in out and "strategy=hybrid" in out


def test_cli_no_rerank_builds_nothing(
    memory_client: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(FakeReranker, "load", MustNotBuild())
    assert run(memory_client, "--no-rerank", "--reranker", "fake") == 0
    assert "rerank: off" in capsys.readouterr().out


def test_cli_skip_prints_the_line_and_a_stderr_warning(
    memory_client: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing(self: FakeReranker) -> None:
        raise RerankerUnavailableError(RerankSkipReason.MODEL_TIMEOUT)

    monkeypatch.setattr(FakeReranker, "load", failing)
    assert run(memory_client, "--rerank", "--reranker", "fake") == 0
    captured = capsys.readouterr()
    assert "rerank: skipped (model_timeout, open)" in captured.out
    assert "WARNING reranking skipped: model_timeout (open)" in captured.err


@pytest.mark.parametrize("strategy", ["dense", "bm25"])
def test_cli_rerank_with_dense_or_bm25_exits_2(
    memory_client: Factory,
    capsys: pytest.CaptureFixture[str],
    strategy: str,
) -> None:
    assert (
        run(memory_client, "--strategy", strategy, "--rerank", "--reranker", "fake")
        == 2
    )
    assert "hybrid strategy only" in capsys.readouterr().err


def test_cli_top_k_above_depth_exits_2(
    memory_client: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    depth = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml").rerank.depth
    code = run(
        memory_client, "--rerank", "--reranker", "fake", "--top-k", str(depth + 1)
    )
    assert code == 2
    assert "rerank.depth" in capsys.readouterr().err


def test_cli_rerank_and_no_rerank_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit) as caught:
        cli.main([QUERY, "--rerank", "--no-rerank"])
    assert caught.value.code == 2
