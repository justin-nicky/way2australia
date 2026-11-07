#!/usr/bin/env python3
"""graphify search guard, without the nudge for searches over docs and specs.

Configured in `.claude/settings.json` (PreToolUse on Bash|Grep) in place of a
direct `graphify hook-guard search`. The graph covers code, so a search whose
every target is a doc, spec, config, evaluation or result path gets no
"run graphify query first" reminder. Any other search (code paths, no explicit
path, or a target it cannot read) is passed to `graphify hook-guard search`
unchanged, which decides as before.

Fails open: any internal error prints nothing and exits 0.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shell import simple_commands  # noqa: E402

SEARCH_TOOLS = {"grep", "egrep", "fgrep", "rg", "ag", "ack", "find"}
# Directories and file types the graph does not help with.
NON_CODE_DIRS = (
    "docs",
    ".kiro",
    "config",
    "evaluation",
    "experiments",
    "knowledge",
    "graphify-out",
    "agent-skills",
    ".claude",
    ".agents",
    ".cursor",
)
NON_CODE_SUFFIXES = (".md", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".toml")
# Options whose value is a separate word, per tool family.
VALUE_OPTIONS = {
    "-A",
    "-B",
    "-C",
    "-m",
    "-e",
    "-f",
    "-g",
    "-t",
    "-T",
    "--glob",
    "--type",
    "--type-not",
    "--max-count",
    "--regexp",
    "--file",
    "--include",
    "--exclude",
    "--exclude-dir",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def is_non_code(target: str, cwd: Path, root: Path) -> bool:
    """True when `target` is a doc/spec/config path or a non-code file type."""
    if not target or target in ("''",):
        return False
    if target.lower().endswith(NON_CODE_SUFFIXES):
        return True
    try:
        path = (cwd / target).resolve()
        rel = path.relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return bool(rel.parts) and rel.parts[0] in NON_CODE_DIRS


def search_targets(words: list[str]) -> list[str] | None:
    """Path arguments of a search command, or None when it has no explicit path."""
    tool = words[0]
    args = words[1:]
    if tool == "git":
        if not args or args[0] != "grep":
            return []
        args = args[1:]
        tool = "grep"
    paths: list[str] = []
    if tool == "find":
        for word in args:
            if word.startswith(("-", "(", "!")):
                break
            paths.append(word)
        return paths or None
    pattern_given = any(w in ("-e", "--regexp", "-f", "--file") for w in args)
    positional: list[str] = []
    i = 0
    while i < len(args):
        word = args[i]
        if word == "--":
            positional.extend(args[i + 1 :])
            break
        if word.startswith("-"):
            i += 2 if word in VALUE_OPTIONS else 1
            continue
        positional.append(word)
        i += 1
    paths = positional if pattern_given else positional[1:]
    return paths or None


def skip_nudge(payload: dict, root: Path) -> bool:
    """True when every search in the call targets only non-code paths."""
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    command = str(tool_input.get("command") or "")
    if not command:
        # The Grep tool: path and glob fields.
        targets = [
            str(tool_input.get(k) or "") for k in ("path", "glob") if tool_input.get(k)
        ]
        return bool(targets) and all(is_non_code(t, cwd, root) for t in targets)
    searches = [
        words
        for words in simple_commands(command)
        if words[0] in SEARCH_TOOLS or words[0] == "git" and words[1:2] == ["grep"]
    ]
    if not searches:
        return False
    for words in searches:
        targets = search_targets(words)
        if not targets or not all(is_non_code(t, cwd, root) for t in targets):
            return False
    return True


def main() -> None:
    try:
        raw = sys.stdin.buffer.read()
        payload = json.loads(raw.decode("utf-8", "replace") or "{}")
        if isinstance(payload, dict) and skip_nudge(payload, _repo_root()):
            return
        result = subprocess.run(
            ["graphify", "hook-guard", "search"],
            input=raw,
            capture_output=True,
            timeout=8,
            check=False,
        )
        sys.stdout.buffer.write(result.stdout)
    except Exception:  # noqa: BLE001 - fail open
        return


if __name__ == "__main__":
    main()
    sys.exit(0)
