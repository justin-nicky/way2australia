"""Unit tests for the workflow-reviewer transcript_metrics.py script."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "agent-skills" / "workflow-reviewer" / "scripts" / "transcript_metrics.py"
)

spec = importlib.util.spec_from_file_location("transcript_metrics", SCRIPT)
assert spec and spec.loader
tm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tm)


@pytest.mark.parametrize(
    ("command", "kinds"),
    [
        ("make verify", ["make verify"]),
        ("echo $(make verify)", ["make verify"]),
        ("echo `make lint`", ["make lint/typecheck"]),
        ("bash -c 'make verify'", ["make verify"]),
        ('sh -c "uv run pytest -q"', ["pytest"]),
        ("(cd x && make verify)", ["make verify"]),
        ("/usr/bin/make verify", ["make verify"]),
        ("git commit -m 'make verify'", ["git commit/push"]),
        ("cat <<EOF\nmake verify\nEOF", []),
    ],
)
def test_command_kinds(command, kinds):
    assert tm.command_kinds(command) == kinds


def _assistant(msg_id: str, tool_id: str, command: str) -> dict:
    return {
        "type": "assistant",
        "timestamp": "2026-11-07T10:00:00Z",
        "message": {
            "role": "assistant",
            "id": msg_id,
            "model": "m",
            "usage": {"input_tokens": 1, "output_tokens": 2},
            "content": [
                {
                    "type": "tool_use",
                    "id": tool_id,
                    "name": "Bash",
                    "input": {"command": command},
                }
            ],
        },
    }


def _user_error(tool_id: str) -> dict:
    return {
        "type": "user",
        "timestamp": "2026-11-07T10:00:01Z",
        "message": {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": tool_id, "is_error": True}
            ],
        },
    }


def test_api_request_rows_are_not_counted_twice(tmp_path: Path):
    first = _assistant("msg_1", "tu_1", "make verify")
    error = _user_error("tu_1")
    rows = [
        {"type": "user", "message": {"role": "user", "content": "brief"}},
        first,
        error,
        {"type": "api-request", "id": "r1", "params": {"model": "m"}},
        {"type": "api-request-blob", "hash": "h1", "message": first["message"]},
        {"type": "api-request-blob", "hash": "h2", "message": error["message"]},
        {"type": "api-request-shape", "shapeHash": "s"},
    ]
    path = tmp_path / "t.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows))
    metrics = tm.analyse(path)
    assert metrics["tool_calls"] == 1
    assert metrics["verify_runs"] == 1
    assert metrics["tool_errors"] == 1
    assert metrics["tokens"]["api_calls"] == 1
    assert metrics["models"] == {"m": 1}
