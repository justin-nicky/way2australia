"""SQLite FTS5 lexical store: settings, schema, read-only open, bind and search
(Spec 007 R4, R5; Spec 009 R6).
"""

import hashlib
import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, NamedTuple
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, ValidationError

from way2australia_rag.ingestion.chunking import ChunkerIdentity
from way2australia_rag.lexical.tokenizer import LexicalTokenizer, tokenizer_named
from way2australia_rag.retrieval.errors import IndexBindingError, RetrievalError
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex

SETTINGS_SCHEMA_VERSION = "1.2"
_LEGACY_SETTINGS_SCHEMA_11 = "1.1"
_LEGACY_SETTINGS_SCHEMA_VERSION = "1.0"
SETTINGS_KIND = "w2a_lexical_index"
SETTINGS_KEY = "lexical_settings"
FTS5_TOKENIZER = "ascii"
BM25_PARAMETERS = {"k1": 1.2, "b": 0.75}

REBUILD_ADVICE = (
    "Rebuild the lexical index with `make index-lexical` for this collection "
    "and index_version."
)

SCHEMA_SQL = (
    "CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE chunks (
      rowid INTEGER PRIMARY KEY,
      point_id TEXT NOT NULL UNIQUE,
      document_id TEXT NOT NULL,
      document_version INTEGER NOT NULL,
      content_hash TEXT NOT NULL,
      access_scope TEXT,
      tenant_id TEXT,
      owner_user_id TEXT,
      owner_present INTEGER NOT NULL,
      lote_languages TEXT NOT NULL,
      payload_json TEXT NOT NULL)""",
    "CREATE VIRTUAL TABLE chunk_terms "
    f"USING fts5(terms, tokenize = '{FTS5_TOKENIZER}')",
)

SEARCH_SQL = (
    "SELECT c.point_id, c.payload_json, bm25(chunk_terms) AS s "
    "FROM chunk_terms JOIN chunks c ON c.rowid = chunk_terms.rowid "
    "WHERE chunk_terms MATCH ? AND {where} "
    "ORDER BY s ASC, c.point_id ASC LIMIT ?"
)


class LexicalIndexError(RetrievalError):
    """The lexical index cannot be built."""


class LexicalIndexBindingError(IndexBindingError):
    """The lexical index cannot be opened or bound. Messages carry field names
    and identity values only, never chunk text or absolute paths."""


class DenseIdentity(BaseModel):
    """The dense identity a lexical file is built for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    collection: str
    index_version: str
    embedder_model_id: str
    embedder_revision: str


class LexicalIdentityInput(BaseModel):
    """Everything `build_lexical_index` needs to record besides the entries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    collection: str
    index_version: str
    dense_identity: DenseIdentity
    chunker: ChunkerIdentity
    hash_contract: str


class LexicalSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.1", "1.2"] = SETTINGS_SCHEMA_VERSION
    kind: Literal["w2a_lexical_index"] = SETTINGS_KIND
    collection: str
    index_version: str
    dense_identity: DenseIdentity
    tokenizer_name: str
    tokenizer_version: str
    fts5_tokenizer: str
    bm25: dict[str, float]
    chunker_name: str
    chunker_version: str
    chunker_params: dict[str, str | int | bool]
    chunker_tokenizer: str | None
    hash_contract: str
    chunk_count: int
    source_chunk_digest: str
    created_at: str
    sqlite_version: str

    def chunker_identity(self) -> ChunkerIdentity:
        return ChunkerIdentity(
            name=self.chunker_name,
            version=self.chunker_version,
            params=dict(sorted(self.chunker_params.items())),
            tokenizer=self.chunker_tokenizer,
        )


ChunkIdentity = tuple[str, str, int, str]


class ChunkSetDifference(NamedTuple):
    only_expected: int
    only_mine: int
    changed: int


def chunk_set_difference(
    expected: Iterable[ChunkIdentity], mine: Iterable[ChunkIdentity]
) -> ChunkSetDifference:
    expected_set = set(expected)
    mine_set = set(mine)
    only_expected = {i[0] for i in expected_set} - {i[0] for i in mine_set}
    only_mine = {i[0] for i in mine_set} - {i[0] for i in expected_set}
    by_id = {i[0]: i for i in expected_set}
    changed = sum(1 for i in mine_set if i[0] in by_id and by_id[i[0]] != i)
    return ChunkSetDifference(len(only_expected), len(only_mine), changed)


def source_chunk_digest(identities: Iterable[ChunkIdentity]) -> str:
    lines = sorted(f"{p}\t{d}\t{v}\t{h}\n" for p, d, v, h in identities)
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def _chunker_identity_differences(
    recorded: ChunkerIdentity, wanted: ChunkerIdentity
) -> str:
    triples: list[tuple[str, Any, Any]] = [
        ("chunker_name", recorded.name, wanted.name),
        ("chunker_version", recorded.version, wanted.version),
        ("chunker_params", recorded.params, wanted.params),
        ("chunker_tokenizer", recorded.tokenizer, wanted.tokenizer),
    ]
    return _differences(triples)


class LexicalRow(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    point_id: str
    payload_json: str
    score: float


def _read_only_connection(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path))}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.execute("PRAGMA query_only = ON")
    return connection


class LexicalIndex:
    """A read-only view of one lexical file."""

    def __init__(
        self, connection: sqlite3.Connection, settings: LexicalSettings, label: str
    ) -> None:
        self._connection = connection
        self.settings = settings
        self.label = label

    @classmethod
    def open(cls, path: Path, collection: str, index_version: str) -> "LexicalIndex":
        label = path.name
        if not path.is_file():
            raise LexicalIndexBindingError(
                f"lexical index '{label}' does not exist. {REBUILD_ADVICE}"
            )
        try:
            connection = _read_only_connection(path)
        except sqlite3.Error:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' cannot be opened. {REBUILD_ADVICE}"
            ) from None
        try:
            settings = cls._read_settings(connection, label)
            cls._check(settings, label, collection, index_version)
        except BaseException:
            connection.close()
            raise
        return cls(connection, settings, label)

    @staticmethod
    def _read_settings(connection: sqlite3.Connection, label: str) -> LexicalSettings:
        try:
            row = connection.execute(
                "SELECT value FROM settings WHERE key = ?", (SETTINGS_KEY,)
            ).fetchone()
        except sqlite3.Error:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' has no readable settings table. "
                f"{REBUILD_ADVICE}"
            ) from None
        if row is None:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' has no recorded settings. {REBUILD_ADVICE}"
            )
        try:
            raw = json.loads(row[0])
        except (TypeError, ValueError):
            raw = None
        if not isinstance(raw, dict):
            raise LexicalIndexBindingError(
                f"lexical index '{label}' has malformed settings. {REBUILD_ADVICE}"
            )
        if raw.get("schema_version") == _LEGACY_SETTINGS_SCHEMA_VERSION:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' was built with lexical settings 1.0; "
                "run `make index-lexical` (with the same `QDRANT_COLLECTION_BASE`) "
                f"to rebuild it. {REBUILD_ADVICE}"
            )
        if raw.get("kind") != SETTINGS_KIND:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' settings kind: recorded "
                f"{str(raw.get('kind'))[:40]!r}, wanted {SETTINGS_KIND!r}. "
                f"{REBUILD_ADVICE}"
            )
        try:
            return LexicalSettings.model_validate(raw)
        except ValidationError as error:
            fields = sorted(
                {".".join(str(p) for p in e["loc"]) for e in error.errors()}
            )
            raise LexicalIndexBindingError(
                f"lexical index '{label}' has malformed settings (invalid "
                f"fields: {', '.join(fields)}). {REBUILD_ADVICE}"
            ) from None

    @staticmethod
    def _check(
        settings: LexicalSettings, label: str, collection: str, index_version: str
    ) -> None:
        try:
            tokenizer_named(settings.tokenizer_name, settings.tokenizer_version)
        except LexicalIndexBindingError as error:
            raise LexicalIndexBindingError(f"lexical index '{label}' {error}") from None
        differences = _differences(
            (
                ("collection", settings.collection, collection),
                ("index_version", settings.index_version, index_version),
            )
        )
        if differences:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' does not match ({differences}). "
                f"{REBUILD_ADVICE}"
            )

    @property
    def tokenizer(self) -> LexicalTokenizer:
        return tokenizer_named(
            self.settings.tokenizer_name, self.settings.tokenizer_version
        )

    def bind_to(self, dense: DenseIndex) -> None:
        s = self.settings
        d = dense.settings
        differences = _differences(
            (
                (
                    "dense_identity.collection",
                    s.dense_identity.collection,
                    dense.collection,
                ),
                (
                    "dense_identity.index_version",
                    s.dense_identity.index_version,
                    d.index_version,
                ),
                (
                    "dense_identity.embedder_model_id",
                    s.dense_identity.embedder_model_id,
                    d.embedder_model_id,
                ),
                (
                    "dense_identity.embedder_revision",
                    s.dense_identity.embedder_revision,
                    d.embedder_revision,
                ),
                ("hash_contract", s.hash_contract, d.hash_contract),
            )
        )
        chunker_diff = _chunker_identity_differences(
            s.chunker_identity(), d.chunker_identity()
        )
        if chunker_diff:
            differences = (
                f"{differences}; {chunker_diff}" if differences else chunker_diff
            )
        if differences:
            raise LexicalIndexBindingError(
                f"lexical index '{self.label}' does not match the dense index "
                f"({differences}). {REBUILD_ADVICE}"
            )
        qdrant = set(dense.chunk_identities())
        if source_chunk_digest(qdrant) == s.source_chunk_digest:
            return
        diff = chunk_set_difference(qdrant, self.chunk_identities())
        raise LexicalIndexBindingError(
            f"lexical index '{self.label}' has a different chunk set than the "
            f"dense index (points only in the dense index: {diff.only_expected}; "
            f"only in the lexical index: {diff.only_mine}; with different "
            f"document_version or content_hash: {diff.changed}). {REBUILD_ADVICE}"
        )

    def check_identity(
        self,
        expected: IndexIdentity,
        chunker_identity: ChunkerIdentity,
        hash_contract: str,
    ) -> None:
        s = self.settings
        differences = _differences(
            (
                (
                    "dense_identity.collection",
                    s.dense_identity.collection,
                    expected.collection,
                ),
                (
                    "dense_identity.index_version",
                    s.dense_identity.index_version,
                    expected.index_version,
                ),
                (
                    "dense_identity.embedder_model_id",
                    s.dense_identity.embedder_model_id,
                    expected.embedder_model_id,
                ),
                (
                    "dense_identity.embedder_revision",
                    s.dense_identity.embedder_revision,
                    expected.embedder_revision,
                ),
                ("hash_contract", s.hash_contract, hash_contract),
            )
        )
        chunker_diff = _chunker_identity_differences(
            s.chunker_identity(), chunker_identity
        )
        if chunker_diff:
            differences = (
                f"{differences}; {chunker_diff}" if differences else chunker_diff
            )
        if differences:
            raise LexicalIndexBindingError(
                f"lexical index '{self.label}' does not match the configured "
                f"index ({differences}). {REBUILD_ADVICE}"
            )

    def document_count(self, where_sql: str, params: tuple[Any, ...]) -> int:
        row = self._connection.execute(
            f"SELECT COUNT(DISTINCT c.document_id) FROM chunks c WHERE {where_sql}",  # noqa: S608
            params,
        ).fetchone()
        return int(row[0])

    def document_versions(self) -> set[tuple[str, int, str]]:
        rows = self._connection.execute(
            "SELECT DISTINCT document_id, document_version, content_hash FROM chunks"
        ).fetchall()
        return {(str(a), int(b), str(c)) for a, b, c in rows}

    def chunks_per_document(self) -> dict[str, int]:
        rows = self._connection.execute(
            "SELECT document_id, COUNT(*) FROM chunks GROUP BY document_id"
        ).fetchall()
        return {str(document_id): int(count) for document_id, count in rows}

    def chunk_identities(self) -> set[ChunkIdentity]:
        rows = self._connection.execute(
            "SELECT point_id, document_id, document_version, content_hash FROM chunks"
        ).fetchall()
        return {(str(a), str(b), int(c), str(e)) for a, b, c, e in rows}

    def search(
        self,
        match_expression: str,
        where_sql: str,
        params: tuple[Any, ...],
        limit: int,
    ) -> list[LexicalRow]:
        sql = SEARCH_SQL.format(where=where_sql)
        rows = self._connection.execute(
            sql, (match_expression, *params, limit)
        ).fetchall()
        return [
            LexicalRow(point_id=str(p), payload_json=str(j), score=float(s))
            for p, j, s in rows
        ]

    @property
    def has_lote_column(self) -> bool:
        return self.settings.schema_version == SETTINGS_SCHEMA_VERSION

    def close(self) -> None:
        self._connection.close()


def _differences(triples: Iterable[tuple[str, Any, Any]]) -> str:
    return "; ".join(
        f"{name}: recorded {have!r}, wanted {want!r}"
        for name, have, want in triples
        if have != want
    )
