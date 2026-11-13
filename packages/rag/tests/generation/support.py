"""Shared helpers for generation tests."""

from pathlib import Path

from way2australia_rag.generation.base import GeneratorOutput, GeneratorUsage
from way2australia_rag.generation.config import GenerationConfig, load_generation_config
from way2australia_rag.generation.context import EvidenceBlock
from way2australia_rag.generation.prompts import (
    PromptRegistry,
    RenderedPrompt,
    render_prompt,
)
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.models import (
    RerankRecord,
    RetrievalResult,
    RetrievedChunk,
)

REPO_ROOT = Path(__file__).resolve().parents[4]


def evidence_block(source_id: str = "S1", text: str = "chunk text") -> EvidenceBlock:
    return EvidenceBlock(
        source_id=source_id,
        document_id=f"doc_{source_id}",
        document_version=1,
        section_id="sec_1",
        title="Title",
        source_authority="owner",
        source_url=None,
        content_language="en",
        chunk_text=text,
    )


def rendered_prompt(source_ids: tuple[str, ...] = ("S1", "S2")) -> RenderedPrompt:
    version = PromptRegistry(REPO_ROOT).get("answer", 1)
    blocks = [evidence_block(sid, f"text of {sid}") for sid in source_ids]
    return render_prompt(version, blocks, "What is the fee?")


# --- Service helpers (T4) -------------------------------------------------------


def generation_config() -> GenerationConfig:
    return load_generation_config(REPO_ROOT / "config/generation.yaml", REPO_ROOT)


def output(
    answer: str,
    citations: list[str],
    *,
    answerable: bool = True,
) -> GeneratorOutput:
    return GeneratorOutput(
        answerable=answerable,
        answer=answer,
        citations=citations,
        usage=GeneratorUsage(input_tokens=1, output_tokens=1, attempts=1),
        stop_reason="end_turn",
    )


def hit(
    rank: int,
    text: str,
    *,
    document_id: str | None = None,
    title: str | None = None,
    source_url: str | None = None,
    authority: str = "owner",
) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        point_id=f"p{rank}",
        score=1.0 / rank,
        document_id=document_id or f"doc_{rank}",
        document_version=2,
        section_id=f"sec_{rank}",
        chunk_position=0,
        title=title or f"Title {rank}",
        chunk_text=text,
        knowledge_domain="business",
        source_authority=authority,
        source_type="faq",
        source_url=source_url,
        content_language="en",
        lote_languages=["*"],
    )


def retrieval_result(
    hits: list[RetrievedChunk], *, fallback_reason: str | None = None
) -> RetrievalResult:
    return RetrievalResult(
        hits=hits,
        collection="way2australia-idx-test",
        index_version="idx-test",
        embedder_model_id="fake",
        embedder_revision="r1",
        embedder_is_fake=True,
        device=None,
        top_k=5,
        latency_ms=1.0,
        strategy="hybrid" if fallback_reason is None else "bm25",
        requested_strategy="hybrid" if fallback_reason else None,
        fallback_reason=fallback_reason,
        rerank=RerankRecord(
            model_id="fake-reranker",
            revision="r2",
            max_length=512,
            is_fake=True,
            device=None,
            depth=20,
            candidates=len(hits),
            truncated_pairs=0,
        ),
    )


class FakeRetriever:
    """Returns a fixed result; records the calls."""

    strategy = Strategy.HYBRID

    def __init__(
        self, hits: list[RetrievedChunk], error: Exception | None = None
    ) -> None:
        self.hits = hits
        self.error = error
        self.calls: list[tuple[str, int, object]] = []

    def retrieve(self, query_text, access, top_k=5, *, lote=None):  # type: ignore[no-untyped-def]
        self.calls.append((query_text, top_k, lote))
        if self.error is not None:
            raise self.error
        return retrieval_result(self.hits)
