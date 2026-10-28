"""Retrieval config validation and the strategy factory (Spec 007 R8)."""

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lexical"))

from conftest import REPO_ROOT
from lexical_support import ingest_dense  # noqa: E402  # pyright: ignore[reportMissingImports]
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.bm25 import BM25Retriever
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.hybrid import HybridRetriever
from way2australia_rag.retrieval.retriever import DenseRetriever
from way2australia_rag.retrieval.strategy import (
    DEFAULT_CONFIG_PATH,
    RetrievalConfig,
    build_retriever,
    load_retrieval_config,
)

GOOD: dict[str, Any] = {
    "schema_version": "1.0",
    "default_strategy": "dense",
    "fusion": {
        "method": "rrf",
        "k": 60,
        "weights": {"dense": 1.0, "bm25": 1.0},
        "candidate_depth": 50,
    },
}


def write(tmp_path: Path, data: Any) -> Path:
    path = tmp_path / "retrieval.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def variant(**changes: Any) -> dict[str, Any]:
    data = yaml.safe_load(yaml.safe_dump(GOOD))
    for key, value in changes.items():
        target = data
        *parents, last = key.split("__")
        for part in parents:
            target = target[part]
        target[last] = value
    return data


def test_committed_config_loads() -> None:
    config = load_retrieval_config(REPO_ROOT / DEFAULT_CONFIG_PATH)
    raw = yaml.safe_load((REPO_ROOT / DEFAULT_CONFIG_PATH).read_text(encoding="utf-8"))
    assert config.default_strategy is Strategy(raw["default_strategy"])
    assert config.fusion.k == 60
    assert config.fusion.weights == {"dense": 1.0, "bm25": 1.0}
    assert config.fusion.candidate_depth == 50
    assert config.fusion.method == "rrf"


def test_good_config_loads(tmp_path: Path) -> None:
    assert isinstance(load_retrieval_config(write(tmp_path, GOOD)), RetrievalConfig)


BAD = [
    ("unknown top-level key", {**GOOD, "extra": 1}, "extra"),
    ("unknown fusion key", variant(fusion__extra=1), "fusion.extra"),
    ("unknown strategy", variant(default_strategy="semantic"), "default_strategy"),
    ("k zero", variant(fusion__k=0), "fusion.k"),
    ("weights missing bm25", variant(fusion__weights={"dense": 1.0}), "fusion.weights"),
    (
        "weights extra leg",
        variant(fusion__weights={"dense": 1, "bm25": 1, "x": 1}),
        "fusion.weights",
    ),
    (
        "weight zero",
        variant(fusion__weights={"dense": 0, "bm25": 1}),
        "fusion.weights",
    ),
    (
        "weight negative",
        variant(fusion__weights={"dense": 1, "bm25": -1}),
        "fusion.weights",
    ),
    ("depth zero", variant(fusion__candidate_depth=0), "fusion.candidate_depth"),
    ("depth 51", variant(fusion__candidate_depth=51), "fusion.candidate_depth"),
    ("method not rrf", variant(fusion__method="linear"), "fusion.method"),
    ("schema version", variant(schema_version="2.0"), "schema_version"),
    ("k bool", variant(fusion__k=True), "fusion.k"),
    ("k quoted", variant(fusion__k="60"), "fusion.k"),
    ("depth quoted", variant(fusion__candidate_depth="50"), "fusion.candidate_depth"),
    ("depth bool", variant(fusion__candidate_depth=True), "fusion.candidate_depth"),
    (
        "weight bool",
        variant(fusion__weights={"dense": True, "bm25": 1}),
        "fusion.weights",
    ),
    (
        "weight quoted",
        variant(fusion__weights={"dense": "1", "bm25": 1}),
        "fusion.weights",
    ),
]


@pytest.mark.parametrize(
    "data,field", [(b[1], b[2]) for b in BAD], ids=[b[0] for b in BAD]
)
def test_invalid_config_is_refused_naming_the_field(
    tmp_path: Path, data: Any, field: str
) -> None:
    with pytest.raises(RetrievalConfigurationError) as caught:
        load_retrieval_config(write(tmp_path, data))
    assert field in str(caught.value)
    assert str(tmp_path) not in str(caught.value)


def test_unreadable_and_non_mapping_files_are_refused(tmp_path: Path) -> None:
    with pytest.raises(RetrievalConfigurationError, match="cannot read"):
        load_retrieval_config(tmp_path / "missing.yaml")
    with pytest.raises(RetrievalConfigurationError, match="mapping"):
        load_retrieval_config(write(tmp_path, ["a"]))


def test_build_retriever_maps_each_strategy(tmp_path: Path) -> None:
    from lexical_support import build_production, open_lexical  # pyright: ignore[reportMissingImports]

    _, dense = ingest_dense()
    target = tmp_path / "lex.sqlite"
    build_production(target)
    lexical = open_lexical(target)
    config = load_retrieval_config(REPO_ROOT / DEFAULT_CONFIG_PATH)
    embedder = FakeEmbedder()
    made = {s: build_retriever(s, dense, embedder, lexical, config) for s in Strategy}
    assert isinstance(made[Strategy.DENSE], DenseRetriever)
    assert isinstance(made[Strategy.BM25], BM25Retriever)
    assert isinstance(made[Strategy.HYBRID], HybridRetriever)
    for strategy, retriever in made.items():
        assert retriever.strategy is strategy
    dense_only = build_retriever(Strategy.DENSE, dense, embedder, None, config)
    assert isinstance(dense_only, DenseRetriever)


@pytest.mark.parametrize("strategy", [Strategy.BM25, Strategy.HYBRID])
def test_lexical_strategies_need_the_lexical_index(strategy: Strategy) -> None:
    _, dense = ingest_dense()
    config = load_retrieval_config(REPO_ROOT / DEFAULT_CONFIG_PATH)
    with pytest.raises(RetrievalConfigurationError, match="lexical"):
        build_retriever(strategy, dense, FakeEmbedder(), None, config)


def test_build_retriever_converts_a_string_value_and_refuses_unknown() -> None:
    _, dense = ingest_dense()
    config = load_retrieval_config(REPO_ROOT / DEFAULT_CONFIG_PATH)
    made = build_retriever("dense", dense, FakeEmbedder(), None, config)  # pyright: ignore[reportArgumentType]
    assert isinstance(made, DenseRetriever)
    with pytest.raises(RetrievalConfigurationError, match="unknown retrieval strategy"):
        build_retriever("semantic", dense, FakeEmbedder(), None, config)  # pyright: ignore[reportArgumentType]
    with pytest.raises(RetrievalConfigurationError, match="lexical"):
        build_retriever("hybrid", dense, FakeEmbedder(), None, config)  # pyright: ignore[reportArgumentType]
