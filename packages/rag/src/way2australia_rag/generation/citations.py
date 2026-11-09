"""Citation validation (Spec 012 R6; design "Data flow" step 6). Fails closed.

Pure function of the model output and the blocks issued for this request. Citation
metadata comes from the blocks, never from the model.
"""

import re
from collections.abc import Sequence
from typing import Final

from way2australia_rag.generation.base import GeneratorOutput
from way2australia_rag.generation.context import EvidenceBlock
from way2australia_rag.generation.models import Citation

_MARKER = re.compile(r"\[(S[1-9][0-9]*)\]")
_URL = re.compile(r"https?://", re.IGNORECASE)

# Closed set of failing rules, recorded as the response `sub_reason`.
RULES: Final = (
    "unknown_id",
    "marker_mismatch",
    "no_citation",
    "duplicate_id",
    "model_url",
)


class CitationValidationError(Exception):
    """A citation rule was broken; `rule` is one of `RULES`."""

    def __init__(self, rule: str) -> None:
        super().__init__(f"citation validation failed ({rule})")
        self.rule = rule


def validate_citations(
    output: GeneratorOutput, blocks: Sequence[EvidenceBlock]
) -> list[Citation]:
    """Return the validated citations in first-marker order, or raise.

    Rules, in order: a listed citation is required (`no_citation`); the answer
    carries no URL (`model_url`); every listed ID and marker was issued
    (`unknown_id`); no listed ID repeats (`duplicate_id`); the set of markers
    equals the set of listed IDs (`marker_mismatch`).
    """
    if not output.citations:
        raise CitationValidationError("no_citation")
    if _URL.search(output.answer):
        raise CitationValidationError("model_url")
    issued = {block.source_id: block for block in blocks}
    markers = _MARKER.findall(output.answer)
    if any(ident not in issued for ident in output.citations) or any(
        marker not in issued for marker in markers
    ):
        raise CitationValidationError("unknown_id")
    if len(set(output.citations)) != len(output.citations):
        raise CitationValidationError("duplicate_id")
    if set(markers) != set(output.citations):
        raise CitationValidationError("marker_mismatch")
    ordered: list[str] = []
    for marker in markers:
        if marker not in ordered:
            ordered.append(marker)
    return [
        Citation(
            source_id=ident,
            document_id=issued[ident].document_id,
            document_version=issued[ident].document_version,
            section_id=issued[ident].section_id,
            title=issued[ident].title,
            source_authority=issued[ident].source_authority,
            source_url=issued[ident].source_url,
        )
        for ident in ordered
    ]
