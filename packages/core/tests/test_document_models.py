from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError
from way2australia_core.documents import (
    AccessScope,
    ApprovalStatus,
    KnowledgeDocument,
    LanguageScope,
    LifecycleStatus,
    SourceAuthority,
)

VALID_HASH = "a" * 64


def document_fields(**overrides: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "document_id": "official_001_ccl_format_scoring_results",
        "document_version": 1,
        "title": "CCL format, scoring and results",
        "tenant_id": "way2australia",
        "knowledge_domain": "official_exam_rules",
        "access_scope": "public",
        "owner_user_id": None,
        "content_language": "en",
        "language_scope": "global",
        "lote_languages": ["*"],
        "source_authority": "naati",
        "source_type": "official_external_summary",
        "source_url": "https://www.naati.com.au/migration-assessments/ccl/",
        "approval_status": "approved",
        "lifecycle_status": "active",
        "last_reviewed_at": "2026-10-09",
        "introduced_in_release": "seed-v1",
        "effective_from": "2026-10-09",
        "effective_to": None,
        "retrieval_enabled": True,
        "synthetic": False,
        "content_hash": VALID_HASH,
        "content": "The CCL test has two dialogues.",
    }
    fields.update(overrides)
    return fields


def make_document(**overrides: Any) -> KnowledgeDocument:
    return KnowledgeDocument.model_validate(document_fields(**overrides))


def assert_invalid(field: str, **overrides: Any) -> ValidationError:
    with pytest.raises(ValidationError) as exc_info:
        make_document(**overrides)
    assert field in str(exc_info.value)
    return exc_info.value


# --- valid construction -----------------------------------------------------


def test_valid_global_document_parses_typed_fields() -> None:
    document = make_document()

    assert document.document_id == "official_001_ccl_format_scoring_results"
    assert document.document_version == 1
    assert document.access_scope is AccessScope.PUBLIC
    assert document.approval_status is ApprovalStatus.APPROVED
    assert document.lifecycle_status is LifecycleStatus.ACTIVE
    assert document.language_scope is LanguageScope.GLOBAL
    assert document.source_authority is SourceAuthority.NAATI
    assert document.lote_languages == ("*",)
    assert document.last_reviewed_at == date(2026, 10, 9)
    assert document.effective_to is None


def test_valid_language_specific_document() -> None:
    document = make_document(
        document_id="language_ml_001_naati_policy",
        language_scope="language_specific",
        lote_languages=["ml"],
    )

    assert document.language_scope is LanguageScope.LANGUAGE_SPECIFIC
    assert document.lote_languages == ("ml",)


def test_future_language_needs_no_code_change() -> None:
    document = make_document(
        language_scope="language_specific", lote_languages=["ta", "hi"]
    )

    assert document.lote_languages == ("ta", "hi")


def test_optional_fields_default_to_none() -> None:
    fields = document_fields()
    for name in (
        "owner_user_id",
        "source_url",
        "last_reviewed_at",
        "effective_from",
        "effective_to",
    ):
        del fields[name]

    document = KnowledgeDocument.model_validate(fields)

    assert document.owner_user_id is None
    assert document.source_url is None
    assert document.last_reviewed_at is None


def test_non_url_source_reference_is_allowed() -> None:
    document = make_document(source_url="fixture://staff-canary")

    assert document.source_url == "fixture://staff-canary"


def test_user_private_document_requires_owner() -> None:
    document = make_document(access_scope="user_private", owner_user_id="user-123")

    assert document.owner_user_id == "user-123"


# --- identity and version (R2) ----------------------------------------------


def test_document_is_immutable() -> None:
    document = make_document()

    with pytest.raises(ValidationError):
        document.document_version = 2  # type: ignore[misc]


def test_new_version_keeps_stable_identity() -> None:
    v1 = make_document()
    v2 = make_document(document_version=2, content="Updated approved content.")

    assert v1.document_id == v2.document_id
    assert v2.document_version == v1.document_version + 1


def test_model_has_no_storage_or_chunk_fields() -> None:
    names = set(KnowledgeDocument.model_fields)

    assert not names & {"path", "file_path", "sha256", "chunk_id", "chunk_ids"}
    assert not any(name.startswith(("chunk", "embedding", "index")) for name in names)


def test_storage_path_is_rejected() -> None:
    assert_invalid("path", path="knowledge/public/business/business_001.md")


@pytest.mark.parametrize(
    "document_id",
    ["", "Business_001", "knowledge/public/doc", "doc id", "../doc", "_doc"],
)
def test_invalid_document_id_is_rejected(document_id: str) -> None:
    assert_invalid("document_id", document_id=document_id)


@pytest.mark.parametrize("version", [0, -1, "1", 1.0, True])
def test_invalid_document_version_is_rejected(version: Any) -> None:
    assert_invalid("document_version", document_version=version)


def test_missing_required_field_is_rejected() -> None:
    fields = document_fields()
    del fields["document_version"]

    with pytest.raises(ValidationError) as exc_info:
        KnowledgeDocument.model_validate(fields)

    assert "document_version" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)


@pytest.mark.parametrize(
    "field", ["title", "tenant_id", "knowledge_domain", "source_type", "content"]
)
def test_blank_required_text_is_rejected(field: str) -> None:
    assert_invalid(field, **{field: "   "})


@pytest.mark.parametrize("content_hash", ["", "abc", "A" * 64, "g" * 64])
def test_invalid_content_hash_is_rejected(content_hash: str) -> None:
    assert_invalid("content_hash", content_hash=content_hash)


# --- language metadata (R9) -------------------------------------------------


@pytest.mark.parametrize("code", ["*", "EN", "english", "e", ""])
def test_invalid_content_language_is_rejected(code: str) -> None:
    assert_invalid("content_language", content_language=code)


def test_empty_lote_languages_is_rejected() -> None:
    assert_invalid(
        "lote_languages", language_scope="language_specific", lote_languages=[]
    )


def test_wildcard_must_stand_alone() -> None:
    assert_invalid("lote_languages", lote_languages=["*", "ml"])


def test_duplicate_lote_languages_are_rejected() -> None:
    assert_invalid(
        "lote_languages",
        language_scope="language_specific",
        lote_languages=["ml", "ml"],
    )


def test_invalid_lote_language_code_is_rejected() -> None:
    assert_invalid(
        "lote_languages",
        language_scope="language_specific",
        lote_languages=["Malayalam"],
    )


def test_global_scope_requires_wildcard() -> None:
    assert_invalid("language_scope", language_scope="global", lote_languages=["ml"])


def test_language_specific_scope_rejects_wildcard() -> None:
    assert_invalid(
        "language_scope", language_scope="language_specific", lote_languages=["*"]
    )


def test_language_metadata_is_independent_of_access_scope() -> None:
    staff_ml = make_document(
        access_scope="staff",
        language_scope="language_specific",
        lote_languages=["ml"],
    )
    public_global = make_document()

    assert staff_ml.access_scope is AccessScope.STAFF
    assert public_global.access_scope is AccessScope.PUBLIC


# --- source and governance metadata -----------------------------------------


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("access_scope", "everyone"),
        ("approval_status", "maybe"),
        ("lifecycle_status", "live"),
        ("source_authority", "wikipedia"),
        ("language_scope", "regional"),
    ],
)
def test_unknown_controlled_value_is_rejected(field: str, value: str) -> None:
    assert_invalid(field, **{field: value})


@pytest.mark.parametrize("field", ["retrieval_enabled", "synthetic"])
@pytest.mark.parametrize("value", ["true", 1, "yes"])
def test_flags_must_be_real_booleans(field: str, value: Any) -> None:
    assert_invalid(field, **{field: value})


def test_user_private_without_owner_is_rejected() -> None:
    assert_invalid("owner_user_id", access_scope="user_private", owner_user_id=None)


def test_owner_on_non_private_document_is_rejected() -> None:
    assert_invalid("owner_user_id", access_scope="public", owner_user_id="user-123")


def test_effective_window_must_be_ordered() -> None:
    assert_invalid(
        "effective_to", effective_from="2026-10-09", effective_to="2026-01-01"
    )


def test_unknown_field_is_rejected() -> None:
    assert_invalid("chunk_id", chunk_id="chunk-1")
