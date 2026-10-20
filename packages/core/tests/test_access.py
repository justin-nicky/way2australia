from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from way2australia_core import AccessContext, Role


def test_valid_context_is_frozen() -> None:
    ctx = AccessContext(role=Role.GUEST, tenant_id="t")
    with pytest.raises(ValidationError):
        ctx.tenant_id = "other"  # type: ignore[misc]


def test_empty_tenant_refused() -> None:
    with pytest.raises(ValidationError):
        AccessContext(role=Role.GUEST, tenant_id="")


def test_unknown_role_refused() -> None:
    with pytest.raises(ValidationError):
        AccessContext(role="root", tenant_id="t")  # type: ignore[arg-type]


def test_no_language_or_scope_fields() -> None:
    assert set(AccessContext.model_fields) == {"role", "tenant_id"}
    with pytest.raises(ValidationError):
        AccessContext(role=Role.GUEST, tenant_id="t", language="ml")  # type: ignore[call-arg]


def test_roles_match_policy_file() -> None:
    path = Path(__file__).resolve().parents[3] / "config/access_policy.yaml"
    roles = yaml.safe_load(path.read_text(encoding="utf-8"))["roles"]
    assert {r.value for r in Role} == set(roles)
