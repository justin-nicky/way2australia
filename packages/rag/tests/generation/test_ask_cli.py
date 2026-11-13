"""`make ask` CLI (Spec 012 R8) on in-memory fixtures with fake components."""

import asyncio
import re
from pathlib import Path
from typing import Any

import pytest
import yaml
from qdrant_client import QdrantClient
from way2australia_rag.generation import cli
from way2australia_rag.generation.fake import FakeGenerator, FakeMode
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.cli import build_chunker
from way2australia_rag.ingestion.config import RuntimeSettings, load_ingestion_config
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.ingestion.tokenization import FakeTokenizer
from way2australia_rag.lexical.build import (
    build_lexical_index,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import DenseIdentity, LexicalIdentityInput
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval import cli as retrieve_cli
from way2australia_rag.retrieval import opening as opening_mod
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.opening import OpenedRetrieval

from .support import REPO_ROOT, output

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

SECRET = "super-secret-key"
QUERY = "Is coaching compulsory?"
SHARED = ["--embedder", "fake", "--strategy", "dense", "--no-rerank"]


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


@pytest.fixture
def indexed() -> Factory:
    client = QdrantClient(":memory:")
    argv = ["--repo-root", str(REPO_ROOT), "--embedder", "fake"]
    assert ingestion_cli.main(argv, client_factory=Factory(client)) == 0
    return Factory(client)


@pytest.fixture
def hybrid_indexed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Factory:
    """In-memory dense index plus a bound lexical file (real hybrid open path)."""
    config = load_ingestion_config(REPO_ROOT / "config/ingestion.yaml")
    collection = collection_name("way2australia", config.index_version)
    model_id, revision = embedder_identity(config, "fake")
    chunker = build_chunker(config, FakeTokenizer())
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    entries = asyncio.run(
        production_entries(repository, chunker, FakeTokenizer(), None)
    )
    lexical_dir = tmp_path / "lex"
    build_lexical_index(
        entries,
        lexical_index_path(lexical_dir, collection),
        LexicalIdentityInput(
            collection=collection,
            index_version=config.index_version,
            dense_identity=DenseIdentity(
                collection=collection,
                index_version=config.index_version,
                embedder_model_id=model_id,
                embedder_revision=revision,
            ),
            chunker=chunker.identity,
            hash_contract=HASH_CONTRACT,
        ),
    )
    for name in ("QDRANT_URL", "QDRANT_API_KEY", "QDRANT_TENANT_ID", "W2A_TENANT_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "way2australia")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(lexical_dir))
    client = QdrantClient(":memory:")
    argv = ["--repo-root", str(REPO_ROOT), "--embedder", "fake"]
    assert ingestion_cli.main(argv, client_factory=Factory(client)) == 0
    return Factory(client)


def ask(factory: Factory, *argv: str, query: str = QUERY) -> int:
    return cli.main(
        [query, "--repo-root", str(REPO_ROOT), *argv], client_factory=factory
    )


def config_copy(tmp_path: Path, **overrides: Any) -> Path:
    raw = yaml.safe_load((REPO_ROOT / "config/generation.yaml").read_text())
    raw.update(overrides)
    path = tmp_path / "generation.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


def test_fake_generator_answers_and_prints_identity(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ask(indexed, *SHARED, "--generator", "fake") == 0
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert lines[0] == "lote: none"
    assert lines[1] == "status: answered"
    assert any(line.startswith("answer:") for line in lines)
    assert any(re.match(r"^\[S1\] .+ - .+ - .+", line) for line in lines)
    assert any(line.startswith("retrieval: strategy dense") for line in lines)
    generator_line = next(line for line in lines if line.startswith("generator:"))
    assert (
        generator_line.startswith("generator: fake (") and "fake=true" in generator_line
    )
    assert any(re.match(r"^prompt: answer v1 [0-9a-f]{12}$", x) for x in lines)
    assert any(line.startswith("tokens: in ") for line in lines)
    assert any(line.startswith("latency: retrieval_ms ") for line in lines)
    assert cli.FAKE_WARNING in captured.err


def test_no_generator_and_null_default_exits_two_without_touching_qdrant(
    indexed: Factory, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    path = config_copy(tmp_path, default_generator=None)
    assert ask(indexed, *SHARED, "--generation-config", str(path)) == 2
    err = capsys.readouterr().err
    assert "--generator fake" in err and "--generator bedrock" in err
    assert indexed.calls == 0


def test_the_committed_default_is_read_from_the_file_not_a_literal(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    default = yaml.safe_load((REPO_ROOT / "config/generation.yaml").read_text())[
        "default_generator"
    ]
    code = ask(indexed, *SHARED)
    if default is None:  # D-C until T6
        assert code == 2
        assert "--generator" in capsys.readouterr().err
    else:  # T6 replaces this test with the configured-provider stub test
        pytest.skip("a default generator is committed; T6 owns this test")


def test_bedrock_without_a_model_id_exits_two(
    indexed: Factory, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    raw = yaml.safe_load((REPO_ROOT / "config/generation.yaml").read_text())
    raw["bedrock"]["model_id"] = None
    path = tmp_path / "generation.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    code = ask(
        indexed, *SHARED, "--generator", "bedrock", "--generation-config", str(path)
    )
    assert code == 2
    assert "--model-id" in capsys.readouterr().err
    assert indexed.calls == 0


@pytest.mark.parametrize(
    ("mode", "status", "needle"),
    [
        (FakeMode.DECLINE, "insufficient_evidence", "message (en): "),
        (FakeMode.UNKNOWN_ID, "insufficient_evidence", "sub_reason: unknown_id"),
        (FakeMode.UNAVAILABLE, "evidence_only", "sub_reason: connection"),
    ],
)
def test_every_status_exits_zero_and_generator_and_retrieval_close(
    indexed: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    mode: FakeMode,
    status: str,
    needle: str,
) -> None:
    built: list[FakeGenerator] = []

    def build(*_: Any, **__: Any) -> FakeGenerator:
        built.append(FakeGenerator(mode))
        return built[0]

    monkeypatch.setattr(cli, "build_generator", build)
    assert ask(indexed, *SHARED) == 0
    out = capsys.readouterr().out
    assert f"status: {status}" in out and needle in out
    assert built[0].closed


def test_the_answer_is_printed_through_safe_text(
    indexed: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Hostile(FakeGenerator):
        def generate(self, prompt: Any) -> Any:
            return output("ok \x1b[31mred\x1b[0m [S1]\n‮fake: line [S1]", ["S1"])

    monkeypatch.setattr(cli, "build_generator", lambda *_a, **_k: Hostile())
    assert ask(indexed, *SHARED) == 0
    out = capsys.readouterr().out
    assert "\x1b" not in out and "‮" not in out
    assert "  ok red [S1]" in out and "  fake: line [S1]" in out


def test_configuration_errors_exit_two(
    indexed: Factory, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    assert ask(indexed, *SHARED, "--generator", "fake", query="   ") == 2
    assert ask(indexed, *SHARED, "--generator", "fake", "--top-k", "0") == 2
    missing = tmp_path / "missing.yaml"
    assert (
        ask(
            indexed, *SHARED, "--generator", "fake", "--generation-config", str(missing)
        )
        == 2
    )
    assert "ERROR GeneratorConfigurationError" in capsys.readouterr().err


def test_output_has_no_secret_path_or_unlisted_chunk_text(
    indexed: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QDRANT_API_KEY", SECRET)
    assert ask(indexed, *SHARED, "--generator", "fake") == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert SECRET not in text
    assert str(REPO_ROOT) not in text
    assert not re.search(r"(?<![\w.])/(?:Users|home|tmp|private)/", text)


def test_parser_extends_the_retrieval_options_without_role_scope_or_tenant() -> None:
    options = {o for a in cli._parser()._actions for o in a.option_strings}
    retrieval = {o for a in retrieve_cli._parser()._actions for o in a.option_strings}
    assert options == retrieval | {"--generator", "--model-id", "--generation-config"}
    assert not {o for o in options if re.search(r"role|scope|tenant", o)}


def test_hybrid_with_fake_reranker_closes_retrieval_on_success(
    hybrid_indexed: Factory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    opened: list[OpenedRetrieval] = []
    real_open = opening_mod.open_retrieval

    def track_open(*args: Any, **kwargs: Any) -> OpenedRetrieval:
        opened.append(real_open(*args, **kwargs))
        return opened[-1]

    monkeypatch.setattr(cli, "open_retrieval", track_open)
    assert (
        ask(
            hybrid_indexed,
            "--embedder",
            "fake",
            "--strategy",
            "hybrid",
            "--reranker",
            "fake",
            "--generator",
            "fake",
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "strategy hybrid" in out and "fake=true" in out
    assert opened and opened[0].lexical is None


def test_hybrid_closes_retrieval_when_answer_errors(
    hybrid_indexed: Factory, monkeypatch: pytest.MonkeyPatch
) -> None:
    from way2australia_rag.generation.service import AnswerService

    opened: list[OpenedRetrieval] = []
    real_open = opening_mod.open_retrieval

    def track_open(*args: Any, **kwargs: Any) -> OpenedRetrieval:
        opened.append(real_open(*args, **kwargs))
        return opened[-1]

    monkeypatch.setattr(cli, "open_retrieval", track_open)

    def fail(*_a: Any, **_k: Any) -> None:
        raise RetrievalError("injected")

    monkeypatch.setattr(AnswerService, "answer", fail)
    assert (
        ask(
            hybrid_indexed,
            "--embedder",
            "fake",
            "--strategy",
            "hybrid",
            "--reranker",
            "fake",
            "--generator",
            "fake",
        )
        == 2
    )
    assert opened and opened[0].lexical is None


def test_make_retrieve_output_is_unchanged_by_the_shared_helper(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = [QUERY, "--repo-root", str(REPO_ROOT), *SHARED, "--top-k", "3"]
    assert retrieve_cli.main(argv, client_factory=indexed) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "lote: none"
    assert lines[1].startswith("index: ")
    assert re.match(r"^hits: \d+ \(strategy=dense, top_k 3, [\d.]+ ms\)$", lines[2])
    assert lines[-1] == "rerank: off"


def test_anthropic_without_a_model_id_exits_two(
    indexed: Factory, capsys: pytest.CaptureFixture[str]
) -> None:
    code = ask(indexed, *SHARED, "--generator", "anthropic")
    assert code == 2
    assert "--model-id" in capsys.readouterr().err
    assert indexed.calls == 0


def test_help_and_advice_name_all_three_generators(
    indexed: Factory, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    assert "anthropic" in cli._parser().format_help()
    path = config_copy(tmp_path, default_generator=None)
    assert ask(indexed, *SHARED, "--generation-config", str(path)) == 2
    assert "--generator anthropic" in capsys.readouterr().err


def test_generator_line_prints_the_response_model(
    indexed: Factory,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Named(FakeGenerator):
        def generate(self, prompt: Any) -> Any:
            return output("ok [S1]", ["S1"]).model_copy(
                update={"response_model": "claude-sonnet-5-5"}
            )

    monkeypatch.setattr(cli, "build_generator", lambda *_a, **_k: Named())
    assert ask(indexed, *SHARED) == 0
    line = next(
        x for x in capsys.readouterr().out.splitlines() if x.startswith("generator:")
    )
    assert "response model claude-sonnet-5-5" in line
