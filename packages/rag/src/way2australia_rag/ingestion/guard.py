"""Truncation guard before embedding (Spec 009 R2)."""

from collections.abc import Sequence

from way2australia_rag.ingestion.chunking import Chunk
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.ingestion.tokenization import ChunkTokenizer


class ChunkTooLongError(IngestionError):
    def __init__(
        self,
        document_id: str,
        section_id: str,
        position: int,
        tokens: int,
        limit: int,
    ) -> None:
        self.document_id = document_id
        self.section_id = section_id
        self.position = position
        self.tokens = tokens
        self.limit = limit
        super().__init__(
            "chunk_too_long: "
            f"section_id={section_id} position={position} "
            f"tokens={tokens} limit={limit}"
        )


def _effective_limit(tokenizer: ChunkTokenizer, cap: int | None) -> int:
    maximum = tokenizer.identity.max_sequence_length
    if cap is None:
        return maximum
    return min(maximum, cap)


def check_chunks(
    document_id: str,
    chunks: Sequence[Chunk],
    tokenizer: ChunkTokenizer,
    cap: int | None,
) -> None:
    """Raise ``ChunkTooLongError`` on the first chunk above the effective limit."""
    limit = _effective_limit(tokenizer, cap)
    for chunk in chunks:
        tokens = tokenizer.count(chunk.text)
        if tokens > limit:
            raise ChunkTooLongError(
                document_id, chunk.section_id, chunk.position, tokens, limit
            )
