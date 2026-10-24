"""Shared fixtures: an isolated repository over the security fixtures.

The security fixtures are never part of the production corpus. This builds a
throwaway repository root in `tmp_path` containing only them, with a generated
manifest, so tests load them through `LocalDocumentRepository` and the JSON
Schema exactly like real documents (design "Security fixtures").
"""

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


@pytest.fixture
def security_repository(tmp_path: Path) -> LocalDocumentRepository:
    return build_security_repository(
        SECURITY_FIXTURES, tmp_path, schema_source=REPO_ROOT / SCHEMA
    )
