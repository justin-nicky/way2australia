"""Opt-in Bedrock smoke test (Spec 012 T3, D-A). Never run by agents or `make verify`.

User-owned check, run once per model to compare:

    make setup-bedrock
    W2A_RUN_BEDROCK_SMOKE=1 W2A_BEDROCK_MODEL_ID=<bedrock model id> \
        uv run pytest packages/rag/tests/generation/test_bedrock_smoke.py -s

It sends one fixed two-block prompt through the configured endpoint and region.
It passes only if the output is schema-constrained structured output that validates
against the v1 schema, cites only issued IDs, and records the model, endpoint,
region or profile and usage. The summary line carries no credentials.
"""

import os

import pytest
from way2australia_rag.generation.bedrock import BedrockGenerator
from way2australia_rag.generation.config import (
    DEFAULT_GENERATION_CONFIG,
    load_generation_config,
)

from .support import REPO_ROOT, rendered_prompt

pytestmark = pytest.mark.skipif(
    os.environ.get("W2A_RUN_BEDROCK_SMOKE") != "1",
    reason="opt-in: W2A_RUN_BEDROCK_SMOKE=1 (needs AWS credentials, bedrock extra)",
)


@pytest.fixture(autouse=True)
def _no_aws_environment() -> None:
    """The suite-wide fixture removes AWS_*; the smoke test needs the real chain."""


def test_bedrock_returns_schema_valid_cited_output() -> None:
    model_id = os.environ.get("W2A_BEDROCK_MODEL_ID")
    assert model_id, "set W2A_BEDROCK_MODEL_ID to the Bedrock model ID to test"
    config = load_generation_config(REPO_ROOT / DEFAULT_GENERATION_CONFIG)
    generator = BedrockGenerator(config.bedrock, model_id, "env")
    try:
        # `generate` validates the response against the v1 output schema.
        output = generator.generate(rendered_prompt(("S1", "S2")))
    finally:
        generator.close()
    assert set(output.citations) <= {"S1", "S2"}
    info = generator.info
    assert info.model_id == model_id
    assert info.endpoint and info.region
    assert output.usage.input_tokens is not None
    assert output.usage.output_tokens is not None
    print(
        f"bedrock smoke: pass model={info.model_id} endpoint={info.endpoint} "
        f"region={info.region} profile={info.inference_profile or '-'} "
        f"answerable={output.answerable} citations={output.citations} "
        f"tokens={output.usage.input_tokens}/{output.usage.output_tokens} "
        f"attempts={output.usage.attempts}"
    )
