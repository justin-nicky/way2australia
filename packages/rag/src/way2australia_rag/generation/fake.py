"""Deterministic fake generator (Spec 012 R4). Drives every test and gate.

It makes no network call and imports no SDK. A `mode` selects one failure or
contract-violation hook; the default cites the first issued source.
"""

import re
from enum import StrEnum

from way2australia_rag.generation.base import (
    GeneratorInfo,
    GeneratorOutput,
    GeneratorUsage,
)
from way2australia_rag.generation.errors import (
    GeneratorDeclinedError,
    GeneratorOutputError,
    GeneratorUnavailableError,
    UnavailableReason,
)
from way2australia_rag.generation.prompts import RenderedPrompt

_ISSUED_ID = re.compile(r'<evidence id="(S[1-9][0-9]*)"')


class FakeMode(StrEnum):
    OK = "ok"
    UNKNOWN_ID = "unknown_id"  # marker and listed ID are not issued
    MARKER_MISMATCH = "marker_mismatch"  # IDs listed, no marker in the text
    DUPLICATE_ID = "duplicate_id"  # a listed ID repeats
    EMPTY_CITATIONS = "empty_citations"  # answerable true, no citations
    MODEL_URL = "model_url"  # the text carries a URL
    DECLINE = "decline"  # answerable false
    REFUSAL = "refusal"  # raises GeneratorDeclinedError
    MALFORMED_JSON = "malformed_json"  # raises GeneratorOutputError("json")
    SCHEMA_MISMATCH = "schema_mismatch"  # raises GeneratorOutputError("schema")
    MAX_TOKENS = "max_tokens"  # raises GeneratorOutputError("max_tokens")
    UNAVAILABLE = "unavailable"  # raises GeneratorUnavailableError(reason)
    NON_ELIGIBLE = "non_eligible"  # raises a plain RuntimeError


def default_fake_info() -> GeneratorInfo:
    return GeneratorInfo(
        provider="fake",
        model_id="fake",
        model_id_source="config",
        endpoint=None,
        region=None,
        inference_profile=None,
        effort=None,
        max_tokens=1024,
        request_timeout_s=20.0,
        retries=0,
        deadline_s=30.0,
        is_fake=True,
    )


def issued_ids(prompt: RenderedPrompt) -> list[str]:
    """Source IDs the rendered prompt issues (escaped text cannot add one)."""
    return _ISSUED_ID.findall(prompt.user)


class FakeGenerator:
    def __init__(
        self,
        mode: FakeMode = FakeMode.OK,
        *,
        citations: list[str] | None = None,
        unavailable: UnavailableReason = UnavailableReason.CONNECTION,
        record: bool = False,
        info: GeneratorInfo | None = None,
    ) -> None:
        self.mode = mode
        self.chosen_citations = citations
        self.unavailable = unavailable
        self.record = record
        self.info = info or default_fake_info()
        self.prompts: list[RenderedPrompt] = []
        self.calls = 0
        self.closed = False

    def generate(self, prompt: RenderedPrompt) -> GeneratorOutput:
        self.calls += 1
        if self.record:
            self.prompts.append(prompt)
        ids = issued_ids(prompt)
        first = ids[0] if ids else None
        mode = self.mode
        if mode == FakeMode.REFUSAL:
            raise GeneratorDeclinedError("fake refusal")
        if mode == FakeMode.MALFORMED_JSON:
            raise GeneratorOutputError("json")
        if mode == FakeMode.SCHEMA_MISMATCH:
            raise GeneratorOutputError("schema")
        if mode == FakeMode.MAX_TOKENS:
            raise GeneratorOutputError("max_tokens")
        if mode == FakeMode.UNAVAILABLE:
            raise GeneratorUnavailableError(self.unavailable)
        if mode == FakeMode.NON_ELIGIBLE:
            raise RuntimeError("fake non-eligible error")
        if mode == FakeMode.DECLINE:
            return self._output(False, "", [], "end_turn", prompt)
        cited = self.chosen_citations
        if cited is None:
            cited = [first] if first else []
        if mode == FakeMode.UNKNOWN_ID:
            return self._output(True, "Fake answer. [S99]", ["S99"], "end_turn", prompt)
        if mode == FakeMode.MARKER_MISMATCH:
            return self._output(
                True, "Fake answer.", cited or ["S1"], "end_turn", prompt
            )
        if mode == FakeMode.DUPLICATE_ID:
            ident = first or "S1"
            return self._output(
                True, f"Fake answer. [{ident}]", [ident, ident], "end_turn", prompt
            )
        if mode == FakeMode.EMPTY_CITATIONS:
            return self._output(
                True, f"Fake answer. [{first or 'S1'}]", [], "end_turn", prompt
            )
        if mode == FakeMode.MODEL_URL:
            ident = first or "S1"
            return self._output(
                True,
                f"See https://example.test/page [{ident}]",
                [ident],
                "end_turn",
                prompt,
            )
        if not cited:
            return self._output(False, "", [], "end_turn", prompt)
        markers = "".join(f"[{c}]" for c in cited)
        return self._output(
            True, f"Fake answer. {markers}", list(cited), "end_turn", prompt
        )

    def _output(
        self,
        answerable: bool,
        answer: str,
        citations: list[str],
        stop_reason: str,
        prompt: RenderedPrompt,
    ) -> GeneratorOutput:
        return GeneratorOutput(
            answerable=answerable,
            answer=answer,
            citations=citations,
            usage=GeneratorUsage(
                input_tokens=(len(prompt.system) + len(prompt.user)) // 4,
                output_tokens=len(answer) // 4,
                attempts=1,
            ),
            stop_reason=stop_reason,
        )

    def close(self) -> None:
        self.closed = True
