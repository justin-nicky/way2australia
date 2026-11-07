"""Shared shell-command parsing for the PreToolUse hooks in this directory.

`simple_commands(command)` returns the simple commands a shell line actually
runs, as word lists, so a hook can match the executable at command position:

- heredoc bodies and quoted text are dropped (a commit message that mentions
  `make verify` is not a run);
- command substitutions (`$(...)`, backticks) and `bash|sh|zsh -c '...'`
  payloads are parsed as commands of their own;
- lines are split on `&&`, `||`, `;`, `|`, `&` and newlines; leading `(`/`{`
  and trailing `)`/`}` are dropped;
- leading environment assignments and wrappers (`time`, `env`, `command`,
  `nice`, `exec`, `caffeinate`, `sudo`, `xargs`, `uv run [options]`,
  `python3 -m uv run`) are stripped;
- the executable is reduced to its base name (`/usr/bin/make` -> `make`).

Standard library only; hooks load it from their own directory.
"""

from __future__ import annotations

import re

HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", re.S)
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
SHELL_C = re.compile(
    r"\b(?:bash|sh|zsh)\s+(?:-[a-zA-Z]+\s+)*-[a-zA-Z]*c[a-zA-Z]*\s+"
    r"(?:'([^']*)'|\"((?:\\.|[^\"\\])*)\")"
)
SEPARATOR = re.compile(r"&&|\|\||[;|&\n]")
ENV_ASSIGN = re.compile(r"^\w+=\S*$")
WRAPPERS = {
    "time",
    "env",
    "command",
    "nice",
    "exec",
    "caffeinate",
    "sudo",
    "xargs",
}
# `uv run` options that take a separate value.
UV_RUN_VALUE_OPTIONS = {
    "--with",
    "--with-requirements",
    "--extra",
    "--group",
    "--package",
    "--project",
    "--directory",
    "--python",
    "-p",
    "--env-file",
    "--index",
}
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


def _strip_wrappers(words: list[str]) -> list[str]:
    while words:
        head = words[0]
        if ENV_ASSIGN.match(head) or head in WRAPPERS:
            words = words[1:]
        elif head == "python3" or head == "python":
            if words[1:3] == ["-m", "uv"]:
                words = ["uv", *words[3:]]
            else:
                return words
        elif head == "uv" and words[1:2] == ["run"]:
            rest = words[2:]
            while rest and rest[0].startswith("-"):
                flag = rest[0]
                rest = rest[1:]
                if flag in UV_RUN_VALUE_OPTIONS and rest:
                    rest = rest[1:]
            words = rest
        else:
            return words
    return words


def simple_commands(command: str, _depth: int = 0) -> list[list[str]]:
    """The simple commands `command` runs, as word lists (see module docstring)."""
    if _depth > MAX_DEPTH:
        return []
    text = HEREDOC.sub("", command)
    nested: list[str] = []
    for match in SHELL_C.finditer(text):
        nested.append(match.group(1) if match.group(1) is not None else match.group(2))
    text = SHELL_C.sub(" ", text)
    text, substituted = _substitutions(text)
    nested.extend(substituted)
    text = QUOTED.sub("''", text)
    commands: list[list[str]] = []
    for segment in SEPARATOR.split(text):
        words = segment.replace("(", " ").replace(")", " ").split()
        words = [w for w in words if w not in ("{", "}")]
        words = _strip_wrappers(words)
        if words:
            words[0] = words[0].rsplit("/", 1)[-1]
            commands.append(words)
    for inner in nested:
        commands.extend(simple_commands(inner, _depth + 1))
    return commands
