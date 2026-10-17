"""Config, settings, baseline agreement and CLI tests (Spec 004 R11, R12)."""

import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_core.documents import AccessScope
from way2australia_rag.ingestion.cli import main
from way2australia_rag.ingestion.config import (
    RuntimeSettings,
    load_ingestion_config,
)
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentValidationError,
    LocalRepositoryConfig,
)

CONFIG = REPO_ROOT / "config/ingestion.yaml"
BASELINE = REPO_ROOT / "experiments/configs/day1_baseline.yaml"
PINNED = "5617a9f61b028005a4858fdac845db406aefb181"

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "QDRANT_COLLECTION_BASE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no stray .env


# --- config -----------------------------------------------------------------


def test_real_config_loads_with_pinned_revision() -> None:
    config = load_ingestion_config(CONFIG)
    assert config.embedder.revision == PINNED
    assert config.embedder.model_id == "BAAI/bge-m3"
    assert config.index_version == "idx-v1"
    assert (config.chunker.name, config.chunker.version) == ("heading", "1")


def _write(tmp_path: Path, **embedder_overrides: object) -> Path:
    raw = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    raw["embedder"].update(embedder_overrides)
    path = tmp_path / "ingestion.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


@pytest.mark.parametrize("bad", ["", "main", "latest", "Main"])
def test_config_refuses_missing_or_floating_revision(tmp_path: Path, bad: str) -> None:
    with pytest.raises(IngestionConfigurationError, match="revision"):
        load_ingestion_config(_write(tmp_path, revision=bad))


def test_config_refuses_unknown_field_and_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "x.yaml"
    path.write_text("schema_version: '1.0'\nsurprise: 1\n", encoding="utf-8")
    with pytest.raises(IngestionConfigurationError) as info:
        load_ingestion_config(path)
    assert str(tmp_path) not in str(info.value)
    with pytest.raises(IngestionConfigurationError) as missing:
        load_ingestion_config(tmp_path / "absent.yaml")
    assert str(tmp_path) not in str(missing.value)


def test_runtime_settings_defaults_and_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    defaults = RuntimeSettings()
    assert defaults.qdrant_url == "http://localhost:6333"
    assert defaults.collection_base == "way2australia"
    assert defaults.qdrant_api_key is None
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("QDRANT_API_KEY", "super-secret-key")
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "throwaway")
    settings = RuntimeSettings()
    assert settings.qdrant_url == ":memory:"
    assert settings.collection_base == "throwaway"
    assert settings.qdrant_api_key is not None
    assert settings.qdrant_api_key.get_secret_value() == "super-secret-key"
    assert "super-secret-key" not in repr(settings)


# --- agreement with experiments/configs/day1_baseline.yaml -------------------


def test_agrees_with_day1_baseline() -> None:
    baseline = yaml.safe_load(BASELINE.read_text(encoding="utf-8"))
    config = load_ingestion_config(CONFIG)
    assert config.embedder.model_id == baseline["embedding"]["model"]
    assert (
        baseline["corpus"]["manifest"]
        == LocalRepositoryConfig(repo_root=REPO_ROOT).manifest_path
    )
    assert {s.value for s in GUEST_PUBLIC_POLICY.allowed_access_scopes} == {
        baseline["corpus"]["required_access_scope"]
    }
    assert baseline["corpus"]["required_access_scope"] == AccessScope.PUBLIC.value


# --- CLI ----------------------------------------------------------------------


def _factory(client: QdrantClient):  # type: ignore[no-untyped-def]
    return lambda _settings: client


def _run(client: QdrantClient, *extra: str, config: Path | None = None) -> int:
    args = ["--repo-root", str(REPO_ROOT), "--embedder", "fake", *extra]
    if config is not None:
        args += ["--config", str(config)]
    return main(args, client_factory=_factory(client))


def test_exit_0_then_idempotent_second_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = QdrantClient(":memory:")
    assert _run(client) == 0
    first = capsys.readouterr().out
    assert "added: 13  updated: 0  unchanged: 0  deleted: 0" in first
    assert "fake=true" in first
    assert "way2australia-idx-v1" in first
    assert _run(client) == 0
    second = capsys.readouterr().out
    assert "added: 0  updated: 0  unchanged: 13  deleted: 0" in second


def test_summary_and_errors_have_no_absolute_paths(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("QDRANT_API_KEY", "super-secret-key")
    assert _run(QdrantClient(":memory:")) == 0
    captured = capsys.readouterr()
    for text in (captured.out, captured.err):
        assert str(REPO_ROOT) not in text
        assert "super-secret-key" not in text
        assert not re.search(r"(?<![\w.])/(?:Users|home|tmp|private)/", text)


def test_exit_1_on_document_failure(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class Failing:
        def __init__(self) -> None:
            self.info = FakeEmbedder().info

        def embed_documents(self, texts):  # type: ignore[no-untyped-def]
            raise RuntimeError("boom with secret document text")

        def embed_query(self, text: str) -> list[float]:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "way2australia_rag.ingestion.cli.build_embedder", lambda *_: Failing()
    )
    assert _run(QdrantClient(":memory:")) == 1
    out = capsys.readouterr().out
    assert "ERROR " in out
    assert "RuntimeError" in out
    assert "secret document text" not in out


def test_exit_2_on_settings_mismatch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    client = QdrantClient(":memory:")
    assert _run(client) == 0
    capsys.readouterr()
    changed = _write(tmp_path, fake_vector_size=32)
    assert _run(client, config=changed) == 2
    err = capsys.readouterr().err
    assert "IndexSettingsMismatchError" in err
    assert "index_version" in err
    assert str(tmp_path) not in err


def test_exit_2_when_optional_group_missing_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    client = QdrantClient(":memory:")
    with (
        patch.object(client, "delete") as delete,
        patch.object(client, "create_collection") as create,
        patch.object(client, "upsert") as upsert,
    ):
        code = main(
            ["--repo-root", str(REPO_ROOT), "--embedder", "bge_m3"],
            client_factory=_factory(client),
        )
    assert code == 2
    err = capsys.readouterr().err
    assert "OptionalDependencyError" in err
    assert "make setup-bge-m3" in err
    assert client.get_collections().collections == []
    create.assert_not_called()
    delete.assert_not_called()
    upsert.assert_not_called()


def test_repository_error_message_is_printed_without_paths(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def bad_run(self: object) -> None:
        raise DocumentValidationError("doc-x", "effective_date", "not a date")

    monkeypatch.setattr("way2australia_rag.ingestion.cli.IngestionService.run", bad_run)
    assert _run(QdrantClient(":memory:")) == 2
    err = capsys.readouterr().err
    assert "doc-x: effective_date: not a date" in err
    assert str(REPO_ROOT) not in err
    assert not re.search(r"(?<![\w.])/(?:Users|home|tmp|private)/", err)


def test_exit_2_on_bad_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    client = QdrantClient(":memory:")
    assert _run(client, config=_write(tmp_path, revision="main")) == 2
    assert "revision" in capsys.readouterr().err
    assert _run(client, config=tmp_path / "absent.yaml") == 2
    assert str(tmp_path) not in capsys.readouterr().err


def test_exit_2_when_qdrant_unreachable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("QDRANT_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("QDRANT_API_KEY", "super-secret-key")
    code = main(["--repo-root", str(REPO_ROOT), "--embedder", "fake"])
    assert code == 2
    err = capsys.readouterr().err
    assert "super-secret-key" not in err
    assert "127.0.0.1" not in err


def test_builds_exactly_one_embedder_per_run(monkeypatch: pytest.MonkeyPatch) -> None:
    from way2australia_rag.ingestion import cli

    calls: list[str] = []
    original = cli.build_embedder

    def counting(config, provider):  # type: ignore[no-untyped-def]
        calls.append(provider)
        return original(config, provider)

    monkeypatch.setattr(cli, "build_embedder", counting)
    assert _run(QdrantClient(":memory:")) == 0
    assert calls == ["fake"]


def test_collection_base_comes_from_environment(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "throwaway")
    assert _run(QdrantClient(":memory:")) == 0
    assert "index: throwaway-idx-v1" in capsys.readouterr().out
