"""Answer service: retrieval, context, pre-gate, generation, citation validation.

Spec 012 R3, R6, R7. The service holds no repository, Qdrant client or lexical
handle (C3): evidence comes only from the retriever's result, which is already
access-filtered and applicability-checked. Model output never reaches retrieval or
access code and never supplies citation metadata.

Only `GeneratorUnavailableError`, `GeneratorDeclinedError` and
`GeneratorOutputError` are caught. Configuration errors, `RetrievalAuthorizationError`
and `LanguageApplicabilityError` propagate (fail closed).
"""

import time
from typing import Any

from way2australia_rag.generation.base import Generator, GeneratorUsage
from way2australia_rag.generation.citations import (
    CitationValidationError,
    validate_citations,
)
from way2australia_rag.generation.config import GenerationConfig
from way2australia_rag.generation.context import ContextBuilder, EvidenceBlock
from way2australia_rag.generation.errors import (
    GeneratorDeclinedError,
    GeneratorOutputError,
    GeneratorUnavailableError,
)
from way2australia_rag.generation.language import (
    FALLBACK_MESSAGE_LANGUAGE,
    message_language,
)
from way2australia_rag.generation.models import (
    AnswerIdentity,
    AnswerReason,
    AnswerResponse,
    AnswerStatus,
    Citation,
    ContextStats,
    EvidenceSource,
)
from way2australia_rag.generation.prompts import PromptVersion, render_prompt
from way2australia_rag.retrieval.access import ResolvedAccess
from way2australia_rag.retrieval.applicability import ResolvedLote
from way2australia_rag.retrieval.base import Retriever
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.text import safe_text


def retrieval_identity(result: RetrievalResult) -> dict[str, Any]:
    """Retrieval fields recorded with an answer (as result 2.5): served path,
    fallback, rerank record, index and lexical identity, `lote`."""
    return {
        "strategy": result.strategy,
        "requested_strategy": result.requested_strategy,
        "fallback_reason": result.fallback_reason,
        "score_kind": result.score_kind,
        "top_k": result.top_k,
        "collection": result.collection,
        "index_version": result.index_version,
        "embedder_model_id": result.embedder_model_id,
        "embedder_revision": result.embedder_revision,
        "embedder_is_fake": result.embedder_is_fake,
        "device": result.device,
        "lexical": result.lexical.model_dump() if result.lexical else None,
        "rerank": result.rerank.model_dump() if result.rerank else None,
        "lote": result.lote,
    }


def _ms(start: float, end: float) -> float:
    return round((end - start) * 1000, 3)


class AnswerService:
    def __init__(
        self,
        retriever: Retriever,
        builder: ContextBuilder,
        prompt_version: PromptVersion,
        generator: Generator,
        config: GenerationConfig,
    ) -> None:
        self._retriever = retriever
        self._builder = builder
        self._prompt = prompt_version
        self._generator = generator
        self._config = config

    def answer(
        self,
        query: str,
        access: ResolvedAccess,
        top_k: int | None = None,
        lote: ResolvedLote | None = None,
    ) -> AnswerResponse:
        started = time.perf_counter()
        result = self._retriever.retrieve(
            query,
            access,
            self._config.retrieval.top_k if top_k is None else top_k,
            lote=lote,
        )
        retrieved = time.perf_counter()
        blocks, stats = self._builder.build(result.hits)
        built = time.perf_counter()
        latency = {
            "retrieval_ms": _ms(started, retrieved),
            "context_ms": _ms(retrieved, built),
        }
        retrieval = retrieval_identity(result)

        def respond(
            status: AnswerStatus,
            reason: AnswerReason | None,
            *,
            sub_reason: str | None = None,
            answer: str | None = None,
            citations: list[Citation] | None = None,
            called: bool = False,
            usage: GeneratorUsage | None = None,
            generation_ms: float = 0.0,
        ) -> AnswerResponse:
            return self._response(
                query,
                status,
                reason,
                sub_reason,
                answer,
                citations or [],
                blocks,
                stats,
                retrieval,
                called,
                usage,
                {
                    **latency,
                    "generation_ms": generation_ms,
                    "total_ms": _ms(started, time.perf_counter()),
                },
            )

        # Pre-gate: no evidence, no generator call.
        if not blocks:
            return respond(AnswerStatus.INSUFFICIENT_EVIDENCE, AnswerReason.NO_EVIDENCE)

        rendered = render_prompt(self._prompt, blocks, query)
        gen_start = time.perf_counter()
        try:
            output = self._generator.generate(rendered)
        except GeneratorUnavailableError as error:
            return respond(
                AnswerStatus.EVIDENCE_ONLY,
                AnswerReason.GENERATOR_UNAVAILABLE,
                sub_reason=error.reason.value,
                called=True,
                generation_ms=_ms(gen_start, time.perf_counter()),
            )
        except GeneratorDeclinedError:
            return respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                AnswerReason.MODEL_DECLINED,
                called=True,
                generation_ms=_ms(gen_start, time.perf_counter()),
            )
        except GeneratorOutputError as error:
            return respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                AnswerReason.OUTPUT_INVALID,
                sub_reason=error.rule,
                called=True,
                generation_ms=_ms(gen_start, time.perf_counter()),
            )
        generation_ms = _ms(gen_start, time.perf_counter())
        if not output.answerable:
            return respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                AnswerReason.MODEL_DECLINED,
                called=True,
                usage=output.usage,
                generation_ms=generation_ms,
            )
        try:
            citations = validate_citations(output, blocks)
        except CitationValidationError as error:
            return respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                AnswerReason.CITATION_INVALID,
                sub_reason=error.rule,
                called=True,
                usage=output.usage,
                generation_ms=generation_ms,
            )
        return respond(
            AnswerStatus.ANSWERED,
            None,
            answer=output.answer,
            citations=citations,
            called=True,
            usage=output.usage,
            generation_ms=generation_ms,
        )

    def _response(
        self,
        query: str,
        status: AnswerStatus,
        reason: AnswerReason | None,
        sub_reason: str | None,
        answer: str | None,
        citations: list[Citation],
        blocks: list[EvidenceBlock],
        stats: ContextStats,
        retrieval: dict[str, Any],
        called: bool,
        usage: GeneratorUsage | None,
        latency: dict[str, float],
    ) -> AnswerResponse:
        message: str | None = None
        language: str | None = None
        evidence: list[EvidenceSource] = []
        if status == AnswerStatus.INSUFFICIENT_EVIDENCE:
            wanted = message_language(query, self._config.languages.script_to_language)
            language = (
                wanted
                if wanted in self._prompt.messages
                else (FALLBACK_MESSAGE_LANGUAGE)
            )
            message = self._prompt.messages[language]
        elif status == AnswerStatus.EVIDENCE_ONLY:
            limit = self._config.evidence_only.snippet_chars
            evidence = [
                EvidenceSource(
                    source_id=block.source_id,
                    document_id=block.document_id,
                    document_version=block.document_version,
                    section_id=block.section_id,
                    title=block.title,
                    source_authority=block.source_authority,
                    source_url=block.source_url,
                    snippet=safe_text(block.chunk_text)[:limit],
                )
                for block in blocks
            ]
        return AnswerResponse(
            status=status,
            reason=reason,
            sub_reason=sub_reason,
            answer=answer,
            citations=citations,
            evidence=evidence,
            message=message,
            message_language=language,
            identity=AnswerIdentity(
                retrieval=retrieval,
                prompt=self._prompt.identity,
                generator=self._generator.info if called else None,
            ),
            usage=usage,
            latency_ms=latency,
            context=stats,
        )
