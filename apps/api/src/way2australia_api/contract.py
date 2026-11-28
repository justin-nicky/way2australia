"""Public answer contract 1.0 and the request model (Spec 013 R9, R11).

`to_contract` is the only mapping from the internal `AnswerResponse`. The two
explicit dicts fail a test, not a request, when an internal enum gains a member.
Citation and evidence fields are copied one by one, never by `model_dump`.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict
from way2australia_rag.generation.models import (
    AnswerReason,
    AnswerResponse,
    AnswerStatus,
)


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str
    lote: str | None = None


class PublicStatus(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    EVIDENCE_ONLY = "evidence_only"


class PublicReason(StrEnum):
    NO_EVIDENCE = "no_evidence"
    NOT_ANSWERABLE = "not_answerable"
    GENERATOR_UNAVAILABLE = "generator_unavailable"


class PublicCitation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str
    document_id: str
    document_version: int
    section_id: str
    title: str
    source_authority: str
    source_url: str | None


class PublicEvidence(PublicCitation):
    snippet: str


class AnswerContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    status: PublicStatus
    reason: PublicReason | None
    answer: str | None
    citations: list[PublicCitation]
    evidence: list[PublicEvidence]
    message: str | None
    message_language: str | None


_STATUS: dict[AnswerStatus, PublicStatus] = {
    AnswerStatus.ANSWERED: PublicStatus.ANSWERED,
    AnswerStatus.INSUFFICIENT_EVIDENCE: PublicStatus.INSUFFICIENT_EVIDENCE,
    AnswerStatus.EVIDENCE_ONLY: PublicStatus.EVIDENCE_ONLY,
}

_REASON: dict[AnswerReason, PublicReason] = {
    AnswerReason.NO_EVIDENCE: PublicReason.NO_EVIDENCE,
    AnswerReason.MODEL_DECLINED: PublicReason.NOT_ANSWERABLE,
    AnswerReason.CITATION_INVALID: PublicReason.NOT_ANSWERABLE,
    AnswerReason.OUTPUT_INVALID: PublicReason.NOT_ANSWERABLE,
    AnswerReason.GENERATOR_UNAVAILABLE: PublicReason.GENERATOR_UNAVAILABLE,
}


def to_contract(response: AnswerResponse, request_id: str) -> AnswerContract:
    return AnswerContract(
        request_id=request_id,
        status=_STATUS[response.status],
        reason=None if response.reason is None else _REASON[response.reason],
        answer=response.answer,
        citations=[
            PublicCitation(
                source_id=c.source_id,
                document_id=c.document_id,
                document_version=c.document_version,
                section_id=c.section_id,
                title=c.title,
                source_authority=c.source_authority,
                source_url=c.source_url,
            )
            for c in response.citations
        ],
        evidence=[
            PublicEvidence(
                source_id=e.source_id,
                document_id=e.document_id,
                document_version=e.document_version,
                section_id=e.section_id,
                title=e.title,
                source_authority=e.source_authority,
                source_url=e.source_url,
                snippet=e.snippet,
            )
            for e in response.evidence
        ],
        message=response.message,
        message_language=response.message_language,
    )
