"""Chunk tokenizers aligned with embedders (Spec 009 R1).

Counts match what the embedder would see, including special tokens. BGE-M3 uses
the ``tokenizers`` library only; PyTorch and ``sentence-transformers`` are never
imported here.
"""

from __future__ import annotations

import json
import os
import unicodedata
from math import ceil
from typing import Protocol

from pydantic import BaseModel, ConfigDict
from tokenizers import Tokenizer

from way2australia_rag.ingestion.config import EmbedderConfig
from way2australia_rag.ingestion.errors import IngestionConfigurationError

_FLOATING_REVISIONS = frozenset({"main", "latest"})

BGE_M3_TOKENIZER_NAME = "bge-m3"
FAKE_TOKENIZER_NAME = "fake"
FAKE_TOKENIZER_MODEL_ID = "fake-tokenizer"
FAKE_TOKENIZER_REVISION = "1"
DEFAULT_FAKE_MAX_SEQUENCE_LENGTH = 512

_TOKENIZER_FILES = ("tokenizer.json", "sentence_bert_config.json")


class TokenizerIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    model_id: str
    revision: str
    max_sequence_length: int


class ChunkTokenizer(Protocol):
    identity: TokenizerIdentity

    def count(self, text: str) -> int: ...


class FakeTokenizer:
    """Deterministic token counts for the fake embedder; no files or network."""

    def __init__(
        self, max_sequence_length: int = DEFAULT_FAKE_MAX_SEQUENCE_LENGTH
    ) -> None:
        if max_sequence_length < 1:
            raise IngestionConfigurationError(
                "fake_max_sequence_length must be at least 1."
            )
        self.identity = TokenizerIdentity(
            name=FAKE_TOKENIZER_NAME,
            model_id=FAKE_TOKENIZER_MODEL_ID,
            revision=FAKE_TOKENIZER_REVISION,
            max_sequence_length=max_sequence_length,
        )

    def count(self, text: str) -> int:
        normalized = unicodedata.normalize("NFKC", text)
        words = normalized.split()
        return 2 + sum(ceil(len(word) / 4) for word in words)


def _tokenizer_config_error(
    model_id: str, revision: str
) -> IngestionConfigurationError:
    return IngestionConfigurationError(
        f"cannot load tokenizer for {model_id} @ {revision}; "
        "run `make setup-bge-m3` once with network access, or use a populated "
        "Hugging Face cache."
    )


def _download_hub_file(model_id: str, filename: str, revision: str) -> str:
    try:
        from huggingface_hub import hf_hub_download as _hf_hub_download
    except ImportError as exc:
        raise IngestionConfigurationError(
            "the tokenizers dependency is missing; reinstall the project."
        ) from exc
    try:
        return _hf_hub_download(
            model_id, filename, revision=revision, local_files_only=True
        )
    except Exception:
        if os.environ.get("HF_HUB_OFFLINE"):
            raise _tokenizer_config_error(model_id, revision) from None
        try:
            return _hf_hub_download(model_id, filename, revision=revision)
        except Exception:
            raise _tokenizer_config_error(model_id, revision) from None


class BgeM3Tokenizer:
    """BGE-M3 tokenizer files at a pinned revision; no model weights."""

    def __init__(self, model_id: str, revision: str | None) -> None:
        cleaned = (revision or "").strip()
        if not cleaned or cleaned.lower() in _FLOATING_REVISIONS:
            raise IngestionConfigurationError(
                "BGE-M3 tokenizer requires a pinned model revision (a full commit "
                "SHA); a missing revision, 'main' or 'latest' is refused."
            )
        self._model_id = model_id
        self._revision = cleaned
        paths = {
            name: _download_hub_file(model_id, name, cleaned)
            for name in _TOKENIZER_FILES
        }
        try:
            config_text = open(
                paths["sentence_bert_config.json"], encoding="utf-8"
            ).read()
            config = json.loads(config_text)
        except (OSError, json.JSONDecodeError, TypeError):
            raise _tokenizer_config_error(model_id, cleaned) from None
        try:
            max_sequence_length = int(config["max_seq_length"])
        except (KeyError, TypeError, ValueError):
            raise _tokenizer_config_error(model_id, cleaned) from None
        if max_sequence_length < 1:
            raise _tokenizer_config_error(model_id, cleaned) from None
        try:
            self._tokenizer = Tokenizer.from_file(paths["tokenizer.json"])
        except Exception:
            raise _tokenizer_config_error(model_id, cleaned) from None
        self.identity = TokenizerIdentity(
            name=BGE_M3_TOKENIZER_NAME,
            model_id=model_id,
            revision=cleaned,
            max_sequence_length=max_sequence_length,
        )

    def count(self, text: str) -> int:
        encoded = self._tokenizer.encode(text)
        return len(encoded.ids)


def embedder_for_run(embedder: EmbedderConfig, provider: str) -> EmbedderConfig:
    """Embedder block for tokenizer construction when CLI overrides ``provider``."""
    if embedder.provider == provider:
        return embedder
    return embedder.model_copy(update={"provider": provider})


def build_tokenizer(embedder: EmbedderConfig) -> ChunkTokenizer:
    """The only constructor: tokenizer identity always matches the embedder config."""
    if embedder.provider == "fake":
        return FakeTokenizer(embedder.fake_max_sequence_length)
    if embedder.provider == "bge_m3":
        return BgeM3Tokenizer(embedder.model_id, embedder.revision)
    raise IngestionConfigurationError(
        f"unsupported embedder provider '{embedder.provider}'."
    )
