"""Index settings, payload fields and point identity tests (Spec 004 R7, R8, R9)."""

import re
import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_chunking import make_document  # type: ignore[import-not-found]
from way2australia_rag.ingestion import identity, payload, settings
from way2australia_rag.ingestion.chunking import Chunk, HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import INGESTION_NAMESPACE, point_id
from way2australia_rag.ingestion.payload import (
    IDENTITY_FIELDS,
    PointPayload,
    build_payload,
)
from way2australia_rag.ingestion.settings import (
    IndexSettings,
    build_index_settings,
    collection_name,
    compare,
    mismatch_message,
)
from way2australia_rag.repositories.hashing import CONTENT_HASH_METADATA_FIELDS

INGESTION_DIR = Path(settings.__file__).parent


def base_settings() -> IndexSettings:
    return build_index_settings("idx-v1", FakeEmbedder().info, HeadingChunker())


# --- IndexSettings / compare -------------------------------------------------


def test_build_index_settings_records_embedder_and_chunker() -> None:
    s = base_settings()
    assert s.schema_version == "1.0"
    assert s.index_version == "idx-v1"
    assert s.embedder_model_id == "fake-hash-embedder"
    assert s.embedder_vector_size == 64
    assert s.embedder_is_fake is True
    assert s.chunker_name == "heading"
    assert s.chunker_max_chunk_chars == 2000
    assert s.hash_contract == "content-hash-v1"
    with pytest.raises(ValidationError):
        s.index_version = "x"  # type: ignore[misc]  # frozen


def test_compare_equal_and_ignores_hash_contract() -> None:
    s = base_settings()
    assert compare(s, s) == []
    assert compare(s, s.model_copy(update={"hash_contract": "content-hash-v2"})) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("index_version", "idx-v2"),
        ("embedder_model_id", "other"),
        ("embedder_revision", "2"),
        ("embedder_vector_size", 1024),
        ("embedder_normalize", False),
        ("embedder_is_fake", False),
        ("chunker_name", "recursive"),
        ("chunker_version", "2"),
        ("chunker_max_chunk_chars", 500),
    ],
)
def test_compare_reports_each_other_field(field: str, value: object) -> None:
    s = base_settings()
    assert compare(s, s.model_copy(update={field: value})) == [field]


def test_every_field_except_hash_contract_is_compared() -> None:
    s = base_settings()
    compared = set(IndexSettings.model_fields) - {"hash_contract"}
    for name in compared:
        current = getattr(s, name)
        changed = (not current) if isinstance(current, bool) else f"{current}-x"
        if isinstance(current, int) and not isinstance(current, bool):
            changed = current + 1
        assert name in compare(s, s.model_copy(update={name: changed}))


def test_mismatch_message_names_fields_and_points_to_new_index_version() -> None:
    s = base_settings()
    message = mismatch_message(
        "w2a-idx-v1", s, s.model_copy(update={"embedder_revision": "9"})
    )
    assert "embedder_revision" in message
    assert "new label" in message and "index_version" in message
    assert "config/ingestion.yaml" in message
    assert "/Users" not in message


def test_collection_name_derivation() -> None:
    assert collection_name("way2australia", "idx-v1") == "way2australia-idx-v1"
    assert collection_name("a", "b") == "a-b"


# --- Payload -----------------------------------------------------------------

EXPECTED_PAYLOAD_FIELDS = {
    "tenant_id",
    "access_scope",
    "owner_user_id",
    "language_scope",
    "lote_languages",
    "content_language",
    "title",
    "knowledge_domain",
    "source_authority",
    "source_type",
    "source_url",
    "chunk_text",
    "content_hash",
    "document_id",
    "document_version",
    "section_id",
    "chunk_position",
}


def test_payload_field_set_equals_design_table() -> None:
    assert set(PointPayload.model_fields) == EXPECTED_PAYLOAD_FIELDS


def test_non_identity_fields_are_hash_covered() -> None:
    non_identity = set(PointPayload.model_fields) - set(IDENTITY_FIELDS)
    allowed = set(CONTENT_HASH_METADATA_FIELDS) | {"chunk_text", "content_hash"}
    assert non_identity <= allowed
    assert set(IDENTITY_FIELDS) <= set(PointPayload.model_fields)
    assert set(IDENTITY_FIELDS) == {
        "document_id",
        "document_version",
        "section_id",
        "chunk_position",
    }


def test_persona_scope_and_last_reviewed_at_absent() -> None:
    fields = set(PointPayload.model_fields)
    assert "persona_scope" not in fields
    assert "last_reviewed_at" not in fields
    for eligibility_only in (
        "approval_status",
        "lifecycle_status",
        "retrieval_enabled",
        "synthetic",
        "introduced_in_release",
        "effective_from",
        "effective_to",
    ):
        assert eligibility_only not in fields


def test_build_payload_copies_document_and_chunk() -> None:
    document = make_document(
        "body",
        access_scope="user_private",
        owner_user_id="u1",
        source_url="https://example.org/x",
        lote_languages=("ml",),
        language_scope="language_specific",
    )
    chunk = Chunk(section_id="main", position=2, text="chunk body")
    p = build_payload(document, chunk).model_dump()
    assert p["access_scope"] == "user_private"
    assert p["language_scope"] == "language_specific"
    assert p["lote_languages"] == ["ml"]
    assert p["chunk_text"] == "chunk body"
    assert p["section_id"] == "main" and p["chunk_position"] == 2
    assert p["content_hash"] == document.content_hash
    assert p["owner_user_id"] == "u1"
    assert p["source_url"] == "https://example.org/x"
    assert all(type(p[k]) in (str, int, list, type(None)) for k in p)


def test_authorization_and_language_fields_are_separate() -> None:
    document = make_document("body", content_language="ml", lote_languages=("*",))
    p = build_payload(document, Chunk(section_id="main", position=0, text="t"))
    assert p.content_language == "ml"
    assert p.lote_languages == ["*"]
    assert p.access_scope == "public"


def test_no_malayalam_specific_lote_languages_in_ingestion_code() -> None:
    for source in INGESTION_DIR.glob("*.py"):
        text = source.read_text(encoding="utf-8")
        assert not re.search(r"""["']ml["']""", text), source.name


# --- Point identity ----------------------------------------------------------


def test_namespace_constant_is_pinned() -> None:
    assert INGESTION_NAMESPACE == uuid.UUID("533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2")
    assert "Fixed UUID namespace" in Path(identity.__file__).read_text(encoding="utf-8")


def test_point_id_stable_and_valid_uuid() -> None:
    a = point_id("doc_a", "main", 0)
    assert a == point_id("doc_a", "main", 0)
    assert str(uuid.UUID(a)) == a
    assert uuid.UUID(a).version == 5
    assert a == str(uuid.uuid5(INGESTION_NAMESPACE, "doc_a\x1fmain\x1f0"))


def test_point_id_distinct_across_document_section_and_position() -> None:
    ids = {
        point_id("doc_a", "main", 0),
        point_id("doc_a", "main", 1),
        point_id("doc_a", "other", 0),
        point_id("doc_b", "main", 0),
        point_id("doc_a", "main1", 0),
        point_id("doc_a", "main", 10),
    }
    assert len(ids) == 6


def test_payload_module_is_importable() -> None:
    assert payload.IDENTITY_FIELDS == IDENTITY_FIELDS
