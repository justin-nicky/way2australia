"""Structure-aware chunker: heading paths and block packing (Spec 009 R3)."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.ingestion.chunking import (
    MAIN_SECTION_ID,
    MIN_CHUNK_TOKENS,
    Chunk,
    ChunkerIdentity,
    slugify,
    split_to_token_budget,
)
from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    IngestionError,
)
from way2australia_rag.ingestion.tokenization import ChunkTokenizer

_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_LIST_ITEM_RE = re.compile(r"^(?:[\-*\+]|\d+[.)])\s")


class DuplicateSectionError(IngestionError):
    """Two sections resolved to the same ``section_id``."""

    def __init__(self, document_id: str, section_id: str) -> None:
        self.document_id = document_id
        self.section_id = section_id
        super().__init__(
            f"duplicate_section: section_id={section_id!r} document_id={document_id!r}"
        )


@dataclass(frozen=True)
class _Section:
    path_texts: tuple[str, ...]
    heading_line: str | None
    body: str


def _section_id(path_texts: tuple[str, ...]) -> str:
    if not path_texts:
        return MAIN_SECTION_ID
    return slugify(" / ".join(path_texts))


def _parse_sections(content: str, document_id: str) -> list[_Section]:
    stack: list[tuple[int, str]] = []
    sections: list[_Section] = []
    seen_ids: set[str] = set()
    body_lines: list[str] = []
    heading_line: str | None = None
    fence: str | None = None
    saw_heading = False

    def flush(path: tuple[str, ...], heading: str | None, lines: list[str]) -> None:
        nonlocal seen_ids
        body = "\n".join(lines).strip()
        if not path and not body and saw_heading:
            return
        if not path and not body:
            return
        section_id = _section_id(path)
        if section_id in seen_ids:
            raise DuplicateSectionError(document_id, section_id)
        seen_ids.add(section_id)
        sections.append(_Section(path, heading, body))

    for line in content.splitlines():
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            body_lines.append(line)
            continue
        if fence is not None:
            body_lines.append(line)
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            path = tuple(t for _, t in stack)
            flush(path, heading_line, body_lines)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
            body_lines = []
            heading_line = line.strip()
            saw_heading = True
        else:
            body_lines.append(line)

    flush(tuple(t for _, t in stack), heading_line, body_lines)
    if not sections and content.strip():
        section_id = MAIN_SECTION_ID
        if section_id in seen_ids:
            raise DuplicateSectionError(document_id, section_id)
        sections.append(_Section((), None, content.strip()))
    return sections


def _is_list_item(line: str) -> bool:
    return bool(_LIST_ITEM_RE.match(line))


def _parse_blocks(body: str) -> list[str]:
    if not body.strip():
        return []
    blocks: list[str] = []
    lines = body.splitlines()
    index = 0
    fence: str | None = None
    while index < len(lines):
        line = lines[index]
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            block_lines = [line]
            index += 1
            if fence is None:
                fence = marker
                while index < len(lines):
                    block_lines.append(lines[index])
                    close = _FENCE_RE.match(lines[index])
                    active_fence = fence
                    if (
                        close
                        and active_fence is not None
                        and close.group(1)[0] == active_fence[0]
                    ):
                        if len(close.group(1)) >= len(active_fence):
                            fence = None
                            index += 1
                            break
                    index += 1
            blocks.append("\n".join(block_lines))
            continue
        if fence is not None:
            block_lines = [line]
            index += 1
            while index < len(lines):
                block_lines.append(lines[index])
                index += 1
            blocks.append("\n".join(block_lines))
            continue
        if not line.strip():
            index += 1
            continue
        if _is_list_item(line):
            item_lines = [line]
            index += 1
            while index < len(lines):
                nxt = lines[index]
                if not nxt.strip():
                    break
                if _is_list_item(nxt) or _HEADING_RE.match(nxt):
                    break
                if nxt.startswith(("  ", "\t")):
                    item_lines.append(nxt)
                    index += 1
                    continue
                break
            blocks.append("\n".join(item_lines))
            continue
        paragraph_lines = [line]
        index += 1
        while index < len(lines):
            nxt = lines[index]
            if not nxt.strip():
                index += 1
                break
            if _is_list_item(nxt) or _FENCE_RE.match(nxt) or _HEADING_RE.match(nxt):
                break
            paragraph_lines.append(nxt)
            index += 1
        blocks.append("\n".join(paragraph_lines))
    return blocks


def _join_blocks(blocks: list[str]) -> str:
    if not blocks:
        return ""
    parts: list[str] = [blocks[0]]
    for block in blocks[1:]:
        if _is_list_item(block) and _is_list_item(parts[-1]):
            parts[-1] = f"{parts[-1]}\n{block}"
        else:
            parts.append(block)
    return "\n\n".join(parts)


def _build_prefix(
    *,
    mode: str,
    title: str,
    path_texts: tuple[str, ...],
    heading_line: str | None,
) -> str:
    if mode == "none":
        if not path_texts:
            return ""
        assert heading_line is not None
        return heading_line
    if mode == "title_and_headings":
        if path_texts:
            return f"{title}\n{' › '.join(path_texts)}"
        return title
    raise IngestionConfigurationError(
        f"unsupported structure context_prefix {mode!r}; "
        "expected 'none' or 'title_and_headings'."
    )


class StructureChunker:
    """Split on headings and block boundaries under a token cap (``structure`` v1)."""

    name = "structure"
    version = "1"

    def __init__(
        self,
        *,
        max_chunk_tokens: int,
        context_prefix: str,
        tokenizer: ChunkTokenizer,
    ) -> None:
        if max_chunk_tokens < MIN_CHUNK_TOKENS:
            raise IngestionConfigurationError(
                f"max_chunk_tokens must be at least {MIN_CHUNK_TOKENS}."
            )
        maximum = tokenizer.identity.max_sequence_length
        if max_chunk_tokens > maximum:
            raise IngestionConfigurationError(
                f"max_chunk_tokens {max_chunk_tokens} exceeds the tokenizer maximum "
                f"{maximum}."
            )
        if context_prefix not in ("none", "title_and_headings"):
            raise IngestionConfigurationError(
                "structure context_prefix must be 'none' or 'title_and_headings'."
            )
        self._max_chunk_tokens = max_chunk_tokens
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
                "max_chunk_tokens": self._max_chunk_tokens,
            },
            tokenizer=tokenizer_ref,
        )

    def chunk(self, document: KnowledgeDocument) -> list[Chunk]:
        sections = _parse_sections(document.content, document.document_id)
        chunks: list[Chunk] = []
        count = self._tokenizer.count
        cap = self._max_chunk_tokens

        for section in sections:
            section_id = _section_id(section.path_texts)
            prefix = _build_prefix(
                mode=self._context_prefix,
                title=document.title,
                path_texts=section.path_texts,
                heading_line=section.heading_line,
            )
            if prefix and count(prefix) > cap // 2:
                raise IngestionConfigurationError(
                    f"prefix for section {section_id!r} in document "
                    f"{document.document_id!r} exceeds half of max_chunk_tokens."
                )
            blocks = _parse_blocks(section.body)
            if not blocks and prefix:
                chunks.append(Chunk(section_id=section_id, position=0, text=prefix))
                continue
            if not blocks and not prefix:
                continue

            packed_bodies = _pack_blocks(blocks, prefix, cap, count)
            for position, body in enumerate(packed_bodies):
                if prefix and body:
                    text = f"{prefix}\n\n{body}"
                elif prefix:
                    text = prefix
                else:
                    text = body
                chunks.append(
                    Chunk(section_id=section_id, position=position, text=text)
                )

        if not chunks:
            chunks.append(
                Chunk(
                    section_id=MAIN_SECTION_ID,
                    position=0,
                    text=document.content.strip() or document.content,
                )
            )
        return chunks


def _compose_chunk(prefix: str, body: str) -> str:
    if prefix and body:
        return f"{prefix}\n\n{body}"
    return prefix or body


def _pack_blocks(
    blocks: list[str],
    prefix: str,
    cap: int,
    count: Callable[[str], int],
) -> list[str]:
    def body_fits(body: str) -> bool:
        return count(_compose_chunk(prefix, body)) <= cap

    if prefix and not body_fits(""):
        raise IngestionConfigurationError(
            "prefix leaves no token budget for section body."
        )

    pieces: list[str] = []
    for block in blocks:
        if body_fits(block):
            pieces.append(block)
        else:
            pieces.extend(split_to_token_budget(block, cap, count, fits=body_fits))

    bodies: list[str] = []
    current_blocks: list[str] = []
    for piece in pieces:
        trial = _join_blocks([*current_blocks, piece]) if current_blocks else piece
        if body_fits(trial):
            current_blocks.append(piece)
        else:
            if current_blocks:
                bodies.append(_join_blocks(current_blocks))
            if body_fits(piece):
                current_blocks = [piece]
            else:
                for split in split_to_token_budget(piece, cap, count, fits=body_fits):
                    bodies.append(split)
                current_blocks = []
    if current_blocks:
        bodies.append(_join_blocks(current_blocks))
    return bodies
