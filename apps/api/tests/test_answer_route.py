"""Answer route, public contract, limits, errors and logging (Spec 013 R9-R13, R16).

Every test uses fakes: a fake-identity lexical file, an in-memory Qdrant client,
fake models. No test calls a real model or API."""

import json
import logging
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal

import pytest
import yaml
from fastapi.testclient import TestClient
from way2australia_api import contract as contract_module
from way2australia_api import lifespan
from way2australia_api.config import Settings
from way2australia_api.contract import (
    AnswerContract,
    PublicCitation,
    PublicEvidence,
    PublicReason,
    PublicStatus,
    to_contract,
)
from way2australia_api.lifespan import StartupError
from way2australia_api.main import create_app
from way2australia_api.slots import SlotPool
from way2australia_rag.generation.fake import FakeGenerator, FakeMode
from way2australia_rag.generation.models import (
    AnswerIdentity,
    AnswerReason,
    AnswerResponse,
    AnswerStatus,
    Citation,
    ContextStats,
    EvidenceSource,
    PromptIdentity,
)
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.retrieval.errors import (
    LanguageApplicabilityError,
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)
from way2australia_rag.serving.stack import ServingNotReadyError, StackHolder

from .support import (
    REPO_ROOT,
    SENTINEL_KEY,
    SENTINEL_URL,
    CountingGenerator,
    fake_settings,
    indexed_client,
    stack_factory,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

QUERY = "How many credits do I need for the CCL test?"
SENTINEL_QUERY = "zq-sentinel-query-text-7731 about the test"
SENTINEL_EXC = "sentinel-client-exception-message-9921"


class BlockingGenerator(FakeGenerator):
    """Blocks on an event once `block` is set; a short wall-clock cap applies."""

    def __init__(self) -> None:
        super().__init__()
        self.block = False
        self.release = threading.Event()

    @property
    def deadline_s(self) -> float:  # type: ignore[override]
        return 0.5

    def generate(self, prompt: Any, *, deadline_s: float | None = None) -> Any:
        if self.block:
            self.release.wait(30)
        return super().generate(prompt, deadline_s=deadline_s)


class RaisingGenerator(FakeGenerator):
    def generate(self, prompt: Any, *, deadline_s: float | None = None) -> Any:
        raise RuntimeError(SENTINEL_EXC)


def write_serving(tmp_path: Path, **sections: dict[str, Any]) -> Path:
    data = yaml.safe_load((REPO_ROOT / "config/serving.yaml").read_text("utf-8"))
    for name, values in sections.items():
        data[name].update(values)
    path = tmp_path / "serving.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def wait_for(predicate: Any, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        assert time.monotonic() < deadline, "timed out"
        time.sleep(0.02)


@pytest.fixture
def open_client(
    fake_lexical: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[Any]:
    """`open_client(generator=..., serving=...)` -> a ready TestClient."""
    clients: list[TestClient] = []

    def make(
        generator: FakeGenerator | None = None,
        serving: dict[str, dict[str, Any]] | None = None,
        api_fake: bool = True,
    ) -> TestClient:
        gen = generator or CountingGenerator()
        monkeypatch.setattr(
            "way2australia_api.lifespan.build_generator", lambda *_a, **_k: gen
        )
        extra: dict[str, Any] = {}
        if serving:
            extra["serving_config"] = write_serving(tmp_path, **serving)
        app = create_app(
            fake_settings(**extra),
            stack_factory=stack_factory(indexed_client()),
        )
        client = TestClient(app, raise_server_exceptions=False)
        client.__enter__()
        clients.append(client)
        wait_for(lambda: client.get("/ready").status_code == 200)
        return client

    yield make
    for client in clients:
        client.__exit__(None, None, None)


def post(client: TestClient, body: Any, **kwargs: Any) -> Any:
    return client.post("/v1/answer", json=body, **kwargs)


# --- contract pin -------------------------------------------------------------------


def test_contract_pin() -> None:
    def shape(model: Any) -> dict[str, Any]:
        return {n: f.annotation for n, f in model.model_fields.items()}

    assert list(AnswerContract.model_fields) == [
        "contract_version",
        "request_id",
        "status",
        "reason",
        "answer",
        "citations",
        "evidence",
        "message",
        "message_language",
    ]
    assert shape(AnswerContract) == {
        "contract_version": Literal["1.0"],
        "request_id": str,
        "status": PublicStatus,
        "reason": PublicReason | None,
        "answer": str | None,
        "citations": list[PublicCitation],
        "evidence": list[PublicEvidence],
        "message": str | None,
        "message_language": str | None,
    }
    citation: dict[str, Any] = {
        "source_id": str,
        "document_id": str,
        "document_version": int,
        "section_id": str,
        "title": str,
        "source_authority": str,
        "source_url": str | None,
    }
    assert shape(PublicCitation) == citation
    assert shape(PublicEvidence) == {**citation, "snippet": str}
    assert {m.value for m in PublicStatus} == {
        "answered",
        "insufficient_evidence",
        "evidence_only",
    }
    assert {m.value for m in PublicReason} == {
        "no_evidence",
        "not_answerable",
        "generator_unavailable",
    }
    assert AnswerContract.model_fields["contract_version"].default == "1.0"


def test_every_internal_member_has_a_public_mapping() -> None:
    assert set(contract_module._STATUS) == set(AnswerStatus)
    assert set(contract_module._REASON) == set(AnswerReason)


def internal(
    status: AnswerStatus,
    reason: AnswerReason | None,
    **fields: Any,
) -> AnswerResponse:
    base: dict[str, Any] = {
        "sub_reason": None,
        "answer": None,
        "citations": [],
        "evidence": [],
        "message": None,
        "message_language": None,
        "usage": None,
        "latency_ms": {},
        "context": ContextStats(
            received=0, deduplicated=0, dropped_by_budget=0, blocks=0, chars=0
        ),
        "identity": AnswerIdentity(
            retrieval={},
            prompt=PromptIdentity(prompt_id="answer", prompt_version=1, sha256="x"),
            generator=None,
        ),
    }
    return AnswerResponse(status=status, reason=reason, **{**base, **fields})


CITATION = Citation(
    source_id="S1",
    document_id="d",
    document_version=2,
    section_id="s",
    title="t",
    source_authority="a",
    source_url="https://example.test/x",
)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (AnswerStatus.ANSWERED, PublicStatus.ANSWERED),
        (AnswerStatus.INSUFFICIENT_EVIDENCE, PublicStatus.INSUFFICIENT_EVIDENCE),
        (AnswerStatus.EVIDENCE_ONLY, PublicStatus.EVIDENCE_ONLY),
    ],
)
def test_status_mapping(status: AnswerStatus, expected: PublicStatus) -> None:
    reason = None if status is AnswerStatus.ANSWERED else AnswerReason.NO_EVIDENCE
    out = to_contract(internal(status, reason), "rid")
    assert out.status is expected
    assert out.request_id == "rid"
    assert out.contract_version == "1.0"


@pytest.mark.parametrize(
    ("reason", "expected"),
    [
        (AnswerReason.NO_EVIDENCE, PublicReason.NO_EVIDENCE),
        (AnswerReason.MODEL_DECLINED, PublicReason.NOT_ANSWERABLE),
        (AnswerReason.CITATION_INVALID, PublicReason.NOT_ANSWERABLE),
        (AnswerReason.OUTPUT_INVALID, PublicReason.NOT_ANSWERABLE),
        (AnswerReason.GENERATOR_UNAVAILABLE, PublicReason.GENERATOR_UNAVAILABLE),
    ],
)
def test_reason_mapping(reason: AnswerReason, expected: PublicReason) -> None:
    out = to_contract(
        internal(AnswerStatus.INSUFFICIENT_EVIDENCE, reason, sub_reason="model_url"),
        "rid",
    )
    assert out.reason is expected
    assert "sub_reason" not in out.model_dump()


def test_citation_and_evidence_are_copied_field_by_field() -> None:
    evidence = EvidenceSource(
        source_id="S1",
        document_id="d",
        document_version=2,
        section_id="s",
        title="t",
        source_authority="a",
        source_url=None,
        snippet="text",
    )
    answered = to_contract(
        internal(AnswerStatus.ANSWERED, None, answer="a [S1]", citations=[CITATION]),
        "r",
    )
    assert answered.citations[0].model_dump() == CITATION.model_dump()
    only = to_contract(
        internal(
            AnswerStatus.EVIDENCE_ONLY,
            AnswerReason.GENERATOR_UNAVAILABLE,
            evidence=[evidence],
        ),
        "r",
    )
    assert only.evidence[0].snippet == "text"


# --- happy path and schema ----------------------------------------------------------


def test_answer_status_codes_per_status(open_client: Any) -> None:
    client = open_client()
    body = post(client, {"query": QUERY}).json()
    assert body["status"] == "answered"
    assert body["contract_version"] == "1.0"
    assert body["citations"] and body["reason"] is None
    assert set(body) == set(AnswerContract.model_fields)


@pytest.mark.parametrize(
    ("mode", "status", "reason"),
    [
        (FakeMode.DECLINE, "insufficient_evidence", "not_answerable"),
        (FakeMode.MODEL_URL, "insufficient_evidence", "not_answerable"),
        (FakeMode.MALFORMED_JSON, "insufficient_evidence", "not_answerable"),
        (FakeMode.UNAVAILABLE, "evidence_only", "generator_unavailable"),
    ],
)
def test_http_mapping_per_internal_reason(
    open_client: Any, mode: FakeMode, status: str, reason: str
) -> None:
    client = open_client(generator=FakeGenerator(mode))
    body = post(client, {"query": QUERY}).json()
    assert (body["status"], body["reason"]) == (status, reason)
    if status == "evidence_only":
        assert body["evidence"] and body["answer"] is None
    else:
        assert body["message"] and body["message_language"]


def test_openapi_lists_answer_contract(open_client: Any) -> None:
    schema = open_client().get("/openapi.json").json()
    contract = schema["components"]["schemas"]["AnswerContract"]
    assert "contract_version" in contract["properties"]
    ref = schema["paths"]["/v1/answer"]["post"]["responses"]["200"]["content"]
    assert ref["application/json"]["schema"]["$ref"].endswith("/AnswerContract")


# --- 422 ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "body",
    [
        {"query": ""},
        {"query": "   \n\t "},
        {"query": "x" * 1001},
        {"query": QUERY, "role": "staff"},
        {"query": QUERY, "tenant_id": "other"},
        {"query": QUERY, "scope": "staff"},
        {"query": QUERY, "top_k": 50},
        {"query": QUERY, "lote": "*"},
        {"query": QUERY, "lote": ""},
        {"query": QUERY, "lote": "zz"},
        {"query": QUERY, "lote": "en"},
        {"lote": "ml"},
        {"query": 5},
    ],
)
def test_invalid_requests_are_422_without_echo(
    open_client: Any, body: dict[str, Any]
) -> None:
    client = open_client()
    response = post(client, body)
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "invalid_request"
    assert payload["request_id"] == response.headers["X-Request-ID"]
    for field in payload["fields"]:
        assert set(field) == {"loc", "msg"}
    assert set(payload) == {"request_id", "error", "fields"}
    for value in ("x" * 50, "staff", "other", QUERY):
        assert value not in response.text


def test_422_does_not_echo_a_sentinel_query(open_client: Any) -> None:
    client = open_client()
    response = post(client, {"query": SENTINEL_QUERY, "role": "staff"})
    assert response.status_code == 422
    assert SENTINEL_QUERY not in response.text


def test_active_lote_is_accepted(open_client: Any) -> None:
    client = open_client()
    assert post(client, {"query": QUERY, "lote": "ml"}).status_code == 200


# --- 413 ----------------------------------------------------------------------------


def test_body_limit_with_and_without_content_length(
    open_client: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = open_client()
    calls: list[int] = []
    monkeypatch.setattr(
        AnswerService,
        "answer",
        lambda *a, **k: calls.append(1),  # pragma: no cover
    )
    big = json.dumps({"query": "a" * 20000})
    with_length = client.post(
        "/v1/answer", content=big, headers={"content-type": "application/json"}
    )
    assert with_length.status_code == 413
    assert with_length.json() == {
        "request_id": with_length.headers["X-Request-ID"],
        "error": "body_too_large",
    }

    def chunks() -> Iterator[bytes]:
        for _ in range(4):
            yield b"a" * 5000

    chunked = client.post(
        "/v1/answer", content=chunks(), headers={"content-type": "application/json"}
    )
    assert chunked.status_code == 413
    assert calls == []


def test_a_body_within_the_limit_is_replayed(open_client: Any) -> None:
    client = open_client()
    assert post(client, {"query": QUERY}).status_code == 200


# --- 503, 500 -----------------------------------------------------------------------


def test_busy_503_with_retry_after(open_client: Any) -> None:
    client = open_client(serving={"concurrency": {"max_in_flight": 1}})
    held = client.app.state.slots.try_acquire()  # type: ignore[attr-defined]
    assert held is not None
    response = post(client, {"query": QUERY})
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "1"
    assert response.json()["error"] == "busy"
    held.release()
    assert post(client, {"query": QUERY}).status_code == 200


def test_not_ready_503_with_retry_after(
    fake_lexical: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "way2australia_api.lifespan.build_generator",
        lambda *_a, **_k: CountingGenerator(),
    )
    gate = threading.Event()
    app = create_app(
        fake_settings(), stack_factory=stack_factory(indexed_client(), gate=gate)
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        response = post(client, {"query": QUERY})
        assert response.status_code == 503
        assert response.headers["Retry-After"] == "5"
        assert response.json()["error"] == "not_ready"
        gate.set()
        wait_for(lambda: client.get("/ready").status_code == 200)


@pytest.mark.parametrize(
    "error",
    [
        RetrievalAuthorizationError(f"forbidden {SENTINEL_EXC}", document_id="doc-x"),
        RetrievalConfigurationError(f"bad config {SENTINEL_EXC}"),
        LanguageApplicabilityError(
            f"not applicable {SENTINEL_EXC}", document_id="doc-y"
        ),
    ],
    ids=lambda e: type(e).__name__,
)
def test_internal_errors_are_500_with_request_id_only(
    open_client: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    error: Exception,
) -> None:
    client = open_client()

    def boom(*_a: Any, **_k: Any) -> Any:
        raise error

    monkeypatch.setattr(AnswerService, "answer", boom)
    with caplog.at_level(logging.INFO):
        response = post(client, {"query": QUERY})
    request_id = response.headers["X-Request-ID"]
    assert response.status_code == 500
    assert response.json() == {"request_id": request_id, "error": "internal_error"}
    assert SENTINEL_EXC not in response.text
    assert client.app.state.slots.in_flight == 0  # type: ignore[attr-defined]
    lines = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(lines) == 1
    text = lines[0].getMessage()
    assert request_id in text and type(error).__name__ in text
    assert SENTINEL_EXC not in text and lines[0].exc_info is None


def test_shutdown_race_is_503_not_ready(
    open_client: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = open_client()

    def closed(*_a: Any, **_k: Any) -> Any:
        raise ServingNotReadyError("no serving stack is open")

    monkeypatch.setattr(StackHolder, "acquire", closed)
    response = post(client, {"query": QUERY})
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "5"
    assert response.json() == {
        "request_id": response.headers["X-Request-ID"],
        "error": "not_ready",
    }
    assert client.app.state.slots.in_flight == 0  # type: ignore[attr-defined]


def test_slot_released_on_success(open_client: Any) -> None:
    client = open_client()
    post(client, {"query": QUERY})
    assert client.app.state.slots.in_flight == 0  # type: ignore[attr-defined]


def test_slot_pool_unit() -> None:
    pool = SlotPool(1)
    slot = pool.try_acquire()
    assert slot is not None and pool.try_acquire() is None
    slot.release()
    slot.release()  # idempotent
    assert pool.in_flight == 0
    assert pool.try_acquire() is not None


# --- abandoned generation -----------------------------------------------------------


def test_blocked_generator_is_capped_and_visible_in_readiness(
    open_client: Any,
) -> None:
    generator = BlockingGenerator()
    client = open_client(
        generator=generator,
        serving={"budget": {"min_generation_s": 0}},
    )
    started = time.monotonic()
    assert post(client, {"query": QUERY}).status_code == 200
    warm = time.monotonic() - started
    generator.block = True
    started = time.monotonic()
    response = post(client, {"query": QUERY})
    elapsed = time.monotonic() - started
    body = response.json()
    assert (body["status"], body["reason"]) == (
        "evidence_only",
        "generator_unavailable",
    )
    assert elapsed < warm + 0.5 + 0.5
    slots = client.app.state.slots  # type: ignore[attr-defined]
    assert slots.in_flight == 1
    ready = client.get("/ready").json()
    assert "abandoned_generation" in ready["degraded_reasons"]
    assert ready["abandoned_in_flight"] == 1
    generator.release.set()
    wait_for(lambda: slots.in_flight == 0)
    ready = client.get("/ready").json()
    assert "abandoned_generation" not in ready["degraded_reasons"]
    assert "abandoned_in_flight" not in ready


# --- request ID, fake header, logging -----------------------------------------------


def test_client_request_id_is_not_echoed(open_client: Any) -> None:
    client = open_client()
    response = post(client, {"query": QUERY}, headers={"X-Request-ID": "client-id-1"})
    assert response.headers["X-Request-ID"] != "client-id-1"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert "client-id-1" not in response.text
    other = post(client, {"query": QUERY})
    assert other.headers["X-Request-ID"] != response.headers["X-Request-ID"]
    assert client.get("/health").headers["X-Request-ID"]


def test_fake_header_present_in_fake_mode_and_absent_otherwise(
    open_client: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = open_client(serving={"concurrency": {"max_in_flight": 1}})
    assert post(client, {"query": QUERY}).headers["X-W2A-Fake"] == "true"
    assert post(client, {"query": ""}).headers["X-W2A-Fake"] == "true"
    huge = client.post(
        "/v1/answer",
        content=json.dumps({"query": "a" * 20000}),
        headers={"content-type": "application/json"},
    )
    assert (huge.status_code, huge.headers["X-W2A-Fake"]) == (413, "true")
    held = client.app.state.slots.try_acquire()  # type: ignore[attr-defined]
    busy = post(client, {"query": QUERY})
    held.release()
    assert (busy.status_code, busy.headers["X-W2A-Fake"]) == (503, "true")
    with monkeypatch.context() as patch:
        patch.setattr(AnswerService, "answer", lambda *_a, **_k: 1 / 0)
        failed = post(client, {"query": QUERY})
    assert (failed.status_code, failed.headers["X-W2A-Fake"]) == (500, "true")
    assert client.get("/ready").json()["fake"] is True
    real = fake_settings().model_copy(update={"api_fake": False})
    client.app.state.settings = real  # type: ignore[attr-defined]
    assert "X-W2A-Fake" not in post(client, {"query": QUERY}).headers


def test_fake_provider_outside_fake_mode_is_refused_at_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built: list[int] = []
    monkeypatch.setattr(
        "way2australia_api.lifespan.build_generator",
        lambda *_a, **_k: built.append(1),
    )
    real = lifespan.load_generation_config

    def fake_default(*args: Any, **kwargs: Any) -> Any:
        config = real(*args, **kwargs)
        return config.model_copy(update={"default_generator": "fake"})

    monkeypatch.setattr(lifespan, "load_generation_config", fake_default)
    settings = Settings(repo_root=REPO_ROOT, api_fake=False)
    with pytest.raises(StartupError, match="fake generator"):
        with TestClient(create_app(settings)):
            pass  # pragma: no cover
    assert built == []


def test_logs_and_bodies_hold_no_sensitive_text(
    open_client: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", SENTINEL_KEY)
    monkeypatch.setenv("QDRANT_URL", SENTINEL_URL)
    caplog.set_level(logging.DEBUG)
    ok = open_client()
    failing = open_client(generator=RaisingGenerator())
    responses = [
        post(ok, {"query": SENTINEL_QUERY}),
        post(failing, {"query": SENTINEL_QUERY}),
        post(ok, {"query": SENTINEL_QUERY, "role": "staff"}),
    ]
    assert [r.status_code for r in responses] == [200, 500, 422]
    for response in responses:
        for text in (SENTINEL_QUERY, SENTINEL_KEY, SENTINEL_URL, SENTINEL_EXC):
            assert text not in response.text
    for text in (SENTINEL_QUERY, SENTINEL_KEY, SENTINEL_URL, SENTINEL_EXC):
        assert text not in caplog.text
    assert "RuntimeError" in caplog.text  # class name only


def test_answer_log_line_fields(
    open_client: Any, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="way2australia_api.answer")
    client = open_client()
    response = post(client, {"query": QUERY})
    lines = [
        json.loads(r.getMessage())
        for r in caplog.records
        if r.name == "way2australia_api.answer"
    ]
    assert len(lines) == 1
    line = lines[0]
    assert line["request_id"] == response.headers["X-Request-ID"]
    assert set(line) == {
        "event",
        "request_id",
        "status",
        "reason",
        "sub_reason",
        "served_strategy",
        "fallback_reason",
        "rerank",
        "breaker",
        "generator",
        "fake",
        "latency_ms",
        "query_chars",
        "script_mix",
        "abandoned_in_flight",
    }
    assert line["query_chars"] == len(QUERY)
    assert line["script_mix"] == "latin"
    assert line["fake"] is True
    assert set(line["latency_ms"]) == {"retrieval", "context", "generation", "total"}
    assert line["rerank"] in {"applied", "off"} or line["rerank"].startswith("skipped")
    for name in ("httpx", "anthropic"):
        assert logging.getLogger(name).level == logging.WARNING
