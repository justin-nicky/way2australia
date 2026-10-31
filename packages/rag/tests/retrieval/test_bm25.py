"""BM25 retriever: ranking, authorization, injection, truncation (Spec 007 R6)."""

import sqlite3
from pathlib import Path
from typing import Any

import pytest
from lexical_support import (
    BASE,
    VERSION,
    identity,
    ingest_dense,
    open_lexical,
    payload,
)
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.lexical.build import build_lexical_index
from way2australia_rag.lexical.store import LexicalIndex, LexicalRow
from way2australia_rag.lexical.tokenizer import MAX_QUERY_TERMS
from way2australia_rag.retrieval.access import ResolvedAccess, resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever, match_expression
from way2australia_rag.retrieval.errors import (
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

TENANT = "way2australia"


def pub(doc: str, text: str, **over: Any) -> dict[str, Any]:
    """A complete public payload (check_hit needs every PointPayload field)."""
    values: dict[str, Any] = {
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "title": f"T {doc}",
        "knowledge_domain": "d",
        "source_authority": "business_policy",
        "source_type": "faq",
        "source_url": None,
        "section_id": "s",
        "chunk_position": 0,
    }
    values.update(over)
    return payload(doc, text, **values)


def guest() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id=TENANT))


@pytest.fixture(scope="module")
def dense() -> DenseIndex:
    return ingest_dense()[1]


def build(tmp_path: Path, entries: list[tuple[str, dict[str, Any]]]) -> LexicalIndex:
    target = tmp_path / "lex.sqlite"
    build_lexical_index(entries, target, identity())
    return open_lexical(target)


def retriever(dense: DenseIndex, lexical: Any) -> BM25Retriever:
    return BM25Retriever(IndexIdentity.from_dense(dense), lexical)


class SpyIndex:
    """Wraps a LexicalIndex and records every `search` call."""

    def __init__(self, inner: LexicalIndex) -> None:
        self.inner = inner
        self.calls: list[tuple[str, str, tuple[Any, ...], int]] = []
        self.settings = inner.settings
        self.label = inner.label

    def search(
        self, match: str, where: str, params: tuple[Any, ...], limit: int
    ) -> list[LexicalRow]:
        self.calls.append((match, where, params, limit))
        return self.inner.search(match, where, params, limit)


def test_ranking_and_result_identity(tmp_path: Path, dense: DenseIndex) -> None:
    lexical = build(
        tmp_path,
        [
            ("p1", pub("doc_a", "coaching coaching coaching sessions")),
            ("p2", pub("doc_b", "mock tests and materials")),
            ("p3", pub("doc_c", "coaching and more words about other things here")),
        ],
    )
    result = retriever(dense, lexical).retrieve("coaching", guest(), 5)
    assert [h.document_id for h in result.hits] == ["doc_a", "doc_c"]
    assert [h.rank for h in result.hits] == [1, 2]
    assert result.hits[0].score > result.hits[1].score > 0
    assert result.strategy == "bm25" == Strategy.BM25
    assert result.score_kind == "bm25"
    assert result.device is None
    assert result.collection == dense.collection
    assert result.index_version == dense.index_version
    assert result.embedder_model_id == dense.settings.embedder_model_id
    assert result.lexical is not None
    assert result.lexical.label == "lex.sqlite"
    assert result.lexical.chunk_count == 3
    assert result.query_terms_truncated is False
    assert result.hits[0].title == "T doc_a"


def test_ties_break_by_point_id(tmp_path: Path, dense: DenseIndex) -> None:
    entries = [(pid, pub(f"doc_{pid}", "same words")) for pid in ("p3", "p1", "p2")]
    lexical = build(tmp_path, entries)
    result = retriever(dense, lexical).retrieve("same", guest(), 5)
    assert [h.point_id for h in result.hits] == ["p1", "p2", "p3"]
    assert len({h.score for h in result.hits}) == 1


def test_top_k_limits(tmp_path: Path, dense: DenseIndex) -> None:
    entries = [(f"p{i}", pub(f"doc_{i}", "term")) for i in range(4)]
    result = retriever(dense, build(tmp_path, entries)).retrieve("term", guest(), 2)
    assert len(result.hits) == 2


FORBIDDEN = [
    ("staff", {"access_scope": "staff"}),
    ("other tenant", {"tenant_id": "other"}),
    ("owned", {"owner_user_id": "u1"}),
]


@pytest.mark.parametrize("name,over", FORBIDDEN, ids=[f[0] for f in FORBIDDEN])
def test_forbidden_rows_are_never_returned(
    tmp_path: Path, dense: DenseIndex, name: str, over: dict[str, Any]
) -> None:
    forbidden = pub("doc_x", "secret secret secret secret", **over)
    lexical = build(
        tmp_path, [("px", forbidden), ("pa", pub("doc_a", "secret allowed"))]
    )
    result = retriever(dense, lexical).retrieve("secret", guest(), 5)
    assert [h.document_id for h in result.hits] == ["doc_a"]


def test_missing_owner_key_row_is_never_returned(
    tmp_path: Path, dense: DenseIndex
) -> None:
    missing = pub("doc_x", "secret secret secret")
    del missing["owner_user_id"]
    lexical = build(tmp_path, [("px", missing), ("pa", pub("doc_a", "secret allowed"))])
    spy = SpyIndex(lexical)
    result = retriever(dense, spy).retrieve("secret", guest(), 5)
    assert [h.document_id for h in result.hits] == ["doc_a"]


class DroppedClauseIndex(SpyIndex):
    """A store double that ignores the access clause."""

    def search(
        self, match: str, where: str, params: tuple[Any, ...], limit: int
    ) -> list[LexicalRow]:
        return self.inner.search(match, "1 = 1", (), limit)


CLAUSE_DROP_VARIANTS = [
    ("staff scope", {"access_scope": "staff"}, "access_scope", False),
    ("other tenant", {"tenant_id": "other"}, "tenant_id", False),
    ("owned", {"owner_user_id": "u1"}, "owner_user_id", False),
    ("missing owner", {}, "owner_user_id", True),
]


@pytest.mark.parametrize(
    "name,over,field,drop_owner",
    CLAUSE_DROP_VARIANTS,
    ids=[v[0] for v in CLAUSE_DROP_VARIANTS],
)
def test_a_store_without_the_clause_trips_check_hit(
    tmp_path: Path,
    dense: DenseIndex,
    name: str,
    over: dict[str, Any],
    field: str,
    drop_owner: bool,
) -> None:
    forbidden = pub("doc_x", "secret", **over)
    if drop_owner:
        del forbidden["owner_user_id"]
    lexical = build(tmp_path, [("px", forbidden), ("pa", pub("doc_a", "secret"))])
    with pytest.raises(RetrievalAuthorizationError) as caught:
        retriever(dense, DroppedClauseIndex(lexical)).retrieve("secret", guest(), 5)
    assert caught.value.document_id == "doc_x"
    assert field in str(caught.value)


HOSTILE = [
    "coaching NEAR tests",
    "coaching AND tests",
    "NOT coaching",
    "coach*",
    "access_scope:staff",
    'unbalanced "quote',
    "(coaching OR (tests",
    "x'; DROP TABLE chunks; --",
    '"" OR 1=1',
    'coaching" OR "access_scope" : "staff',
]


@pytest.mark.parametrize("query", HOSTILE)
def test_hostile_queries_stay_inert(
    tmp_path: Path, dense: DenseIndex, query: str
) -> None:
    lexical = build(
        tmp_path,
        [
            ("pa", pub("doc_a", "coaching tests coach staff drop table")),
            ("px", pub("doc_x", "coaching staff secret", access_scope="staff")),
        ],
    )
    spy = SpyIndex(lexical)
    statements: list[str] = []
    lexical._connection.set_trace_callback(statements.append)  # type: ignore[attr-defined]
    result = retriever(dense, spy).retrieve(query, guest(), 5)
    assert all(h.document_id == "doc_a" for h in result.hits)
    for match, where, params, limit in spy.calls:
        # the MATCH argument is exactly the quoted lexical-v1 terms
        from way2australia_rag.lexical.tokenizer import query_terms

        assert match == match_expression(query_terms(query).terms)
        assert where.startswith("c.access_scope IN (?)")
        assert params == ("public", TENANT)
        assert limit == 5
    # the SQL text is the constant statement; the raw query never appears in it
    selects = [s for s in statements if "chunk_terms MATCH" in s]
    assert selects
    assert all(query not in s for s in selects if len(query) > 3)
    assert len({_shape(s) for s in selects}) == 1
    tables = {
        row[0]
        for row in lexical._connection.execute(  # type: ignore[attr-defined]
            "SELECT name FROM sqlite_master"
        )
    }
    assert "chunks" in tables


def _shape(statement: str) -> str:
    """The traced statement with bound values blanked out."""
    import re

    return re.sub(r"'[^']*'", "?", statement)


def test_match_expression_quotes_and_escapes() -> None:
    assert match_expression(["a", "near"]) == '"a" OR "near"'
    assert match_expression(['x"y']) == '"x""y"'


def test_zero_term_query_does_not_search(tmp_path: Path, dense: DenseIndex) -> None:
    spy = SpyIndex(build(tmp_path, [("p1", pub("doc_a", "coaching"))]))
    result = retriever(dense, spy).retrieve("?! ... --", guest(), 5)
    assert result.hits == []
    assert spy.calls == []
    assert result.query_terms_truncated is False
    assert result.strategy == "bm25"


def test_more_than_64_terms_are_truncated(tmp_path: Path, dense: DenseIndex) -> None:
    spy = SpyIndex(build(tmp_path, [("p1", pub("doc_a", "w0 w1 w70"))]))
    query = " ".join(f"w{i}" for i in range(70))
    result = retriever(dense, spy).retrieve(query, guest(), 5)
    assert result.query_terms_truncated is True
    ((match, *_),) = spy.calls
    quoted = match.split(" OR ")
    assert len(quoted) == MAX_QUERY_TERMS == 64
    assert quoted == [f'"w{i}"' for i in range(64)]
    assert [h.document_id for h in result.hits] == ["doc_a"]


def test_validation_messages_equal_the_dense_ones(
    tmp_path: Path, dense: DenseIndex
) -> None:
    bm25 = retriever(dense, build(tmp_path, [("p1", pub("doc_a", "x"))]))
    dense_retriever = DenseRetriever(dense, FakeEmbedder())
    for query, top_k in (
        ("  ", 5),
        (None, 5),
        ("x", 0),
        ("x", 51),
        ("x", True),
        ("x", "5"),
    ):
        with pytest.raises(RetrievalConfigurationError) as a:
            bm25.retrieve(query, guest(), top_k)  # type: ignore[arg-type]
        with pytest.raises(RetrievalConfigurationError) as b:
            dense_retriever.retrieve(query, guest(), top_k)  # type: ignore[arg-type]
        assert str(a.value) == str(b.value)


def test_malformed_payload_json_fails_closed(tmp_path: Path, dense: DenseIndex) -> None:
    lexical = build(tmp_path, [("p1", pub("doc_a", "coaching"))])
    path = tmp_path / "lex.sqlite"
    lexical.close()
    connection = sqlite3.connect(path)
    with connection:
        connection.execute("UPDATE chunks SET payload_json = 'not json'")
    connection.close()
    with pytest.raises(RetrievalAuthorizationError):
        retriever(dense, open_lexical(path)).retrieve("coaching", guest(), 5)


def test_base_names() -> None:
    assert BASE and VERSION
    assert [s.value for s in Strategy] == ["dense", "bm25", "hybrid"]


def test_standalone_path_returns_the_hits_of_the_spec_007_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Spec 008 R5: the bm25 retriever built from configuration only (standalone
    open, no dense index) equals the Spec 007 one bound to a dense fixture."""
    from conftest import REPO_ROOT
    from lexical_support import build_production
    from way2australia_rag.ingestion.config import load_ingestion_config
    from way2australia_rag.retrieval.opening import open_retrieval
    from way2australia_rag.retrieval.strategy import load_retrieval_config

    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    config = config.model_copy(update={"index_version": VERSION})
    directory = tmp_path / "lex"
    directory.mkdir()
    target = directory / f"{BASE}-{VERSION}.sqlite"
    build_production(target)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", BASE)
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    from way2australia_rag.ingestion.config import load_runtime_settings

    settings = load_runtime_settings(RetrievalConfigurationError)
    spec_007 = BM25Retriever(
        IndexIdentity.from_dense(dense_fixture()), open_lexical(target)
    )
    opened = open_retrieval(
        Strategy.BM25,
        settings=settings,
        ingestion_config=config,
        retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
        provider="fake",
        repo_root=REPO_ROOT,
    )
    try:
        for query in ("Is coaching compulsory?", "mock tests", "NAATI CCL"):
            old = spec_007.retrieve(query, guest(), 5)
            new = opened.retriever.retrieve(query, guest(), 5)
            assert old.hits and old.hits == new.hits
            assert (old.collection, old.index_version, old.embedder_model_id) == (
                new.collection,
                new.index_version,
                new.embedder_model_id,
            )
            assert old.embedder_is_fake == new.embedder_is_fake
    finally:
        opened.close()


def dense_fixture() -> DenseIndex:
    return ingest_dense()[1]
