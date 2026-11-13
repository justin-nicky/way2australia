"""Opt-in direct Anthropic API smoke test (Spec 012 T5b, R17). Never run by agents
or `make verify`.

User-owned check, run once per model to compare (T6 gate):

    make setup-anthropic
    ANTHROPIC_API_KEY=... W2A_RUN_ANTHROPIC_SMOKE=1 \
        W2A_ANTHROPIC_MODEL_ID=claude-sonnet-5-5 \
        uv run pytest packages/rag/tests/generation/test_anthropic_smoke.py -s

It sends the same fixed two-block prompt as the Bedrock smoke test. It passes only if
the output is schema-constrained structured output that validates against the v1
schema, cites only issued IDs, and records the model, endpoint, response model and
usage. The summary line carries no key.
"""

import os

import pytest
from way2australia_rag.generation.anthropic_api import AnthropicGenerator
from way2australia_rag.generation.config import (
    DEFAULT_GENERATION_CONFIG,
    load_generation_config,
)

from .support import REPO_ROOT, rendered_prompt

pytestmark = pytest.mark.skipif(
    os.environ.get("W2A_RUN_ANTHROPIC_SMOKE") != "1",
    reason="opt-in: W2A_RUN_ANTHROPIC_SMOKE=1 (needs ANTHROPIC_API_KEY, extra)",
)


@pytest.fixture(autouse=True)
def _no_aws_environment() -> None:
    """Overrides the suite-wide fixture of the same name (conftest), which removes
    ANTHROPIC_* and the opt-in variables; the smoke test needs the real key."""


def test_anthropic_returns_schema_valid_cited_output() -> None:
    model_id = os.environ.get("W2A_ANTHROPIC_MODEL_ID")
    assert model_id, "set W2A_ANTHROPIC_MODEL_ID to the bare model ID to test"
    config = load_generation_config(REPO_ROOT / DEFAULT_GENERATION_CONFIG)
    generator = AnthropicGenerator(config.anthropic, model_id, "env")
    try:
        # `generate` validates the response against the v1 output schema and checks
        # that the response model equals the configured model.
        output = generator.generate(rendered_prompt(("S1", "S2")))
    finally:
        generator.close()
    assert set(output.citations) <= {"S1", "S2"}
    info = generator.info
    assert info.model_id == model_id
    assert info.endpoint == "api"
    assert output.response_model == model_id
    assert output.usage.input_tokens is not None
    assert output.usage.output_tokens is not None
    print(
        f"anthropic smoke: pass model={info.model_id} endpoint={info.endpoint} "
        f"response_model={output.response_model} "
        f"answerable={output.answerable} citations={output.citations} "
        f"tokens={output.usage.input_tokens}/{output.usage.output_tokens} "
        f"attempts={output.usage.attempts}"
    )
