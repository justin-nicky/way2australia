"""SQLite FTS5 lexical store: settings, schema, read-only open, bind and search
(Spec 007 R4, R5).

The file is a derived artifact. Chunk text is tokenized with `lexical-v1` and
stored as space-joined tokens in an FTS5 table that uses the `ascii` tokenizer
(it treats every non-ASCII character as a token character, so Malayalam words
stay whole). Opening is read-only and never writes to the file.
"""

import hashlib
import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, NamedTuple
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, ValidationError

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.lexical.tokenizer import TOKENIZER_NAME, TOKENIZER_VERSION
from way2australia_rag.retrieval.errors import IndexBindingError, RetrievalError
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex

SETTINGS_SCHEMA_VERSION = "1.0"
SETTINGS_KIND = "w2a_lexical_index"
SETTINGS_KEY = "lexical_settings"
FTS5_TOKENIZER = "ascii"
BM25_PARAMETERS = {"k1": 1.2, "b": 0.75}  # FTS5's fixed values, recorded

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
    chunker_name: str
    chunker_version: str
    chunker_max_chunk_chars: int
    hash_contract: str


class LexicalSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"] = SETTINGS_SCHEMA_VERSION
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
    chunker_max_chunk_chars: int
    hash_contract: str
    chunk_count: int
    source_chunk_digest: str
    created_at: str
    sqlite_version: str


ChunkIdentity = tuple[str, str, int, str]  # point_id, document_id, version, hash


class ChunkSetDifference(NamedTuple):
    """Counts only. `only_expected`: points the reference has and the file lacks;
    `only_mine`: the reverse; `changed`: same point, other version or hash."""

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
    """SHA-256 of the sorted lines `point_id\\tdocument_id\\tversion\\thash\\n`."""
    lines = sorted(f"{p}\t{d}\t{v}\t{h}\n" for p, d, v, h in identities)
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


class LexicalRow(BaseModel):
    """One search row. `score` is SQLite's raw `bm25()` (lower is better)."""

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
        for field, wanted in (
            ("schema_version", SETTINGS_SCHEMA_VERSION),
            ("kind", SETTINGS_KIND),
        ):
            if raw.get(field) != wanted:
                raise LexicalIndexBindingError(
                    f"lexical index '{label}' settings {field}: recorded "
                    f"{str(raw.get(field))[:40]!r}, wanted {wanted!r}. "
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
        differences = _differences(
            (
                ("tokenizer_name", settings.tokenizer_name, TOKENIZER_NAME),
                ("tokenizer_version", settings.tokenizer_version, TOKENIZER_VERSION),
                ("collection", settings.collection, collection),
                ("index_version", settings.index_version, index_version),
            )
        )
        if differences:
            raise LexicalIndexBindingError(
                f"lexical index '{label}' does not match ({differences}). "
                f"{REBUILD_ADVICE}"
            )

    def bind_to(self, dense: DenseIndex) -> None:
        """Refuse unless this file belongs to `dense` (identity, chunker, chunk set)."""
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
                ("chunker_name", s.chunker_name, d.chunker_name),
                ("chunker_version", s.chunker_version, d.chunker_version),
                (
                    "chunker_max_chunk_chars",
                    s.chunker_max_chunk_chars,
                    d.chunker_max_chunk_chars,
                ),
                ("hash_contract", s.hash_contract, d.hash_contract),
            )
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
        self, expected: IndexIdentity, chunker: Chunker, hash_contract: str
    ) -> None:
        """Refuse unless this file was built for `expected`, `chunker` and
        `hash_contract`. Names fields and identity values only."""
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
                ("chunker_name", s.chunker_name, chunker.name),
                ("chunker_version", s.chunker_version, chunker.version),
                (
                    "chunker_max_chunk_chars",
                    s.chunker_max_chunk_chars,
                    chunker.max_chunk_chars,
                ),
                ("hash_contract", s.hash_contract, hash_contract),
            )
        )
        if differences:
            raise LexicalIndexBindingError(
                f"lexical index '{self.label}' does not match the configured "
                f"index ({differences}). {REBUILD_ADVICE}"
            )

    def document_count(self, where_sql: str, params: tuple[Any, ...]) -> int:
        """Distinct documents under the access clause (`where_sql` comes from
        the access-clause builder and refers to the table as `c`)."""
        row = self._connection.execute(
            f"SELECT COUNT(DISTINCT c.document_id) FROM chunks c WHERE {where_sql}",  # noqa: S608
            params,
        ).fetchone()
        return int(row[0])

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
        """The only query method. `where_sql` must come from the access-clause
        builder; `match_expression` is bound as a parameter, never formatted."""
        sql = SEARCH_SQL.format(where=where_sql)
        rows = self._connection.execute(
            sql, (match_expression, *params, limit)
        ).fetchall()
        return [
            LexicalRow(point_id=str(p), payload_json=str(j), score=float(s))
            for p, j, s in rows
        ]

    def close(self) -> None:
        self._connection.close()


def _differences(triples: Iterable[tuple[str, Any, Any]]) -> str:
    return "; ".join(
        f"{name}: recorded {have!r}, wanted {want!r}"
        for name, have, want in triples
        if have != want
    )
