"""Chunker and section_id tests (Spec 004 R4)."""

import asyncio
import threading
import unicodedata
from typing import Any

import pytest
from conftest import REPO_ROOT, manifest_document_count
from way2australia_core.documents import KnowledgeDocument
from way2australia_rag.ingestion.chunking import (
    MIN_CHUNK_CHARS,
    Chunker,
    HeadingChunker,
    slugify,
)
from way2australia_rag.ingestion.errors import IngestionConfigurationError
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)


def make_document(content: str, **overrides: Any) -> KnowledgeDocument:
    fields: dict[str, Any] = {
        "document_id": "doc_a",
        "document_version": 1,
        "title": "Doc A",
        "tenant_id": "way2australia",
        "knowledge_domain": "business",
        "access_scope": "public",
        "content_language": "en",
        "language_scope": "global",
        "lote_languages": ("*",),
        "source_authority": "owner_approved",
        "source_type": "faq",
        "approval_status": "approved",
        "lifecycle_status": "active",
        "introduced_in_release": "r1",
        "retrieval_enabled": True,
        "synthetic": False,
        "content_hash": "0" * 64,
        "content": content,
    }
    fields.update(overrides)
    return KnowledgeDocument.model_validate(fields)


def ids(chunks: list[Any]) -> list[tuple[str, int]]:
    return [(c.section_id, c.position) for c in chunks]


def test_satisfies_chunker_protocol() -> None:
    chunker: Chunker = HeadingChunker()
    assert (chunker.name, chunker.version, chunker.max_chunk_chars) == (
        "heading",
        "1",
        2000,
    )


def test_no_headings_is_main_section() -> None:
    chunks = HeadingChunker().chunk(make_document("Just a paragraph.\n\nAnother."))
    assert ids(chunks) == [("main", 0)]
    assert chunks[0].text == "Just a paragraph.\n\nAnother."


def test_preamble_and_headings() -> None:
    doc = make_document("Intro text.\n\n# Fees\nCosts.\n\n## Refunds\nNone.")
    chunks = HeadingChunker().chunk(doc)
    assert ids(chunks) == [("main", 0), ("fees", 0), ("refunds", 0)]
    assert chunks[1].text == "# Fees\n\nCosts."


def test_slug_rules() -> None:
    assert slugify("  Hello,   World!  ") == "hello-world"
    assert slugify("ＦＵＬＬ　Width") == "full-width"  # NFKC
    assert slugify("!!!") == "section"
    assert slugify("") == "section"


def test_slugs_stable_under_reordering() -> None:
    a = make_document("# Alpha\none\n\n# Beta\ntwo")
    b = make_document("# Beta\ntwo\n\n# Alpha\none")
    chunker = HeadingChunker()
    assert sorted(ids(chunker.chunk(a))) == sorted(ids(chunker.chunk(b)))


def test_leaf_heading_text_only() -> None:
    doc = make_document("# Parent\n## Child\ntext")
    assert [c.section_id for c in HeadingChunker().chunk(doc)] == ["parent", "child"]


def test_duplicate_headings_get_unique_ids_in_order() -> None:
    doc = make_document("# Fees\na\n\n# Fees\nb\n\n# Fees\nc")
    assert [c.section_id for c in HeadingChunker().chunk(doc)] == [
        "fees",
        "fees-2",
        "fees-3",
    ]


def test_duplicate_suffix_does_not_collide_with_literal_heading() -> None:
    doc = make_document("# Fees\na\n\n# Fees 2\nb\n\n# Fees\nc")
    result = [c.section_id for c in HeadingChunker().chunk(doc)]
    assert len(set(result)) == 3


def test_malayalam_and_other_scripts_slug_without_special_casing() -> None:
    doc = make_document(
        "# ഫീസ് വിവരങ്ങൾ\nഉള്ളടക്കം\n\n# 费用 说明\n内容\n\n# Тарифы\nтекст"
    )
    result = [c.section_id for c in HeadingChunker().chunk(doc)]
    assert result == ["ഫീസ്-വിവരങ്ങൾ", "费用-说明", "тарифы"]


def test_slug_drops_joiners_instead_of_splitting_words() -> None:
    # Malayalam chillu written with ZWJ and a virama word with ZWNJ.
    assert slugify("ന\u200dന്\u200d") == "നന്"
    assert slugify("ക്\u200cഷ") == "ക്ഷ"
    assert slugify("a\u200bb \ufeffc") == "ab-c"


def test_nfc_and_nfd_malayalam_headings_give_same_slug() -> None:
    # U+0D4A (MALAYALAM VOWEL SIGN O) decomposes to U+0D46 U+0D3E under NFD.
    nfc = unicodedata.normalize("NFC", "കൊച്ചി ഫീസ് വിവരങ്ങൾ")
    nfd = unicodedata.normalize("NFD", nfc)
    assert nfc != nfd
    assert slugify(nfc) == slugify(nfd)
    chunker = HeadingChunker()
    assert ids(chunker.chunk(make_document(f"# {nfc}\nഉള്ളടക്കം"))) == ids(
        chunker.chunk(make_document(f"# {nfd}\nഉള്ളടക്കം"))
    )


def test_section_id_comes_from_full_heading_not_truncated_chunk_text() -> None:
    cap = 40
    heading = "very long heading " * 4 + "unique-tail"
    assert len(heading) > cap // 2
    chunks = HeadingChunker(max_chunk_chars=cap).chunk(
        make_document(f"# {heading}\nbody text here")
    )
    assert {c.section_id for c in chunks} == {slugify(heading)}
    assert "unique-tail" not in chunks[0].text  # heading truncated in text only
    assert all(len(c.text) <= cap for c in chunks)


def test_too_small_cap_is_rejected() -> None:
    for cap in (0, 1, 2, 4, 15):
        with pytest.raises(IngestionConfigurationError):
            HeadingChunker(max_chunk_chars=cap)


def test_smallest_cap_terminates_and_respects_cap() -> None:
    body = "alpha beta gamma delta " * 20
    doc = make_document(f"# Hi\n{body}\n\n# A very long heading line here\n{body}")
    cap = MIN_CHUNK_CHARS
    done = threading.Event()
    result: list[Any] = []

    def run() -> None:
        result.extend(HeadingChunker(max_chunk_chars=cap).chunk(doc))
        done.set()

    threading.Thread(target=run, daemon=True).start()
    assert done.wait(timeout=5), "chunker did not terminate"
    assert all(len(c.text) <= cap for c in result)
    # pieces start with the full heading line when it fits in half the cap
    short = [c for c in result if c.section_id == "hi"]
    assert short and all(c.text.startswith("# Hi\n\n") for c in short)


def test_long_section_splits_within_cap_keeping_section_id() -> None:
    paragraphs = "\n\n".join(f"Paragraph {i} " + "word " * 20 for i in range(10))
    cap = 300
    chunks = HeadingChunker(max_chunk_chars=cap).chunk(
        make_document(f"# Long\n{paragraphs}")
    )
    assert len(chunks) > 1
    assert {c.section_id for c in chunks} == {"long"}
    assert [c.position for c in chunks] == list(range(len(chunks)))
    assert all(len(c.text) <= cap for c in chunks)
    assert all(c.text.startswith("# Long\n\n") for c in chunks)


def test_oversized_paragraph_and_word_split_within_cap() -> None:
    cap = 50
    body = "x" * 120 + " " + "short words here " * 10
    chunks = HeadingChunker(max_chunk_chars=cap).chunk(make_document(body))
    assert len(chunks) > 1
    assert all(len(c.text) <= cap for c in chunks)
    assert {c.section_id for c in chunks} == {"main"}


def test_deterministic() -> None:
    doc = make_document("Intro\n\n# A\n" + "text " * 500 + "\n\n# A\nmore")
    chunker = HeadingChunker(max_chunk_chars=200)
    assert chunker.chunk(doc) == chunker.chunk(doc)


def test_headings_inside_code_fences_ignored() -> None:
    doc = make_document("Intro\n\n```\n# not a heading\n```\n\n# Real\nbody")
    chunks = HeadingChunker().chunk(doc)
    assert ids(chunks) == [("main", 0), ("real", 0)]
    assert "# not a heading" in chunks[0].text


def test_tilde_fence_and_unclosed_fence() -> None:
    doc = make_document("~~~\n# hidden\n~~~\n\n# Shown\nx")
    assert [c.section_id for c in HeadingChunker().chunk(doc)] == ["main", "shown"]
    unclosed = make_document("```\n# hidden\nstill code")
    assert ids(HeadingChunker().chunk(unclosed)) == [("main", 0)]


def test_seed_corpus_is_one_main_chunk_per_document() -> None:
    """Baseline only: seed files have no headings, so this is not evidence
    that heading chunking works (see design "Seed reality")."""
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))
    documents = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))
    assert len(documents) == manifest_document_count()
    chunker = HeadingChunker()
    for document in documents:
        assert ids(chunker.chunk(document)) == [("main", 0)], document.document_id
