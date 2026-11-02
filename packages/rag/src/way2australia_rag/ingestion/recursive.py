"""Recursive token chunker (Spec 009 R4)."""

from __future__ import annotations

from collections.abc import Callable

from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.ingestion.chunking import (
    MAIN_SECTION_ID,
    MIN_CHUNK_TOKENS,
    SENTENCE_END_MARKS,
    Chunk,
    ChunkerIdentity,
    split_at_sentence_ends,
    split_on_separator,
    split_on_spaces,
    split_to_token_budget,
)
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.tokenization import (
    BgeM3Tokenizer,
    ChunkTokenizer,
    FakeTokenizer,
)

_RECURSIVE_SEPARATORS: tuple[str | None, ...] = ("\n\n", "\n", None, " ")


class RecursiveChunker:
    """Structure-blind recursive token chunker (``recursive`` v1)."""

    name = "recursive"
    version = "1"

    def __init__(
        self,
        *,
        target_tokens: int,
        overlap_tokens: int,
        context_prefix: str,
        tokenizer: ChunkTokenizer,
    ) -> None:
        if target_tokens < MIN_CHUNK_TOKENS:
            raise IngestionConfigurationError(
                f"target_tokens must be at least {MIN_CHUNK_TOKENS}."
            )
        maximum = tokenizer.identity.max_sequence_length
        if target_tokens > maximum:
            raise IngestionConfigurationError(
                f"target_tokens {target_tokens} exceeds the tokenizer maximum "
                f"{maximum}."
            )
        if overlap_tokens < 0 or overlap_tokens >= target_tokens / 2:
            raise IngestionConfigurationError(
                "overlap_tokens must be at least 0 and less than half of target_tokens."
            )
        if context_prefix not in ("none", "title"):
            raise IngestionConfigurationError(
                "recursive context_prefix must be 'none' or 'title'."
            )
        self._target_tokens = target_tokens
        self._overlap_tokens = overlap_tokens
        self._context_prefix = context_prefix
        self._tokenizer = tokenizer

    @property
    def identity(self) -> ChunkerIdentity:
        tok = self._tokenizer.identity
        tokenizer_ref = f"{tok.model_id}@{tok.revision}"
        return ChunkerIdentity(
            name=self.name,
            version=self.version,
            params={
                "context_prefix": self._context_prefix,
                "overlap_tokens": self._overlap_tokens,
                "target_tokens": self._target_tokens,
            },
            tokenizer=tokenizer_ref,
        )

    def chunk(self, document: KnowledgeDocument) -> list[Chunk]:
        body = document.content.strip()
        if not body:
            return [Chunk(section_id=MAIN_SECTION_ID, position=0, text="")]

        prefix = ""
        if self._context_prefix == "title":
            prefix = f"{document.title}\n\n"

        count = self._tokenizer.count
        if prefix and count(prefix) > self._target_tokens:
            raise IngestionConfigurationError(
                f"title prefix for document {document.document_id!r} exceeds "
                "target_tokens."
            )

        def chunk_fits(piece: str) -> bool:
            composed = f"{prefix}{piece}" if prefix else piece
            return count(composed) <= self._target_tokens

        units = _split_to_units(body, chunk_fits, count)
        bodies = _pack_with_overlap(
            units,
            chunk_fits,
            self._overlap_tokens,
            count,
            self._tokenizer,
        )

        chunks: list[Chunk] = []
        for position, piece in enumerate(bodies):
            text = f"{prefix}{piece}" if prefix else piece
            chunks.append(
                Chunk(section_id=MAIN_SECTION_ID, position=position, text=text)
            )
        return chunks


def _split_to_units(
    text: str,
    chunk_fits: Callable[[str], bool],
    count: Callable[[str], int],
) -> list[str]:
    return _recursive_split(text, 0, chunk_fits, count)


def _recursive_split(
    text: str,
    separator_index: int,
    chunk_fits: Callable[[str], bool],
    count: Callable[[str], int],
) -> list[str]:
    if chunk_fits(text):
        return [text]
    if separator_index >= len(_RECURSIVE_SEPARATORS):
        return split_to_token_budget(text, 0, count, fits=chunk_fits)
    separator = _RECURSIVE_SEPARATORS[separator_index]
    if separator is None:
        parts = split_at_sentence_ends(text)
    elif separator == " ":
        parts = split_on_spaces(text)
    else:
        parts = split_on_separator(text, separator)
        if separator == "\n\n":
            parts = [part for part in parts if part.strip()]
        else:
            parts = [part for part in parts if part]
    if len(parts) <= 1:
        return _recursive_split(text, separator_index + 1, chunk_fits, count)
    units: list[str] = []
    for part in parts:
        if chunk_fits(part):
            units.append(part)
        else:
            units.extend(_recursive_split(part, separator_index + 1, chunk_fits, count))
    return units


def _content_count(tokenizer: ChunkTokenizer, text: str) -> int:
    if isinstance(tokenizer, (FakeTokenizer, BgeM3Tokenizer)):
        return tokenizer.content_count(text)
    return tokenizer.count(text)


def _overlap_tail(
    units: list[str],
    overlap_tokens: int,
    tokenizer: ChunkTokenizer,
) -> list[str]:
    if overlap_tokens <= 0 or not units:
        return []
    tail: list[str] = []
    total = 0
    for unit in reversed(units):
        unit_count = _content_count(tokenizer, unit)
        if unit_count > overlap_tokens:
            break
        if total + unit_count > overlap_tokens:
            break
        tail.insert(0, unit)
        total += unit_count
    return tail


def _overlap_for_next_chunk(
    prev_units: list[str],
    next_unit: str,
    overlap_tokens: int,
    tokenizer: ChunkTokenizer,
    chunk_fits: Callable[[str], bool],
) -> list[str]:
    """Longest trailing run within overlap, trimmed until the next unit fits."""
    tail = _overlap_tail(prev_units, overlap_tokens, tokenizer)
    tail = [unit for unit in tail if chunk_fits(unit)]
    while tail:
        if chunk_fits(_join_units(tail + [next_unit])):
            return tail
        tail = tail[1:]
    return []


def _pack_with_overlap(
    units: list[str],
    chunk_fits: Callable[[str], bool],
    overlap_tokens: int,
    count: Callable[[str], int],
    tokenizer: ChunkTokenizer,
) -> list[str]:
    if not units:
        return [""]

    chunk_units: list[list[str]] = []
    current: list[str] = []

    def joined(parts: list[str]) -> str:
        return _join_units(parts)

    def start_next(from_units: list[str] | None = None) -> None:
        nonlocal current
        if from_units is None:
            current = []
            return
        current = _overlap_tail(from_units, overlap_tokens, tokenizer)

    start_next()

    for unit in units:
        if not chunk_fits(unit):
            if current:
                chunk_units.append(current)
            for piece in split_to_token_budget(unit, 0, count, fits=chunk_fits):
                chunk_units.append([piece])
            start_next(chunk_units[-1])
            continue

        trial = joined(current + [unit]) if current else unit
        if chunk_fits(trial):
            current.append(unit)
            continue

        if current:
            chunk_units.append(current)
            current = _overlap_for_next_chunk(
                current, unit, overlap_tokens, tokenizer, chunk_fits
            )
            trial = joined(current + [unit]) if current else unit
            if chunk_fits(trial):
                current.append(unit)
                continue

        if chunk_fits(unit):
            current = [unit]
        else:
            for piece in split_to_token_budget(unit, 0, count, fits=chunk_fits):
                chunk_units.append([piece])
            start_next(chunk_units[-1])

    if current:
        chunk_units.append(current)

    return [joined(block) for block in chunk_units]


def _join_units(units: list[str]) -> str:
    if not units:
        return ""
    text = units[0]
    for unit in units[1:]:
        if unit and text and text[-1] in SENTENCE_END_MARKS and not unit[0].isspace():
            text = f"{text} {unit}"
        else:
            text = f"{text}{unit}"
    return text
