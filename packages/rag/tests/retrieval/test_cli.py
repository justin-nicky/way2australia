"""Retrieval CLI and shared settings loader tests (Spec 005 R1, R5, R6, R11)."""

import re
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml
from conftest import REPO_ROOT
from qdrant_client import QdrantClient, models
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.retrieval import cli
from way2australia_rag.retrieval.index import DenseIndex

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

SECRET = "super-secret-key"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in (
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION_BASE",
        "W2A_TENANT_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no stray .env


class Factory:
    def __init__(self, client: QdrantClient) -> None:
        self.client = client
        self.calls = 0

    def __call__(self, settings: RuntimeSettings) -> QdrantClient:
        self.calls += 1
        return self.client


def ingest(client: QdrantClient, config: Path | None = None) -> None:
    argv = ["--repo-root", str(REPO_ROOT), "--embedder", "fake"]
    if config is not None:
        argv += ["--config", str(config)]
    assert ingestion_cli.main(argv, client_factory=Factory(client)) == 0


def retrieve(
    factory: Factory, *extra: str, query: str = "Is coaching compulsory?"
) -> int:
    return cli.main(
        [query, "--repo-root", str(REPO_ROOT), "--embedder", "fake", *extra],
        client_factory=factory,
    )


@pytest.fixture
def indexed() -> Factory:
    client = QdrantClient(":memory:")
    ingest(client)
    return Factory(client)


def test_success_prints_header_and_hit_lines(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    assert retrieve(indexed, "--top-k", "3") == 0
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert lines[0].startswith("index: way2australia-idx-v1 (index_version idx-v1;")
    assert "fake=true" in lines[0] and "device=" in lines[0]
    hits = lines[2:]
    assert 1 <= len(hits) <= 3
    assert re.match(r"^1  \S+  \S+  -?\d+\.\d{4}  .+", hits[0])


def test_output_has_no_secret_path_or_chunk_text(
    indexed: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QDRANT_API_KEY", SECRET)
    assert retrieve(indexed) == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert SECRET not in text
    assert str(REPO_ROOT) not in text
    assert not re.search(r"(?<![\w.])/(?:Users|home|tmp|private)/", text)
    chunk_texts = [
        str((r.payload or {})["chunk_text"])
        for r in indexed.client.scroll("way2australia-idx-v1", limit=50)[0]
    ]
    assert chunk_texts
    for chunk in chunk_texts:
        assert chunk[:60] not in text


def test_parser_has_no_role_scope_or_tenant_option() -> None:
    options = {
        option for action in cli._parser()._actions for option in action.option_strings
    }
    assert options == {
        "-h",
        "--help",
        "--repo-root",
        "--config",
        "--top-k",
        "--embedder",
    }
    for flag in ("--role", "--scope", "--tenant", "--tenant-id", "--access-scope"):
        with pytest.raises(SystemExit):
            cli.main(["q", flag, "x"])


@pytest.mark.parametrize(
    "extra, query",
    [
        (("--top-k", "0"), "q"),
        (("--top-k", "51"), "q"),
        ((), "   "),
    ],
)
def test_bad_args_exit_2_without_client(
    extra: tuple[str, ...], query: str, capsys: pytest.CaptureFixture[str]
) -> None:
    factory = Factory(QdrantClient(":memory:"))
    assert retrieve(factory, *extra, query=query) == 2
    assert "RetrievalConfigurationError" in capsys.readouterr().err
    assert factory.calls == 0


def test_bad_config_exit_2_without_client(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    factory = Factory(QdrantClient(":memory:"))
    code = cli.main(
        ["q", "--repo-root", str(REPO_ROOT), "--config", str(tmp_path / "no.yaml")],
        client_factory=factory,
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "IngestionConfigurationError" in err and str(tmp_path) not in err
    assert factory.calls == 0


@pytest.mark.parametrize("value", ["", "   ", "\t"])
def test_empty_tenant_exits_2_for_both_clis(
    value: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", value)
    factory = Factory(QdrantClient(":memory:"))
    assert retrieve(factory) == 2
    retrieval_err = capsys.readouterr().err
    assert "RetrievalConfigurationError" in retrieval_err
    code = ingestion_cli.main(
        ["--repo-root", str(REPO_ROOT), "--embedder", "fake"],
        client_factory=factory,
    )
    assert code == 2
    ingestion_err = capsys.readouterr().err
    assert "IngestionConfigurationError" in ingestion_err
    for err in (retrieval_err, ingestion_err):
        assert "W2A_TENANT_ID" in err
        assert "tenant_id" not in err
    assert factory.calls == 0


def test_settings_error_never_echoes_values(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", "  ")
    monkeypatch.setenv("QDRANT_API_KEY", SECRET)
    assert retrieve(Factory(QdrantClient(":memory:"))) == 2
    assert SECRET not in capsys.readouterr().err


def test_missing_extra_exits_2_with_no_client(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    factory = Factory(QdrantClient(":memory:"))
    code = cli.main(
        ["q", "--repo-root", str(REPO_ROOT), "--embedder", "bge_m3"],
        client_factory=factory,
    )
    assert code == 2
    assert "OptionalDependencyError" in capsys.readouterr().err
    assert factory.calls == 0


def test_unreachable_qdrant_prints_class_name_only(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("QDRANT_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("QDRANT_API_KEY", SECRET)
    code = cli.main(["q", "--repo-root", str(REPO_ROOT), "--embedder", "fake"])
    assert code == 2
    err = capsys.readouterr().err
    assert SECRET not in err and "127.0.0.1" not in err


def test_missing_collection_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert retrieve(Factory(QdrantClient(":memory:"))) == 2
    err = capsys.readouterr().err
    assert "IndexBindingError" in err and "does not exist" in err


def _advice_ok(err: str) -> None:
    assert "config/ingestion.yaml" not in err
    assert "Re-run ingestion" in err


def test_missing_settings_refusal_advice_is_for_retrieval(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    from way2australia_rag.ingestion.store import SETTINGS_COLLECTION_SUFFIX

    indexed.client.delete_collection(
        "way2australia-idx-v1" + SETTINGS_COLLECTION_SUFFIX
    )
    assert retrieve(indexed) == 2
    _advice_ok(capsys.readouterr().err)


def test_malformed_settings_refusal_advice_is_for_retrieval(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    from way2australia_rag.ingestion.store import (
        SETTINGS_COLLECTION_SUFFIX,
        SETTINGS_POINT_ID,
    )

    indexed.client.overwrite_payload(
        "way2australia-idx-v1" + SETTINGS_COLLECTION_SUFFIX,
        payload={"embedder_vector_size": "SECRET-VALUE"},
        points=[SETTINGS_POINT_ID],
    )
    assert retrieve(indexed) == 2
    err = capsys.readouterr().err
    assert "IndexBindingError" in err and "malformed or foreign" in err
    assert "SECRET-VALUE" not in err
    _advice_ok(err)


def test_settings_mismatch_refusal_advice_is_for_retrieval(
    indexed: Factory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = yaml.safe_load((REPO_ROOT / "config/ingestion.yaml").read_text("utf-8"))
    raw["embedder"]["fake_vector_size"] = 32
    changed = tmp_path / "ingestion.yaml"
    changed.write_text(yaml.safe_dump(raw), encoding="utf-8")
    assert retrieve(indexed, "--config", str(changed)) == 2
    err = capsys.readouterr().err
    assert "IndexBindingError" in err and "embedder_vector_size" in err
    _advice_ok(err)


def test_hit_failing_recheck_exits_2(
    indexed: Factory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = DenseIndex.search

    def tampered(self: DenseIndex, *args: Any, **kwargs: Any) -> list[Any]:
        points: list[models.ScoredPoint] = original(self, *args, **kwargs)
        for point in points:
            point.payload = {**(point.payload or {}), "tenant_id": "other"}
        return points

    monkeypatch.setattr(DenseIndex, "search", tampered)
    assert retrieve(indexed) == 2
    err = capsys.readouterr().err
    assert "RetrievalAuthorizationError" in err and "tenant_id" in err


def test_other_tenant_gets_zero_hits_and_exit_0(
    indexed: Factory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", "another-tenant")
    assert retrieve(indexed) == 0
    assert "hits: 0" in capsys.readouterr().out
