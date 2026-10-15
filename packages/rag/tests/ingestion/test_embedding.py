"""Embedder interface and FakeEmbedder tests (Spec 004 R5)."""

import math
import subprocess
import sys

import pytest
from way2australia_rag.ingestion.embedding import Embedder, EmbedderInfo, FakeEmbedder
from way2australia_rag.ingestion.errors import IngestionConfigurationError


def test_same_text_gives_same_vector() -> None:
    a = FakeEmbedder().embed_documents(["hello", "മലയാളം"])
    b = FakeEmbedder().embed_documents(["hello", "മലയാളം"])
    assert a == b
    assert a[0] != a[1]


@pytest.mark.parametrize("size", [1, 7, 32, 64, 100, 1024])
def test_declared_vector_size(size: int) -> None:
    embedder = FakeEmbedder(vector_size=size)
    assert embedder.info.vector_size == size
    assert len(embedder.embed_query("x")) == size
    assert all(len(v) == size for v in embedder.embed_documents(["a", "b"]))


def test_default_size_is_64() -> None:
    assert FakeEmbedder().info.vector_size == 64


def test_vectors_are_l2_normalized() -> None:
    for vector in FakeEmbedder().embed_documents(["a", "", "long text " * 50]):
        assert math.isclose(math.sqrt(sum(v * v for v in vector)), 1.0, rel_tol=1e-9)
    assert FakeEmbedder().info.normalize is True


def test_query_and_document_methods_agree_and_are_separate() -> None:
    embedder = FakeEmbedder()
    assert embedder.embed_query("q") == embedder.embed_documents(["q"])[0]
    assert embedder.embed_documents([]) == []


def test_info_reports_fake_identity() -> None:
    info = FakeEmbedder().info
    assert info.is_fake is True
    assert info.model_id == "fake-hash-embedder"
    assert info.revision == "1"
    with pytest.raises(Exception):
        info.model_id = "other"  # frozen


def test_conforms_to_protocol() -> None:
    embedder: Embedder = FakeEmbedder()
    assert isinstance(embedder.info, EmbedderInfo)


def test_invalid_vector_size_rejected() -> None:
    with pytest.raises(IngestionConfigurationError):
        FakeEmbedder(vector_size=0)


def test_no_pytorch_import() -> None:
    code = (
        "import sys; import way2australia_rag.ingestion.embedding as m; "
        "m.FakeEmbedder().embed_query('x'); "
        "bad = [n for n in ('torch', 'sentence_transformers') if n in sys.modules]; "
        "sys.exit(1 if bad else 0)"
    )
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0
