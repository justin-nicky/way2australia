"""Shared fixtures: an isolated repository over the security fixtures.

The security fixtures are never part of the production corpus. This builds a
throwaway repository root in `tmp_path` containing only them, with a generated
manifest, so tests load them through `LocalDocumentRepository` and the JSON
Schema exactly like real documents (design "Security fixtures").
"""

import json
import os
from pathlib import Path

import pytest
from way2australia_rag.evaluation.cli import DEFAULT_SUITE
from way2australia_rag.evaluation.security_corpus import build_security_repository
from way2australia_rag.ingestion.config import load_ingestion_config
from way2australia_rag.repositories import LocalDocumentRepository

REPO_ROOT = Path(__file__).resolve().parents[3]


class KeepOpenClient:
    """A view of an in-memory Qdrant client whose `close` does nothing.

    `open_retrieval(...).close()` now closes the client it opened (Spec 013 R2).
    A test that opens a stack twice over one in-memory client, or reads the
    client after a CLI run, hands out this view so the shared client survives."""

    def __init__(self, inner: object) -> None:
        self._inner = inner

    def close(self) -> None:
        return None

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)


PRODUCTION_INGESTION = REPO_ROOT / "config/ingestion.yaml"
HEADING_INGESTION_FIXTURE = (
    Path(__file__).resolve().parent / "ingestion/fixtures/heading-idx-v1-ingestion.yaml"
)


def load_production_ingestion_config():
    return load_ingestion_config(PRODUCTION_INGESTION)


_PRODUCTION_CONFIG = load_production_ingestion_config()
PRODUCTION_INDEX_VERSION = _PRODUCTION_CONFIG.index_version
PRODUCTION_COLLECTION = f"way2australia-{PRODUCTION_INDEX_VERSION}"
SECURITY_FIXTURES = REPO_ROOT / "tests/fixtures/security"
SCHEMA = "knowledge/schemas/document_metadata.schema.json"

FIXTURE_IDS = {
    "staff_only_canary.md": "fixture_staff_canary",
    "poisoned_public_document.md": "fixture_public_poisoned",
}


LIVE_SUITE = DEFAULT_SUITE  # the live suite is whatever the CLI defaults to


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


HUB_OPT_OUT_VARIABLES = ("W2A_RUN_BGE_M3_SMOKE", "W2A_RUN_RERANKER_SMOKE")


def apply_hub_offline_empty_cache(monkeypatch: pytest.MonkeyPatch) -> bool:
    """Force offline mode and an empty cache unless a smoke opt-out is set.

    Returns True when the offline setup was applied.
    """
    if any(os.environ.get(name) == "1" for name in HUB_OPT_OUT_VARIABLES):
        return False
    empty = REPO_ROOT / ".local" / "pytest-hf-empty"
    empty.mkdir(parents=True, exist_ok=True)
    hub = empty / "hub"
    hub.mkdir(exist_ok=True)
    transformers = empty / "transformers"
    transformers.mkdir(exist_ok=True)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("HF_HOME", str(empty))
    monkeypatch.setenv("HF_HUB_CACHE", str(hub))
    monkeypatch.setenv("HUGGINGFACE_HUB_CACHE", str(hub))
    monkeypatch.setenv("TRANSFORMERS_CACHE", str(transformers))
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    return True


@pytest.fixture(autouse=True)
def hub_offline_empty_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests must not depend on a warm Hugging Face cache (Spec 009 T7).

    Opt out with W2A_RUN_BGE_M3_SMOKE=1 for the BGE-M3 smoke test, or with
    W2A_RUN_RERANKER_SMOKE=1 for the reranker smoke test (Spec 011 T1).
    """
    apply_hub_offline_empty_cache(monkeypatch)


@pytest.fixture
def security_repository(tmp_path: Path) -> LocalDocumentRepository:
    return build_security_repository(
        SECURITY_FIXTURES, tmp_path, schema_source=REPO_ROOT / SCHEMA
    )
