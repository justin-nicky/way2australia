"""Seed corpus and security-fixture boundary checks (R11, Spec 002 T8)."""

import asyncio
import json
from pathlib import Path

import pytest
from conftest import FIXTURE_IDS, REPO_ROOT, SECURITY_FIXTURES
from way2australia_rag.repositories import (
    DEFAULT_APPROVED_ROOTS,
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.repositories.local import under_root

MANIFEST = REPO_ROOT / "knowledge/manifest/document_manifest.jsonl"

pytestmark = pytest.mark.integration


def manifest_records() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def seed_documents() -> list:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    return asyncio.run(repository.list_documents())


def test_seed_ids_and_versions_are_unique() -> None:
    documents = seed_documents()

    ids = [d.document_id for d in documents]
    pairs = [(d.document_id, d.document_version) for d in documents]
    assert len(set(ids)) == len(ids)
    assert len(set(pairs)) == len(pairs)
    records = manifest_records()
    assert len({r["document_id"] for r in records}) == len(records)


def test_security_fixtures_are_not_in_the_production_corpus() -> None:
    fixture_ids = set(FIXTURE_IDS.values())
    listed = {r["document_id"] for r in manifest_records()}
    paths = [str(r["path"]) for r in manifest_records()]

    assert SECURITY_FIXTURES.is_dir()
    assert listed.isdisjoint(fixture_ids)
    assert not any(p.startswith("tests/") for p in paths)
    fixtures_dir = SECURITY_FIXTURES.relative_to(REPO_ROOT).as_posix()
    assert not under_root(fixtures_dir, DEFAULT_APPROVED_ROOTS)
    assert {d.document_id for d in seed_documents()}.isdisjoint(fixture_ids)
    eligible = asyncio.run(
        list_eligible_documents(
            LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT)),
            GUEST_PUBLIC_POLICY,
        )
    )
    assert {d.document_id for d in eligible}.isdisjoint(fixture_ids)


def test_no_fixture_file_sits_under_a_production_root() -> None:
    for root in DEFAULT_APPROVED_ROOTS:
        for path in (REPO_ROOT / root).rglob("*.md"):
            assert path.name not in FIXTURE_IDS, Path(path).name
