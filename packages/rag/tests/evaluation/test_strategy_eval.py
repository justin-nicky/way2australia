"""Strategy option and result format 2.1 (Spec 007 R8, R9, R14; T6).

No model, no Docker: fake-hash vectors on in-memory Qdrant, SQLite files and
result files under tmp_path only.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT, live_suite_rows
from qdrant_client import QdrantClient
from retrieval.test_retriever import guest
from way2australia_rag.evaluation import cli
from way2australia_rag.evaluation.results import read_result
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.lexical.build import build_lexical_index
from way2australia_rag.lexical.store import (
    DenseIdentity,
    LexicalIdentityInput,
    LexicalIndex,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval import cli as retrieve_cli
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.strategy import (
    build_retriever,
    load_retrieval_config,
)

from .dense_equivalence import FIXTURE_NAME, run_equivalence
from .test_cli import (
    BASE,
    VERSION,
    index_factory,
)
from .test_cli import run as eval_cli
from .test_retrieval_eval import (
    RealStub,
    build,
    golden,
    run,
    suite_of,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)
COLLECTION = f"{BASE}-{VERSION}"
FIXTURE = Path(__file__).parent / "fixtures" / FIXTURE_NAME
RETRIEVAL_CONFIG = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml")


# ---- dense equivalence ------------------------------------------------------


def test_dense_2_1_equals_the_pre_change_2_0_result() -> None:
    before = json.loads(FIXTURE.read_text(encoding="utf-8"))
    after = run_equivalence()
    assert before["schema_version"] == "2.0" and after["schema_version"] == "2.1"
    new_row_keys = {"query_terms_truncated", "leg_ranks"}
    assert len(after["cases"]) == len(before["cases"]) > 0
    for old, new in zip(before["cases"], after["cases"], strict=True):
        assert {k: v for k, v in new.items() if k not in new_row_keys} == old
        assert new["query_terms_truncated"] is None and new["leg_ranks"] is None
    skipped = {
        "schema_version",
        "cases",
        "latency_ms",
        "unanswerable",
        "score_kind",
        "fusion",
        "lexical_index",
        "truncated_query_count",
    }
    for key, value in before.items():
        if key not in skipped:
            assert after[key] == value, key
    for key, value in before["latency_ms"].items():
        assert after["latency_ms"][key] == value, key
    assert after["latency_ms"]["legs"] is None
    unanswerable = dict(after["unanswerable"])
    assert unanswerable.pop("score_kind") == "dense_cosine"
    assert unanswerable == before["unanswerable"]
    assert after["score_kind"] == "dense_cosine"
    assert after["fusion"] is None and after["lexical_index"] is None
    assert after["truncated_query_count"] is None


def test_dense_latency_span_ends_after_check_hit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    index, _emb, retriever = build()
    clock = {"now": 0.0}
    from way2australia_rag.retrieval import retriever as module

    real_check = module.check_hit

    def slow_check(payload: Any, access: Any) -> Any:
        clock["now"] += 1.0  # one fake second per checked hit
        return real_check(payload, access)

    monkeypatch.setattr(module, "perf_counter", lambda: clock["now"])
    monkeypatch.setattr(module, "check_hit", slow_check)
    result = retriever.retrieve("body 1", guest(), 5)
    assert result.hits
    assert result.latency_ms == pytest.approx(1000.0 * len(result.hits))


# ---- 2.1 documents per strategy --------------------------------------------


def make_world(tmp_path: Path, count: int = 8):  # noqa: ANN201
    """Dense index plus a lexical file built from the same points."""
    from retrieval.test_retriever import make_payload
    from way2australia_rag.ingestion.identity import point_id
    from way2australia_rag.ingestion.settings import build_index_settings
    from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
    from way2australia_rag.retrieval.index import DenseIndex

    emb = RealStub()
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VERSION)
    store.ensure_collection(build_index_settings(VERSION, emb.info, HeadingChunker()))
    for i in range(count):
        text = f"SECRET-CHUNK body {i}"
        store.replace_document(
            f"doc_{i}",
            [
                IndexPoint(
                    point_id=point_id(f"doc_{i}", "main", 0),
                    vector=emb.embed_documents([text])[0],
                    payload=make_payload(f"doc_{i}", text),
                )
            ],
        )
    index = DenseIndex.open(client, BASE, VERSION, emb.info)
    lexical = build_lexical(client, tmp_path / "lex" / f"{COLLECTION}.sqlite")
    return client, index, emb, lexical


def build_lexical(client: QdrantClient, target: Path, drop: int = 0) -> LexicalIndex:
    points, _ = client.scroll(COLLECTION, limit=100, with_payload=True)
    entries = [(str(p.id), dict(p.payload or {})) for p in points]
    info = RealStub().info
    chunker = HeadingChunker()
    build_lexical_index(
        entries[drop:],
        target,
        LexicalIdentityInput(
            collection=COLLECTION,
            index_version=VERSION,
            dense_identity=DenseIdentity(
                collection=COLLECTION,
                index_version=VERSION,
                embedder_model_id=info.model_id,
                embedder_revision=info.revision,
            ),
            chunker_name=chunker.name,
            chunker_version=chunker.version,
            chunker_max_chunk_chars=chunker.max_chunk_chars,
            hash_contract=HASH_CONTRACT,
        ),
    )
    return LexicalIndex.open(target, COLLECTION, VERSION)


def strategy_suite():  # noqa: ANN201
    return suite_of(
        [
            golden(1, ["doc_1"], query="body 1"),
            golden(2, ["doc_2", "doc_3"], query="body 2 3", lang="mixed"),
            golden(3, ["doc_9"], query="body 9"),
        ]
    )


def run_strategy(tmp_path: Path, strategy: Strategy, suite=None):  # noqa: ANN001, ANN201
    _client, index, emb, lexical = make_world(tmp_path)
    retriever = build_retriever(strategy, index, emb, lexical, RETRIEVAL_CONFIG)
    return run(
        index,
        emb,
        retriever,
        suite or strategy_suite(),
        fusion=RETRIEVAL_CONFIG.fusion if strategy == Strategy.HYBRID else None,
    )


COMMON_KEYS = {
    "retrieval_strategy",
    "score_kind",
    "fusion",
    "lexical_index",
    "truncated_query_count",
}


@pytest.mark.parametrize(
    ("strategy", "score_kind"),
    [
        (Strategy.DENSE, "dense_cosine"),
        (Strategy.BM25, "bm25"),
        (Strategy.HYBRID, "rrf"),
    ],
)
def test_2_1_keys_for_each_strategy(
    tmp_path: Path, strategy: Strategy, score_kind: str
) -> None:
    doc = run_strategy(tmp_path, strategy)
    assert doc["schema_version"] == "2.1"
    assert COMMON_KEYS <= set(doc)
    assert doc["retrieval_strategy"] == strategy.value
    assert doc["score_kind"] == score_kind
    assert doc["unanswerable"]["score_kind"] == score_kind
    fusion = doc["fusion"]
    lexical = doc["lexical_index"]
    if strategy == Strategy.HYBRID:
        assert fusion == {
            "method": "rrf",
            "k": RETRIEVAL_CONFIG.fusion.k,
            "weights": dict(RETRIEVAL_CONFIG.fusion.weights),
            "candidate_depth": RETRIEVAL_CONFIG.fusion.candidate_depth,
        }
        assert set(doc["latency_ms"]["legs"]) == {"dense", "bm25"}
        for leg in doc["latency_ms"]["legs"].values():
            assert set(leg) == {"p50", "p95"}
    else:
        assert fusion is None and doc["latency_ms"]["legs"] is None
    if strategy == Strategy.DENSE:
        assert lexical is None and doc["truncated_query_count"] is None
    else:
        assert set(lexical) == {
            "label",
            "tokenizer_name",
            "tokenizer_version",
            "source_chunk_digest",
            "chunk_count",
        }
        assert lexical["label"] == f"{COLLECTION}.sqlite"
        assert doc["truncated_query_count"] == 0
    for row in doc["cases"]:
        assert "query_terms_truncated" in row and "leg_ranks" in row


def test_leg_ranks_cover_the_relevant_documents(tmp_path: Path) -> None:
    bm25 = run_strategy(tmp_path / "a", Strategy.BM25)
    hybrid = run_strategy(tmp_path / "b", Strategy.HYBRID)
    for doc, legs in ((bm25, {"bm25"}), (hybrid, {"dense", "bm25"})):
        for row in doc["cases"]:
            assert set(row["leg_ranks"]) == legs
            for ranks in row["leg_ranks"].values():
                assert set(ranks) == set(row["relevant_document_ids"])
    first = bm25["cases"][0]
    assert first["relevant_document_ids"] == ["doc_1"]
    assert first["leg_ranks"]["bm25"]["doc_1"] == 1
    missing = bm25["cases"][2]
    assert missing["leg_ranks"]["bm25"] == {"doc_9": None}
    hybrid_first = hybrid["cases"][0]["leg_ranks"]
    assert hybrid_first["bm25"]["doc_1"] == 1
    assert hybrid_first["dense"]["doc_1"] == 2  # fake embedder: deterministic


def leg_order(tmp_path: Path, strategy: Strategy, query: str) -> list[str]:
    """Full deduped document ranking of one leg, read at candidate depth."""
    _client, index, emb, lexical = make_world(tmp_path)
    retriever = build_retriever(strategy, index, emb, lexical, RETRIEVAL_CONFIG)
    result = retriever.retrieve(query, guest(), RETRIEVAL_CONFIG.fusion.candidate_depth)
    return [h.document_id for h in result.hits]


def test_hybrid_leg_ranks_beyond_top_k_are_real_document_ranks(
    tmp_path: Path,
) -> None:
    suite = suite_of([golden(1, ["doc_7"], query="body 1")])
    _client, index, emb, lexical = make_world(tmp_path / "w")
    retriever = build_retriever(Strategy.HYBRID, index, emb, lexical, RETRIEVAL_CONFIG)
    doc = run(index, emb, retriever, suite, top_k=1, fusion=RETRIEVAL_CONFIG.fusion)
    row = doc["cases"][0]
    assert row["hit"] is False
    dense_order = leg_order(tmp_path / "d", Strategy.DENSE, "body 1")
    bm25_order = leg_order(tmp_path / "b", Strategy.BM25, "body 1")
    assert row["leg_ranks"]["dense"] == {"doc_7": dense_order.index("doc_7") + 1}
    assert row["leg_ranks"]["bm25"] == {"doc_7": bm25_order.index("doc_7") + 1}
    assert dense_order.index("doc_7") + 1 > 1
    assert bm25_order.index("doc_7") + 1 > 1


def test_hybrid_leg_ranks_use_document_rank_and_null_for_absence() -> None:
    from retrieval.test_retriever import make_payload
    from way2australia_rag.evaluation.retrieval_eval import document_leg_ranks
    from way2australia_rag.retrieval.base import validate_request
    from way2australia_rag.retrieval.fusion import FusionConfig
    from way2australia_rag.retrieval.hybrid import HybridRetriever
    from way2australia_rag.retrieval.models import RetrievalResult, RetrievedChunk

    def chunk(doc: str, position: int, rank: int) -> RetrievedChunk:
        payload = make_payload(doc, "text", chunk_position=position)
        return RetrievedChunk(
            rank=rank,
            point_id=f"{doc}-{position}",
            score=1.0 / rank,
            **payload.model_dump(
                include={
                    "document_id",
                    "document_version",
                    "section_id",
                    "chunk_position",
                    "title",
                    "chunk_text",
                    "knowledge_domain",
                    "source_authority",
                    "source_type",
                    "source_url",
                    "content_language",
                    "lote_languages",
                }
            ),
        )

    class Leg:
        def __init__(self, strategy: Strategy, docs: list[tuple[str, int]]) -> None:
            self.strategy = strategy
            self._docs = docs

        def retrieve(self, query_text: str, access: Any, top_k: int = 5):  # noqa: ANN201
            validate_request(query_text, top_k)
            hits = [chunk(d, p, i) for i, (d, p) in enumerate(self._docs, 1)]
            return RetrievalResult(
                hits=hits,
                collection="c",
                index_version="v",
                embedder_model_id="m",
                embedder_revision="r",
                embedder_is_fake=False,
                device=None,
                top_k=top_k,
                latency_ms=1.0,
            )

    # dense: A has two chunks first, then B, then C -> document ranks A=1 B=2 C=3
    dense = Leg(Strategy.DENSE, [("A", 0), ("A", 1), ("B", 0), ("C", 0)])
    bm25 = Leg(Strategy.BM25, [("C", 0), ("C", 1), ("A", 0)])
    fusion = FusionConfig(
        method="rrf", k=60, weights={"dense": 1.0, "bm25": 1.0}, candidate_depth=50
    )
    result = HybridRetriever(dense, bm25, fusion).retrieve("q", None, 1)  # type: ignore[arg-type]
    assert result.leg_document_ranks == {"dense": ["A", "B", "C"], "bm25": ["C", "A"]}
    legs = document_leg_ranks(result)
    assert legs == {
        "dense": {"A": 1, "B": 2, "C": 3},
        "bm25": {"C": 1, "A": 2},
    }


@pytest.mark.parametrize("strategy", [Strategy.BM25, Strategy.HYBRID])
def test_truncation_flag_and_count(tmp_path: Path, strategy: Strategy) -> None:
    long_query = " ".join(f"w{i}" for i in range(70))
    suite = suite_of(
        [
            golden(1, ["doc_1"], query="body 1"),
            golden(2, ["doc_2"], query=long_query),
        ]
    )
    doc = run_strategy(tmp_path, strategy, suite)
    assert [r["query_terms_truncated"] for r in doc["cases"]] == [False, True]
    assert doc["truncated_query_count"] == 1


# ---- CLI --------------------------------------------------------------------


@pytest.fixture
def lexical_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = tmp_path / "lex"
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    return directory


def eval_world(lexical_dir: Path):  # noqa: ANN202
    factory = index_factory(RealStub())
    build_lexical(factory.client, lexical_dir / f"{COLLECTION}.sqlite").close()
    return factory


@pytest.mark.parametrize("strategy", ["dense", "bm25", "hybrid"])
def test_eval_cli_writes_a_2_1_result_without_text(
    tmp_path: Path,
    lexical_env: Path,
    capsys: pytest.CaptureFixture[str],
    strategy: str,
) -> None:
    factory = eval_world(lexical_env)
    out = tmp_path / "r.json"
    assert eval_cli(factory, "--strategy", strategy, "--output", str(out)) == 0
    text = out.read_text(encoding="utf-8")
    doc = json.loads(text)
    assert doc["schema_version"] == "2.1" and doc["retrieval_strategy"] == strategy
    queries = [
        r["query"]
        for kind in ("golden_answerable", "unanswerable_refusal")
        for r in live_suite_rows(kind)
    ]
    assert queries and not any(q in text for q in queries)
    assert "chunk doc_" not in text
    assert str(tmp_path) not in text and str(REPO_ROOT) not in text
    assert f"strategy: {strategy}" in capsys.readouterr().out
    # never overwritten
    assert eval_cli(factory, "--strategy", strategy, "--output", str(out)) == 2
    assert out.read_text(encoding="utf-8") == text


def test_eval_cli_default_strategy_comes_from_the_config(
    tmp_path: Path, lexical_env: Path
) -> None:
    factory = eval_world(lexical_env)
    config = tmp_path / "retrieval.yaml"
    config.write_text(
        (REPO_ROOT / "config/retrieval.yaml")
        .read_text(encoding="utf-8")
        .replace("default_strategy: hybrid", "default_strategy: bm25"),
        encoding="utf-8",
    )
    out = tmp_path / "r.json"
    assert (
        eval_cli(factory, "--retrieval-config", str(config), "--output", str(out)) == 0
    )
    assert json.loads(out.read_text())["retrieval_strategy"] == "bm25"


def test_eval_cli_unknown_strategy_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["retrieval", "--strategy", "semantic"])
    assert exit_info.value.code == 2


@pytest.mark.parametrize("strategy", ["bm25", "hybrid"])
def test_eval_cli_missing_lexical_file_exits_2_and_writes_nothing(
    tmp_path: Path,
    lexical_env: Path,
    capsys: pytest.CaptureFixture[str],
    strategy: str,
) -> None:
    factory = index_factory(RealStub())
    out = tmp_path / "r.json"
    assert eval_cli(factory, "--strategy", strategy, "--output", str(out)) == 2
    err = capsys.readouterr().err
    assert "LexicalIndexBindingError" in err and "make index-lexical" in err
    assert str(tmp_path) not in err
    assert not out.exists()


def test_eval_cli_default_strategy_with_missing_lexical_file_exits_2(
    tmp_path: Path, lexical_env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No `--strategy` and the committed config: the default needs the lexical
    file, and the refusal names `make index-lexical`."""
    assert RETRIEVAL_CONFIG.default_strategy != Strategy.DENSE
    factory = index_factory(RealStub())
    out = tmp_path / "r.json"
    assert eval_cli(factory, "--output", str(out)) == 2
    err = capsys.readouterr().err
    assert "LexicalIndexBindingError" in err and "make index-lexical" in err
    assert str(tmp_path) not in err
    assert not out.exists()


def test_eval_cli_lexical_mismatch_exits_2(
    tmp_path: Path, lexical_env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    factory = index_factory(RealStub())
    build_lexical(factory.client, lexical_env / f"{COLLECTION}.sqlite", drop=1).close()
    out = tmp_path / "r.json"
    assert eval_cli(factory, "--strategy", "hybrid", "--output", str(out)) == 2
    assert "LexicalIndexBindingError" in capsys.readouterr().err
    assert not out.exists()


@pytest.mark.parametrize("strategy", ["dense", "bm25", "hybrid"])
def test_eval_cli_still_refuses_a_fake_embedder(
    tmp_path: Path, lexical_env: Path, strategy: str
) -> None:
    factory = eval_world(lexical_env)
    out = tmp_path / "r.json"
    code = eval_cli(
        factory,
        "--strategy",
        strategy,
        "--output",
        str(out),
        embedder=lambda config, provider: __import__(
            "way2australia_rag.ingestion.embedding", fromlist=["FakeEmbedder"]
        ).FakeEmbedder(),
    )
    assert code == 2 and factory.calls == 0 and not out.exists()


# ---- make retrieve ------------------------------------------------------------


@pytest.fixture
def retrieve_world(lexical_env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):  # noqa: ANN201
    from retrieval.test_cli import Factory, ingest
    from way2australia_rag.lexical.cli import main as lexical_main

    monkeypatch.chdir(tmp_path)
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "QDRANT_COLLECTION_BASE"):
        monkeypatch.delenv(name, raising=False)
    client = QdrantClient(":memory:")
    ingest(client)
    assert lexical_main(["--repo-root", str(REPO_ROOT), "--embedder", "fake"]) == 0
    return Factory(client)


def retrieve(factory, *extra: str, query: str = "Is coaching compulsory?") -> int:  # noqa: ANN001
    return retrieve_cli.main(
        [query, "--repo-root", str(REPO_ROOT), "--embedder", "fake", *extra],
        client_factory=factory,
    )


def test_retrieve_hybrid_prints_strategy_and_leg_ranks(
    retrieve_world, capsys: pytest.CaptureFixture[str]
) -> None:
    assert retrieve(retrieve_world, "--strategy", "hybrid", "--top-k", "3") == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert "strategy=hybrid" in lines[1]
    hits = lines[2:]
    assert 1 <= len(hits) <= 3
    for hit in hits:
        assert re.match(
            r"^\d+  \S+  \S+  -?\d+\.\d{4}  .+  dense=(\d+|-)  bm25=(\d+|-)$", hit
        ), hit


def test_retrieve_bm25_has_no_leg_suffix_and_never_embeds(
    retrieve_world, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from way2australia_rag.ingestion.embedding import FakeEmbedder

    def boom(self: Any, text: str) -> Any:
        raise AssertionError("bm25 must not embed the query")

    monkeypatch.setattr(FakeEmbedder, "embed_query", boom)
    assert retrieve(retrieve_world, "--strategy", "bm25") == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert "strategy=bm25" in lines[1]
    assert lines[2:] and not any("dense=" in line for line in lines[2:])


def test_retrieve_default_strategy_is_the_config_default(
    retrieve_world, capsys: pytest.CaptureFixture[str]
) -> None:
    assert retrieve(retrieve_world) == 0
    out = capsys.readouterr().out.splitlines()[1]
    assert f"strategy={RETRIEVAL_CONFIG.default_strategy.value}" in out


def test_retrieve_prints_a_truncation_note(
    retrieve_world, capsys: pytest.CaptureFixture[str]
) -> None:
    query = " ".join(f"coaching{i}" for i in range(70))
    assert retrieve(retrieve_world, "--strategy", "bm25", query=query) == 0
    assert "first 64 distinct terms" in capsys.readouterr().out


def test_retrieve_missing_lexical_file_exits_2(
    retrieve_world,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(tmp_path / "elsewhere"))
    assert retrieve(retrieve_world, "--strategy", "hybrid") == 2
    err = capsys.readouterr().err
    assert "LexicalIndexBindingError" in err and "make index-lexical" in err
    assert str(tmp_path) not in err


def test_retrieve_default_strategy_with_missing_lexical_file_exits_2(
    retrieve_world,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert RETRIEVAL_CONFIG.default_strategy != Strategy.DENSE
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(tmp_path / "elsewhere"))
    assert retrieve(retrieve_world) == 2  # no --strategy: the committed default
    err = capsys.readouterr().err
    assert "LexicalIndexBindingError" in err and "make index-lexical" in err
    assert str(tmp_path) not in err


def test_retrieve_unknown_strategy_is_a_usage_error(retrieve_world) -> None:  # noqa: ANN001
    with pytest.raises(SystemExit) as exit_info:
        retrieve(retrieve_world, "--strategy", "semantic")
    assert exit_info.value.code == 2


# ---- reading result files ---------------------------------------------------

RESULTS = REPO_ROOT / "experiments/results"


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("retrieval-baseline-idx-v1-20261023T063534Z.json", "1.0"),
        ("retrieval-evaluation-idx-v1-20261024T193140Z.json", "2.0"),
    ],
)
def test_committed_1_0_and_2_0_files_read_as_dense(name: str, version: str) -> None:
    run_ = read_result(RESULTS / name)
    assert run_.schema_version == version
    assert run_.info["retrieval_strategy"] == "dense"
    assert run_.info["lexical"] is None


def test_a_2_1_file_reads_with_strategy_and_lexical(tmp_path: Path) -> None:
    doc = run_strategy(tmp_path / "w", Strategy.HYBRID)
    path = tmp_path / "r.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    run_ = read_result(path)
    assert run_.schema_version == "2.1"
    assert run_.info["retrieval_strategy"] == "hybrid"
    assert run_.info["lexical"]["tokenizer_name"] == "lexical-v1"
    assert len(run_.cases) == len(doc["cases"])
    assert all(row.source_authority is not None for row in run_.cases.values())


def test_runner_requires_fusion_for_hybrid(tmp_path: Path) -> None:
    from way2australia_rag.evaluation.errors import EvaluationConfigurationError

    _c, index, emb, lexical = make_world(tmp_path)
    retriever = build_retriever(Strategy.HYBRID, index, emb, lexical, RETRIEVAL_CONFIG)
    with pytest.raises(EvaluationConfigurationError, match="fusion"):
        run(index, emb, retriever, strategy_suite())
