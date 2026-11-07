"""Answer contract models (Spec 012 R3)."""

import pytest
from pydantic import ValidationError
from way2australia_rag.generation.base import GeneratorInfo, GeneratorUsage
from way2australia_rag.generation.models import (
    AnswerIdentity,
    AnswerReason,
    AnswerResponse,
    AnswerStatus,
    Citation,
    ContextStats,
    PromptIdentity,
)


def _identity(*, with_generator: bool) -> AnswerIdentity:
    prompt = PromptIdentity(prompt_id="answer", prompt_version=1, sha256="abc")
    generator = None
    if with_generator:
        generator = GeneratorInfo(
            provider="fake",
            model_id="fake",
            endpoint=None,
            region=None,
            inference_profile=None,
            effort=None,
            max_tokens=1024,
            request_timeout_s=20.0,
            retries=0,
            deadline_s=30.0,
            is_fake=True,
        )
    return AnswerIdentity(
        retrieval={"strategy": "hybrid"},
        prompt=prompt,
        generator=generator,
    )


def _stats() -> ContextStats:
    return ContextStats(
        received=1,
        deduplicated=0,
        dropped_by_budget=0,
        blocks=1,
        chars=10,
    )


def test_extra_fields_refused() -> None:
    with pytest.raises(ValidationError):
        Citation(
            source_id="S1",
            document_id="d",
            document_version=1,
            section_id="s",
            title="t",
            source_authority="owner",
            source_url=None,
            surprise="nope",  # type: ignore[call-arg]
        )


def test_answered_has_no_reason() -> None:
    response = AnswerResponse(
        status=AnswerStatus.ANSWERED,
        reason=None,
        sub_reason=None,
        answer="Fee is 10 [S1].",
        citations=[
            Citation(
                source_id="S1",
                document_id="d",
                document_version=1,
                section_id="s",
                title="t",
                source_authority="owner",
                source_url=None,
            )
        ],
        evidence=[],
        message=None,
        message_language="en",
        identity=_identity(with_generator=True),
        usage=GeneratorUsage(input_tokens=1, output_tokens=2, attempts=1),
        latency_ms={"total_ms": 1.0},
        context=_stats(),
    )
    assert response.reason is None


def test_insufficient_evidence_requires_reason() -> None:
    with pytest.raises(ValidationError):
        AnswerResponse(
            status=AnswerStatus.INSUFFICIENT_EVIDENCE,
            reason=None,
            sub_reason="no_evidence",
            answer=None,
            citations=[],
            evidence=[],
            message="safe",
            message_language="en",
            identity=_identity(with_generator=False),
            usage=None,
            latency_ms={"total_ms": 1.0},
            context=_stats(),
        )


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        (AnswerStatus.INSUFFICIENT_EVIDENCE, AnswerReason.NO_EVIDENCE),
        (AnswerStatus.INSUFFICIENT_EVIDENCE, AnswerReason.MODEL_DECLINED),
        (AnswerStatus.INSUFFICIENT_EVIDENCE, AnswerReason.CITATION_INVALID),
        (AnswerStatus.INSUFFICIENT_EVIDENCE, AnswerReason.OUTPUT_INVALID),
        (AnswerStatus.EVIDENCE_ONLY, AnswerReason.GENERATOR_UNAVAILABLE),
    ],
)
def test_non_answered_status_requires_reason(
    status: AnswerStatus, reason: AnswerReason
) -> None:
    AnswerResponse(
        status=status,
        reason=reason,
        sub_reason=None,
        answer=None,
        citations=[],
        evidence=[],
        message="safe" if status == AnswerStatus.INSUFFICIENT_EVIDENCE else None,
        message_language="en",
        identity=_identity(with_generator=status != AnswerStatus.INSUFFICIENT_EVIDENCE),
        usage=None,
        latency_ms={"total_ms": 1.0},
        context=_stats(),
    )


def test_answered_with_reason_refused() -> None:
    with pytest.raises(ValidationError):
        AnswerResponse(
            status=AnswerStatus.ANSWERED,
            reason=AnswerReason.NO_EVIDENCE,
            sub_reason=None,
            answer="x",
            citations=[],
            evidence=[],
            message=None,
            message_language="en",
            identity=_identity(with_generator=True),
            usage=None,
            latency_ms={"total_ms": 1.0},
            context=_stats(),
        )
