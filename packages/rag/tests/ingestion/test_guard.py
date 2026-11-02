"""Truncation guard tests (Spec 009 R2)."""

import pytest
from way2australia_rag.ingestion.chunking import Chunk
from way2australia_rag.ingestion.guard import ChunkTooLongError, check_chunks
from way2australia_rag.ingestion.tokenization import FakeTokenizer


def test_at_limit_passes() -> None:
    tokenizer = FakeTokenizer(max_sequence_length=6)
    chunks = [Chunk(section_id="main", position=0, text="hello world")]
    assert tokenizer.count(chunks[0].text) == 6
    check_chunks("doc_a", chunks, tokenizer, None)


def test_above_limit_raises_with_fields() -> None:
    tokenizer = FakeTokenizer(max_sequence_length=5)
    chunks = [Chunk(section_id="fees", position=2, text="hello world")]
    with pytest.raises(ChunkTooLongError) as caught:
        check_chunks("doc_b", chunks, tokenizer, cap=5)
    error = caught.value
    assert error.document_id == "doc_b"
    assert error.section_id == "fees"
    assert error.position == 2
    assert error.tokens == 6
    assert error.limit == 5
    assert "chunk_too_long" in str(error)
    assert "hello" not in str(error)


def test_cap_none_uses_model_maximum() -> None:
    tokenizer = FakeTokenizer(max_sequence_length=10)
    chunks = [Chunk(section_id="main", position=0, text="a")]
    check_chunks("doc_c", chunks, tokenizer, cap=None)
    long = Chunk(section_id="main", position=0, text="hello world extra words here")
    with pytest.raises(ChunkTooLongError) as caught:
        check_chunks("doc_c", [long], tokenizer, cap=None)
    assert caught.value.limit == 10


def test_cap_below_model_maximum() -> None:
    tokenizer = FakeTokenizer(max_sequence_length=512)
    chunks = [Chunk(section_id="main", position=0, text="hello world")]
    with pytest.raises(ChunkTooLongError) as caught:
        check_chunks("doc_d", chunks, tokenizer, cap=4)
    assert caught.value.limit == 4
