"""Shared generation test fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _no_aws_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test can reach AWS by accident (T3 rule)."""
    for name in list(os.environ):
        if name.startswith(("AWS_", "W2A_BEDROCK")) or name == "W2A_RUN_BEDROCK_SMOKE":
            monkeypatch.delenv(name, raising=False)
