"""Shared fixtures: an isolated repository over the security fixtures.

The security fixtures are never part of the production corpus. This builds a
throwaway repository root in `tmp_path` containing only them, with a generated
manifest, so tests load them through `LocalDocumentRepository` and the JSON
Schema exactly like real documents (design "Security fixtures").
"""

import json
from pathlib import Path

import pytest
from way2australia_rag.evaluation.security_corpus import build_security_repository
from way2australia_rag.repositories import LocalDocumentRepository

REPO_ROOT = Path(__file__).resolve().parents[3]
SECURITY_FIXTURES = REPO_ROOT / "tests/fixtures/security"
SCHEMA = "knowledge/schemas/document_metadata.schema.json"

FIXTURE_IDS = {
    "staff_only_canary.md": "fixture_staff_canary",
    "poisoned_public_document.md": "fixture_public_poisoned",
}


LIVE_SUITE = "evaluation/suites/public-eval-v2.json"


LEGACY_SUITE = "evaluation/suites/public-eval-v1.json"


def live_suite_rows(
    dataset_type: str, *, active_only: bool = False, suite: str = LIVE_SUITE
) -> list[dict]:
    """Raw rows of a suite's datasets of one type (default: the live suite;
    never a literal count)."""
    manifest = json.loads((REPO_ROOT / suite).read_text(encoding="utf-8"))
    rows: list[dict] = []
    for ref in manifest["datasets"]:
        if ref["type"] != dataset_type:
            continue
        text = (REPO_ROOT / ref["path"]).read_text(encoding="utf-8")
        rows += [json.loads(x) for x in text.splitlines() if x.strip()]
    if active_only:
        rows = [r for r in rows if r.get("status", "active") == "active"]
    return rows


def manifest_document_count() -> int:
    """Number of documents in the live manifest (never a literal)."""
    manifest = REPO_ROOT / "knowledge/manifest/document_manifest.jsonl"
    return sum(
        1 for x in manifest.read_text(encoding="utf-8").splitlines() if x.strip()
    )


@pytest.fixture
def security_repository(tmp_path: Path) -> LocalDocumentRepository:
    return build_security_repository(
        SECURITY_FIXTURES, tmp_path, schema_source=REPO_ROOT / SCHEMA
    )
