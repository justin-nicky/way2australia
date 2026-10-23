"""Loader date validation (R2) and authorization policy vs configuration (R3)."""

import asyncio
from pathlib import Path

import pytest
import yaml
from test_validate_knowledge import REPO_ROOT, build_repo, metadata, write_doc
from way2australia_core.documents import AccessScope
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    ManifestValidationError,
)
from way2australia_rag.repositories.manifest import DATE_FIELDS


def load(root: Path) -> None:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))
    asyncio.run(repository.list_documents())


def test_date_fields_cover_the_schema_date_fields() -> None:
    assert set(DATE_FIELDS) == {"last_reviewed_at", "effective_from", "effective_to"}


@pytest.mark.parametrize("field", DATE_FIELDS)
@pytest.mark.parametrize("bad", ["2026-01-01T00:00:00", "2026-02-31", "1/2/2026", ""])
def test_bad_date_fails_loading_naming_document_and_field(
    tmp_path: Path, field: str, bad: str
) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata(**{field: bad}))])

    with pytest.raises(ManifestValidationError) as excinfo:
        load(tmp_path)

    message = str(excinfo.value)
    assert f"doc_a: {field}: must be a YYYY-MM-DD date" in message
    assert str(tmp_path) not in message
    assert "/" not in message.replace("YYYY-MM-DD", "").replace("documents", "")


@pytest.mark.parametrize("field", DATE_FIELDS)
def test_valid_date_loads(tmp_path: Path, field: str) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata(**{field: "2026-02-28"}))])
    load(tmp_path)


def test_seed_corpus_still_loads() -> None:
    load(REPO_ROOT)


def test_guest_policy_agrees_with_access_policy_config() -> None:
    config = yaml.safe_load(
        (REPO_ROOT / "config/access_policy.yaml").read_text(encoding="utf-8")
    )
    guest_scopes = config["roles"]["guest"]["allowed_scopes"]

    assert guest_scopes == ["public"]
    assert {
        AccessScope(s) for s in guest_scopes
    } == GUEST_PUBLIC_POLICY.allowed_access_scopes

    named = {s for role in config["roles"].values() for s in role["allowed_scopes"]}
    members = {scope.value for scope in AccessScope}
    assert named == members
