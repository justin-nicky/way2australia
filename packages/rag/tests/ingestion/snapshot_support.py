"""Helpers for chunker output snapshot tests (Spec 009 T2)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from way2australia_core.documents import KnowledgeDocument
from way2australia_rag.ingestion.chunking import Chunk, Chunker

_COLLAPSE_WS = re.compile(r"\s+")


def collapse_whitespace(text: str) -> str:
    return _COLLAPSE_WS.sub(" ", text).strip()


def assert_structure_chunks_whitespace_fidelity(
    chunks: list[Chunk], document: KnowledgeDocument
) -> None:
    """Bodies (after the prefix block) must appear in collapsed ``content``."""
    source = collapse_whitespace(document.content)
    for chunk in chunks:
        if "\n\n" not in chunk.text:
            continue
        _, body = chunk.text.split("\n\n", 1)
        if not body.strip():
            continue
        collapsed = collapse_whitespace(body)
        assert collapsed in source, (
            f"whitespace-collapsed chunk body is not a substring of document content "
            f"for {document.document_id!r} position {chunk.position}"
        )


def assert_recursive_chunks_whitespace_fidelity(
    chunks: list[Chunk],
    document: KnowledgeDocument,
    *,
    context_prefix: str,
) -> None:
    source = collapse_whitespace(document.content)
    title = collapse_whitespace(document.title) if document.title else ""
    for chunk in chunks:
        if context_prefix == "title":
            assert "\n\n" in chunk.text, chunk.text[:80]
            prefix, body = chunk.text.split("\n\n", 1)
            assert collapse_whitespace(prefix) == title
            collapsed = collapse_whitespace(body)
        else:
            collapsed = collapse_whitespace(chunk.text)
        assert collapsed in source, (
            f"whitespace-collapsed chunk body is not a substring of document content "
            f"for {document.document_id!r} position {chunk.position}"
        )


SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"


def chunks_to_records(chunks: list[Chunk]) -> list[dict[str, Any]]:
    return [
        {"section_id": c.section_id, "position": c.position, "text": c.text}
        for c in chunks
    ]


def snapshot_for_document(
    chunker: Chunker, document: KnowledgeDocument
) -> list[dict[str, Any]]:
    return chunks_to_records(chunker.chunk(document))


def load_snapshot(name: str) -> dict[str, list[dict[str, Any]]]:
    path = SNAPSHOT_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def assert_matches_snapshot(
    chunker: Chunker,
    documents: list[KnowledgeDocument],
    snapshot_name: str,
) -> None:
    expected = load_snapshot(snapshot_name)
    for document in documents:
        key = document.document_id
        assert key in expected, f"missing {key!r} in snapshot {snapshot_name}"
        actual = snapshot_for_document(chunker, document)
        assert actual == expected[key], (
            f"snapshot mismatch for {key!r} in {snapshot_name}; "
            "bump the chunker version if intentional"
        )
