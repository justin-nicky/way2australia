"""Shared helpers for the lexical tests."""

import asyncio
import json
import sqlite3
import warnings
from pathlib import Path
from typing import Any

from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.store import QdrantIndexStore
from way2australia_rag.lexical.build import build_lexical_index, production_entries
from way2australia_rag.lexical.store import (
    DenseIdentity,
    LexicalIdentityInput,
    LexicalIndex,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.index import DenseIndex

BASE = "w2a-lex"
VERSION = "v1"
COLLECTION = f"{BASE}-{VERSION}"


def repository() -> LocalDocumentRepository:
    return LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))


def identity(**over: Any) -> LexicalIdentityInput:
    embedder = FakeEmbedder().info
    chunker = HeadingChunker()
    values: dict[str, Any] = {
        "collection": COLLECTION,
        "index_version": VERSION,
        "dense_identity": DenseIdentity(
            collection=COLLECTION,
            index_version=VERSION,
            embedder_model_id=embedder.model_id,
            embedder_revision=embedder.revision,
        ),
        "chunker_name": chunker.name,
        "chunker_version": chunker.version,
        "chunker_max_chunk_chars": chunker.max_chunk_chars,
        "hash_contract": HASH_CONTRACT,
    }
    values.update(over)
    return LexicalIdentityInput(**values)


def payload(
    document_id: str, text: str, *, scope: str = "public", **over: Any
) -> dict[str, Any]:
    values: dict[str, Any] = {
        "tenant_id": "way2australia",
        "access_scope": scope,
        "owner_user_id": None,
        "chunk_text": text,
        "content_hash": f"hash-{document_id}",
        "document_id": document_id,
        "document_version": 1,
    }
    values.update(over)
    return values


def synthetic_entries() -> list[tuple[str, dict[str, Any]]]:
    return [
        ("p1", payload("doc_a", "Coaching sessions are live")),
        ("p2", payload("doc_b", "ഉള്ളത് ഉപകരണങ്ങൾ ചെയ്യാൻ")),
        ("p3", payload("doc_c", "mock tests and materials")),
    ]


def ingest_dense(client: QdrantClient | None = None) -> tuple[QdrantClient, DenseIndex]:
    """Ingest the seed corpus with the fake embedder into in-memory Qdrant."""
    client = client or QdrantClient(":memory:")
    embedder = FakeEmbedder()
    service = IngestionService(
        repository(),
        GUEST_PUBLIC_POLICY,
        HeadingChunker(),
        embedder,
        QdrantIndexStore(client, BASE, VERSION),
        batch_size=8,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        report = asyncio.run(service.run())
    assert not report.failures
    return client, DenseIndex.open(client, BASE, VERSION, embedder.info)


def build_production(target: Path, **over: Any) -> None:
    entries = asyncio.run(production_entries(repository(), HeadingChunker()))
    build_lexical_index(entries, target, identity(**over))


def open_lexical(path: Path) -> LexicalIndex:
    return LexicalIndex.open(path, COLLECTION, VERSION)


def rewrite_settings(path: Path, **changes: Any) -> None:
    """Edit the recorded settings JSON of a built file (test tampering)."""
    connection = sqlite3.connect(path)
    try:
        with connection:
            (raw,) = connection.execute(
                "SELECT value FROM settings WHERE key = 'lexical_settings'"
            ).fetchone()
            settings = json.loads(raw)
            for key, value in changes.items():
                target = settings
                *parents, last = key.split(".")
                for part in parents:
                    target = target[part]
                target[last] = value
            connection.execute(
                "UPDATE settings SET value = ? WHERE key = 'lexical_settings'",
                (json.dumps(settings),),
            )
    finally:
        connection.close()
