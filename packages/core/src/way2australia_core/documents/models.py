"""Storage-independent knowledge-document domain model.

`KnowledgeDocument` describes one version of one source document. It carries
no storage paths and no chunk/index fields: chunks, embeddings and indexes are
derived artifacts with their own identities.
"""

import re
from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from way2australia_core.documents.enums import (
    AccessScope,
    ApprovalStatus,
    LanguageScope,
    LifecycleStatus,
    SourceAuthority,
)

ALL_LOTE_LANGUAGES = "*"
"""`lote_languages` marker for knowledge shared by every CCL language."""

_DOCUMENT_ID_PATTERN = r"^[a-z0-9][a-z0-9_-]*$"
_LANGUAGE_CODE = re.compile(r"^[a-z]{2,3}$")
_SHA256_HEX_PATTERN = r"^[0-9a-f]{64}$"

NonEmptyStr = Annotated[str, Field(min_length=1, pattern=r"\S")]
"""A string containing at least one non-whitespace character."""


def _check_language_code(value: str, field_name: str) -> str:
    if not _LANGUAGE_CODE.fullmatch(value):
        raise ValueError(
            f"{field_name} must be a lowercase ISO 639 code (e.g. 'en', 'ml'), "
            f"got {value!r}"
        )
    return value


class KnowledgeDocument(BaseModel):
    """One approved-or-candidate version of a stable knowledge document.

    Identity is `document_id`; `document_version` increments when approved
    content changes. Neither depends on where the document is stored.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: Annotated[str, Field(pattern=_DOCUMENT_ID_PATTERN)]
    document_version: Annotated[int, Field(ge=1, strict=True)]
    title: NonEmptyStr
    tenant_id: NonEmptyStr
    knowledge_domain: NonEmptyStr

    access_scope: AccessScope
    owner_user_id: NonEmptyStr | None = None

    content_language: str
    language_scope: LanguageScope
    lote_languages: tuple[str, ...]

    source_authority: SourceAuthority
    source_type: NonEmptyStr
    source_url: NonEmptyStr | None = None

    approval_status: ApprovalStatus
    lifecycle_status: LifecycleStatus
    last_reviewed_at: date | None = None

    introduced_in_release: NonEmptyStr
    effective_from: date | None = None
    effective_to: date | None = None

    retrieval_enabled: Annotated[bool, Field(strict=True)]
    synthetic: Annotated[bool, Field(strict=True)]

    content_hash: Annotated[str, Field(pattern=_SHA256_HEX_PATTERN)]
    content: NonEmptyStr

    @field_validator("content_language")
    @classmethod
    def _validate_content_language(cls, value: str) -> str:
        return _check_language_code(value, "content_language")

    @field_validator("lote_languages")
    @classmethod
    def _validate_lote_languages(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("lote_languages must not be empty")
        if len(set(value)) != len(value):
            raise ValueError(f"lote_languages contains duplicates: {list(value)}")
        if ALL_LOTE_LANGUAGES in value:
            if len(value) != 1:
                raise ValueError(
                    f"lote_languages must be exactly ['{ALL_LOTE_LANGUAGES}'] "
                    f"when it contains '{ALL_LOTE_LANGUAGES}', got {list(value)}"
                )
            return value
        for code in value:
            _check_language_code(code, "lote_languages entry")
        return value

    @model_validator(mode="after")
    def _validate_cross_field_rules(self) -> Self:
        is_global = self.lote_languages == (ALL_LOTE_LANGUAGES,)
        if self.language_scope is LanguageScope.GLOBAL and not is_global:
            raise ValueError(
                "language_scope 'global' requires lote_languages "
                f"['{ALL_LOTE_LANGUAGES}'], got {list(self.lote_languages)}"
            )
        if self.language_scope is LanguageScope.LANGUAGE_SPECIFIC and is_global:
            raise ValueError(
                "language_scope 'language_specific' requires explicit language "
                f"codes in lote_languages, not '{ALL_LOTE_LANGUAGES}'"
            )

        if self.access_scope is AccessScope.USER_PRIVATE:
            if self.owner_user_id is None:
                raise ValueError("access_scope 'user_private' requires owner_user_id")
        elif self.owner_user_id is not None:
            raise ValueError(
                "owner_user_id is only allowed with access_scope 'user_private', "
                f"got access_scope {self.access_scope.value!r}"
            )

        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_to < self.effective_from
        ):
            raise ValueError(
                f"effective_to ({self.effective_to}) is before "
                f"effective_from ({self.effective_from})"
            )
        return self
