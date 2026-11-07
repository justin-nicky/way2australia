"""Shared helpers for generation tests."""

from pathlib import Path

from way2australia_rag.generation.context import EvidenceBlock
from way2australia_rag.generation.prompts import (
    PromptRegistry,
    RenderedPrompt,
    render_prompt,
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
