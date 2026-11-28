"""Readiness model and model locks (Spec 013 R7, R8)."""

import threading
from collections.abc import Sequence

import pytest
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.rerank.base import RerankScores
from way2australia_rag.rerank.errors import RerankerUnavailableError, RerankSkipReason
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.breaker import CircuitBreaker
from way2australia_rag.retrieval.errors import FallbackReason
from way2australia_rag.serving.locks import LockedEmbedder, LockedReranker
from way2australia_rag.serving.readiness import Readiness


def test_starting_and_failed_are_503_with_no_detail() -> None:
    readiness = Readiness(fake=True)
    snap = readiness.snapshot()
    assert (snap.http_status, snap.to_body()) == (
        503,
        {"status": "starting", "fake": True},
    )
    readiness.set_failed()
    snap = readiness.snapshot()
    assert (snap.http_status, snap.to_body()["status"]) == (503, "failed")


def test_ready_ok_has_no_reasons() -> None:
    readiness = Readiness()
    readiness.set_ready()
    snap = readiness.snapshot()
    assert snap.http_status == 200
    assert snap.to_body() == {
        "status": "ok",
        "degraded_reasons": [],
        "breaker": "closed",
        "fake": False,
    }


def test_each_degraded_reason_and_the_breaker_states() -> None:
    now = [0.0]
    breaker = CircuitBreaker(
        1, 10, lambda: now[0], open_reason=FallbackReason.QDRANT_UNAVAILABLE
    )
    readiness = Readiness()
    readiness.set_ready()
    readiness.set_breaker_provider(lambda: breaker)
    assert readiness.snapshot().degraded_reasons == ("dense_circuit_open",)
    now[0] = 11.0
    breaker.admit()  # the probe: half-open
    assert readiness.snapshot().degraded_reasons == ("dense_circuit_half_open",)
    assert readiness.snapshot().breaker == "half_open"
    readiness.set_rerank_skipped(True)
    readiness.set_reopen_refused(True)
    readiness.set_abandoned_provider(lambda: 2)
    snap = readiness.snapshot()
    assert snap.status == "degraded"
    assert snap.degraded_reasons == (
        "dense_circuit_half_open",
        "rerank_skipped",
        "dense_reopen_refused",
        "abandoned_generation",
    )
    assert snap.to_body()["abandoned_in_flight"] == 2
    readiness.set_reopen_refused(False)
    assert "dense_reopen_refused" not in readiness.snapshot().degraded_reasons


class GatedEmbedder(FakeEmbedder):
    def __init__(self) -> None:
        super().__init__(8)
        self.inside = threading.Event()
        self.release = threading.Event()

    def embed_query(self, text: str) -> list[float]:
        self.inside.set()
        assert self.release.wait(5)
        return super().embed_query(text)


class RecordingReranker(FakeReranker):
    def __init__(self) -> None:
        super().__init__()
        self.scored = threading.Event()

    def score(self, query: str, texts: Sequence[str]) -> RerankScores:
        result = super().score(query, texts)
        self.scored.set()
        return result


def test_embedder_and_reranker_locks_are_separate() -> None:
    embedder = GatedEmbedder()
    reranker = RecordingReranker()
    locked_e = LockedEmbedder(embedder)
    locked_r = LockedReranker(reranker)
    thread = threading.Thread(target=locked_e.embed_query, args=("a",))
    thread.start()
    try:
        assert embedder.inside.wait(5)
        # Request A is inside the embedder; request B reranks meanwhile.
        locked_r.score("q", ["x", "y"])
        assert reranker.scored.is_set()
        # A second embed is serialized behind A.
        second = threading.Thread(target=locked_e.embed_query, args=("b",))
        second.start()
        second.join(0.2)
        assert second.is_alive()
    finally:
        embedder.release.set()
        thread.join(5)
        second.join(5)
    assert not thread.is_alive() and not second.is_alive()


def test_locks_pass_identity_through() -> None:
    embedder = FakeEmbedder(8)
    reranker = FakeReranker()
    assert LockedEmbedder(embedder).info is embedder.info
    assert LockedEmbedder(embedder).device == embedder.device
    assert LockedReranker(reranker).info is reranker.info
    assert LockedReranker(reranker).device == reranker.device


def test_eligible_reranker_load_failure_is_sticky_and_asked_once() -> None:
    inner = FakeReranker(fail_on_load=True)
    locked = LockedReranker(inner)
    for _ in range(3):
        with pytest.raises(RerankerUnavailableError) as raised:
            locked.load()
        assert raised.value.reason is RerankSkipReason.MODEL_UNAVAILABLE
    assert inner.load_calls == 1
    assert locked.load_failed


def test_non_eligible_reranker_load_failure_is_not_sticky() -> None:
    class Broken(FakeReranker):
        def load(self) -> None:
            self.load_calls += 1
            raise ValueError("config")

    inner = Broken()
    locked = LockedReranker(inner)
    for _ in range(2):
        with pytest.raises(ValueError):
            locked.load()
    assert inner.load_calls == 2
    assert not locked.load_failed
