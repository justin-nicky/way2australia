"""Chunker interface and the heading-based baseline chunker (Spec 004 R4).

The chunker is pure and deterministic: no I/O, no clock, no randomness. It
contains no language-specific behavior.
"""

import re
import unicodedata
from typing import Protocol

from pydantic import BaseModel, ConfigDict
from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.ingestion.errors import IngestionConfigurationError

MIN_CHUNK_CHARS = 16  # keeps the body budget >= 1 even with a truncated heading
MAIN_SECTION_ID = "main"
FALLBACK_SECTION_ID = "section"

_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_PARAGRAPH_BREAK_RE = re.compile(r"\n[ \t]*\n")


class Chunk(BaseModel):
    """One indexable piece of a document section."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    section_id: str
    position: int  # 0-based piece index within the section
    text: str


class Chunker(Protocol):
    name: str
    version: str
    max_chunk_chars: int

    def chunk(self, document: KnowledgeDocument) -> list[Chunk]: ...


def _is_word_char(char: str) -> bool:
    # Letters and digits, plus combining marks (category M*), which many
    # scripts need inside words; `\w` alone would split such words apart.
    return char.isalnum() or unicodedata.category(char).startswith("M")


def slugify(text: str) -> str:
    """NFKC, lower-case, runs of non-word characters become `-`, trimmed.

    Invisible format characters (Unicode category Cf, e.g. ZWJ/ZWNJ, which
    Malayalam and other Indic scripts use inside words) are dropped, not
    treated as separators, so they never split a word.
    """
    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
    parts: list[str] = []
    in_separator = True
    for char in normalized:
        if _is_word_char(char):
            parts.append(char)
            in_separator = False
        elif not in_separator:
            parts.append("-")
            in_separator = True
    slug = "".join(parts).strip("-")
    return slug or FALLBACK_SECTION_ID


class _Section:
    def __init__(self, heading_line: str | None, heading_text: str | None) -> None:
        self.heading_line = heading_line
        self.heading_text = heading_text
        self.lines: list[str] = []


def _parse_sections(content: str) -> list[_Section]:
    sections: list[_Section] = [_Section(None, None)]
    fence: str | None = None
    for line in content.splitlines():
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            sections[-1].lines.append(line)
            continue
        heading = None if fence is not None else _HEADING_RE.match(line)
        if heading:
            sections.append(_Section(line.strip(), heading.group(2).strip()))
        else:
            sections[-1].lines.append(line)
    return sections


def _split_words(text: str, budget: int) -> list[str]:
    pieces: list[str] = []
    current = ""
    for word in text.split():
        while len(word) > budget:  # a single word longer than the cap
            if current:
                pieces.append(current)
                current = ""
            pieces.append(word[:budget])
            word = word[budget:]
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= budget:
            current = f"{current} {word}"
        else:
            pieces.append(current)
            current = word
    if current:
        pieces.append(current)
    return pieces


def _split_body(body: str, budget: int) -> list[str]:
    """Pack paragraphs up to `budget`; split oversized ones on whitespace."""
    pieces: list[str] = []
    current = ""
    for paragraph in _PARAGRAPH_BREAK_RE.split(body):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > budget:
            if current:
                pieces.append(current)
                current = ""
            pieces.extend(_split_words(paragraph, budget))
        elif not current:
            current = paragraph
        elif len(current) + 2 + len(paragraph) <= budget:
            current = f"{current}\n\n{paragraph}"
        else:
            pieces.append(current)
            current = paragraph
    if current:
        pieces.append(current)
    return pieces


class HeadingChunker:
    """Split on ATX headings outside code fences; cap piece size in characters."""

    name = "heading"
    version = "1"

    def __init__(self, max_chunk_chars: int = 2000) -> None:
        if max_chunk_chars < MIN_CHUNK_CHARS:
            raise IngestionConfigurationError(
                f"max_chunk_chars must be at least {MIN_CHUNK_CHARS}"
            )
        self.max_chunk_chars = max_chunk_chars

    def chunk(self, document: KnowledgeDocument) -> list[Chunk]:
        sections = _parse_sections(document.content)
        has_preamble = bool("\n".join(sections[0].lines).strip())
        used: set[str] = {MAIN_SECTION_ID} if has_preamble else set()
        chunks: list[Chunk] = []

        for index, section in enumerate(sections):
            body = "\n".join(section.lines).strip()
            if index == 0:
                if not body:
                    continue
                section_id = MAIN_SECTION_ID
                prefix = ""
            else:
                assert section.heading_text is not None
                assert section.heading_line is not None
                section_id = self._unique_slug(section.heading_text, used)
                # The full heading line is kept whenever it fits in half the
                # cap; only a longer heading is truncated, so the body budget
                # below is always >= 1 (cap >= MIN_CHUNK_CHARS).
                prefix = section.heading_line[: self.max_chunk_chars // 2]
            used.add(section_id)

            budget = self.max_chunk_chars - (len(prefix) + 2 if prefix else 0)
            pieces = _split_body(body, budget) if body else []
            if prefix and not pieces:
                pieces = [""]  # a heading with no body is still one chunk
            for position, piece in enumerate(pieces):
                text = f"{prefix}\n\n{piece}" if prefix and piece else prefix or piece
                chunks.append(
                    Chunk(section_id=section_id, position=position, text=text)
                )
        if not chunks:
            chunks.append(
                Chunk(section_id=MAIN_SECTION_ID, position=0, text=document.content)
            )
        return chunks

    @staticmethod
    def _unique_slug(heading_text: str, used: set[str]) -> str:
        base = slugify(heading_text)
        slug = base
        counter = 2
        while slug in used:
            slug = f"{base}-{counter}"
            counter += 1
        return slug
