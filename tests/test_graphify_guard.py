"""Unit tests for tools/hooks/graphify_guard.py and tools/hooks/_shell.py."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "tools" / "hooks"
# Must match .claude/settings.json PreToolUse Bash|Grep hook command.
SETTINGS_HOOK_CMD = (
    'python3 "$CLAUDE_PROJECT_DIR/tools/hooks/graphify_guard.py" || true'
)


def _load(name: str):
    sys.path.insert(0, str(HOOKS))
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


shell = _load("_shell")
guard = _load("graphify_guard")


class TestSimpleCommands:
    @pytest.mark.parametrize(
        ("command", "expected"),
        [
            ("make verify", [["make", "verify"]]),
            ("A=1 time uv run --extra x make test", [["make", "test"]]),
            ("python3 -m uv run pytest -q", [["pytest", "-q"]]),
            ("/usr/bin/grep x y", [["grep", "x", "y"]]),
            ("(cd a && make verify)", [["cd", "a"], ["make", "verify"]]),
            ("echo $(make verify)", [["echo"], ["make", "verify"]]),
            ("echo `rg x`", [["echo"], ["rg", "x"]]),
            ("bash -c 'make verify'", [["make", "verify"]]),
            ("git commit -m 'make verify'", [["git", "commit", "-m", "''"]]),
            ("cat <<EOF\nmake verify\nEOF", [["cat"]]),
        ],
    )
    def test_parsing(self, command, expected):
        assert shell.simple_commands(command) == expected


class TestSkipNudge:
    @pytest.mark.parametrize(
        "command",
        [
            'grep -n "^#" docs/project/ROADMAP.md',
            "grep -rn foo .kiro/specs",
            "grep -rn foo .kiro docs",
            "rg -g '*.md' foo config",
            "grep -A3 -n x NOTES.md",
            'find docs -name "*.md"',
            "git grep foo -- docs",
        ],
    )
    def test_non_code_searches_skip(self, command):
        payload = {"tool_input": {"command": command}, "cwd": str(ROOT)}
        assert guard.skip_nudge(payload, ROOT)

    @pytest.mark.parametrize(
        "command",
        [
            "grep -rn foo packages/rag/src",
            "rg foo",
            "grep -rn foo docs packages",
            "cat x | grep foo",
            "git status",
            "grep -rn foo ''",
        ],
    )
    def test_code_or_unknown_searches_do_not_skip(self, command):
        payload = {"tool_input": {"command": command}, "cwd": str(ROOT)}
        assert not guard.skip_nudge(payload, ROOT)

    def test_grep_tool_paths(self):
        cwd = str(ROOT)
        docs = {"tool_input": {"pattern": "x", "path": "docs/project"}, "cwd": cwd}
        code = {"tool_input": {"pattern": "x", "path": "packages"}, "cwd": cwd}
        bare = {"tool_input": {"pattern": "x"}, "cwd": cwd}
        md = {"tool_input": {"pattern": "x", "glob": "*.md"}, "cwd": cwd}
        assert guard.skip_nudge(docs, ROOT)
        assert guard.skip_nudge(md, ROOT)
        assert not guard.skip_nudge(code, ROOT)
        assert not guard.skip_nudge(bare, ROOT)

    def test_path_outside_repo_does_not_skip(self, tmp_path: Path):
        payload = {"tool_input": {"command": f"grep x {tmp_path}"}, "cwd": str(ROOT)}
        assert not guard.skip_nudge(payload, ROOT)


class TestMain:
    def _run(self, payload: dict, env_path: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
        env["PATH"] = env_path
        return subprocess.run(
            SETTINGS_HOOK_CMD,
            shell=True,
            cwd=ROOT,
            env=env,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def _fake_graphify(self, tmp_path: Path) -> str:
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        exe = bin_dir / "graphify"
        exe.write_text("#!/bin/sh\ncat >/dev/null\necho NUDGE\n")
        exe.chmod(0o755)
        return f"{bin_dir}{os.pathsep}{os.environ['PATH']}"

    def test_code_search_passes_through(self, tmp_path: Path):
        path = self._fake_graphify(tmp_path)
        payload = {"tool_input": {"command": "grep x packages"}, "cwd": str(ROOT)}
        result = self._run(payload, path)
        assert result.returncode == 0
        assert result.stdout.strip() == "NUDGE"

    def test_docs_search_is_silent(self, tmp_path: Path):
        path = self._fake_graphify(tmp_path)
        payload = {"tool_input": {"command": "grep x docs"}, "cwd": str(ROOT)}
        result = self._run(payload, path)
        assert result.returncode == 0
        assert result.stdout == ""

    def test_missing_graphify_fails_open(self, tmp_path: Path):
        payload = {"tool_input": {"command": "grep x packages"}, "cwd": str(ROOT)}
        result = self._run(payload, str(tmp_path))
        assert result.returncode == 0
        assert result.stdout == ""

    def test_bad_json_fails_open(self, tmp_path: Path):
        path = self._fake_graphify(tmp_path)
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
        env["PATH"] = path
        result = subprocess.run(
            SETTINGS_HOOK_CMD,
            shell=True,
            cwd=ROOT,
            env=env,
            input="not json",
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout == ""


def test_settings_uses_wrapper():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    commands = [
        hook["command"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
    ]
    assert SETTINGS_HOOK_CMD in commands
    assert "graphify hook-guard search" not in commands
