#!/usr/bin/env python3
"""Verify budget: refuse a third full-suite `make verify` or `make test` per agent.

Configured once in `.claude/settings.json` (PreToolUse on Bash). Cursor Desktop
also runs those hooks; duplicate firings for the same command are deduped.

Each agent session gets VERIFY_BUDGET runs (default 2: one normal, one hub-free).
The next full-suite run is refused with advice to run targeted pytest.
`make test-unit`, `make test-integration`, targeted pytest, lint and typecheck
are never counted or blocked.

Fails open: any internal error allows the command.
User controls (state dir defaults to ~/.cache/verify-budget):
  rm counts.json          reset every counter
  touch off               disable the hook
  log.jsonl               one line per counted or refused run
"""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shell import simple_commands  # noqa: E402

STATE = Path(
    os.environ.get("VERIFY_BUDGET_STATE", str(Path.home() / ".cache" / "verify-budget"))
)


def _budget() -> int:
    return int(os.environ.get("VERIFY_BUDGET", "2"))


def _dedupe_window_s() -> float:
    return float(os.environ.get("VERIFY_BUDGET_DEDUPE_S", "3"))


MAX_AGE_S = 2 * 24 * 3600

MESSAGE = (
    "verify-budget: full-suite `make verify` or `make test` already ran {count} times "
    "in this agent session (budget {budget}). While iterating, run targeted pytest on "
    "the tests for the files you changed, e.g. "
    "`uv run pytest packages/rag/tests/<area>/test_x.py -q`. "
    "`make verify` is for once after your last edit. If this was meant to be that "
    "final check, stop and report that the budget blocked it; the reviewer runs the "
    "full suite. Do not work around this by running the verify steps one by one."
)


def repo_root() -> Path | None:
    override = os.environ.get("VERIFY_BUDGET_REPO")
    if override:
        return Path(override).resolve()
    script = Path(__file__).resolve()
    by_layout = script.parent.parent.parent
    if (by_layout / "pyproject.toml").is_file():
        return by_layout
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        root = Path(out.stdout.strip()).resolve()
        if (root / "pyproject.toml").is_file():
            return root
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _make_targets(words: list[str]) -> list[str]:
    """Targets after make/gmake, skipping -C, -f, -j and other flags."""
    targets: list[str] = []
    i = 1
    while i < len(words):
        w = words[i]
        if w in ("-C", "--directory", "-f", "--file", "--makefile") and i + 1 < len(
            words
        ):
            i += 2
            continue
        if w.startswith("-") and w not in ("-", "--"):
            i += 1
            continue
        targets.append(w)
        i += 1
    return targets


def runs_budgeted_make(command: str) -> bool:
    """True for `make verify` or full `make test` (not test-unit/integration),
    including inside `$(...)`, backticks, `bash -c '...'` and `uv run`."""
    for words in simple_commands(command):
        if len(words) < 2 or words[0] not in ("make", "gmake"):
            continue
        for target in _make_targets(words):
            if target in ("verify", "test"):
                return True
    return False


def in_repo(payload: dict, root: Path) -> bool:
    root_s = str(root)
    places = [payload.get("cwd") or ""] + list(payload.get("workspace_roots") or [])
    for raw in places:
        if not raw:
            continue
        try:
            resolved = str(Path(raw).resolve())
        except OSError:
            continue
        if resolved == root_s or resolved.startswith(root_s + os.sep):
            return True
    return False


def agent_key(host: str, payload: dict) -> str:
    if host == "claude":
        return "claude:%s:%s" % (
            payload.get("session_id"),
            payload.get("agent_id") or "main",
        )
    return "cursor:%s" % (
        payload.get("transcript_path") or payload.get("conversation_id")
    )


def _load_counts(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _save_counts(path: Path, counts: dict) -> None:
    path.write_text(json.dumps(counts, indent=1))


def count_run(key: str, command: str) -> tuple[int, bool]:
    """Record one run for `key` unless deduped; return (count, incremented)."""
    STATE.mkdir(parents=True, exist_ok=True)
    now = time.time()
    norm_cmd = " ".join(command.split())
    with open(STATE / "counts.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = STATE / "counts.json"
        counts = _load_counts(path)
        counts = {k: v for k, v in counts.items() if now - v.get("last", 0) < MAX_AGE_S}
        entry = counts.setdefault(key, {"count": 0, "last": 0.0})
        dedupe = entry.get("dedupe") or {}
        last_fp = dedupe.get("fp")
        last_ts = float(dedupe.get("ts", 0))
        fp = f"{key}\0{norm_cmd}"
        if last_fp == fp and now - last_ts < _dedupe_window_s():
            _save_counts(path, counts)
            return entry["count"], False
        entry["count"] += 1
        entry["last"] = now
        entry["dedupe"] = {"fp": fp, "ts": now}
        _save_counts(path, counts)
        return entry["count"], True


def log(record: dict) -> None:
    with open(STATE / "log.jsonl", "a") as handle:
        handle.write(json.dumps(record) + "\n")


def decide(host: str, payload: dict) -> str | None:
    """Return a refusal message, or None to allow."""
    if (STATE / "off").exists():
        return None
    root = repo_root()
    if root is None or not in_repo(payload, root):
        return None
    command = (
        payload.get("command") or (payload.get("tool_input") or {}).get("command") or ""
    )
    if not runs_budgeted_make(command):
        return None
    key = agent_key(host, payload)
    count, incremented = count_run(key, command)
    budget = _budget()
    refused = count > budget
    if incremented:
        log(
            {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "host": host,
                "key": key,
                "count": count,
                "refused": refused,
                "payload_keys": sorted(payload),
                "command": command[:200],
            }
        )
    if refused:
        shown = count - 1 if incremented else count
        return MESSAGE.format(count=shown, budget=budget)
    return None


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "claude"
    message = None
    try:
        message = decide(host, json.loads(sys.stdin.read() or "{}"))
    except Exception:  # noqa: BLE001 - fail open
        message = None
    if host == "cursor":
        if message:
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "user_message": message,
                        "agent_message": message,
                    }
                )
            )
        else:
            print(json.dumps({"permission": "allow"}))
    elif message:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": message,
                    }
                }
            )
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
