"""AnswerService end to end, fake retriever and generator (Spec 012 R3, R6, R7)."""

from typing import Any

import pytest
from way2australia_core import AccessContext, Role
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.errors import UnavailableReason
from way2australia_rag.generation.fake import FakeGenerator, FakeMode
from way2australia_rag.generation.models import AnswerReason, AnswerStatus
from way2australia_rag.generation.prompts import PromptRegistry
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.errors import (
    LanguageApplicabilityError,
    RetrievalAuthorizationError,
)

from .support import REPO_ROOT, FakeRetriever, generation_config, hit

ACCESS = resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))
CONFIG = generation_config()
PROMPT = PromptRegistry(REPO_ROOT).get(CONFIG.prompt.id, CONFIG.prompt.version)
HITS = [
    hit(
        1,
        "Coaching is optional.",
        source_url="https://example.test/a",
        authority="naati",
    ),
    hit(2, "Fees change every year."),
]


def service(
    generator: Any, hits: list[Any] | None = None, retriever: Any = None
) -> AnswerService:
    return AnswerService(
        retriever or FakeRetriever(HITS if hits is None else hits),
        ContextBuilder(CONFIG.context),
        PROMPT,
        generator,
        CONFIG,
    )


def test_answered_with_validated_citations_and_complete_identity() -> None:
    generator = FakeGenerator(citations=["S2", "S1"])
    response = service(generator).answer("Is coaching compulsory?", ACCESS)
    assert response.status == AnswerStatus.ANSWERED
    assert response.reason is None and response.sub_reason is None
    assert response.answer == "Fake answer. [S2][S1]"
    assert [c.source_id for c in response.citations] == ["S2", "S1"]
    assert response.citations[1].source_url == "https://example.test/a"
    assert response.citations[1].source_authority == "naati"
    assert response.message is None and response.evidence == []
    identity = response.identity
    assert identity.generator == generator.info
    assert identity.prompt == PROMPT.identity
    retrieval = identity.retrieval
    assert retrieval["strategy"] == "hybrid"
    assert retrieval["rerank"]["model_id"] == "fake-reranker"
    assert {
        "requested_strategy",
        "fallback_reason",
        "index_version",
        "collection",
        "embedder_model_id",
        "embedder_is_fake",
        "lexical",
        "lote",
        "top_k",
    } <= set(retrieval)
    assert response.usage is not None and response.usage.attempts == 1
    assert set(response.latency_ms) == {
        "retrieval_ms",
        "context_ms",
        "generation_ms",
        "total_ms",
    }
    assert response.context.blocks == 2 and response.context.received == 2


def test_top_k_defaults_from_config_and_lote_is_passed() -> None:
    retriever = FakeRetriever(HITS)
    lote = ResolvedLote(code="ml")
    service(FakeGenerator(), retriever=retriever).answer("q", ACCESS, lote=lote)
    service(FakeGenerator(), retriever=retriever).answer("q", ACCESS, top_k=3)
    assert retriever.calls[0][1] == CONFIG.retrieval.top_k
    assert retriever.calls[0][2] == lote
    assert retriever.calls[1][1] == 3


def test_pre_gate_makes_zero_generator_calls() -> None:
    generator = FakeGenerator()
    response = service(generator, hits=[]).answer("anything", ACCESS)
    assert generator.calls == 0
    assert response.status == AnswerStatus.INSUFFICIENT_EVIDENCE
    assert response.reason == AnswerReason.NO_EVIDENCE
    assert response.identity.generator is None
    assert response.usage is None
    assert response.message == PROMPT.messages["en"]
    assert response.message_language == "en"
    assert response.latency_ms["generation_ms"] == 0.0


@pytest.mark.parametrize(
    ("mode", "status", "reason", "sub_reason"),
    [
        (
            FakeMode.DECLINE,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.MODEL_DECLINED,
            None,
        ),
        (
            FakeMode.REFUSAL,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.MODEL_DECLINED,
            None,
        ),
        (
            FakeMode.MAX_TOKENS,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.OUTPUT_INVALID,
            "max_tokens",
        ),
        (
            FakeMode.MALFORMED_JSON,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.OUTPUT_INVALID,
            "json",
        ),
        (
            FakeMode.SCHEMA_MISMATCH,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.OUTPUT_INVALID,
            "schema",
        ),
        (
            FakeMode.UNKNOWN_ID,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.CITATION_INVALID,
            "unknown_id",
        ),
        (
            FakeMode.MARKER_MISMATCH,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.CITATION_INVALID,
            "marker_mismatch",
        ),
        (
            FakeMode.DUPLICATE_ID,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.CITATION_INVALID,
            "duplicate_id",
        ),
        (
            FakeMode.EMPTY_CITATIONS,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.CITATION_INVALID,
            "no_citation",
        ),
        (
            FakeMode.MODEL_URL,
            AnswerStatus.INSUFFICIENT_EVIDENCE,
            AnswerReason.CITATION_INVALID,
            "model_url",
        ),
    ],
)
def test_every_contract_defect_end_to_end(
    mode: FakeMode, status: AnswerStatus, reason: AnswerReason, sub_reason: str | None
) -> None:
    generator = FakeGenerator(mode)
    response = service(generator).answer("Is coaching compulsory?", ACCESS)
    assert generator.calls == 1
    assert (response.status, response.reason, response.sub_reason) == (
        status,
        reason,
        sub_reason,
    )
    assert response.answer is None and response.citations == []
    assert response.message == PROMPT.messages["en"]
    assert response.identity.generator == generator.info


@pytest.mark.parametrize("sub", list(UnavailableReason))
def test_generator_unavailable_serves_evidence_only(sub: UnavailableReason) -> None:
    generator = FakeGenerator(FakeMode.UNAVAILABLE, unavailable=sub)
    response = service(generator).answer("Is coaching compulsory?", ACCESS)
    assert response.status == AnswerStatus.EVIDENCE_ONLY
    assert response.reason == AnswerReason.GENERATOR_UNAVAILABLE
    assert response.sub_reason == sub.value
    assert response.answer is None and response.message is None
    assert [s.source_id for s in response.evidence] == ["S1", "S2"]
    assert response.evidence[0].source_url == "https://example.test/a"
    assert response.evidence[0].snippet == "Coaching is optional."


def test_evidence_only_snippets_use_safe_text_and_are_cut() -> None:
    text = "line one\n\x1b[31mred\x1b[0m‮evil " + "x" * 500
    generator = FakeGenerator(FakeMode.UNAVAILABLE)
    response = service(generator, hits=[hit(1, text)]).answer("q", ACCESS)
    snippet = response.evidence[0].snippet
    assert len(snippet) <= CONFIG.evidence_only.snippet_chars
    assert "\n" not in snippet and "\x1b" not in snippet and "‮" not in snippet
    assert snippet.startswith("line one red")


def test_non_eligible_generator_errors_propagate() -> None:
    with pytest.raises(RuntimeError):
        service(FakeGenerator(FakeMode.NON_ELIGIBLE)).answer("q", ACCESS)


@pytest.mark.parametrize(
    "error",
    [
        RetrievalAuthorizationError("blocked", document_id="doc_x"),
        LanguageApplicabilityError("blocked", document_id="doc_x"),
    ],
)
def test_retrieval_errors_propagate_without_a_generator_call(error: Exception) -> None:
    generator = FakeGenerator()
    with pytest.raises(type(error)):
        service(generator, retriever=FakeRetriever(HITS, error)).answer("q", ACCESS)
    assert generator.calls == 0


def test_message_language_follows_the_query_script() -> None:
    malayalam = "കോചിംഗ് വേണോ?"
    response = service(FakeGenerator(), hits=[]).answer(malayalam, ACCESS)
    assert response.message_language == "ml"
    assert response.message == PROMPT.messages["ml"]
    mixed = f"Is coaching {malayalam}"
    assert (
        service(FakeGenerator(), hits=[]).answer(mixed, ACCESS).message_language == "ml"
    )
    assert (
        service(FakeGenerator(), hits=[])
        .answer("plain english", ACCESS)
        .message_language
        == "en"
    )


def test_a_mapped_code_without_a_message_falls_back_to_the_default_language() -> None:
    config = CONFIG.model_copy(
        update={
            "languages": CONFIG.languages.model_copy(
                update={"script_to_language": {"devanagari": "zz"}}
            )
        }
    )
    svc = AnswerService(
        FakeRetriever([]),
        ContextBuilder(config.context),
        PROMPT,
        FakeGenerator(),
        config,
    )
    response = svc.answer("कोचिंग", ACCESS)
    assert response.message_language == "en"
    assert response.message == PROMPT.messages["en"]


def test_output_cannot_change_citation_metadata_or_inject_text() -> None:
    generator = FakeGenerator(FakeMode.MODEL_URL)
    response = service(generator).answer("q", ACCESS)
    dumped = response.model_dump_json()
    assert "example.test/page" not in dumped
    assert response.citations == []


def test_a_prompt_records_only_issued_evidence() -> None:
    generator = FakeGenerator(record=True)
    service(generator).answer("Is coaching compulsory?", ACCESS)
    assert len(generator.prompts) == 1
    user = generator.prompts[0].user
    assert 'id="S1"' in user and 'id="S2"' in user and 'id="S3"' not in user
