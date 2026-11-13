"""Shared generation test fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _no_aws_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test can reach AWS or the Anthropic API by accident (T3 rule, T5b)."""
    for name in list(os.environ):
        if (
            name.startswith(("AWS_", "W2A_BEDROCK", "ANTHROPIC_", "W2A_ANTHROPIC"))
            or name == "W2A_RUN_BEDROCK_SMOKE"
            or name == "W2A_RUN_ANTHROPIC_SMOKE"
        ):
            monkeypatch.delenv(name, raising=False)
