"""Chunk tokenizer tests (Spec 009 R1)."""

import importlib
import importlib.util
import os
import sys
from pathlib import Path

import pytest
from conftest import REPO_ROOT
from way2australia_rag.ingestion.bge_m3 import BGE_M3_MODEL_ID
from way2australia_rag.ingestion.config import EmbedderConfig, load_ingestion_config
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.tokenization import (
    BgeM3Tokenizer,
    FakeTokenizer,
    build_tokenizer,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "bge_m3"
SHA = "0123456789abcdef0123456789abcdef01234567"


def test_fake_counts_english_malayalam_and_empty() -> None:
    tokenizer = FakeTokenizer()
    assert tokenizer.count("") == 2
    assert tokenizer.count("hello world") == 6
    assert tokenizer.count("NAATI CCL പരീക്ഷ") == 7


def test_build_tokenizer_dispatch_fake_and_bge_m3(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_cfg = EmbedderConfig(
        provider="fake",
        model_id="ignored",
        revision="1",
        batch_size=1,
        normalize=True,
        fake_vector_size=8,
        fake_max_sequence_length=64,
    )
    fake = build_tokenizer(fake_cfg)
    assert fake.identity.name == "fake"
    assert fake.identity.max_sequence_length == 64

    def fake_download(
        repo_id: str, filename: str, *, revision: str, local_files_only: bool = False
    ) -> str:
        return str(FIXTURE_DIR / filename)

    monkeypatch.setattr("huggingface_hub.hf_hub_download", fake_download)
    bge_cfg = EmbedderConfig(
        provider="bge_m3",
        model_id=BGE_M3_MODEL_ID,
        revision=SHA,
        batch_size=1,
        normalize=True,
        fake_vector_size=8,
    )
    bge = build_tokenizer(bge_cfg)
    assert bge.identity.name == "bge-m3"
    assert bge.identity.max_sequence_length == 128


@pytest.fixture
def hub(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(
        repo_id: str,
        filename: str,
        *,
        revision: str,
        local_files_only: bool = False,
    ) -> str:
        if revision != SHA:
            raise OSError("revision mismatch")
        return str(FIXTURE_DIR / filename)

    monkeypatch.setattr("huggingface_hub.hf_hub_download", fake_download)


def test_bge_m3_cache_hit_counts(hub: None) -> None:
    tokenizer = BgeM3Tokenizer(BGE_M3_MODEL_ID, SHA)
    assert tokenizer.count("hello world") >= 1


def test_bge_m3_miss_offline_refused(
    hub: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    def miss(*_a: object, **_k: object) -> str:
        raise OSError("missing")

    monkeypatch.setattr("huggingface_hub.hf_hub_download", miss)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    with pytest.raises(IngestionConfigurationError) as caught:
        BgeM3Tokenizer(BGE_M3_MODEL_ID, SHA)
    message = str(caught.value)
    assert BGE_M3_MODEL_ID in message and SHA in message
    assert "http" not in message.lower() and ".cache" not in message


def test_bge_m3_miss_online_download(
    hub: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[bool] = []

    def download(
        repo_id: str,
        filename: str,
        *,
        revision: str,
        local_files_only: bool = False,
    ) -> str:
        calls.append(local_files_only)
        if local_files_only:
            raise OSError("missing")
        return str(FIXTURE_DIR / filename)

    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    monkeypatch.setattr("huggingface_hub.hf_hub_download", download)
    BgeM3Tokenizer(BGE_M3_MODEL_ID, SHA)
    assert calls == [True, False, True, False]


def test_bge_m3_wrong_revision_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_revision(*_a: object, **_k: object) -> str:
        raise OSError("bad revision")

    monkeypatch.setattr("huggingface_hub.hf_hub_download", bad_revision)
    with pytest.raises(IngestionConfigurationError) as caught:
        BgeM3Tokenizer(BGE_M3_MODEL_ID, SHA)
    assert "http" not in str(caught.value).lower() and ".cache" not in str(caught.value)


@pytest.mark.parametrize("bad", [None, "", "main", "latest"])
def test_bge_m3_refuses_floating_revision(bad: str | None) -> None:
    with pytest.raises(IngestionConfigurationError):
        BgeM3Tokenizer(BGE_M3_MODEL_ID, bad)


def test_import_pin_never_loads_torch_or_sentence_transformers(
    hub: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("torch", "sentence_transformers"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    before = set(sys.modules)
    importlib.reload(
        importlib.import_module("way2australia_rag.ingestion.tokenization")
    )
    BgeM3Tokenizer(BGE_M3_MODEL_ID, SHA)
    heavy = {"torch", "sentence_transformers"}
    assert not heavy & (set(sys.modules) - before)


@pytest.mark.skipif(
    os.environ.get("W2A_RUN_BGE_M3_SMOKE") != "1",
    reason="set W2A_RUN_BGE_M3_SMOKE=1 (after `make setup-bge-m3`)",
)
@pytest.mark.skipif(
    importlib.util.find_spec("sentence_transformers") is None,
    reason="optional 'bge-m3' group not installed",
)
def test_bge_m3_smoke_matches_sentence_transformer_tokenizer() -> None:
    revision = load_ingestion_config(
        REPO_ROOT / "config/ingestion.yaml"
    ).embedder.revision
    tokenizer = BgeM3Tokenizer(BGE_M3_MODEL_ID, revision)
    from sentence_transformers import SentenceTransformer  # pyright: ignore

    model = SentenceTransformer(BGE_M3_MODEL_ID, revision=revision)
    english = "How do I prepare for the NAATI CCL test?"
    malayalam = "NAATI CCL പരീക്ഷയ്ക്ക് എങ്ങനെ തയ്യാറെടുക്കാം?"
    for text in (english, malayalam):
        assert tokenizer.count(text) == len(model.tokenizer(text)["input_ids"])
    assert tokenizer.identity.max_sequence_length == model.max_seq_length
