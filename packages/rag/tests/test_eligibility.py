import asyncio
from pathlib import Path
from typing import Any

import pytest
from way2australia_core.documents import (
    AccessScope,
    ApprovalStatus,
    KnowledgeDocument,
    LifecycleStatus,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentQuery,
    EligibilityPolicy,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import (
    compute_content_hash,
    normalize_body,
)
from way2australia_rag.repositories.local import _matches

REPO_ROOT = Path(__file__).resolve().parents[3]
SECURITY_FIXTURES = REPO_ROOT / "tests/fixtures/security"


def make_document(**overrides: Any) -> KnowledgeDocument:
    fields: dict[str, Any] = {
        "document_id": "doc_a",
        "document_version": 1,
        "title": "Doc A",
        "tenant_id": "way2australia",
        "knowledge_domain": "official_exam_rules",
        "access_scope": "public",
        "owner_user_id": None,
        "content_language": "en",
        "language_scope": "global",
        "lote_languages": ["*"],
        "source_authority": "naati",
        "source_type": "official_external_summary",
        "source_url": None,
        "approval_status": "approved",
        "lifecycle_status": "active",
        "last_reviewed_at": None,
        "introduced_in_release": "seed-v1",
        "effective_from": None,
        "effective_to": None,
        "retrieval_enabled": True,
        "synthetic": False,
        "content_hash": "a" * 64,
        "content": "text",
    }
    fields.update(overrides)
    return KnowledgeDocument.model_validate(fields)


class IgnoresQueryRepository:
    """A faulty repository that returns everything regardless of the query."""

    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self._documents = documents

    async def get_document(
        self, document_id: str, version: int | None = None
    ) -> KnowledgeDocument:
        raise NotImplementedError

    async def list_documents(
        self, query: DocumentQuery | None = None
    ) -> list[KnowledgeDocument]:
        return list(self._documents)


def eligible_ids(
    documents: list[KnowledgeDocument],
    policy: EligibilityPolicy = GUEST_PUBLIC_POLICY,
    lote_language: str | None = None,
) -> list[str]:
    repository = IgnoresQueryRepository(documents)
    result = asyncio.run(list_eligible_documents(repository, policy, lote_language))
    return [d.document_id for d in result]


def test_active_approved_public_document_is_eligible() -> None:
    document = make_document()

    assert GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == ["doc_a"]


@pytest.mark.parametrize("status", ["deprecated", "archived", "draft"])
def test_non_active_lifecycle_is_excluded(status: str) -> None:
    document = make_document(lifecycle_status=status)

    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []


@pytest.mark.parametrize("status", ["pending_review", "rejected", "test_only"])
def test_non_approved_status_is_excluded(status: str) -> None:
    document = make_document(approval_status=status)

    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []


def test_retrieval_disabled_is_excluded() -> None:
    document = make_document(retrieval_enabled=False)

    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []


def test_synthetic_is_excluded_even_when_otherwise_eligible() -> None:
    document = make_document(synthetic=True, source_authority="synthetic")

    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []


@pytest.mark.parametrize("scope", ["staff", "subscriber", "admin"])
def test_non_public_scope_is_excluded_for_guest(scope: str) -> None:
    document = make_document(access_scope=scope)

    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []


def test_user_private_scope_is_excluded_for_guest() -> None:
    document = make_document(access_scope="user_private", owner_user_id="user-1")

    assert eligible_ids([document]) == []


def test_policy_scopes_are_server_input_and_can_be_widened_explicitly() -> None:
    staff = make_document(document_id="staff_doc", access_scope="staff")
    public = make_document(document_id="public_doc")
    policy = EligibilityPolicy(frozenset({AccessScope.PUBLIC, AccessScope.STAFF}))

    assert eligible_ids([staff, public], policy) == ["staff_doc", "public_doc"]
    assert eligible_ids([staff, public]) == ["public_doc"]


def test_policy_requires_at_least_one_scope() -> None:
    with pytest.raises(ValueError):
        EligibilityPolicy(frozenset())


def test_language_metadata_does_not_broaden_access() -> None:
    staff_global = make_document(
        document_id="staff_global", access_scope="staff", lote_languages=["*"]
    )
    staff_ml = make_document(
        document_id="staff_ml",
        access_scope="staff",
        language_scope="language_specific",
        lote_languages=["ml"],
        content_language="ml",
    )

    for language in (None, "ml", "en", "*"):
        assert eligible_ids([staff_global, staff_ml], lote_language=language) == []


def test_language_filter_narrows_eligible_documents_only() -> None:
    global_doc = make_document(document_id="global_doc")
    ml_doc = make_document(
        document_id="ml_doc",
        language_scope="language_specific",
        lote_languages=["ml"],
        content_language="ml",
    )
    hi_doc = make_document(
        document_id="hi_doc",
        language_scope="language_specific",
        lote_languages=["hi"],
        content_language="hi",
    )
    docs = [global_doc, ml_doc, hi_doc]

    assert eligible_ids(docs) == ["global_doc", "ml_doc", "hi_doc"]
    assert eligible_ids(docs, lote_language="ml") == ["global_doc", "ml_doc"]
    assert eligible_ids(docs, lote_language="hi") == ["global_doc", "hi_doc"]


def test_policy_query_carries_every_condition_and_the_server_scopes() -> None:
    query = GUEST_PUBLIC_POLICY.query("ml")

    assert query.allowed_access_scopes == frozenset({AccessScope.PUBLIC})
    assert query.approval_status is ApprovalStatus.APPROVED
    assert query.lifecycle_status is LifecycleStatus.ACTIVE
    assert query.retrieval_enabled is True
    assert query.synthetic is False
    assert query.lote_language == "ml"


def test_local_repository_applies_the_policy_query() -> None:
    documents = [
        make_document(document_id="ok"),
        make_document(document_id="old", lifecycle_status="deprecated"),
        make_document(document_id="off", retrieval_enabled=False),
    ]

    class Fixed(IgnoresQueryRepository):
        async def list_documents(
            self, query: DocumentQuery | None = None
        ) -> list[KnowledgeDocument]:
            assert query is not None
            return [d for d in self._documents if _matches(d, query)]

    result = asyncio.run(list_eligible_documents(Fixed(documents), GUEST_PUBLIC_POLICY))

    assert [d.document_id for d in result] == ["ok"]


@pytest.mark.integration
def test_seed_corpus_is_entirely_eligible_for_guest() -> None:
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=REPO_ROOT))

    stored = asyncio.run(repository.list_documents())
    eligible = asyncio.run(list_eligible_documents(repository, GUEST_PUBLIC_POLICY))

    assert len(stored) == 13
    assert {d.document_id for d in eligible} == {d.document_id for d in stored}


def load_fixture(name: str) -> KnowledgeDocument:
    metadata, body = split_frontmatter(
        (SECURITY_FIXTURES / name).read_text(encoding="utf-8")
    )
    fields = {k: v for k, v in metadata.items() if k in KnowledgeDocument.model_fields}
    fields["content"] = normalize_body(body)
    fields["content_hash"] = compute_content_hash(body, metadata)
    return KnowledgeDocument.model_validate(fields)


@pytest.mark.parametrize(
    "name", ["staff_only_canary.md", "poisoned_public_document.md"]
)
def test_security_fixtures_are_valid_but_ineligible_for_guest(name: str) -> None:
    document = load_fixture(name)

    assert document.retrieval_enabled is True
    assert not GUEST_PUBLIC_POLICY.is_eligible(document)
    assert eligible_ids([document]) == []
