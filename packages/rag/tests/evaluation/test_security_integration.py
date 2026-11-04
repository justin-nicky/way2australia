"""Authorization isolation on Docker Qdrant (Spec 006 R9; closes Spec 005 retro F3).

Builds the throwaway security index on the real Qdrant server under a unique
`w2a-sectest-*` base, asserts no forbidden point is returned, and removes its own
collection and `-settings` in `finally`. Skipped when Qdrant is unreachable.
Never touches other collections.
"""

import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from conftest import LIVE_SUITE, REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.evaluation.security_eval import (
    PATHS,
    run_security_evaluation,
    security_gate_chunkers,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    build_security_index,
    delete_security_index,
)
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.strategy import load_retrieval_config

QDRANT_URL = "http://localhost:6333"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_client() -> Iterator[QdrantClient]:
    client = QdrantClient(url=QDRANT_URL, timeout=30)
    try:
        client.get_collections()
    except Exception as error:  # any connection failure means "not reachable"
        client.close()
        pytest.skip(
            f"Qdrant is not reachable at {QDRANT_URL} "
            f"({type(error).__name__}); run `docker compose up -d qdrant`"
        )
    yield client
    client.close()


@pytest.mark.parametrize("path", PATHS)
def test_server_filter_keeps_every_forbidden_point_out(
    path: str,
    live_client: QdrantClient,
    security_repository: LocalDocumentRepository,
    tmp_path: Path,
) -> None:
    """Spec 007 R12 and Spec 008 R10: every gated path on the real server, one
    path per run (`hybrid_fallback_query` included: a live Qdrant with an
    unavailable dense leg); the lexical file lives in `tmp_path`."""
    suite = load_suite(REPO_ROOT, LIVE_SUITE)
    queries, deferred = select_security_queries(suite)
    base = f"w2a-sectest-{uuid.uuid4().hex[:8]}"
    index = None
    try:
        index = build_security_index(
            live_client,
            base,
            [q.text for q in queries],
            FakeEmbedder(FAKE_VECTOR_SIZE),
            HeadingChunker(),
            seed_repository=LocalDocumentRepository(LocalRepositoryConfig(REPO_ROOT)),
            security_repository=security_repository,
            tenant_id="way2australia",
            lexical_dir=tmp_path / "lexical",
        )
        access = resolve_access(
            AccessContext(role=Role.GUEST, tenant_id="way2australia")
        )
        config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
        report = run_security_evaluation(
            index, access, queries, deferred, config, [path]
        )
        assert report.paths == (path,)
        assert report.violations == []
        assert report.query_count == len(queries)
        assert index.lexical_rows_per_variant == index.points_per_variant
    finally:
        names = [f"{base}-sec-v1", f"{base}-sec-v1-settings"]
        if index is not None:
            delete_security_index(index)
        for name in names:  # belt and braces if the build failed half way
            if live_client.collection_exists(name):
                live_client.delete_collection(name)


def test_recursive_v1_full_gate_on_docker(
    live_client: QdrantClient,
    security_repository: LocalDocumentRepository,
    tmp_path: Path,
) -> None:
    """Spec 009 R9: the recursive chunker gate on the real Qdrant server."""
    suite = load_suite(REPO_ROOT, LIVE_SUITE)
    queries, deferred = select_security_queries(suite)
    base = f"w2a-sectest-{uuid.uuid4().hex[:8]}"
    chunker = next(c for c in security_gate_chunkers() if c.name == "recursive")
    index = None
    try:
        index = build_security_index(
            live_client,
            base,
            [q.text for q in queries],
            FakeEmbedder(FAKE_VECTOR_SIZE),
            chunker,
            seed_repository=LocalDocumentRepository(LocalRepositoryConfig(REPO_ROOT)),
            security_repository=security_repository,
            tenant_id="way2australia",
            lexical_dir=tmp_path / "lexical-rec",
        )
        access = resolve_access(
            AccessContext(role=Role.GUEST, tenant_id="way2australia")
        )
        config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")
        report = run_security_evaluation(index, access, queries, deferred, config)
        assert report.passed
        assert report.violations == []
        assert index.chunker.name == "recursive"
    finally:
        names = [f"{base}-sec-v1", f"{base}-sec-v1-settings"]
        if index is not None:
            delete_security_index(index)
        for name in names:
            if live_client.collection_exists(name):
                live_client.delete_collection(name)
