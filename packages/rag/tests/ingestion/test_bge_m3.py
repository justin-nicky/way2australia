"""BGE-M3 adapter tests. No model is loaded; the real-model test is opt-in."""

import importlib
import importlib.util
import math
import os
import sys

import pytest
from way2australia_rag.ingestion.bge_m3 import BgeM3Embedder
from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    OptionalDependencyError,
)

SHA = "0123456789abcdef0123456789abcdef01234567"


@pytest.mark.parametrize("bad", [None, "", "  ", "main", "latest", "MAIN"])
def test_refuses_missing_or_floating_revision(bad: str | None) -> None:
    with pytest.raises(IngestionConfigurationError):
        BgeM3Embedder(bad)


def test_reports_pinned_revision_and_identity() -> None:
    info = BgeM3Embedder(SHA).info
    assert info.revision == SHA
    assert info.model_id == "BAAI/bge-m3"
    assert info.vector_size == 1024
    assert info.normalize is True
    assert info.is_fake is False


def test_constructing_does_not_load_the_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    BgeM3Embedder(SHA)  # must not raise: loading is lazy


def test_missing_group_raises_optional_dependency_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)  # simulate absent
    embedder = BgeM3Embedder(SHA)
    with pytest.raises(OptionalDependencyError, match="make setup-bge-m3"):
        embedder.embed_documents(["hello"])


def test_module_import_works_without_the_group(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    module = importlib.reload(
        importlib.import_module("way2australia_rag.ingestion.bge_m3")
    )
    assert module.BgeM3Embedder is not None


def test_model_loaded_once_with_revision_and_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []
    encodes: list[int] = []

    class FakeModel:
        def encode(self, texts: list[str], **kwargs: object) -> list[list[float]]:
            encodes.append(int(kwargs["batch_size"]))  # type: ignore[call-overload]
            assert kwargs["normalize_embeddings"] is True
            return [[1.0, 0.0] for _ in texts]

    def fake_loader(self: BgeM3Embedder) -> FakeModel:
        calls.append((self.info.model_id, self.info.revision))
        return FakeModel()

    monkeypatch.setattr(BgeM3Embedder, "_load_model", fake_loader)
    embedder = BgeM3Embedder(SHA, batch_size=4)
    assert embedder.embed_documents(["a", "b"]) == [[1.0, 0.0], [1.0, 0.0]]
    assert embedder.embed_query("c") == [1.0, 0.0]
    assert embedder.embed_documents([]) == []
    assert calls == [("BAAI/bge-m3", SHA)]
    assert encodes == [4, 4]


@pytest.mark.skipif(
    os.environ.get("W2A_RUN_BGE_M3_SMOKE") != "1",
    reason=(
        "set W2A_RUN_BGE_M3_SMOKE=1 (after `make setup-bge-m3`) "
        "to run the real-model smoke test"
    ),
)
@pytest.mark.skipif(
    importlib.util.find_spec("sentence_transformers") is None,
    reason="optional 'bge-m3' group not installed; run `make setup-bge-m3`",
)
def test_real_model_smoke() -> None:
    revision = os.environ.get(
        "W2A_BGE_M3_REVISION", "5617a9f61b028005a4858fdac845db406aefb181"
    )
    embedder = BgeM3Embedder(revision)
    vectors = embedder.embed_documents(
        [
            "How do I prepare for the NAATI CCL test?",
            "NAATI CCL പരീക്ഷയ്ക്ക് എങ്ങനെ തയ്യാറെടുക്കാം?",
        ]
    )
    assert len(vectors) == 2
    for vec in vectors:
        assert len(vec) == 1024
        assert math.isclose(math.sqrt(sum(x * x for x in vec)), 1.0, abs_tol=1e-3)
