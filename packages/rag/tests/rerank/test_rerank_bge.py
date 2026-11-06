"""BgeRerankerV2M3 adapter. No model is loaded; the real-model test is opt-in."""

import os
import subprocess
import sys

import httpx
import pytest
from huggingface_hub.errors import LocalEntryNotFoundError
from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    OptionalDependencyError,
)
from way2australia_rag.rerank import bge
from way2australia_rag.rerank.bge import BgeRerankerV2M3
from way2australia_rag.rerank.errors import RerankerUnavailableError, RerankSkipReason
from way2australia_rag.retrieval.errors import RetrievalConfigurationError

SHA = "0123456789abcdef0123456789abcdef01234567"


@pytest.fixture
def extra_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bge, "_extra_installed", lambda: True)


@pytest.mark.parametrize("bad", [None, "", "  ", "main", "latest", "MAIN"])
def test_refuses_missing_or_floating_revision(
    extra_installed: None, bad: str | None
) -> None:
    with pytest.raises(IngestionConfigurationError):
        BgeRerankerV2M3(bad)


def test_identity_and_no_load_at_construction(
    extra_installed: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(self: BgeRerankerV2M3) -> None:
        raise AssertionError("model must not load at construction")

    monkeypatch.setattr(BgeRerankerV2M3, "_load_model", fail)
    reranker = BgeRerankerV2M3(SHA, max_length=256)
    assert reranker.info.model_id == "BAAI/bge-reranker-v2-m3"
    assert reranker.info.revision == SHA
    assert reranker.info.max_length == 256
    assert reranker.info.is_fake is False
    assert reranker.device is None


def test_missing_extra_is_refused_naming_the_setup_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bge, "_extra_installed", lambda: False)
    with pytest.raises(OptionalDependencyError, match="make setup-bge-m3"):
        BgeRerankerV2M3(SHA)


def test_missing_extra_at_load(
    extra_installed: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    with pytest.raises(OptionalDependencyError, match="make setup-bge-m3"):
        BgeRerankerV2M3(SHA).load()


def failing(error: Exception) -> type[BgeRerankerV2M3]:
    class Failing(BgeRerankerV2M3):
        def _load_model(self) -> object:
            raise error

    return Failing


def raised(error: Exception) -> BaseException:
    with pytest.raises(BaseException) as caught:
        failing(error)(SHA).load()
    return caught.value


def test_network_failure_at_load_becomes_a_skip_with_the_cause_chain(
    extra_installed: None,
) -> None:
    original = OSError("connect")
    original.__cause__ = httpx.ConnectError("refused")
    error = raised(original)
    assert isinstance(error, RerankerUnavailableError)
    assert error.reason is RerankSkipReason.MODEL_UNAVAILABLE
    assert error.__cause__ is original


def test_timeout_at_load(extra_installed: None) -> None:
    original = OSError("slow")
    original.__cause__ = httpx.ReadTimeout("slow")
    error = raised(original)
    assert isinstance(error, RerankerUnavailableError)
    assert error.reason is RerankSkipReason.MODEL_TIMEOUT


@pytest.mark.parametrize("with_network", [False, True])
def test_offline_not_cached_is_a_configuration_error_with_advice(
    extra_installed: None, with_network: bool
) -> None:
    offline = LocalEntryNotFoundError("nothing cached")
    if with_network:
        offline.__cause__ = httpx.ConnectError("refused")
    original = OSError("load")
    original.__cause__ = offline
    error = raised(original)
    assert isinstance(error, RetrievalConfigurationError)
    assert not isinstance(error, RerankerUnavailableError)
    assert "make setup-bge-m3" in str(error)


def test_unrelated_load_errors_propagate_unchanged(extra_installed: None) -> None:
    original = OSError("corrupt cache")
    assert raised(original) is original


def test_importing_the_adapter_does_not_import_sentence_transformers() -> None:
    code = (
        "import sys, way2australia_rag.rerank.bge, way2australia_rag.rerank.build;"
        "sys.exit(1 if 'sentence_transformers' in sys.modules else 0)"
    )
    assert subprocess.run([sys.executable, "-I", "-c", code]).returncode == 0


@pytest.mark.skipif(
    os.environ.get("W2A_RUN_RERANKER_SMOKE") != "1",
    reason="opt-in real-model smoke test (W2A_RUN_RERANKER_SMOKE=1)",
)
def test_real_model_orders_an_obvious_pair() -> None:  # pragma: no cover
    from conftest import REPO_ROOT
    from way2australia_rag.retrieval.strategy import load_retrieval_config

    config = load_retrieval_config(REPO_ROOT / "config/retrieval.yaml").rerank
    reranker = BgeRerankerV2M3(config.revision, config.max_length, config.batch_size)
    scored = reranker.score(
        "What is the capital of France?",
        ["Paris is the capital of France.", "Bananas are rich in potassium."],
    )
    assert scored.scores[0] > scored.scores[1]
    assert reranker.device is not None
