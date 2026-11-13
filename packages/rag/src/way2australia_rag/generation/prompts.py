"""Versioned prompt registry and rendering (Spec 012 R2)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from way2australia_rag.generation.context import EvidenceBlock
from way2australia_rag.generation.models import PromptIdentity

DEFAULT_PROMPTS_REGISTRY = "config/prompts/registry.yaml"
DEFAULT_PROMPTS_ROOT = "config/prompts"
ANSWER_V1_SHA256 = "7284d3b35cbdd4e5ff18570b770ae1d8c54153e9be3e04bdec6e8be8a6d55c11"


class PromptConfigurationError(Exception):
    """Prompt registry mismatch or unknown pair (CLI exit 2)."""


def _inside(repo_root: Path, relative: str) -> Path:
    """Resolve ``relative`` under ``repo_root``; refuse anything that escapes it."""
    root = repo_root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise PromptConfigurationError(
            f"'{Path(relative).name}' resolves outside the repository."
        )
    return path


def _read_json(path: Path, *, prompt_id: str, prompt_version: int) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PromptConfigurationError(
            f"prompt pair ({prompt_id!r}, {prompt_version}) "
            f"cannot read '{path.name}' as JSON."
        ) from error


class PromptVersion(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_id: str
    prompt_version: int
    sha256: str
    system_text: str
    output_schema: dict[str, Any]
    messages: dict[str, str]

    @property
    def identity(self) -> PromptIdentity:
        return PromptIdentity(
            prompt_id=self.prompt_id,
            prompt_version=self.prompt_version,
            sha256=self.sha256,
        )


class RenderedPrompt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    identity: PromptIdentity
    system: str
    user: str
    output_schema: dict[str, Any]


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[5]


def compute_version_sha256(prompts_root: Path, file_paths: list[str]) -> str:
    """SHA-256 over file bytes in sorted path order."""
    digest = hashlib.sha256()
    for rel in sorted(file_paths):
        digest.update((prompts_root / rel).read_bytes())
    return digest.hexdigest()


def _escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_prompt(
    version: PromptVersion,
    blocks: list[EvidenceBlock],
    query: str,
) -> RenderedPrompt:
    """Build system text and a user message: evidence blocks, then the question."""
    parts: list[str] = []
    for block in blocks:
        parts.append(
            '<evidence id="'
            + _escape_attr(block.source_id)
            + '" title="'
            + _escape_attr(block.title)
            + '" authority="'
            + _escape_attr(block.source_authority)
            + '">'
            + _escape_text(block.chunk_text)
            + "</evidence>"
        )
    parts.append("<question>" + _escape_text(query) + "</question>")
    user = "\n".join(parts)
    return RenderedPrompt(
        identity=version.identity,
        system=version.system_text,
        user=user,
        output_schema=version.output_schema,
    )


class PromptRegistry:
    """Load committed prompt versions and verify content hashes."""

    def __init__(self, repo_root: Path | None = None) -> None:
        root = (repo_root or _repo_root_from_here()).resolve()
        self._prompts_root = _inside(root, DEFAULT_PROMPTS_ROOT)
        registry_path = _inside(root, DEFAULT_PROMPTS_REGISTRY)
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise PromptConfigurationError(
                "config/prompts/registry.yaml is not a mapping."
            )
        versions_raw = raw.get("versions")
        if not isinstance(versions_raw, list):
            raise PromptConfigurationError(
                "config/prompts/registry.yaml has no versions list."
            )
        self._versions: dict[tuple[str, int], PromptVersion] = {}
        for entry in versions_raw:
            if not isinstance(entry, dict):
                raise PromptConfigurationError(
                    "config/prompts/registry.yaml has an invalid version entry."
                )
            prompt_id = entry.get("prompt_id")
            prompt_version = entry.get("prompt_version")
            expected_sha = entry.get("sha256")
            files = entry.get("files")
            if (
                not isinstance(prompt_id, str)
                or not isinstance(prompt_version, int)
                or not isinstance(expected_sha, str)
                or not isinstance(files, list)
                or not all(isinstance(x, str) for x in files)
            ):
                raise PromptConfigurationError(
                    f"prompt pair ({prompt_id!r}, {prompt_version!r}) is incomplete."
                )
            actual = compute_version_sha256(self._prompts_root, files)
            if actual != expected_sha:
                raise PromptConfigurationError(
                    f"prompt pair ({prompt_id!r}, {prompt_version}) "
                    f"sha256 mismatch (registry {expected_sha}, computed {actual})."
                )
            version_dir = self._version_dir(files)
            self._versions[(prompt_id, prompt_version)] = self._load_version_files(
                prompt_id, prompt_version, expected_sha, version_dir, files
            )

    @staticmethod
    def _version_dir(files: list[str]) -> Path:
        first = Path(files[0])
        if len(first.parts) < 2:
            raise PromptConfigurationError(
                "prompt version file paths must live under <id>/vN/."
            )
        return Path(*first.parts[:-1])

    def _load_version_files(
        self,
        prompt_id: str,
        prompt_version: int,
        sha256: str,
        version_rel: Path,
        files: list[str],
    ) -> PromptVersion:
        base = self._prompts_root / version_rel
        system_path = base / "system.md"
        schema_path = base / "output_schema.json"
        messages_path = base / "messages.yaml"
        for path in (system_path, schema_path, messages_path):
            if not path.is_file():
                raise PromptConfigurationError(
                    f"prompt pair ({prompt_id!r}, {prompt_version}) "
                    f"missing file {path.name!r}."
                )
        system_text = system_path.read_text(encoding="utf-8")
        output_schema = _read_json(
            schema_path, prompt_id=prompt_id, prompt_version=prompt_version
        )
        if not isinstance(output_schema, dict):
            raise PromptConfigurationError(
                f"prompt pair ({prompt_id!r}, {prompt_version}) "
                "output_schema.json is not an object."
            )
        messages_raw = yaml.safe_load(messages_path.read_text(encoding="utf-8"))
        if not isinstance(messages_raw, dict):
            raise PromptConfigurationError(
                f"prompt pair ({prompt_id!r}, {prompt_version}) "
                "messages.yaml is not a mapping."
            )
        messages = {str(k): str(v) for k, v in messages_raw.items()}
        return PromptVersion(
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            sha256=sha256,
            system_text=system_text,
            output_schema=output_schema,
            messages=messages,
        )

    def get(self, prompt_id: str, prompt_version: int) -> PromptVersion:
        try:
            return self._versions[(prompt_id, prompt_version)]
        except KeyError as error:
            raise PromptConfigurationError(
                f"unknown prompt pair ({prompt_id!r}, {prompt_version})."
            ) from error
