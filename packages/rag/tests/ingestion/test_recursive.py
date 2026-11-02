"""Recursive chunker tests (Spec 009 R4)."""

from __future__ import annotations

import asyncio

import pytest
from conftest import REPO_ROOT
from snapshot_support import (  # type: ignore[import-not-found]
    assert_matches_snapshot,
    assert_recursive_chunks_whitespace_fidelity,
    load_snapshot,
)
from test_chunking import make_document  # type: ignore[import-not-found]
from way2australia_rag.ingestion.chunking import MAIN_SECTION_ID, split_at_sentence_ends
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.recursive import RecursiveChunker
from way2australia_rag.ingestion.tokenization import FakeTokenizer


def recursive_chunker(**overrides: object) -> RecursiveChunker:
    tokenizer = FakeTokenizer()
    params: dict[str, object] = {
        "target_tokens": 32,
        "overlap_tokens": 4,
        "context_prefix": "title",
        "tokenizer": tokenizer,
    }
    params.update(overrides)
    return RecursiveChunker(**params)  # type: ignore[arg-type]


def test_no_chunk_above_target() -> None:
    doc = make_document("word " * 300)
    tokenizer = FakeTokenizer()
    chunker = RecursiveChunker(
        target_tokens=32, overlap_tokens=4, context_prefix="none", tokenizer=tokenizer
    )
    chunks = chunker.chunk(doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert tokenizer.count(chunk.text) <= 32


def test_overlap_at_most_configured() -> None:
    words = [f"term{i:03d}" for i in range(120)]
    doc = make_document(" ".join(words))
    tokenizer = FakeTokenizer()
    overlap = 4
    chunker = RecursiveChunker(
        target_tokens=32,
        overlap_tokens=overlap,
        context_prefix="none",
        tokenizer=tokenizer,
    )
    chunks = chunker.chunk(doc)
    for left, right in zip(chunks, chunks[1:], strict=False):
        best = 0
        for size in range(1, min(len(left.text), len(right.text)) + 1):
            suffix = left.text[-size:]
            if right.text.startswith(suffix):
                best = max(best, tokenizer.content_count(suffix))
        assert best <= overlap


def test_deterministic() -> None:
    doc = make_document("repeat " * 100)
    chunker = recursive_chunker()
    assert chunker.chunk(doc) == chunker.chunk(doc)


@pytest.mark.parametrize(
    ("target", "overlap"),
    [
        (31, 0),
        (32, 16),
        (-1, 0),
    ],
)
def test_invalid_parameters_refused(target: int, overlap: int) -> None:
    with pytest.raises(IngestionConfigurationError):
        recursive_chunker(target_tokens=target, overlap_tokens=overlap)


def test_seed_documents_many_chunks_at_small_target() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    chunker = recursive_chunker(target_tokens=32)
    multi = sum(1 for d in documents if len(chunker.chunk(d)) > 1)
    assert multi >= len(documents) - 1


def test_seed_documents_one_chunk_at_large_target() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    chunker = recursive_chunker(
        target_tokens=512, overlap_tokens=0, context_prefix="none"
    )
    for document in documents:
        chunks = chunker.chunk(document)
        assert len(chunks) == 1
        assert chunks[0].section_id == MAIN_SECTION_ID


def test_whitespace_collapsed_fidelity_on_synthetic_fixture() -> None:
    fixture = load_snapshot("recursive-v1-synthetic-fixture.json")
    doc = make_document(
        str(fixture["content"]), title=str(fixture.get("title", "Doc A"))
    )
    chunker = recursive_chunker(
        target_tokens=32, overlap_tokens=4, context_prefix="title"
    )
    assert_recursive_chunks_whitespace_fidelity(
        chunker.chunk(doc), doc, context_prefix="title"
    )


def test_whitespace_collapsed_fidelity_on_seed_corpus() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    chunker = recursive_chunker(
        target_tokens=32, overlap_tokens=4, context_prefix="title"
    )
    for document in documents:
        assert_recursive_chunks_whitespace_fidelity(
            chunker.chunk(document), document, context_prefix="title"
        )


def test_overlap_shorter_tail_when_longest_does_not_fit() -> None:
    title = " ".join(["abcd"] * 24)
    words = [f"w{i:02d}" for i in range(40)]
    doc = make_document(" ".join(words), title=title)
    tokenizer = FakeTokenizer()
    overlap = 10
    chunker = RecursiveChunker(
        target_tokens=32,
        overlap_tokens=overlap,
        context_prefix="title",
        tokenizer=tokenizer,
    )
    chunks = chunker.chunk(doc)
    assert len(chunks) > 2
    for left, right in zip(chunks, chunks[1:], strict=False):
        best = 0
        for size in range(1, min(len(left.text), len(right.text)) + 1):
            suffix = left.text[-size:]
            if right.text.startswith(suffix):
                best = max(best, tokenizer.content_count(suffix))
        assert best <= overlap
    body_left = chunks[0].text.split("\n\n", 1)[-1]
    body_right = chunks[1].text.split("\n\n", 1)[-1]
    shared = 0
    for size in range(1, min(len(body_left), len(body_right)) + 1):
        if body_right.startswith(body_left[-size:]):
            shared = max(shared, tokenizer.content_count(body_left[-size:]))
    assert 0 < shared <= overlap
    assert shared < tokenizer.content_count(" ".join(words[:6]))


def test_sentence_end_rule_shared_with_structure() -> None:
    assert split_at_sentence_ends("Price is 1.5 today.") == ["Price is 1.5 today."]
    assert split_at_sentence_ends("Visit naati.com.au. Next") == [
        "Visit naati.com.au.",
        "Next",
    ]


def test_recursive_snapshot_synthetic() -> None:
    fixture = load_snapshot("recursive-v1-synthetic-fixture.json")
    doc = make_document(
        str(fixture["content"]), title=str(fixture.get("title", "Doc A"))
    )
    chunker = recursive_chunker(
        target_tokens=32, overlap_tokens=4, context_prefix="title"
    )
    actual = [
        {"section_id": c.section_id, "position": c.position, "text": c.text}
        for c in chunker.chunk(doc)
    ]
    assert actual == fixture["chunks"]


def test_recursive_seed_snapshot() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    assert_matches_snapshot(
        recursive_chunker(target_tokens=32, overlap_tokens=4, context_prefix="title"),
        documents,
        "recursive-v1-seed-fake-32.json",
    )


def test_heading_seed_snapshot_unchanged() -> None:
    from way2australia_rag.ingestion.chunking import HeadingChunker
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    assert_matches_snapshot(HeadingChunker(), documents, "heading-v1-seed-fake.json")
