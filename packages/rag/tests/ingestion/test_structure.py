"""Structure chunker tests (Spec 009 R3)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from conftest import REPO_ROOT, manifest_document_count
from snapshot_support import (  # type: ignore[import-not-found]
    assert_matches_snapshot,
    assert_structure_chunks_whitespace_fidelity,
    load_snapshot,
)
from test_chunking import make_document  # type: ignore[import-not-found]
from way2australia_rag.ingestion.chunking import MAIN_SECTION_ID, split_at_sentence_ends
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.ingestion.structure import (
    DuplicateSectionError,
    StructureChunker,
)
from way2australia_rag.ingestion.tokenization import FakeTokenizer

SOURCE_ROOT = (
    Path(__file__).resolve().parents[2] / "src" / "way2australia_rag" / "ingestion"
)


def structure_chunker(**overrides: object) -> StructureChunker:
    tokenizer = FakeTokenizer()
    params: dict[str, object] = {
        "max_chunk_tokens": 512,
        "context_prefix": "none",
        "tokenizer": tokenizer,
    }
    params.update(overrides)
    return StructureChunker(**params)  # type: ignore[arg-type]


def test_nested_headings_distinct_section_ids() -> None:
    doc = make_document("# Parent\nbody\n\n## Child\nnested\n\n# Other\nx")
    chunks = structure_chunker().chunk(doc)
    ids = {c.section_id for c in chunks}
    assert ids == {"parent", "parent-child", "other"}


def test_same_heading_under_different_parents() -> None:
    doc = make_document("# Fees\na\n\n## Refunds\nb\n\n# Mocks\n## Refunds\nc")
    ids = [c.section_id for c in structure_chunker().chunk(doc)]
    assert "fees-refunds" in ids
    assert "mocks-refunds" in ids
    assert len(set(ids)) == len(ids)


def test_duplicate_sibling_headings_raise() -> None:
    doc = make_document("# Fees\na\n\n# Fees\nb")
    with pytest.raises(DuplicateSectionError) as exc:
        structure_chunker().chunk(doc)
    assert exc.value.section_id == "fees"
    assert str(exc.value).startswith("duplicate_section:")


def test_main_collision_with_heading_slug() -> None:
    doc = make_document("preamble\n\n# Main\nbody")
    with pytest.raises(DuplicateSectionError) as exc:
        structure_chunker().chunk(doc)
    assert exc.value.section_id == MAIN_SECTION_ID


def test_fence_blocks_are_atomic_and_headings_inside_ignored() -> None:
    doc = make_document("```\n# not a heading\n```\n\n# Real\nafter")
    chunks = structure_chunker(max_chunk_tokens=64).chunk(doc)
    assert any("# not a heading" in c.text for c in chunks)
    assert any(c.section_id == "real" for c in chunks)
    assert all(c.section_id != "not-a-heading" for c in chunks)


def test_long_list_splits_only_between_items() -> None:
    items = "\n".join(f"- item {i} " + "word " * 5 for i in range(8))
    doc = make_document(f"# List\n{items}")
    chunks = structure_chunker(max_chunk_tokens=40).chunk(doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert "- item" in chunk.text
        assert chunk.text.count("- item") >= 1


def test_malayalam_paragraph_packs() -> None:
    doc = make_document(
        "# Malayalam\nഇത് ഒരു നീളമുള്ള മലയാളം ഖണ്ഡികയാണ്. രണ്ടാമത്തെ വാക്യവും ഇവിടെ ഉൾപ്പെടുന്നു."
    )
    chunks = structure_chunker(
        max_chunk_tokens=64, context_prefix="title_and_headings"
    ).chunk(doc)
    assert chunks
    assert all(
        structure_chunker(max_chunk_tokens=64).chunk(doc)[0].section_id == "malayalam"
        for _ in [0]
    )


def test_oversized_block_stays_space_separated_substring() -> None:
    body = "word " * 80
    doc = make_document(body)
    chunks = StructureChunker(
        max_chunk_tokens=32, context_prefix="none", tokenizer=FakeTokenizer()
    ).chunk(doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.text in doc.content
        assert "\nword" not in chunk.text


def test_oversized_block_splits_within_cap() -> None:
    body = "word " * 400
    doc = make_document(body)
    tokenizer = FakeTokenizer()
    cap = 32
    chunks = StructureChunker(
        max_chunk_tokens=cap, context_prefix="none", tokenizer=tokenizer
    ).chunk(doc)
    assert len(chunks) > 1
    assert all(tokenizer.count(c.text) <= cap for c in chunks)


def test_prefix_modes() -> None:
    doc = make_document("# Fees\nCosts.")
    none_chunks = structure_chunker(context_prefix="none").chunk(doc)
    assert none_chunks[0].text.startswith("# Fees")
    titled = structure_chunker(context_prefix="title_and_headings").chunk(doc)
    assert titled[0].text.startswith("Doc A\nFees")


def test_section_ids_stable_when_other_sections_change() -> None:
    base = make_document("# Alpha\none\n\n# Beta\ntwo")
    extended = make_document("# Gamma\nzero\n\n# Alpha\none\n\n# Beta\ntwo")
    reordered = make_document("# Beta\ntwo\n\n# Alpha\none")
    without_gamma = make_document("# Alpha\none\n\n# Beta\ntwo")
    base_ids = {c.section_id for c in structure_chunker().chunk(base)}
    ext_ids = {c.section_id for c in structure_chunker().chunk(extended)}
    reordered_ids = {c.section_id for c in structure_chunker().chunk(reordered)}
    trimmed_ids = {c.section_id for c in structure_chunker().chunk(without_gamma)}
    assert {"alpha", "beta"}.issubset(base_ids)
    assert {"alpha", "beta"}.issubset(ext_ids)
    assert reordered_ids == {"alpha", "beta"}
    assert trimmed_ids == {"alpha", "beta"}


def test_malayalam_paragraph_splits_when_over_cap() -> None:
    long_body = "ഇത് ഒരു നീളമുള്ള മലയാളം ഖണ്ഡികയാണ്. " * 20
    doc = make_document(f"# Malayalam\n{long_body}")
    chunks = structure_chunker(max_chunk_tokens=32).chunk(doc)
    assert len(chunks) > 1
    assert all(c.section_id == "malayalam" for c in chunks)


def test_seed_corpus_one_main_chunk_each() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    assert len(documents) == manifest_document_count()
    chunker = structure_chunker(max_chunk_tokens=512)
    for document in documents:
        chunks = chunker.chunk(document)
        assert len(chunks) == 1, document.document_id
        assert chunks[0].section_id == MAIN_SECTION_ID


def test_sentence_end_rule_examples() -> None:
    assert split_at_sentence_ends("Hello? Next") == ["Hello?", "Next"]
    assert split_at_sentence_ends("Stop! Now") == ["Stop!", "Now"]
    assert split_at_sentence_ends("Hello.\nNext") == ["Hello.", "Next"]
    assert split_at_sentence_ends("Hello. Next") == ["Hello.", "Next"]
    assert split_at_sentence_ends("1.5 stays") == ["1.5 stays"]
    assert split_at_sentence_ends("A$20.00 ok") == ["A$20.00 ok"]
    assert split_at_sentence_ends("see naati.com.au today") == [
        "see naati.com.au today"
    ]
    assert split_at_sentence_ends("e.g. word") == ["e.g.", "word"]
    assert split_at_sentence_ends("അവസാനം। തുടര്") == ["അവസാനം।", "തുടര്"]


def test_prefix_too_long_refused() -> None:
    doc = make_document("# " + "heading " * 80 + "\nbody")
    with pytest.raises(IngestionConfigurationError):
        structure_chunker(max_chunk_tokens=32).chunk(doc)


def test_whitespace_collapsed_fidelity_on_synthetic_fixture() -> None:
    fixture = load_snapshot("structure-v1-synthetic-fixture.json")
    doc = make_document(
        str(fixture["content"]), title=str(fixture.get("title", "Doc A"))
    )
    chunker = structure_chunker(
        max_chunk_tokens=64, context_prefix="title_and_headings"
    )
    assert_structure_chunks_whitespace_fidelity(chunker.chunk(doc), doc)


def test_whitespace_collapsed_fidelity_on_seed_corpus() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    chunker = structure_chunker(max_chunk_tokens=512)
    for document in documents:
        assert_structure_chunks_whitespace_fidelity(chunker.chunk(document), document)


def test_structure_snapshot_synthetic() -> None:
    fixture = load_snapshot("structure-v1-synthetic-fixture.json")
    doc = make_document(
        str(fixture["content"]), title=str(fixture.get("title", "Doc A"))
    )
    chunker = structure_chunker(
        max_chunk_tokens=64, context_prefix="title_and_headings"
    )
    actual = [
        {"section_id": c.section_id, "position": c.position, "text": c.text}
        for c in chunker.chunk(doc)
    ]
    assert actual == fixture["chunks"]


def test_structure_seed_snapshot() -> None:
    from way2australia_rag.repositories import (
        GUEST_PUBLIC_POLICY,
        LocalDocumentRepository,
        LocalRepositoryConfig,
        list_eligible_documents,
    )

    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    assert_matches_snapshot(
        structure_chunker(max_chunk_tokens=512),
        documents,
        "structure-v1-seed-fake.json",
    )


def test_no_language_specific_literals_in_chunker_modules() -> None:
    banned = []
    for name in ("structure.py", "recursive.py", "chunking.py"):
        text = (SOURCE_ROOT / name).read_text(encoding="utf-8")
        if '"ml"' in text or "'ml'" in text:
            banned.append(name)
        if "0x0" in text.lower() or "\\u0" in text:
            banned.append(name)
    assert not banned
