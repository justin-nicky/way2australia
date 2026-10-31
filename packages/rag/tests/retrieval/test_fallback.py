"""The hybrid fallback policy (Spec 008 R6, R7, R2, R11)."""

import socket
import subprocess
import threading
from collections.abc import Iterator
from pathlib import Path
from time import perf_counter
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.config import (
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.retrieval import cli as retrieve_cli
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.strategy import (
    QdrantTimeouts,
    load_retrieval_config,
)

from .test_hybrid import stub_result
from .test_opening import fake_lexical  # noqa: F401  (fixture)


def access() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


class Primary:
    """A primary that raises the queued errors, then returns a hybrid result."""

    strategy = Strategy.HYBRID

    def __init__(self, *errors: Exception | None) -> None:
        self.errors = list(errors)
        self.calls = 0
        self.seen: list[tuple[ResolvedAccess, int]] = []

    def retrieve(
        self, query_text: str, access: ResolvedAccess, top_k: int = 5
    ) -> RetrievalResult:
        self.calls += 1
        self.seen.append((access, top_k))
        error = self.errors.pop(0) if self.errors else None
        if error is not None:
            raise error
        return stub_result(["a"]).model_copy(
            update={"strategy": "hybrid", "score_kind": "rrf"}
        )


class Fallback:
    strategy = Strategy.BM25

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.seen: list[tuple[ResolvedAccess, int]] = []

    def retrieve(
        self, query_text: str, access: ResolvedAccess, top_k: int = 5
    ) -> RetrievalResult:
        self.seen.append((access, top_k))
        if self.error is not None:
            raise self.error
        return stub_result(["b"]).model_copy(
            update={
                "strategy": "bm25",
                "score_kind": "bm25",
                "requested_strategy": "bm25",
            }
        )


def unavailable(reason: FallbackReason) -> RetrievalUnavailableError:
    return RetrievalUnavailableError(reason)


def test_primary_success_is_marked_hybrid_without_a_reason() -> None:
    result = FallbackRetriever(Primary(), Fallback(), None).retrieve("q", access(), 3)
    assert result.strategy == "hybrid"
    assert result.requested_strategy == "hybrid"
    assert result.fallback_reason is None


def test_dense_leg_failure_on_one_query_leaves_the_others_hybrid() -> None:
    primary = Primary(None, unavailable(FallbackReason.QDRANT_TIMEOUT), None)
    retriever = FallbackRetriever(primary, Fallback(), None)
    results = [retriever.retrieve("q", access(), 3) for _ in range(3)]
    assert [r.strategy for r in results] == ["hybrid", "bm25", "hybrid"]
    assert results[1].fallback_reason == "qdrant_timeout"
    assert results[1].requested_strategy == "hybrid"
    assert results[0].fallback_reason is None and results[2].fallback_reason is None
    assert primary.calls == 3  # the primary is retried on every query


@pytest.mark.parametrize("reason", list(FallbackReason))
def test_every_reason_falls_back_with_the_same_access_and_top_k(
    reason: FallbackReason,
) -> None:
    a = access()
    primary, fallback = Primary(unavailable(reason)), Fallback()
    result = FallbackRetriever(primary, fallback, None).retrieve("q", a, 4)
    assert result.fallback_reason == reason.value
    assert fallback.seen[0][0] is a and fallback.seen[0][1] == 4
    assert primary.seen[0][0] is a and primary.seen[0][1] == 4


def test_latency_includes_the_failed_attempt() -> None:
    result = FallbackRetriever(
        Primary(unavailable(FallbackReason.QDRANT_UNAVAILABLE)), Fallback(), None
    ).retrieve("q", access(), 3)
    legs = result.leg_latency_ms
    assert legs is not None and set(legs) == {"dense_attempt", "bm25"}
    assert result.latency_ms == pytest.approx(legs["dense_attempt"] + legs["bm25"])


@pytest.mark.parametrize(
    "error",
    [
        RetrievalConfigurationError("a missing revision"),
        OSError("not a valid model identifier"),
        ValueError("a non-eligible dense error"),
        RetrievalAuthorizationError("forbidden", document_id="d"),
    ],
    ids=["config", "model-id", "other", "authorization-dense"],
)
def test_non_eligible_primary_errors_are_raised(error: Exception) -> None:
    fallback = Fallback()
    with pytest.raises(type(error)):
        FallbackRetriever(Primary(error), fallback, None).retrieve("q", access(), 3)
    assert fallback.seen == []


@pytest.mark.parametrize(
    "error",
    [
        RetrievalAuthorizationError("forbidden", document_id="d"),
        RuntimeError("sqlite failed"),
    ],
    ids=["authorization-bm25", "bm25-error"],
)
def test_a_fallback_error_is_raised(error: Exception) -> None:
    with pytest.raises(type(error)):
        FallbackRetriever(
            Primary(unavailable(FallbackReason.QDRANT_UNAVAILABLE)),
            Fallback(error),
            None,
        ).retrieve("q", access(), 3)


def test_open_reason_serves_bm25_without_a_primary() -> None:
    result = FallbackRetriever(
        None, Fallback(), FallbackReason.MODEL_UNAVAILABLE
    ).retrieve("q", access(), 3)
    assert result.strategy == "bm25"
    assert result.fallback_reason == "model_unavailable"


def test_a_model_load_failure_with_a_network_cause_falls_back() -> None:
    from way2australia_rag.ingestion.embedding import FakeEmbedder
    from way2australia_rag.retrieval.retriever import DenseRetriever

    class Offline(FakeEmbedder):
        def embed_query(self, text: str) -> list[float]:
            error = OSError("We couldn't connect")
            error.__cause__ = ConnectionError("down")
            raise error

    class Index:  # never reached
        settings: Any = None

    retriever = FallbackRetriever(
        DenseRetriever(Index(), Offline()),  # type: ignore[arg-type]
        Fallback(),
        None,
    )
    assert retriever.retrieve("q", access(), 3).fallback_reason == "model_unavailable"


def test_fusion_and_hybrid_are_unchanged() -> None:
    done = subprocess.run(  # noqa: S603
        [
            "git",
            "diff",
            "--stat",
            "HEAD",
            "--",
            "packages/rag/src/way2australia_rag/retrieval/fusion.py",
            "packages/rag/src/way2australia_rag/retrieval/hybrid.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0 and done.stdout.strip() == ""


# --- open_retrieval and the CLI -------------------------------------------------


def closed_port() -> int:
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


@pytest.fixture
def stalled_port() -> Iterator[int]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(8)
    accepted: list[socket.socket] = []
    stop = threading.Event()

    def accept_forever() -> None:
        server.settimeout(0.2)
        while not stop.is_set():
            try:
                accepted.append(server.accept()[0])
            except OSError:
                continue

    thread = threading.Thread(target=accept_forever, daemon=True)
    thread.start()
    yield server.getsockname()[1]
    stop.set()
    thread.join(timeout=2)
    for connection in accepted:
        connection.close()
    server.close()


def client_at(port: int, timeout: int = 1) -> Any:
    def factory(_settings: object) -> QdrantClient:
        return QdrantClient(
            url=f"http://127.0.0.1:{port}", timeout=timeout, check_compatibility=False
        )

    return factory


def open_hybrid(
    strategy: Strategy, factory: Any, timeouts: QdrantTimeouts | None = None
) -> Any:
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    settings = load_runtime_settings(RetrievalConfigurationError)
    retrieval = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
    if timeouts is not None:
        retrieval = retrieval.model_copy(update={"qdrant": timeouts})
    return open_retrieval(
        strategy,
        settings=settings,
        ingestion_config=config,
        retrieval_config=retrieval,
        provider="fake",
        repo_root=REPO_ROOT,
        client_factory=factory,
    )


def test_closed_port_hybrid_serves_bm25_with_qdrant_unavailable(
    fake_lexical: Path,  # noqa: F811
) -> None:
    opened = open_hybrid(Strategy.HYBRID, client_at(closed_port()))
    try:
        result = opened.retriever.retrieve("Is coaching compulsory?", access(), 5)
        assert result.strategy == "bm25" and result.hits
        assert result.requested_strategy == "hybrid"
        assert result.fallback_reason == "qdrant_unavailable"
        assert opened.index_settings is None
        assert opened.document_count(access()) > 0
        bm25 = open_hybrid(Strategy.BM25, client_at(closed_port()))
        try:
            plain = bm25.retriever.retrieve("Is coaching compulsory?", access(), 5)
        finally:
            bm25.close()
        assert [h.point_id for h in result.hits] == [h.point_id for h in plain.hits]
    finally:
        opened.close()


def test_closed_port_dense_is_unavailable(fake_lexical: Path) -> None:  # noqa: F811
    with pytest.raises(RetrievalUnavailableError) as caught:
        open_hybrid(Strategy.DENSE, client_at(closed_port()))
    assert caught.value.reason is FallbackReason.QDRANT_UNAVAILABLE


def test_stalled_qdrant_through_open_retrieval_serves_bm25_within_the_bound(
    fake_lexical: Path,  # noqa: F811
    stalled_port: int,
) -> None:
    """Open-time stall: the connect and query timeouts (1 s) plus at most 2 s."""
    started = perf_counter()
    opened = open_hybrid(
        Strategy.HYBRID,
        client_at(stalled_port, 1),
        QdrantTimeouts(connect_timeout_s=1, query_timeout_s=1),
    )
    try:
        result = opened.retriever.retrieve("Is coaching compulsory?", access(), 5)
        assert result.strategy == "bm25"
        assert result.fallback_reason == "qdrant_timeout"
        assert perf_counter() - started < 1 + 2
    finally:
        opened.close()


def test_a_missing_extra_at_open_is_raised_not_a_fallback(
    fake_lexical: Path,  # noqa: F811
) -> None:
    def no_extra(*_a: Any, **_k: Any) -> Any:
        raise RetrievalConfigurationError("the bge-m3 extra is missing")

    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    with pytest.raises(RetrievalConfigurationError):
        open_retrieval(
            Strategy.HYBRID,
            settings=load_runtime_settings(RetrievalConfigurationError),
            ingestion_config=config,
            retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
            provider="fake",
            repo_root=REPO_ROOT,
            client_factory=client_at(closed_port()),
            embedder_factory=no_extra,
        )


def run_cli(*extra: str, port: int) -> int:
    return retrieve_cli.main(
        [
            "Is coaching compulsory?",
            "--repo-root",
            str(REPO_ROOT),
            "--embedder",
            "fake",
            *extra,
        ],
        client_factory=client_at(port),
    )


def test_cli_hybrid_with_qdrant_down_prints_the_fallback_header(
    fake_lexical: Path,  # noqa: F811
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run_cli("--strategy", "hybrid", port=closed_port()) == 0
    out = capsys.readouterr()
    assert out.out.splitlines()[0] == (
        "strategy: bm25 (requested: hybrid; fallback: qdrant_unavailable)"
    )
    assert "WARNING retrieval fell back to bm25: qdrant_unavailable" in out.err
    assert "127.0.0.1" not in out.out + out.err


def test_cli_explicit_dense_with_qdrant_down_exits_2(
    fake_lexical: Path,  # noqa: F811
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run_cli("--strategy", "dense", port=closed_port()) == 2
    err = capsys.readouterr().err
    assert "ERROR RetrievalUnavailableError" in err and "qdrant_unavailable" in err
    assert "127.0.0.1" not in err
