"""Answer contract models (Spec 012 R3)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from way2australia_rag.generation.base import GeneratorInfo, GeneratorUsage


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    EVIDENCE_ONLY = "evidence_only"


class AnswerReason(StrEnum):
    NO_EVIDENCE = "no_evidence"
    MODEL_DECLINED = "model_declined"
    CITATION_INVALID = "citation_invalid"
    OUTPUT_INVALID = "output_invalid"
    GENERATOR_UNAVAILABLE = "generator_unavailable"


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    document_id: str
    document_version: int
    section_id: str
    title: str
    source_authority: str
    source_url: str | None


class EvidenceSource(Citation):
    snippet: str


class PromptIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_id: str
    prompt_version: int
    sha256: str


class AnswerIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    retrieval: dict[str, Any]
    prompt: PromptIdentity
    generator: GeneratorInfo | None


class ContextStats(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    received: int
    deduplicated: int
    dropped_by_budget: int
    blocks: int
    chars: int


class AnswerResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: AnswerStatus
    reason: AnswerReason | None
    sub_reason: str | None
    answer: str | None
    citations: list[Citation]
    evidence: list[EvidenceSource]
    message: str | None
    message_language: str | None
    identity: AnswerIdentity
    usage: GeneratorUsage | None
    latency_ms: dict[str, float]
    context: ContextStats

    @model_validator(mode="after")
    def _status_reason_shape(self) -> "AnswerResponse":
        if self.status == AnswerStatus.ANSWERED:
            if self.reason is not None:
                raise ValueError("answered status must not carry a reason")
        elif self.reason is None:
            raise ValueError(f"{self.status.value} requires a reason")
        return self
