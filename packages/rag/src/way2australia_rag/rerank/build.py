"""Reranker factory (Spec 011 R3). Called only when reranking is on."""

from way2australia_rag.rerank.base import Reranker
from way2australia_rag.rerank.bge import BGE_RERANKER_MODEL_ID, BgeRerankerV2M3
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.strategy import RerankConfig


def build_reranker(config: RerankConfig, provider: str | None = None) -> Reranker:
    """`provider` overrides `config.provider` (for example `--reranker fake`)."""
    chosen = provider or config.provider
    if chosen == "fake":
        return FakeReranker(
            model_id=config.model_id,
            revision=config.revision or "fake",
            max_length=config.max_length,
        )
    if chosen == "bge":
        if config.model_id != BGE_RERANKER_MODEL_ID:
            raise RetrievalConfigurationError(
                f"the bge reranker supports only {BGE_RERANKER_MODEL_ID}; "
                "check rerank.model_id."
            )
        return BgeRerankerV2M3(
            config.revision,
            max_length=config.max_length,
            batch_size=config.batch_size,
        )
    raise RetrievalConfigurationError(f"unknown reranker provider {chosen!r}")
