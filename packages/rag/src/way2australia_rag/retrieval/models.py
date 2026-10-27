"""Retrieval result models (Spec 005 R5).

`chunk_text` is untrusted data: it is returned, never interpreted.
"""

from pydantic import BaseModel, ConfigDict


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rank: int
    point_id: str
    score: float
    document_id: str
    document_version: int
    section_id: str
    chunk_position: int
    title: str
    chunk_text: str
    knowledge_domain: str
    source_authority: str
    source_type: str
    source_url: str | None
    content_language: str
    lote_languages: list[str]
    leg_ranks: dict[str, int | None] | None = None


class LexicalIdentity(BaseModel):
    """Which lexical index produced a result (file name only, never a path)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    tokenizer_name: str
    tokenizer_version: str
    source_chunk_digest: str
    chunk_count: int


class RetrievalResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hits: list[RetrievedChunk]
    collection: str
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_is_fake: bool
    device: str | None
    top_k: int
    latency_ms: float
    strategy: str = "dense"
    score_kind: str = "dense_cosine"
    leg_latency_ms: dict[str, float] | None = None
    lexical: LexicalIdentity | None = None
    query_terms_truncated: bool | None = None
