"""Shared fixtures: an isolated repository over the security fixtures.

The security fixtures are never part of the production corpus. This builds a
throwaway repository root in `tmp_path` containing only them, with a generated
manifest, so tests load them through `LocalDocumentRepository` and the JSON
Schema exactly like real documents (design "Security fixtures").
"""

import json
import shutil
from pathlib import Path

import pytest
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_body_sha256, sha256_hex

REPO_ROOT = Path(__file__).resolve().parents[3]
SECURITY_FIXTURES = REPO_ROOT / "tests/fixtures/security"
SCHEMA = "knowledge/schemas/document_metadata.schema.json"
ISOLATED_ROOT = "security_corpus"

FIXTURE_IDS = {
    "staff_only_canary.md": "fixture_staff_canary",
    "poisoned_public_document.md": "fixture_public_poisoned",
}


@pytest.fixture
def security_repository(tmp_path: Path) -> LocalDocumentRepository:
    (tmp_path / SCHEMA).parent.mkdir(parents=True)
    shutil.copy(REPO_ROOT / SCHEMA, tmp_path / SCHEMA)
    (tmp_path / ISOLATED_ROOT).mkdir()
    records = []
    for name in sorted(FIXTURE_IDS):
        raw = (SECURITY_FIXTURES / name).read_bytes()
        (tmp_path / ISOLATED_ROOT / name).write_bytes(raw)
        metadata, body = split_frontmatter(raw.decode("utf-8"))
        records.append(
            {
                **metadata,
                "path": f"{ISOLATED_ROOT}/{name}",
                "sha256": sha256_hex(raw),
                "body_sha256": compute_body_sha256(body),
            }
        )
    manifest = tmp_path / "knowledge/manifest/document_manifest.jsonl"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )
    return LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=tmp_path, approved_roots=(ISOLATED_ROOT,))
    )
