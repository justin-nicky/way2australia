"""Unit tests for tools/hooks/verify_budget.py (verify budget hook)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "tools" / "hooks" / "verify_budget.py"
# Must match .claude/settings.json PreToolUse Bash hook command.
SETTINGS_HOOK_CMD = (
    'python3 "$CLAUDE_PROJECT_DIR/tools/hooks/verify_budget.py" claude || true'
)


def _run_settings_hook(
    *,
    cwd: Path,
    project_dir: str,
    payload: dict,
    state_dir: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = project_dir
    if state_dir is not None:
        env["VERIFY_BUDGET_STATE"] = str(state_dir)
    return subprocess.run(
        SETTINGS_HOOK_CMD,
        shell=True,
        cwd=cwd,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def _load_hook_module(monkeypatch: pytest.MonkeyPatch, state: Path, repo: Path):
    monkeypatch.setenv("VERIFY_BUDGET_STATE", str(state))
    monkeypatch.setenv("VERIFY_BUDGET_REPO", str(repo))
    monkeypatch.setenv("VERIFY_BUDGET", "2")
    spec = importlib.util.spec_from_file_location("verify_budget", HOOK_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_budget"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def hook_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state = tmp_path / "state"
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    mod = _load_hook_module(monkeypatch, state, repo)
    return mod, state, repo


class TestRunsBudgetedMake:
    def test_plain_verify(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("make verify")

    def test_make_test_counts(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("make test")

    def test_test_unit_and_integration_excluded(self, hook_env):
        mod, _, _ = hook_env
        assert not mod.runs_budgeted_make("make test-unit")
        assert not mod.runs_budgeted_make("make test-integration")

    def test_env_prefix_and_wrappers(self, hook_env):
        mod, _, _ = hook_env
        cmd = "HF_HOME=/tmp/x HF_HUB_OFFLINE=1 time make verify"
        assert mod.runs_budgeted_make(cmd)

    def test_and_chain(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("make lint && make verify")

    def test_quoted_verify_inside_and(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("cd /tmp && make verify")

    def test_heredoc_does_not_false_positive(self, hook_env):
        mod, _, _ = hook_env
        cmd = "cat <<'EOF'\nmake verify\nEOF"
        assert not mod.runs_budgeted_make(cmd)

    def test_make_c_dir_verify(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("make -C . verify")
        assert mod.runs_budgeted_make("make -C subdir verify")

    def test_gmake(self, hook_env):
        mod, _, _ = hook_env
        assert mod.runs_budgeted_make("gmake verify")

    def test_pytest_not_counted(self, hook_env):
        mod, _, _ = hook_env
        assert not mod.runs_budgeted_make("uv run pytest packages/rag/tests/foo.py")


class TestAgentAndBudget:
    def test_per_agent_counting(self, hook_env, monkeypatch):
        monkeypatch.setenv("VERIFY_BUDGET_DEDUPE_S", "0")
        mod, _, repo = hook_env
        payload = {
            "cwd": str(repo),
            "session_id": "s1",
            "agent_id": "a1",
            "command": "make verify",
        }
        assert mod.decide("claude", payload) is None
        payload["command"] = "make test"
        assert mod.decide("claude", payload) is None
        payload["command"] = "make verify"
        msg = mod.decide("claude", payload)
        assert msg is not None
        assert "budget" in msg.lower()

        payload2 = {**payload, "session_id": "s2"}
        assert mod.decide("claude", payload2) is None

    def test_dedupe_same_command(self, hook_env):
        mod, _, repo = hook_env
        payload = {
            "cwd": str(repo),
            "session_id": "s1",
            "agent_id": "main",
            "command": "make verify",
        }
        mod.decide("claude", payload)
        mod.decide("claude", payload)
        counts = json.loads((mod.STATE / "counts.json").read_text())
        key = "claude:s1:main"
        assert counts[key]["count"] == 1

    def test_off_file_allows_unlimited(self, hook_env):
        mod, state, repo = hook_env
        state.mkdir(parents=True, exist_ok=True)
        (state / "off").touch()
        payload = {"cwd": str(repo), "session_id": "s1", "command": "make verify"}
        for _ in range(5):
            assert mod.decide("claude", payload) is None

    def test_fail_open_on_decide_error(self, hook_env, monkeypatch):
        import io

        mod, _, _ = hook_env

        def boom(_host, _payload):
            raise RuntimeError("broken")

        monkeypatch.setattr(mod, "decide", boom)
        monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0


class TestRepoRoot:
    def test_layout_from_script_path(self, hook_env):
        mod, _, repo = hook_env
        assert mod.repo_root() == repo.resolve()


class TestSettingsHookCommand:
    def test_allows_ls_from_packages_rag_cwd(self, tmp_path: Path):
        state = tmp_path / "state"
        payload = {
            "cwd": str(ROOT / "packages" / "rag"),
            "session_id": "shell-test",
            "command": "ls",
        }
        result = _run_settings_hook(
            cwd=ROOT / "packages" / "rag",
            project_dir=str(ROOT),
            payload=payload,
            state_dir=state,
        )
        assert result.returncode == 0
        assert "permissionDecision" not in result.stdout
        assert "permissionDecisionReason" not in result.stdout

    def test_missing_script_fail_open_with_or_true(self, tmp_path: Path):
        payload = {"cwd": str(tmp_path), "session_id": "x", "command": "ls"}
        result = _run_settings_hook(
            cwd=tmp_path,
            project_dir=str(tmp_path / "no-hook-here"),
            payload=payload,
        )
        assert result.returncode == 0
        assert "permissionDecision" not in result.stdout
