"""Context builder: retrieved hits to bounded, ordered evidence blocks (Spec 012 R1).

It only reads the hits it is given. It never calls retrieval, Qdrant or the
lexical file, and it adds no chunk it was not handed.
"""

import unicodedata
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from way2australia_rag.generation.config import ContextConfig
from way2australia_rag.generation.models import ContextStats
from way2australia_rag.retrieval.models import RetrievedChunk


class EvidenceBlock(BaseModel):
    """One piece of evidence with a backend-issued source ID (`S1`, `S2`, ...)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    document_id: str
    document_version: int
    section_id: str
    title: str
    source_authority: str
    source_url: str | None
    content_language: str
    chunk_text: str


def _normalize(text: str) -> str:
    """Comparison key only: NFC, whitespace runs to one space, stripped."""
    return " ".join(unicodedata.normalize("NFC", text).split())


class ContextBuilder:
    """Deduplicate, budget and number retrieval hits. Deterministic."""

    def __init__(self, config: ContextConfig) -> None:
        self._config = config

    def build(
        self, hits: Sequence[RetrievedChunk]
    ) -> tuple[list[EvidenceBlock], ContextStats]:
        # Exact-text deduplication only. Neighbouring chunks are NOT merged
        # (design "Data flow" step 2, R1 decision): overlap and title prefixes
        # cannot be removed from the payload without chunker internals.
        seen: set[str] = set()
        unique: list[RetrievedChunk] = []
        for hit in hits:
            key = _normalize(hit.chunk_text)
            if key in seen:
                continue
            seen.add(key)
            unique.append(hit)

        # Rank order is kept. Whole blocks only; the first block that does not
        # fit ends the list, so a lower-ranked block never replaces a higher one.
        kept: list[RetrievedChunk] = []
        chars = 0
        for hit in unique:
            if len(kept) >= self._config.max_blocks:
                break
            if chars + len(hit.chunk_text) > self._config.max_chars:
                break
            kept.append(hit)
            chars += len(hit.chunk_text)

        blocks = [
            EvidenceBlock(
                source_id=f"S{index}",
                document_id=hit.document_id,
                document_version=hit.document_version,
                section_id=hit.section_id,
                title=hit.title,
                source_authority=hit.source_authority,
                source_url=hit.source_url,
                content_language=hit.content_language,
                chunk_text=hit.chunk_text,
            )
            for index, hit in enumerate(kept, start=1)
        ]
        stats = ContextStats(
            received=len(hits),
            deduplicated=len(hits) - len(unique),
            dropped_by_budget=len(unique) - len(kept),
            blocks=len(blocks),
            chars=chars,
        )
        return blocks, stats
