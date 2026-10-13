"""Controlled vocabularies for knowledge-document metadata.

Authorization (`AccessScope`) and language applicability (`LanguageScope`)
are separate concepts and must never be derived from each other.
"""

from enum import StrEnum


class AccessScope(StrEnum):
    """Who may retrieve a document. Phase 1 retrieves only `public`."""

    PUBLIC = "public"
    STAFF = "staff"
    SUBSCRIBER = "subscriber"
    USER_PRIVATE = "user_private"
    ADMIN = "admin"


class ApprovalStatus(StrEnum):
    """Governance state of the document content."""

    APPROVED = "approved"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    TEST_ONLY = "test_only"


class LifecycleStatus(StrEnum):
    """Lifecycle of a document version. Mirrors the metadata JSON Schema."""

    ACTIVE = "active"
    DRAFT = "draft"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class LanguageScope(StrEnum):
    """Whether knowledge applies to all CCL languages or to specific ones."""

    GLOBAL = "global"
    LANGUAGE_SPECIFIC = "language_specific"


class SourceAuthority(StrEnum):
    """Authority behind a document, as named in `config/source_precedence.yaml`."""

    OWNER_APPROVED = "owner_approved"
    WAY2AUSTRALIA_PUBLIC_WEBSITE = "way2australia_public_website"
    NAATI = "naati"
    NAATI_LANGUAGE_POLICY = "naati_language_policy"
    HOME_AFFAIRS = "home_affairs"
    SYNTHETIC = "synthetic"
