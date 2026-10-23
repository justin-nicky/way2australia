"""Server-side access context (Spec 005 R1).

An `AccessContext` says who is asking (role) and for which tenant. It carries no
scopes and no language fields: scopes are a policy decision made in server code,
and language never grants or denies access.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


class Role(StrEnum):
    """Roles defined in `config/access_policy.yaml`."""

    GUEST = "guest"
    STAFF = "staff"
    SUBSCRIBER = "subscriber"
    REGISTERED_USER = "registered_user"
    ADMIN = "admin"


class AccessContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Role
    tenant_id: str

    @field_validator("tenant_id")
    @classmethod
    def _tenant_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("tenant_id must not be blank")
        return value
