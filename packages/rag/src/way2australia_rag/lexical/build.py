"""Build the lexical index file (Spec 007 R4).

A build is a full rebuild: written to a temporary file next to the target and
moved into place with `os.replace`. Any failure removes the temporary file and
leaves a previous target untouched. No embedder and no Qdrant are involved.
"""

import json
import os
import sqlite3
import uuid
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import build_payload
from way2australia_rag.lexical.store import (
    BM25_PARAMETERS,
    FTS5_TOKENIZER,
    SCHEMA_SQL,
    SETTINGS_KEY,
    LexicalIdentityInput,
    LexicalIndexError,
    LexicalSettings,
    source_chunk_digest,
)
from way2australia_rag.lexical.tokenizer import (
    TOKENIZER_NAME,
    TOKENIZER_VERSION,
    tokenize,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepository,
    list_eligible_documents,
)

Entry = tuple[str, Mapping[str, Any]]  # (point_id, payload as indexed)

DEFAULT_SUBDIRECTORY = ".local/lexical"


def default_lexical_dir(repo_root: Path) -> Path:
    return repo_root / DEFAULT_SUBDIRECTORY


def lexical_index_path(lexical_dir: Path, collection: str) -> Path:
    return lexical_dir / f"{collection}.sqlite"


async def production_entries(
    repository: DocumentRepository, chunker: Chunker
) -> list[Entry]:
    """The chunks, payloads and point IDs ingestion writes to Qdrant, for the
    documents eligible under `GUEST_PUBLIC_POLICY`."""
    entries: list[Entry] = []
    documents = await list_eligible_documents(repository, GUEST_PUBLIC_POLICY)
    for document in sorted(documents, key=lambda d: d.document_id):
        for chunk in chunker.chunk(document):
            payload = build_payload(document, chunk).model_dump(mode="json")
            entries.append(
                (
                    point_id(document.document_id, chunk.section_id, chunk.position),
                    payload,
                )
            )
    return entries


def _identity(point: str, payload: Mapping[str, Any]) -> tuple[str, str, int, str]:
    try:
        return (
            point,
            str(payload["document_id"]),
            int(payload["document_version"]),
            str(payload["content_hash"]),
        )
    except (KeyError, TypeError, ValueError):
        raise LexicalIndexError(
            f"payload for point '{point}' lacks document_id, document_version "
            "or content_hash."
        ) from None


def build_lexical_index(
    entries: Iterable[Entry], target: Path, identity: LexicalIdentityInput
) -> LexicalSettings:
    """Write the lexical file for `entries` atomically and return its settings."""
    materialized = list(entries)
    identities = [_identity(p, payload) for p, payload in materialized]
    settings = LexicalSettings(
        collection=identity.collection,
        index_version=identity.index_version,
        dense_identity=identity.dense_identity,
        tokenizer_name=TOKENIZER_NAME,
        tokenizer_version=TOKENIZER_VERSION,
        fts5_tokenizer=FTS5_TOKENIZER,
        bm25=dict(BM25_PARAMETERS),
        chunker_name=identity.chunker_name,
        chunker_version=identity.chunker_version,
        chunker_max_chunk_chars=identity.chunker_max_chunk_chars,
        hash_contract=identity.hash_contract,
        chunk_count=len(materialized),
        source_chunk_digest=source_chunk_digest(identities),
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        sqlite_version=sqlite3.sqlite_version,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f"{target.name}.tmp-{uuid.uuid4().hex}")
    try:
        connection = sqlite3.connect(temp)
        try:
            connection.execute("PRAGMA journal_mode = OFF")
            with connection:
                for statement in SCHEMA_SQL:
                    connection.execute(statement)
                connection.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?)",
                    (SETTINGS_KEY, settings.model_dump_json()),
                )
                for point, payload in materialized:
                    _insert(connection, point, payload)
        finally:
            connection.close()
        os.replace(temp, target)
    except BaseException as error:
        temp.unlink(missing_ok=True)
        if isinstance(error, sqlite3.Error):
            raise LexicalIndexError(
                f"building the lexical index failed ({type(error).__name__})."
            ) from None
        raise
    return settings


def _insert(
    connection: sqlite3.Connection, point: str, payload: Mapping[str, Any]
) -> None:
    _, document_id, version, content_hash = _identity(point, payload)
    owner_present = 1 if "owner_user_id" in payload else 0
    cursor = connection.execute(
        "INSERT INTO chunks (point_id, document_id, document_version, content_hash, "
        "access_scope, tenant_id, owner_user_id, owner_present, payload_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            point,
            document_id,
            version,
            content_hash,
            payload.get("access_scope"),
            payload.get("tenant_id"),
            payload.get("owner_user_id"),
            owner_present,
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
        ),
    )
    terms = " ".join(tokenize(str(payload.get("chunk_text", ""))))
    connection.execute(
        "INSERT INTO chunk_terms (rowid, terms) VALUES (?, ?)",
        (cursor.lastrowid, terms),
    )
