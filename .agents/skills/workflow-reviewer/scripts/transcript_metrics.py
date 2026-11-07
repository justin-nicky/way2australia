#!/usr/bin/env python3
"""Extract workflow metrics from agent transcripts (Claude Code or Cursor .jsonl).

Usage:
    python3 transcript_metrics.py PATH [PATH ...] [--json OUT.json]

PATH is a transcript file or a session directory. For a session directory the
parent transcript (``<dir>.jsonl`` or ``<dir>/<dir-name>.jsonl``) and every
``subagents/*.jsonl`` inside it are read. Prints one Markdown summary per
transcript; ``--json`` also writes the full metrics.

Standard library only. Read-only: never writes next to the transcripts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

READ = {"Read", "read_file", "ReadFile", "view"}
SEARCH = {
    "Grep",
    "Glob",
    "Search",
    "grep_search",
    "codebase_search",
    "file_search",
    "LS",
    "list_dir",
}
EDIT = {
    "Edit",
    "Write",
    "MultiEdit",
    "StrReplace",
    "NotebookEdit",
    "edit_file",
    "write",
    "search_replace",
    "Delete",
}
SHELL = {"Bash", "Shell", "run_terminal_cmd", "terminal"}
AGENT = {"Task", "Agent", "CallDynamicTool"}

COMMAND_KINDS = [
    ("make verify", re.compile(r"\bmake\s+verify\b")),
    ("make test-integration", re.compile(r"\bmake\s+test-integration\b")),
    ("make test", re.compile(r"\bmake\s+test(-unit)?\b(?!-integration)")),
    ("make lint/typecheck", re.compile(r"\bmake\s+(lint|typecheck|format)\b")),
    (
        "make eval/ingest/index",
        re.compile(
            r"\bmake\s+(eval-\w+|ingest|index-lexical|retrieve|retrieval-baseline)\b"
        ),
    ),
    ("make skills", re.compile(r"\bmake\s+skills-(sync|check)\b")),
    ("pytest", re.compile(r"\bpytest\b")),
    ("ruff/pyright", re.compile(r"\b(ruff|pyright)\b")),
    ("graphify update", re.compile(r"\bgraphify\s+update\b")),
    ("graphify query/path/explain", re.compile(r"\bgraphify\s+(query|path|explain)\b")),
    ("git commit/push", re.compile(r"\bgit\s+(commit|push|merge)\b")),
    (
        "git restore/stash/reset/checkout",
        re.compile(r"\bgit\s+(restore|stash|reset|checkout)\b"),
    ),
    (
        "git (read-only)",
        re.compile(r"\bgit\s+(status|diff|log|show|branch|rev-parse|ls-files)\b"),
    ),
]
NON_MESSAGE_ROWS = {"api-request", "api-request-blob", "api-request-shape"}
CURSOR_TS = re.compile(r"<timestamp>([^<]+)</timestamp>")
# Heuristics for file reads and writes done through the shell (common in auto modes).
SHELL_WRITE = re.compile(
    r"(\bsed\s+-i\b|\btee\b|(?<![<>&\d])>{1,2}\s*[\w./~-]+\.\w+|\bapply_patch\b|\.write_text\(|open\([^)]*['\"]w)"
)
SHELL_READ = re.compile(r"^\s*(cat|sed\s+-n|head|tail|less|nl|wc)\b")


def category(name: str) -> str:
    if name in READ:
        return "read"
    if name in SEARCH:
        return "search"
    if name in EDIT:
        return "edit"
    if name in SHELL:
        return "shell"
    if name in AGENT:
        return "agent"
    return "other"


def tool_path(inp: dict) -> str | None:
    for key in ("file_path", "path", "target_file", "notebook_path"):
        value = inp.get(key)
        if isinstance(value, str):
            return value
    return None


HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n.*?\n\1\b", re.S)
QUOTED = re.compile(r"(['\"])(?:\\.|(?!\1).)*\1", re.S)
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\n|\|")
WRAPPER = re.compile(
    r"^(?:(?:[A-Za-z_][A-Za-z0-9_]*=\S*|uv\s+run(?:\s+--\S+)*|python3?\s+-m|time|exec|env|sudo)\s+)*"
)
# Spec and record files: editing them is bookkeeping, not a code change.
RECORD_FILE = re.compile(
    r"(\.kiro/specs/|task-reviews\.md$|tasks\.md$|review\.md$|requirements\.md$|design\.md$|graphify-out/)"
)


SHELL_C = re.compile(
    r"\b(?:bash|sh|zsh)\s+(?:-[a-zA-Z]+\s+)*-[a-zA-Z]*c[a-zA-Z]*\s+"
    r"(?:'([^']*)'|\"((?:\\.|[^\"\\])*)\")"
)
MAX_DEPTH = 4


def _substitutions(text: str) -> tuple[str, list[str]]:
    """Remove `$(...)` and backtick substitutions; return (rest, inner commands)."""
    inner: list[str] = []
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("$(", i) and not text.startswith("$((", i):
            depth, j = 1, i + 2
            while j < len(text) and depth:
                if text[j] == "(":
                    depth += 1
                elif text[j] == ")":
                    depth -= 1
                j += 1
            inner.append(text[i + 2 : j - 1] if depth == 0 else text[i + 2 :])
            out.append(" ")
            i = j
        elif text[i] == "`":
            j = text.find("`", i + 1)
            end = len(text) if j == -1 else j
            inner.append(text[i + 1 : end])
            out.append(" ")
            i = end + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out), inner


def executed_parts(command: str, depth: int = 0) -> list[str]:
    """The command lines actually run: heredoc bodies and quoted strings removed
    (text that merely mentions a command is not a run), with `$(...)`, backtick
    and `bash|sh|zsh -c '...'` payloads parsed as command lines of their own.
    Mirrors `tools/hooks/_shell.py`; this script stays standalone."""
    if depth > MAX_DEPTH:
        return []
    text = HEREDOC.sub("", command)
    nested = [
        m.group(1) if m.group(1) is not None else m.group(2)
        for m in SHELL_C.finditer(text)
    ]
    text = SHELL_C.sub(" ", text)
    text, substituted = _substitutions(text)
    nested += substituted
    parts = [QUOTED.sub("''", text)]
    for inner in nested:
        parts += executed_parts(inner, depth + 1)
    return parts


def executed_text(command: str) -> str:
    """All executed command lines of `command`, one per line."""
    return "\n".join(executed_parts(command))


def command_kinds(command: str) -> list[str]:
    """Kinds of the commands actually run: each segment of a command line
    (split on `&&`, `||`, `;`, `|`, newlines), including subshells and
    `bash -c` payloads, after leading environment assignments and wrappers such
    as `uv run` are stripped, must start with the command."""
    kinds = []
    for segment in SEGMENT_SPLIT.split(executed_text(command)):
        segment = WRAPPER.sub("", segment.strip(" \t(){}"))
        segment = re.sub(r"^\S*/(?=\S)", "", segment, count=1)
        for kind, pattern in COMMAND_KINDS:
            if kind not in kinds and pattern.match(segment):
                kinds.append(kind)
    return kinds


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def parse_time(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%A, %b %d, %Y, %I:%M %p", "%A, %B %d, %Y, %I:%M %p"):
        try:
            return datetime.strptime(value.split(" (")[0].strip(), fmt)
        except ValueError:
            continue
    return None


def analyse(path: Path) -> dict:
    tools: list[dict] = []
    usage_by_message: dict[str, dict] = {}
    models: Counter = Counter()
    times: list[datetime] = []
    brief = None
    errors = 0
    fmt = "unknown"

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "type" in row and fmt == "unknown":
            fmt = "claude-code"
        elif "role" in row and "type" not in row and fmt == "unknown":
            fmt = "cursor"
        message = row.get("message") if isinstance(row.get("message"), dict) else {}
        role = row.get("role") or message.get("role") or row.get("type")
        stamp = row.get("timestamp")
        if isinstance(stamp, str) and (t := parse_time(stamp)):
            times.append(t)
        if row.get("type") in NON_MESSAGE_ROWS:
            # Request bookkeeping (Claude Code `api-request*` rows) repeats
            # messages already logged as `user`/`assistant` rows.
            continue
        content = message.get("content")
        if role == "user":
            text = text_of(content)
            if brief is None and text and not row.get("isMeta"):
                brief = text
            if (m := CURSOR_TS.search(text)) and (t := parse_time(m.group(1))):
                times.append(t)
            if isinstance(content, list):
                errors += sum(
                    1
                    for b in content
                    if isinstance(b, dict)
                    and b.get("type") == "tool_result"
                    and b.get("is_error")
                )
        if role == "assistant":
            if message.get("model"):
                models[message["model"]] += 1
            if isinstance(message.get("usage"), dict) and message.get("id"):
                usage_by_message[message["id"]] = message["usage"]
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    inp = (
                        block.get("input")
                        if isinstance(block.get("input"), dict)
                        else {}
                    )
                    tools.append({"name": block.get("name", "?"), "input": inp})

    sequence = []
    reads: Counter = Counter()
    edits: Counter = Counter()
    kinds: Counter = Counter()
    for index, call in enumerate(tools):
        cat = category(call["name"])
        inp = call["input"]
        entry = {"i": index, "tool": call["name"], "cat": cat}
        if cat in ("read", "edit") and (p := tool_path(inp)):
            entry["path"] = p
            (reads if cat == "read" else edits)[p] += 1
        if cat == "shell":
            command = str(inp.get("command", ""))
            entry["command"] = command[:200]
            entry["kinds"] = command_kinds(command)
            entry["writes"] = bool(SHELL_WRITE.search(command))
            entry["reads"] = bool(SHELL_READ.search(command))
            kinds.update(entry["kinds"])
        sequence.append(entry)

    def is_code_edit(e: dict) -> bool:
        if e["cat"] == "edit":
            return not RECORD_FILE.search(e.get("path", ""))
        return bool(e.get("writes"))

    last_edit = max((e["i"] for e in sequence if is_code_edit(e)), default=-1)
    verify_runs = [e["i"] for e in sequence if "make verify" in e.get("kinds", [])]
    first_lookup = next(
        (
            (
                "graphify"
                if any(k.startswith("graphify q") for k in e.get("kinds", []))
                else e["cat"]
            )
            for e in sequence
            if e["cat"] in ("read", "search")
            or any(k.startswith("graphify q") for k in e.get("kinds", []))
        ),
        None,
    )
    tokens = None
    if usage_by_message:
        keys = (
            "input_tokens",
            "output_tokens",
            "cache_read_input_tokens",
            "cache_creation_input_tokens",
        )
        tokens = {
            k: sum(int(u.get(k) or 0) for u in usage_by_message.values()) for k in keys
        }
        tokens["total"] = sum(tokens.values())
        tokens["api_calls"] = len(usage_by_message)

    return {
        "path": str(path),
        "format": fmt,
        "models": dict(models),
        "start": min(times).isoformat() if times else None,
        "end": max(times).isoformat() if times else None,
        "wall_seconds": (max(times) - min(times)).total_seconds()
        if len(times) > 1
        else None,
        "brief_chars": len(brief) if brief else 0,
        "brief_head": (brief or "")[:300],
        "tool_calls": len(sequence),
        "by_category": dict(Counter(e["cat"] for e in sequence)),
        "by_tool": dict(Counter(e["tool"] for e in sequence)),
        "shell_reads": sum(1 for e in sequence if e.get("reads")),
        "shell_writes": sum(1 for e in sequence if e.get("writes")),
        "command_kinds": dict(kinds),
        "verify_runs": len(verify_runs),
        "verify_runs_before_last_edit": sum(1 for i in verify_runs if i < last_edit),
        "first_codebase_lookup": first_lookup,
        "repeated_reads": {p: n for p, n in reads.most_common() if n > 1},
        "distinct_files_read": len(reads),
        "edits_per_file": dict(edits.most_common(15)),
        "tool_errors": errors,
        "tokens": tokens,
        "shell_sequence": [
            {"i": e["i"], "kinds": e["kinds"], "command": e["command"]}
            for e in sequence
            if e["cat"] == "shell" and e["kinds"]
        ],
    }


def expand(arg: str) -> list[Path]:
    path = Path(arg).expanduser()
    if path.is_file():
        return [path]
    if path.is_dir():
        found = []
        for parent in (path.with_suffix(".jsonl"), path / f"{path.name}.jsonl"):
            if parent.is_file():
                found.append(parent)
        found += sorted((path / "subagents").glob("*.jsonl"))
        return found
    print(f"skip: {arg} (not found)", file=sys.stderr)
    return []


def render(m: dict) -> str:
    tok = m["tokens"]
    tok_text = (
        f"{tok['total']:,} (in {tok['input_tokens']:,}, out {tok['output_tokens']:,}, "
        f"cache read {tok['cache_read_input_tokens']:,}, cache write {tok['cache_creation_input_tokens']:,}; "
        f"{tok['api_calls']} API calls)"
        if tok
        else "n/a (not recorded in this transcript format)"
    )
    wall = f"{m['wall_seconds'] / 60:.1f} min" if m["wall_seconds"] else "n/a"
    lines = [
        f"### {Path(m['path']).stem}",
        f"- brief starts: {' '.join(m['brief_head'].split())[:160] or 'n/a'}",
        f"- format: {m['format']}; models: {m['models'] or 'n/a'}; wall time: {wall}",
        f"- brief: {m['brief_chars']} chars",
        f"- tool calls: {m['tool_calls']} {m['by_category']}; via shell: ~{m['shell_reads']} reads, ~{m['shell_writes']} writes (heuristic)",
        f"- tokens: {tok_text}",
        f"- commands: {m['command_kinds'] or 'none'}",
        f"- make verify runs: {m['verify_runs']} ({m['verify_runs_before_last_edit']} before the last code edit; spec/record edits ignored)",
        f"- first codebase lookup: {m['first_codebase_lookup']}",
        f"- files read: {m['distinct_files_read']} distinct; repeated: "
        + (
            ", ".join(
                f"{Path(p).name}×{n}" for p, n in list(m["repeated_reads"].items())[:10]
            )
            or "none"
        ),
        "- most-edited: "
        + (
            ", ".join(
                f"{Path(p).name}×{n}" for p, n in list(m["edits_per_file"].items())[:8]
            )
            or "none"
        ),
        f"- tool errors: {m['tool_errors']}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("paths", nargs="+")
    parser.add_argument(
        "--json", type=Path, help="also write full metrics as JSON to this file"
    )
    args = parser.parse_args()
    files = [p for arg in args.paths for p in expand(arg)]
    if not files:
        print("no transcripts found", file=sys.stderr)
        return 2
    results = [analyse(p) for p in files]
    print("\n\n".join(render(m) for m in results))
    if args.json:
        args.json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
