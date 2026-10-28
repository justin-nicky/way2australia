"""Lexical build, open and search tests (Spec 007 R4, R5)."""

import asyncio
import json
import sqlite3
from pathlib import Path

import pytest
from conftest import REPO_ROOT
from lexical_support import (
    COLLECTION,
    VERSION,
    build_production,
    identity,
    open_lexical,
    payload,
    repository,
    rewrite_settings,
    synthetic_entries,
)
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.lexical import build as build_module
from way2australia_rag.lexical.build import build_lexical_index, production_entries
from way2australia_rag.lexical.store import (
    LexicalIndex,
    LexicalIndexBindingError,
    LexicalIndexError,
    source_chunk_digest,
)
from way2australia_rag.repositories import GUEST_PUBLIC_POLICY, list_eligible_documents
from way2australia_rag.retrieval.errors import IndexBindingError

ANY_ROW = "c.tenant_id = ?"


def build(tmp_path: Path, entries=None, **over) -> Path:
    target = tmp_path / "lex.sqlite"
    build_lexical_index(entries or synthetic_entries(), target, identity(**over))
    return target


def test_build_records_settings(tmp_path: Path) -> None:
    target = tmp_path / "lex.sqlite"
    settings = build_lexical_index(synthetic_entries(), target, identity())
    assert settings.chunk_count == 3
    assert settings.tokenizer_name == "lexical-v1"
    assert settings.fts5_tokenizer == "ascii"
    assert settings.bm25 == {"k1": 1.2, "b": 0.75}
    assert (settings.collection, settings.index_version) == (COLLECTION, VERSION)
    assert settings.dense_identity.collection == COLLECTION
    index = open_lexical(target)
    assert index.settings == settings
    assert index.label == "lex.sqlite"
    index.close()


def test_digest_is_stable_and_order_independent(tmp_path: Path) -> None:
    entries = synthetic_entries()
    a = build_lexical_index(entries, tmp_path / "a.sqlite", identity())
    b = build_lexical_index(list(reversed(entries)), tmp_path / "b.sqlite", identity())
    assert a.source_chunk_digest == b.source_chunk_digest
    expected = source_chunk_digest(
        (p, d["document_id"], d["document_version"], d["content_hash"])
        for p, d in entries
    )
    assert a.source_chunk_digest == expected
    changed = [(p, {**d, "content_hash": "other"}) for p, d in entries]
    c = build_lexical_index(changed, tmp_path / "c.sqlite", identity())
    assert c.source_chunk_digest != a.source_chunk_digest


def test_search_keeps_malayalam_words_whole(tmp_path: Path) -> None:
    index = open_lexical(build(tmp_path))
    rows = index.search('"ഉള്ളത്"', ANY_ROW, ("way2australia",), 5)
    assert [r.point_id for r in rows] == ["p2"]
    # a prefix of the word (a different token) does not match
    assert index.search('"ഉള്ള"', ANY_ROW, ("way2australia",), 5) == []
    rows = index.search('"coaching" OR "mock"', ANY_ROW, ("way2australia",), 5)
    assert {r.point_id for r in rows} == {"p1", "p3"}
    assert all(r.score <= 0 for r in rows)
    index.close()


def test_atomic_replace_keeps_old_file_after_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = build(tmp_path)
    before = target.read_bytes()

    def boom(text: str) -> list[str]:
        raise RuntimeError("injected")

    monkeypatch.setattr(build_module, "tokenize", boom)
    with pytest.raises(RuntimeError, match="injected"):
        build_lexical_index([("x", payload("doc_x", "text"))], target, identity())
    assert target.read_bytes() == before
    assert [p.name for p in tmp_path.iterdir()] == ["lex.sqlite"]


def test_failed_first_build_leaves_no_file(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "lex.sqlite"
    dup = [("same", payload("doc_a", "x")), ("same", payload("doc_b", "y"))]
    with pytest.raises(LexicalIndexError):
        build_lexical_index(dup, target, identity())
    assert not target.exists()
    assert list((tmp_path / "sub").iterdir()) == []


def test_entry_without_identity_fields_is_refused(tmp_path: Path) -> None:
    with pytest.raises(LexicalIndexError, match="lacks document_id"):
        build_lexical_index(
            [("x", {"chunk_text": "t"})], tmp_path / "lex.sqlite", identity()
        )
    assert list(tmp_path.iterdir()) == []


def test_missing_owner_key_is_recorded(tmp_path: Path) -> None:
    no_owner = {
        k: v for k, v in payload("doc_m", "words").items() if k != "owner_user_id"
    }
    target = build(tmp_path, [("m", no_owner), ("n", payload("doc_n", "words"))])
    connection = sqlite3.connect(target)
    rows = dict(connection.execute("SELECT point_id, owner_present FROM chunks"))
    connection.close()
    assert rows == {"m": 0, "n": 1}


def test_production_entries_match_eligible_documents() -> None:
    chunker = HeadingChunker()
    entries = asyncio.run(production_entries(repository(), chunker))
    documents = asyncio.run(list_eligible_documents(repository(), GUEST_PUBLIC_POLICY))
    expected = {
        point_id(d.document_id, c.section_id, c.position)
        for d in documents
        for c in chunker.chunk(d)
    }
    assert {p for p, _ in entries} == expected
    assert len(entries) == len(expected)
    assert {pl["document_id"] for _, pl in entries} == {
        d.document_id for d in documents
    }
    assert all(pl["access_scope"] == "public" for _, pl in entries)


def test_production_entries_never_read_security_fixtures() -> None:
    entries = asyncio.run(production_entries(repository(), HeadingChunker()))
    fixture_ids = {"fixture_staff_canary", "fixture_public_poisoned"}
    assert not fixture_ids & {pl["document_id"] for _, pl in entries}
    fixture_text = (
        REPO_ROOT / "tests/fixtures/security/staff_only_canary.md"
    ).read_text("utf-8")
    assert fixture_text.strip()
    assert all(pl["chunk_text"] not in fixture_text for _, pl in entries)


def test_open_refuses_missing_file(tmp_path: Path) -> None:
    with pytest.raises(LexicalIndexBindingError, match="make index-lexical"):
        open_lexical(tmp_path / "nope.sqlite")


def test_open_refuses_non_sqlite_and_missing_settings(tmp_path: Path) -> None:
    junk = tmp_path / "junk.sqlite"
    junk.write_bytes(b"not a database at all" * 20)
    with pytest.raises(LexicalIndexBindingError):
        open_lexical(junk)
    empty = tmp_path / "empty.sqlite"
    sqlite3.connect(empty).close()
    with pytest.raises(LexicalIndexBindingError, match="settings"):
        open_lexical(empty)
    no_row = tmp_path / "norow.sqlite"
    connection = sqlite3.connect(no_row)
    connection.execute("CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)")
    connection.commit()
    connection.close()
    with pytest.raises(LexicalIndexBindingError, match="no recorded settings"):
        open_lexical(no_row)


def test_open_refuses_malformed_settings(tmp_path: Path) -> None:
    target = build(tmp_path)
    connection = sqlite3.connect(target)
    connection.execute("UPDATE settings SET value = 'not json'")
    connection.commit()
    connection.close()
    with pytest.raises(LexicalIndexBindingError, match="malformed"):
        open_lexical(target)


def test_open_refuses_missing_settings_field(tmp_path: Path) -> None:
    target = build(tmp_path)
    connection = sqlite3.connect(target)
    (raw,) = connection.execute("SELECT value FROM settings").fetchone()
    data = json.loads(raw)
    del data["chunk_count"]
    connection.execute("UPDATE settings SET value = ?", (json.dumps(data),))
    connection.commit()
    connection.close()
    with pytest.raises(LexicalIndexBindingError, match="chunk_count"):
        open_lexical(target)


@pytest.mark.parametrize(
    ("changes", "needle"),
    [
        ({"schema_version": "9.9"}, "schema_version"),
        ({"kind": "other"}, "kind"),
        ({"tokenizer_version": "2"}, "tokenizer_version"),
        ({"tokenizer_name": "lexical-v2"}, "tokenizer_name"),
        ({"collection": "other-v1"}, "collection"),
        ({"index_version": "v9"}, "index_version"),
    ],
)
def test_open_refuses_identity_mismatches(
    tmp_path: Path, changes: dict, needle: str
) -> None:
    target = build(tmp_path)
    rewrite_settings(target, **changes)
    with pytest.raises(LexicalIndexBindingError, match=needle) as error:
        open_lexical(target)
    assert isinstance(error.value, IndexBindingError)
    assert "make index-lexical" in str(error.value)
    assert str(tmp_path) not in str(error.value)


def test_build_production_helper_runs(tmp_path: Path) -> None:
    target = tmp_path / "prod.sqlite"
    build_production(target)
    index = LexicalIndex.open(target, COLLECTION, VERSION)
    assert index.settings.chunk_count > 0
    index.close()
