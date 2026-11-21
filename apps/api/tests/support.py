"""Helpers for the serving tests: a fake-identity lexical file built from the real
corpus, an in-memory Qdrant client holding the fake-embedder index, and counters.

No test calls a real model or API (Spec 013 testing strategy)."""

import dataclasses
import socket
from collections.abc import Callable
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from way2australia_api.config import Settings
from way2australia_rag.generation.fake import FakeGenerator
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.serving.readiness import Readiness
from way2australia_rag.serving.stack import (
    ServingInputs,
    StackHolder,
    open_serving_stack,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

SENTINEL_KEY = "sk-sentinel-secret-key"
SENTINEL_URL = "http://sentinel-qdrant.invalid:6333"


class CountingClient:
    """Delegates to a real in-memory client and counts `close` calls."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class ClientFactory:
    def __init__(self, client: Any) -> None:
        self.client = client

    def __call__(self, _settings: object) -> Any:
        return self.client


def indexed_client() -> CountingClient:
    inner = QdrantClient(":memory:")
    argv = ["--repo-root", str(REPO_ROOT), "--embedder", "fake"]
    code = ingestion_cli.main(argv, client_factory=lambda _s: inner)
    assert code == 0
    return CountingClient(inner)


def down_client() -> Any:
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return QdrantClient(
        url=f"http://127.0.0.1:{port}", timeout=1, check_compatibility=False
    )


class CountingGenerator(FakeGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.closed = 0

    def close(self) -> None:
        self.closed += 1


class CountingEmbedder(FakeEmbedder):
    closed = 0

    def close(self) -> None:
        self.closed += 1


class CountingReranker(FakeReranker):
    closed = 0

    def close(self) -> None:
        self.closed += 1


def fake_settings(**overrides: Any) -> Settings:
    return Settings(repo_root=REPO_ROOT, api_fake=True, **overrides)


def stack_factory(
    client: Any,
    *,
    gate: Any = None,
    reranker: FakeReranker | None = None,
    embedder: Callable[..., Any] | None = None,
) -> Callable[[ServingInputs, Readiness], StackHolder]:
    """A phase 2 factory: waits on `gate`, then opens the real stack over the
    in-memory client with fake models."""

    def factory(inputs: ServingInputs, readiness: Readiness) -> StackHolder:
        if gate is not None:
            gate.wait(10)
        changes: dict[str, Any] = {"client_factory": ClientFactory(client)}
        if reranker is not None:
            changes["reranker_factory"] = lambda _c, _p=None: reranker
        if embedder is not None:
            changes["embedder_factory"] = embedder
        return open_serving_stack(dataclasses.replace(inputs, **changes), readiness)

    return factory
