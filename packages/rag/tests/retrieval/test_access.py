"""Access resolution, filter derivation and hit re-check (Spec 005 R1-R3)."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from qdrant_client import models
from way2australia_core import AccessContext, Role
from way2australia_core.documents import AccessScope
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.repositories import GUEST_PUBLIC_POLICY, EligibilityPolicy
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    check_hit,
    guest_access,
    resolve_access,
)
from way2australia_rag.retrieval.errors import (
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)

SECRET_TEXT = "SECRET-CHUNK-TEXT"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("W2A_TENANT_ID", raising=False)
    monkeypatch.chdir(tmp_path)


def payload(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "tenant_id": "way2australia",
        "access_scope": "public",
        "owner_user_id": None,
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "title": "T",
        "knowledge_domain": "d",
        "source_authority": "business_policy",
        "source_type": "faq",
        "source_url": None,
        "chunk_text": SECRET_TEXT,
        "content_hash": "a" * 64,
        "document_id": "doc-1",
        "document_version": 1,
        "section_id": "s",
        "chunk_position": 0,
    }
    base.update(over)
    return base


def guest() -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id="way2australia"))


def test_guest_resolves_to_identical_policy() -> None:
    assert guest().policy is GUEST_PUBLIC_POLICY


@pytest.mark.parametrize("role", [r for r in Role if r is not Role.GUEST])
def test_non_guest_roles_refused(role: Role) -> None:
    with pytest.raises(RetrievalConfigurationError):
        resolve_access(AccessContext(role=role, tenant_id="t"))


def test_guest_access_uses_settings_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", " acme ")
    ctx = guest_access(RuntimeSettings())
    assert ctx == AccessContext(role=Role.GUEST, tenant_id="acme")


def test_filter_derived_from_policy_and_context() -> None:
    f = build_access_filter(guest())
    scope, tenant, owner = f.must  # type: ignore[misc]
    assert isinstance(scope, models.FieldCondition) and scope.key == "access_scope"
    assert scope.match == models.MatchAny(any=["public"])
    assert isinstance(tenant, models.FieldCondition)
    assert tenant.match == models.MatchValue(value="way2australia")
    assert isinstance(owner, models.IsNullCondition)
    assert owner.is_null.key == "owner_user_id"

    custom = ResolvedAccess(
        EligibilityPolicy(frozenset({AccessScope.PUBLIC, AccessScope.STAFF})), "other"
    )
    f2 = build_access_filter(custom)
    assert f2.must[0].match == models.MatchAny(any=["public", "staff"])  # type: ignore[index,union-attr]
    assert f2.must[1].match == models.MatchValue(value="other")  # type: ignore[index,union-attr]


def test_check_hit_accepts_valid_payload() -> None:
    assert check_hit(payload(), guest()).document_id == "doc-1"


@pytest.mark.parametrize(
    ("over", "field"),
    [
        ({"access_scope": "staff"}, "access_scope"),
        ({"access_scope": "bogus"}, "access_scope"),
        ({"tenant_id": "someone-else"}, "tenant_id"),
        ({"owner_user_id": "u1"}, "owner_user_id"),
    ],
)
def test_check_hit_rejects_violations(over: dict[str, Any], field: str) -> None:
    with pytest.raises(RetrievalAuthorizationError) as info:
        check_hit(payload(**over), guest())
    message = str(info.value)
    assert "doc-1" in message and field in message
    assert SECRET_TEXT not in message


def test_check_hit_rejects_malformed_payload() -> None:
    bad = payload(extra_field="x")
    del bad["title"]
    with pytest.raises(RetrievalAuthorizationError) as info:
        check_hit(bad, guest())
    assert SECRET_TEXT not in str(info.value)
    with pytest.raises(RetrievalAuthorizationError):
        check_hit({}, guest())


@pytest.mark.parametrize("value", ["", "  "])
def test_empty_tenant_setting_refused(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", value)
    with pytest.raises(ValidationError):
        RuntimeSettings()


def test_default_tenant() -> None:
    assert RuntimeSettings().tenant_id == "way2australia"


# --- Spec 007 T4: SQL access clause ---------------------------------------


def _policy(*scopes: AccessScope) -> ResolvedAccess:
    return ResolvedAccess(
        policy=EligibilityPolicy(allowed_access_scopes=frozenset(scopes)),
        tenant_id="way2australia",
    )


def test_sql_clause_is_constant_and_parameterised() -> None:
    from way2australia_rag.retrieval.access import build_sql_access_clause

    clause, params = build_sql_access_clause(guest())
    assert clause == (
        "c.access_scope IN (?) AND c.tenant_id = ? "
        "AND c.owner_present = 1 AND c.owner_user_id IS NULL"
    )
    assert params == ("public", "way2australia")
    assert "way2australia" not in clause


def test_both_builders_cover_the_same_three_conditions() -> None:
    from way2australia_rag.retrieval.access import build_sql_access_clause

    for access in (guest(), _policy(AccessScope.PUBLIC, AccessScope.STAFF)):
        scopes = sorted(str(s) for s in access.policy.allowed_access_scopes)
        qdrant = build_access_filter(access)
        clause, params = build_sql_access_clause(access)
        conditions = qdrant.must
        assert isinstance(conditions, list) and len(conditions) == 3
        scope_cond, tenant_cond, owner_cond = conditions
        assert isinstance(scope_cond, models.FieldCondition)
        assert isinstance(scope_cond.match, models.MatchAny)
        assert scope_cond.match.any == scopes
        assert isinstance(tenant_cond, models.FieldCondition)
        assert isinstance(tenant_cond.match, models.MatchValue)
        assert tenant_cond.match.value == access.tenant_id
        assert isinstance(owner_cond, models.IsNullCondition)
        assert owner_cond.is_null.key == "owner_user_id"
        assert params == (*scopes, access.tenant_id)
        assert clause.count("?") == len(scopes) + 1
        assert "owner_present = 1 AND c.owner_user_id IS NULL" in clause


def test_a_different_policy_changes_both_builders() -> None:
    from way2australia_rag.retrieval.access import build_sql_access_clause

    wider = _policy(AccessScope.PUBLIC, AccessScope.STAFF)
    assert build_access_filter(wider) != build_access_filter(guest())
    assert build_sql_access_clause(wider) != build_sql_access_clause(guest())
