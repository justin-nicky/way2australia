"""Guest access resolution, filter builder and hit re-check (Spec 005 R1-R3).

Authorization comes only from the server-side policy object chosen here. The
filter is built from that policy and the server tenant; nothing from a query,
an evaluation case or the LLM reaches it.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import ValidationError
from qdrant_client import models
from way2australia_core import AccessContext, Role
from way2australia_core.documents import AccessScope

from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.repositories import GUEST_PUBLIC_POLICY, EligibilityPolicy
from way2australia_rag.retrieval.errors import (
    RetrievalAuthorizationError,
    RetrievalConfigurationError,
)


@dataclass(frozen=True, slots=True)
class ResolvedAccess:
    policy: EligibilityPolicy
    tenant_id: str


def guest_access(settings: RuntimeSettings) -> AccessContext:
    """The only constructor used by CLIs and the baseline; tenant is server config."""
    return AccessContext(role=Role.GUEST, tenant_id=settings.tenant_id)


def resolve_access(context: AccessContext) -> ResolvedAccess:
    """The only mapping from role to policy."""
    if context.role is Role.GUEST:
        return ResolvedAccess(policy=GUEST_PUBLIC_POLICY, tenant_id=context.tenant_id)
    raise RetrievalConfigurationError(f"role '{context.role}' is not implemented")


def build_access_filter(access: ResolvedAccess) -> models.Filter:
    """The only place an authorization filter is built.

    A point without `owner_user_id` does not match `is_null`, so it is excluded.
    """
    scopes = sorted(str(scope) for scope in access.policy.allowed_access_scopes)
    return models.Filter(
        must=[
            models.FieldCondition(
                key="access_scope", match=models.MatchAny(any=scopes)
            ),
            models.FieldCondition(
                key="tenant_id", match=models.MatchValue(value=access.tenant_id)
            ),
            models.IsNullCondition(is_null=models.PayloadField(key="owner_user_id")),
        ]
    )


def check_hit(payload: Mapping[str, object], access: ResolvedAccess) -> PointPayload:
    """Second line of defense: re-check a hit against the same policy.

    Errors name `document_id` (when readable) and field names only.
    """
    raw_id = payload.get("document_id")
    doc = raw_id if isinstance(raw_id, str) else "<unreadable>"
    try:
        hit = PointPayload.model_validate(payload)
    except ValidationError as error:
        fields = sorted({".".join(str(p) for p in e["loc"]) for e in error.errors()})
        raise RetrievalAuthorizationError(
            f"hit for document '{doc}' has a malformed payload: "
            f"check {', '.join(fields)}"
        ) from None
    failed: list[str] = []
    try:
        if AccessScope(hit.access_scope) not in access.policy.allowed_access_scopes:
            failed.append("access_scope")
    except ValueError:
        failed.append("access_scope")
    if hit.tenant_id != access.tenant_id:
        failed.append("tenant_id")
    if hit.owner_user_id is not None:
        failed.append("owner_user_id")
    if failed:
        raise RetrievalAuthorizationError(
            f"hit for document '{hit.document_id}' violates access policy: "
            f"{', '.join(failed)}"
        )
    return hit
