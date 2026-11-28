"""Route-level authorization over the security corpus (Spec 013 R14).

The stack is the production serving open, pointed at a throwaway index from
`build_security_repository` and `build_security_index` (in-memory Qdrant,
temporary lexical file, fake embedder). No test calls a real model or API.
"""

import json
import logging
import time
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient
from way2australia_api.main import create_app
from way2australia_rag.evaluation.security_corpus import (
    SCHEMA,
    build_security_repository,
)
from way2australia_rag.evaluation.security_index import (
    SECURITY_INDEX_VERSION,
    SecurityIndex,
    build_security_index,
    delete_security_index,
    is_forbidden_document,
)
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import load_runtime_settings
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.breaker import Admission, BreakerState
from way2australia_rag.retrieval.errors import FallbackReason
from way2australia_rag.serving.readiness import Readiness
from way2australia_rag.serving.stack import (
    ServingInputs,
    StackHolder,
    open_serving_stack,
)

from .support import REPO_ROOT, fake_settings

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

# These strings are the dense and lexical probes: the builder plants a forbidden
# point (staff scope, other tenant, injection, and the other variants) as a
# nearest neighbour of each one.
QUERIES = (
    "staff scope fixture nearest neighbour",
    "other tenant injection fixture",
)
ACCESS_BODIES = (
    {"query": QUERIES[0], "role": "staff"},
    {"query": QUERIES[0], "tenant_id": "other-tenant"},
    {"query": QUERIES[0], "scope": "staff"},
)
LOGGER = "way2australia_api.answer"


class _SharedClient:
    """Forwards to the security index client and ignores `close`.

    The serving stack closes whatever client it opened. The test still owns
    the in-memory client and deletes the throwaway collection at the end.
    """

    def __init__(self, inner: QdrantClient) -> None:
        self._inner = inner

    def close(self) -> None:
        return None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def _forbidden_is_nearest(index: SecurityIndex, query: str) -> None:
    """The route test would pass vacuously if the corpus had no forbidden hit."""
    points = index.client.query_points(
        index.collection,
        query=index.embedder.embed_query(query),
        using="dense",
        limit=5,
        with_payload=True,
    ).points
    assert points
    best = points[0].score
    winners = [
        point
        for point in points
        if point.score is not None and point.score >= best - 1e-9
    ]
    assert any(
        is_forbidden_document(str((point.payload or {})["document_id"]))
        for point in winners
    )


def _stack_factory(
    index: SecurityIndex, *, rerank: bool, errors: list[str]
) -> Callable[[ServingInputs, Readiness], StackHolder]:
    """Phase 2 open against the throwaway index.

    Phase 1 has already checked the ordinary fake lexical file. This factory
    retargets collection, index version and tokenizer at the security build.
    The security file is `lexical-v1` (the builder's default) and `sec-v1`.
    """

    def factory(inputs: ServingInputs, readiness: Readiness) -> StackHolder:
        retrieval = inputs.retrieval_config.model_copy(
            update={
                "lexical": inputs.retrieval_config.lexical.model_copy(
                    update={"tokenizer": "lexical-v1"}
                ),
                "rerank": inputs.retrieval_config.rerank.model_copy(
                    update={"enabled": rerank}
                ),
            }
        )
        ingestion = inputs.ingestion_config.model_copy(
            update={"index_version": SECURITY_INDEX_VERSION}
        )
        runtime = inputs.settings.model_copy(
            update={
                "collection_base": index.collection_base,
                "lexical_index_dir": index.lexical_path.parent,
            }
        )
        try:
            return open_serving_stack(
                ServingInputs(
                    **{
                        **inputs.__dict__,
                        "settings": runtime,
                        "ingestion_config": ingestion,
                        "retrieval_config": retrieval,
                        "client_factory": lambda _settings: _SharedClient(index.client),
                    }
                ),
                readiness,
            )
        except Exception as error:
            errors.append(f"{type(error).__name__}: {error}")
            raise

    return factory


def _wait_ready(client: TestClient, errors: list[str]) -> None:
    deadline = time.monotonic() + 20
    last = ""
    while time.monotonic() < deadline:
        response = client.get("/ready")
        if response.status_code == 200:
            return
        last = response.text
        time.sleep(0.05)
    detail = "; ".join(errors) if errors else last
    raise AssertionError(f"server did not become ready: {detail}")


def _clients(
    index: SecurityIndex, *, rerank: bool
) -> Iterator[tuple[TestClient, list[str]]]:
    errors: list[str] = []
    app = create_app(
        fake_settings(),
        stack_factory=_stack_factory(index, rerank=rerank, errors=errors),
        on_fatal=lambda: None,
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        _wait_ready(client, errors)
        yield client, errors


def _document_ids(payload: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for key in ("citations", "evidence"):
        for item in payload[key]:
            found.append(str(item["document_id"]))
    return found


def _answer_logs(caplog: pytest.LogCaptureFixture) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in caplog.records:
        if record.name != LOGGER:
            continue
        try:
            row = json.loads(record.getMessage())
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("event") == "answer":
            rows.append(row)
    return rows


def _trip_breaker(client: TestClient) -> None:
    """Open the breaker without an open-time BM25 start.

    An open-time fallback runs `verify_fresh`, which refuses this lexical file:
    the synthetic forbidden rows are not repository documents. Tripping the
    breaker on the already-open hybrid stack serves those same rows through
    the BM25 SQL filter.
    """
    holder = client.app.state.loader.holder  # type: ignore[attr-defined]
    breaker = holder.breaker
    assert breaker is not None
    threshold = client.app.state.serving_config.breaker.failure_threshold  # type: ignore[attr-defined]
    for _ in range(threshold):
        breaker.record_failure(Admission.DENSE, FallbackReason.QDRANT_UNAVAILABLE)
    assert breaker.state is BreakerState.OPEN


def _assert_clean(response: Any, query: str) -> None:
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["contract_version"] == "1.0"
    leaked = [
        document_id
        for document_id in _document_ids(payload)
        if is_forbidden_document(document_id)
    ]
    assert leaked == [], f"{query!r} returned forbidden documents {leaked}"


def test_route_hides_forbidden_documents_on_every_serving_path(
    fake_lexical: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    assert fake_lexical.is_dir()
    caplog.set_level(logging.INFO, logger=LOGGER)
    tenant = load_runtime_settings().tenant_id
    lote_codes = active_lote_codes(REPO_ROOT)
    assert lote_codes
    client = QdrantClient(":memory:")
    index = build_security_index(
        client,
        f"w2a-sectest-{uuid.uuid4().hex[:8]}",
        QUERIES,
        FakeEmbedder(),
        HeadingChunker(2000),
        seed_repository=LocalDocumentRepository(
            LocalRepositoryConfig(repo_root=REPO_ROOT)
        ),
        security_repository=build_security_repository(
            REPO_ROOT / "tests/fixtures/security",
            tmp_path / "fixtures",
            schema_source=REPO_ROOT / SCHEMA,
        ),
        tenant_id=tenant,
        lexical_dir=tmp_path / "lexical",
        active_lote_code=lote_codes[0],
    )
    try:
        for variant in ("staff_scope", "other_tenant", "injection"):
            assert index.points_per_variant[variant] == len(QUERIES)
        for query in QUERIES:
            _forbidden_is_nearest(index, query)
        # The server opens its own read-only connection.
        index.lexical.close()

        bodies = [
            {"query": QUERIES[0]},
            {"query": QUERIES[1], "lote": lote_codes[0]},
        ]
        # (rerank, trip breaker, expected log fields)
        hybrid = {"served_strategy": "hybrid", "fallback_reason": None, "rerank": "off"}
        bm25 = {
            "served_strategy": "bm25",
            "fallback_reason": "qdrant_unavailable",
            "rerank": "off",
        }
        reranked = {
            "served_strategy": "hybrid",
            "fallback_reason": None,
            "rerank": "applied",
        }
        paths: tuple[tuple[bool, bool, dict[str, Any]], ...] = (
            (False, False, hybrid),
            (False, True, bm25),
            (True, False, reranked),
        )
        for rerank, trip, expect in paths:
            caplog.clear()
            for http, _errors in _clients(index, rerank=rerank):
                if trip:
                    _trip_breaker(http)
                for body in bodies:
                    response = http.post("/v1/answer", json=body)
                    _assert_clean(response, str(body["query"]))
                for body in ACCESS_BODIES:
                    refused = http.post("/v1/answer", json=body)
                    assert refused.status_code == 422, refused.text
                    assert refused.json()["error"] == "invalid_request"
                    assert "citations" not in refused.json()
                logs = _answer_logs(caplog)
                assert len(logs) == len(bodies)
                for row in logs:
                    for key, value in expect.items():
                        assert row[key] == value, row
    finally:
        delete_security_index(index)
        client.close()
