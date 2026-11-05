"""RerankConfig, schema 1.3 and the reranker factory (Spec 011 R2, R3)."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from conftest import REPO_ROOT
from way2australia_rag.rerank import bge
from way2australia_rag.rerank.bge import BgeRerankerV2M3
from way2australia_rag.rerank.build import build_reranker
from way2australia_rag.rerank.fake import FakeReranker
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.strategy import (
    DEFAULT_CONFIG_PATH,
    RerankConfig,
    load_retrieval_config,
)

SHA = "0123456789abcdef0123456789abcdef01234567"
BASE: dict[str, Any] = {
    "default_strategy": "hybrid",
    "fusion": {
        "method": "rrf",
        "k": 60,
        "weights": {"dense": 1.0, "bm25": 1.0},
        "candidate_depth": 30,
    },
    "qdrant": {"connect_timeout_s": 2, "query_timeout_s": 3},
}
RERANK: dict[str, Any] = {
    "enabled": True,
    "provider": "bge",
    "model_id": "BAAI/bge-reranker-v2-m3",
    "revision": SHA,
    "depth": 20,
    "max_length": 512,
    "batch_size": 16,
}


def write(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "retrieval.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def v13(**rerank: Any) -> dict[str, Any]:
    return {**BASE, "schema_version": "1.3", "rerank": {**RERANK, **rerank}}


def test_committed_file_is_1_3_with_reranking_off_and_a_pinned_revision() -> None:
    path = REPO_ROOT / DEFAULT_CONFIG_PATH
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = load_retrieval_config(path)
    assert raw["schema_version"] == "1.3"
    assert raw["rerank"]["enabled"] is False
    assert config.rerank.enabled is False
    assert config.rerank.model_id == "BAAI/bge-reranker-v2-m3"
    revision = config.rerank.revision or ""
    assert len(revision) == 40 and set(revision) <= set("0123456789abcdef")


def test_1_3_loads_all_fields(tmp_path: Path) -> None:
    config = load_retrieval_config(write(tmp_path, v13()))
    assert config.rerank == RerankConfig.model_validate(RERANK)


@pytest.mark.parametrize("version", ["1.1", "1.2"])
def test_older_schemas_load_with_reranking_off(tmp_path: Path, version: str) -> None:
    config = load_retrieval_config(write(tmp_path, {**BASE, "schema_version": version}))
    assert config.rerank.enabled is False


@pytest.mark.parametrize("version", ["1.1", "1.2"])
def test_older_schemas_refuse_a_rerank_block(tmp_path: Path, version: str) -> None:
    data = {**BASE, "schema_version": version, "rerank": RERANK}
    with pytest.raises(RetrievalConfigurationError, match="rerank"):
        load_retrieval_config(write(tmp_path, data))


def test_1_3_requires_the_block(tmp_path: Path) -> None:
    with pytest.raises(RetrievalConfigurationError, match="rerank"):
        load_retrieval_config(write(tmp_path, {**BASE, "schema_version": "1.3"}))


@pytest.mark.parametrize(
    ("changes", "key"),
    [
        ({"depth": 31}, "rerank.depth"),  # above candidate_depth 30
        ({"depth": 0}, "rerank.depth"),
        ({"max_length": 31}, "rerank.max_length"),
        ({"max_length": 8193}, "rerank.max_length"),
        ({"batch_size": 0}, "rerank.batch_size"),
        ({"batch_size": 257}, "rerank.batch_size"),
        ({"revision": "main"}, "rerank.revision"),
        ({"revision": "latest"}, "rerank.revision"),
        ({"revision": " "}, "rerank.revision"),
        ({"revision": None}, "rerank.revision"),
        ({"provider": "other"}, "rerank.provider"),
        ({"surprise": 1}, "rerank.surprise"),
    ],
)
def test_invalid_values_are_refused_naming_the_key(
    tmp_path: Path, changes: dict[str, Any], key: str
) -> None:
    with pytest.raises(RetrievalConfigurationError) as caught:
        load_retrieval_config(write(tmp_path, v13(**changes)))
    assert key in str(caught.value)
    assert str(tmp_path) not in str(caught.value)


def test_disabled_block_may_omit_the_revision(tmp_path: Path) -> None:
    config = load_retrieval_config(write(tmp_path, v13(enabled=False, revision=None)))
    assert config.rerank.revision is None


def test_factory_builds_fake_and_bge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bge, "_extra_installed", lambda: True)
    config = RerankConfig.model_validate(RERANK)
    assert isinstance(build_reranker(config), BgeRerankerV2M3)
    fake = build_reranker(config, "fake")
    assert isinstance(fake, FakeReranker) and fake.info.is_fake
    assert fake.info.max_length == config.max_length
    with pytest.raises(RetrievalConfigurationError):
        build_reranker(config, "nope")
