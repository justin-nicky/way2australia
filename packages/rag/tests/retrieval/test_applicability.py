"""LOTE applicability filters and re-check (Spec 010 T2)."""

import json
from pathlib import Path
from typing import Any, NoReturn

import pytest
from conftest import REPO_ROOT
from lexical_support import (
    COLLECTION,
    VERSION,
    identity,
    ingest_dense,
    rewrite_settings,
)
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.ingestion.settings import build_index_settings
from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.lexical.build import build_lexical_index
from way2australia_rag.lexical.store import (
    LexicalIndex,
    LexicalIndexBindingError,
    LexicalIndexError,
)
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    build_sql_access_clause,
    resolve_access,
)
from way2australia_rag.retrieval.applicability import (
    ResolvedLote,
    build_lote_condition,
    build_sql_lote_clause,
    check_applicable,
    dense_query_filter,
    encode_lote_column,
    resolve_lote,
    sql_access_with_lote,
    valid_lote_languages,
)
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    LanguageApplicabilityError,
    RetrievalConfigurationError,
    RetrievalUnavailableError,
)
from way2australia_rag.retrieval.fallback import FallbackRetriever
from way2australia_rag.retrieval.fusion import FusionConfig
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

EMBEDDER = FakeEmbedder()
BASE = "w2a-lote"
VER = "v1"
COLLECTION_NAME = f"{BASE}-{VER}"
FUSION = FusionConfig(
    method="rrf", candidate_depth=20, k=60, weights={"dense": 1.0, "bm25": 1.0}
)


def guest() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def temp_registry(tmp_path: Path, codes: dict[str, str]) -> Path:
    (tmp_path / "config").mkdir()
    body = {
        "product_support": {
            name: {"internal_code": code, "status": "active"}
            for name, code in codes.items()
        }
    }
    (tmp_path / "config/language_registry.json").write_text(json.dumps(body))
    return tmp_path


def payload_dict(document_id: str, text: str, **over: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "tenant_id": "way2australia",
        "access_scope": "public",
        "owner_user_id": None,
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "title": document_id,
        "knowledge_domain": "d",
        "source_authority": "owner_approved",
        "source_type": "faq",
        "source_url": None,
        "chunk_text": text,
        "content_hash": "a" * 64,
        "document_id": document_id,
        "document_version": 1,
        "section_id": "main",
        "chunk_position": 0,
    }
    values.update(over)
    return values


def make_payload(document_id: str, text: str, **over: Any) -> PointPayload:
    return PointPayload.model_validate(payload_dict(document_id, text, **over))


def build_lexical(
    tmp_path: Path,
    entries: list[tuple[str, dict[str, Any]]],
    *,
    tokenizer_name: str = "lexical-v1",
) -> Path:
    from way2australia_rag.lexical.tokenizer import TOKENIZERS

    target = tmp_path / "lex.sqlite"
    build_lexical_index(
        entries,
        target,
        identity(collection=COLLECTION_NAME, index_version=VER),
        tokenizer=TOKENIZERS[tokenizer_name],
    )
    return target


def test_resolve_lote_with_temp_registry(tmp_path: Path) -> None:
    root = temp_registry(tmp_path, {"a": "ml", "b": "zz"})
    active = active_lote_codes(root)
    assert resolve_lote(None, active) is None
    assert resolve_lote("ml", active) == ResolvedLote(code="ml")
    with pytest.raises(RetrievalConfigurationError, match="not active"):
        resolve_lote("xx", active)
    with pytest.raises(RetrievalConfigurationError, match="empty"):
        resolve_lote("", active)
    with pytest.raises(RetrievalConfigurationError, match="\\*"):
        resolve_lote("*", active)
    with pytest.raises(RetrievalConfigurationError, match="not a LOTE"):
        resolve_lote("en", active)


@pytest.mark.parametrize(
    "value, ok",
    [
        (["*"], True),
        (["ml"], True),
        (["ml", "ta"], True),
        (["ml", "ml"], False),
        ([], False),
        (["*", "ml"], False),
        ("ml", False),
        (None, False),
    ],
)
def test_valid_lote_languages(value: object, ok: bool) -> None:
    assert valid_lote_languages(value) is ok


def test_access_builders_unchanged_without_lote() -> None:
    access = guest()
    assert dense_query_filter(access, None) == build_access_filter(access)
    assert sql_access_with_lote(access, None) == build_sql_access_clause(access)


def test_lexical_builder_writes_lote_column(tmp_path: Path) -> None:
    path = build_lexical(
        tmp_path,
        [
            ("p1", payload_dict("d1", "alpha", lote_languages=["ml"])),
            ("p2", payload_dict("d2", "beta", lote_languages=["*"])),
        ],
    )
    import sqlite3

    rows = (
        sqlite3.connect(path)
        .execute("SELECT lote_languages FROM chunks ORDER BY point_id")
        .fetchall()
    )
    assert rows == [("|ml|",), ("|*|",)]


def test_lexical_builder_refuses_star_plus_code(tmp_path: Path) -> None:
    with pytest.raises(LexicalIndexError):
        build_lexical(
            tmp_path,
            [("p1", payload_dict("d1", "x", lote_languages=["*", "ml"]))],
        )
    assert not (tmp_path / "lex.sqlite").exists()


def _tagged_entries(code: str, other: str) -> list[tuple[str, dict[str, Any]]]:
    tags = {
        "star": ["*"],
        "code": [code],
        "both": [code, other],
        "other": [other],
    }
    return [
        (
            name,
            payload_dict(
                f"doc_{name}",
                f"querytoken {name} text",
                lote_languages=lote,
            ),
        )
        for name, lote in tags.items()
    ]


def _qdrant_index(entries: list[tuple[str, dict[str, Any]]]) -> DenseIndex:
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VER)
    settings = build_index_settings(VER, EMBEDDER.info, HeadingChunker())
    store.ensure_collection(settings)
    for _name, body in entries:
        p = make_payload(
            body["document_id"],
            body["chunk_text"],
            lote_languages=body["lote_languages"],
        )
        store.replace_document(
            p.document_id,
            [
                IndexPoint(
                    point_id=point_id(p.document_id, p.section_id, p.chunk_position),
                    vector=EMBEDDER.embed_documents([p.chunk_text])[0],
                    payload=p,
                )
            ],
        )
    return DenseIndex.open(client, BASE, VER, EMBEDDER.info)


def _doc_sets(
    index: DenseIndex, lex_path: Path, access: ResolvedAccess, lote: ResolvedLote | None
) -> tuple[set[str], set[str]]:
    dense = DenseRetriever(index, EMBEDDER)
    identity = IndexIdentity.from_dense(index)
    lexical = LexicalIndex.open(lex_path, COLLECTION_NAME, VER)
    bm25 = BM25Retriever(identity, lexical)
    try:
        d_ids = {
            h.document_id
            for h in dense.retrieve("querytoken", access, 10, lote=lote).hits
        }
        b_ids = {
            h.document_id
            for h in bm25.retrieve("querytoken", access, 10, lote=lote).hits
        }
    finally:
        lexical.close()
    return d_ids, b_ids


def test_store_parity_on_tagged_rows(tmp_path: Path) -> None:
    root = temp_registry(tmp_path, {"a": "ml", "b": "zz"})
    code, other = active_lote_codes(root)
    entries = _tagged_entries(code, other)
    index = _qdrant_index(entries)
    lex_path = build_lexical(tmp_path, entries)
    access = guest()
    expected = {
        None: {f"doc_{n}" for n in ("star", "code", "both", "other")},
        code: {"doc_star", "doc_code", "doc_both"},
        other: {"doc_star", "doc_both", "doc_other"},
    }
    for lote_arg in (ResolvedLote(code=code), ResolvedLote(code=other), None):
        d_ids, b_ids = _doc_sets(index, lex_path, access, lote_arg)
        assert d_ids == b_ids
        key = lote_arg.code if lote_arg is not None else None
        assert d_ids == expected[key]


class DroppedFilterIndex(DenseIndex):
    def search(self, vector, query_filter, limit):  # type: ignore[no-untyped-def]
        return super().search(vector, build_access_filter(guest()), limit)


def _fallback_query_primary() -> Any:
    class UnavailableHybrid:
        strategy = Strategy.HYBRID

        def retrieve(
            self,
            query_text: str,
            access: ResolvedAccess,
            top_k: int = 5,
            *,
            lote: ResolvedLote | None = None,
        ) -> NoReturn:
            raise RetrievalUnavailableError(FallbackReason.QDRANT_UNAVAILABLE)

    return UnavailableHybrid()


def _retriever_by_factory(
    factory: str,
    *,
    dense: DenseRetriever,
    bm25: BM25Retriever,
    hybrid: HybridRetriever,
) -> Any:
    if factory == "dense":
        return dense
    if factory == "bm25":
        return bm25
    if factory == "hybrid":
        return hybrid
    if factory == "fallback_open":
        return FallbackRetriever(None, bm25, FallbackReason.QDRANT_UNAVAILABLE)
    if factory == "fallback_query":
        return FallbackRetriever(_fallback_query_primary(), bm25, None)
    raise AssertionError(factory)


@pytest.mark.parametrize(
    "factory",
    ["dense", "bm25", "hybrid", "fallback_open", "fallback_query"],
)
def test_non_applicable_first_hit_excluded(tmp_path: Path, factory: str) -> None:
    entries = [
        ("na", payload_dict("doc_na", "targetword only here", lote_languages=["zz"])),
        ("ok", payload_dict("doc_ok", "targetword good", lote_languages=["*"])),
    ]
    index = _qdrant_index(entries)
    lex_path = build_lexical(tmp_path, entries)
    access = guest()
    root = temp_registry(tmp_path, {"a": "ml"})
    lote = resolve_lote("ml", active_lote_codes(root))
    assert lote is not None
    identity = IndexIdentity.from_dense(index)
    lexical = LexicalIndex.open(lex_path, COLLECTION_NAME, VER)
    dense = DenseRetriever(index, EMBEDDER)
    bm25 = BM25Retriever(identity, lexical)
    hybrid = HybridRetriever(dense, bm25, FUSION)
    try:
        r = _retriever_by_factory(factory, dense=dense, bm25=bm25, hybrid=hybrid)
        without = r.retrieve("targetword", access, 5).hits
        with_lote = r.retrieve("targetword", access, 5, lote=lote).hits
        without_ids = {h.document_id for h in without}
        assert without_ids == {"doc_na", "doc_ok"}
        assert {h.document_id for h in with_lote} == {"doc_ok"}
    finally:
        lexical.close()


class DroppedLoteClauseLexical:
    """Lexical double that ignores the lote portion of the WHERE clause."""

    def __init__(self, inner: LexicalIndex) -> None:
        self.inner = inner
        self.settings = inner.settings
        self.label = inner.label
        self.has_lote_column = inner.has_lote_column

    @property
    def tokenizer(self):
        return self.inner.tokenizer

    def search(
        self, match: str, where: str, params: tuple[Any, ...], limit: int
    ) -> list[Any]:
        access_where, access_params = build_sql_access_clause(guest())
        return self.inner.search(match, access_where, access_params, limit)


def _dropped_lote_setup(
    tmp_path: Path,
    *,
    tokenizer_name: str = "lexical-v1",
) -> tuple[DenseIndex, BM25Retriever, HybridRetriever, LexicalIndex]:
    entries = [("na", payload_dict("doc_na", "needle", lote_languages=["zz"]))]
    index = _qdrant_index(entries)
    lex_path = build_lexical(tmp_path, entries, tokenizer_name=tokenizer_name)
    lexical = LexicalIndex.open(lex_path, COLLECTION_NAME, VER)
    dropped = DroppedLoteClauseLexical(lexical)
    identity = IndexIdentity.from_dense(index)
    dense = DenseRetriever(index, EMBEDDER)
    bm25 = BM25Retriever(identity, dropped)  # type: ignore[arg-type]
    hybrid = HybridRetriever(dense, bm25, FUSION)
    return index, bm25, hybrid, lexical


def test_dropped_filter_raises_language_applicability(tmp_path: Path) -> None:
    entries = [("na", payload_dict("doc_na", "needle", lote_languages=["zz"]))]
    index = _qdrant_index(entries)
    spy = DroppedFilterIndex(
        index._client,  # noqa: SLF001
        index.collection,
        index.settings,
        index._query_timeout_s,  # noqa: SLF001
    )
    root = temp_registry(tmp_path, {"a": "ml"})
    lote = resolve_lote("ml", active_lote_codes(root))
    with pytest.raises(LanguageApplicabilityError):
        DenseRetriever(spy, EMBEDDER).retrieve("needle", guest(), 5, lote=lote)


@pytest.mark.parametrize(
    "factory",
    ["bm25", "hybrid", "fallback_open", "fallback_query"],
)
@pytest.mark.parametrize("tokenizer_name", ["lexical-v1", "lexical-v2"])
def test_dropped_lote_clause_raises_language_applicability(
    tmp_path: Path, factory: str, tokenizer_name: str
) -> None:
    index, bm25, hybrid, lexical = _dropped_lote_setup(
        tmp_path, tokenizer_name=tokenizer_name
    )
    root = temp_registry(tmp_path, {"a": "ml"})
    lote = resolve_lote("ml", active_lote_codes(root))
    dense = DenseRetriever(index, EMBEDDER)
    retriever = _retriever_by_factory(factory, dense=dense, bm25=bm25, hybrid=hybrid)
    try:
        with pytest.raises(LanguageApplicabilityError):
            retriever.retrieve("needle", guest(), 5, lote=lote)
    finally:
        lexical.close()


def test_language_applicability_not_caught_by_fallback() -> None:
    class ApplicabilityPrimary:
        strategy = Strategy.HYBRID

        def retrieve(
            self,
            query_text: str,
            access: ResolvedAccess,
            top_k: int = 5,
            *,
            lote: ResolvedLote | None = None,
        ) -> NoReturn:
            raise LanguageApplicabilityError(
                "hit for document 'doc_x' is not applicable to lote 'ml'.",
                document_id="doc_x",
            )

    class NeverFallback:
        strategy = Strategy.BM25

        def retrieve(
            self,
            query_text: str,
            access: ResolvedAccess,
            top_k: int = 5,
            *,
            lote: ResolvedLote | None = None,
        ) -> NoReturn:
            raise AssertionError("fallback must not run")

    with pytest.raises(LanguageApplicabilityError):
        FallbackRetriever(  # pyright: ignore[reportArgumentType]
            ApplicabilityPrimary(), NeverFallback(), None
        ).retrieve("q", guest(), 5, lote=ResolvedLote(code="ml"))


def test_hits_with_lote_subset_of_without_lote(tmp_path: Path) -> None:
    root = temp_registry(tmp_path, {"a": "ml", "b": "zz"})
    code, other = active_lote_codes(root)
    entries = _tagged_entries(code, other)
    index = _qdrant_index(entries)
    lote = resolve_lote(code, active_lote_codes(root))
    dense = DenseRetriever(index, EMBEDDER)
    access = guest()
    all_ids = {h.document_id for h in dense.retrieve("querytoken", access, 10).hits}
    with_lote = dense.retrieve("querytoken", access, 10, lote=lote).hits
    filtered = {h.document_id for h in with_lote}
    assert filtered <= all_ids


@pytest.mark.parametrize("strategy", [Strategy.DENSE, Strategy.BM25, Strategy.HYBRID])
def test_seed_corpus_ml_lote_matches_no_lote(
    strategy: Strategy, tmp_path: Path
) -> None:
    import asyncio

    from lexical_support import production_entries, repository
    from way2australia_rag.ingestion.tokenization import FakeTokenizer

    _client, dense_index = ingest_dense()
    dense_identity = IndexIdentity.from_dense(dense_index)
    entries = asyncio.run(
        production_entries(repository(), HeadingChunker(), FakeTokenizer(), None)
    )
    lex_path = tmp_path / "lex.sqlite"
    build_lexical_index(entries, lex_path, identity())
    lexical = LexicalIndex.open(lex_path, COLLECTION, VERSION)
    dense = DenseRetriever(dense_index, EMBEDDER)
    bm25 = BM25Retriever(dense_identity, lexical)
    hybrid = HybridRetriever(dense, bm25, FUSION)
    retrievers = {
        Strategy.DENSE: dense,
        Strategy.BM25: bm25,
        Strategy.HYBRID: hybrid,
    }
    access = guest()
    lote = resolve_lote("ml", active_lote_codes(REPO_ROOT))
    query = "Coaching sessions are live"
    try:
        plain = retrievers[strategy].retrieve(query, access, 5)
        filtered = retrievers[strategy].retrieve(query, access, 5, lote=lote)
        plain_ids = [h.document_id for h in plain.hits]
        filtered_ids = [h.document_id for h in filtered.hits]
        assert plain_ids == filtered_ids
    finally:
        lexical.close()


def test_lexical_document_count_refuses_lote_on_lexical_11(tmp_path: Path) -> None:
    from way2australia_rag.retrieval.opening import _lexical_document_count

    path = build_lexical(tmp_path, [("p1", payload_dict("d1", "word"))])
    rewrite_settings(path, schema_version="1.1")
    index = LexicalIndex.open(path, COLLECTION_NAME, VER)
    root = temp_registry(tmp_path, {"a": "ml"})
    lote = resolve_lote("ml", active_lote_codes(root))
    try:
        assert _lexical_document_count(index, guest(), None) == 1
        with pytest.raises(LexicalIndexBindingError, match="make index-lexical"):
            _lexical_document_count(index, guest(), lote)
    finally:
        index.close()


def test_lexical_11_serves_without_lote_refuses_with_lote(tmp_path: Path) -> None:
    path = build_lexical(tmp_path, [("p1", payload_dict("d1", "word"))])
    rewrite_settings(path, schema_version="1.1")
    index = LexicalIndex.open(path, COLLECTION_NAME, VER)
    dense_index = _qdrant_index([("p1", payload_dict("d1", "word"))])
    dense_id = IndexIdentity.from_dense(dense_index)
    bm25 = BM25Retriever(dense_id, index)
    assert bm25.retrieve("word", guest(), 5).hits
    root = temp_registry(tmp_path, {"a": "ml"})
    lote = resolve_lote("ml", active_lote_codes(root))
    with pytest.raises(LexicalIndexBindingError):
        bm25.retrieve("word", guest(), 5, lote=lote)
    index.close()


def test_malformed_lote_on_qdrant_point_raises_for_any_lote(tmp_path: Path) -> None:
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VER)
    settings = build_index_settings(VER, EMBEDDER.info, HeadingChunker())
    store.ensure_collection(settings)
    bad = make_payload("bad_doc", "text", lote_languages=["*", "ml"])
    store.replace_document(
        bad.document_id,
        [
            IndexPoint(
                point_id=point_id(bad.document_id, bad.section_id, bad.chunk_position),
                vector=EMBEDDER.embed_documents([bad.chunk_text])[0],
                payload=bad,
            )
        ],
    )
    index = DenseIndex.open(client, BASE, VER, EMBEDDER.info)
    root = temp_registry(tmp_path, {"a": "ml", "b": "zz"})
    for code in active_lote_codes(root):
        with pytest.raises(LanguageApplicabilityError):
            DenseRetriever(index, EMBEDDER).retrieve(
                "text", guest(), 5, lote=ResolvedLote(code=code)
            )


def test_build_lote_condition_and_sql() -> None:
    lote = ResolvedLote(code="ml")
    cond = build_lote_condition(lote)
    assert cond.key == "lote_languages"
    sql, params = build_sql_lote_clause(lote)
    assert params == ("|*|", "|ml|")
    assert "instr" in sql


def test_check_applicable_and_encode() -> None:
    payload = make_payload("d", "t", lote_languages=["ml"])
    check_applicable(payload, ResolvedLote(code="ml"))
    assert encode_lote_column(["ml", "ta"]) == "|ml|ta|"
    assert encode_lote_column(["*"]) == "|*|"
