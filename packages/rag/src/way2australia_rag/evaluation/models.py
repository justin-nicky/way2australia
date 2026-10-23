"""Typed evaluation suite and case models (Spec 006 R1, R3).

Case models ignore unknown fields so new case fields never break loading.
`access_context` is loaded but never used: retrieval always uses the
server-resolved access, never a case's own claim.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetType(StrEnum):
    GOLDEN_ANSWERABLE = "golden_answerable"
    UNANSWERABLE_REFUSAL = "unanswerable_refusal"
    SECURITY = "security"


class CaseStatus(StrEnum):
    """Mirrors `evaluation_case.schema.json`."""

    ACTIVE = "active"
    REVIEW_REQUIRED = "review_required"
    POTENTIALLY_OBSOLETE = "potentially_obsolete"
    DEPRECATED = "deprecated"
    REPLACED = "replaced"
    SUGGESTED = "suggested"


class DatasetRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: DatasetType
    path: str


class SuiteManifest(BaseModel):
    """Suite manifest. Fields beyond id, version and datasets default to
    empty: the schema check (`validate-evaluation`) enforces them, the loader
    stays tolerant."""

    model_config = ConfigDict(extra="ignore")

    evaluation_suite_id: str
    version: int
    status: str = ""
    introduced_in_release: str = ""
    datasets: list[DatasetRef]
    case_count: int | None = None


class CaseBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    case_id: str
    case_version: int
    # A plain string on purpose: a status outside `CaseStatus` is reported by
    # `validate-evaluation` and excluded here, never a load failure (R12).
    status: str
    evaluation_suite_id: str = ""
    query: str
    access_context: dict[str, Any] | None = None  # never used for access


class GoldenCase(CaseBase):
    answerable: bool
    relevant_document_ids: list[str]
    relevant_section_ids: list[str] = Field(default_factory=list)
    query_language: str
    category: str


class UnanswerableCase(CaseBase):
    answerable: bool
    expected_behavior: str


class SecurityCase(CaseBase):
    attack_type: str
    expected_behavior: str


AnyCase = GoldenCase | UnanswerableCase | SecurityCase

CASE_MODELS: dict[DatasetType, type[CaseBase]] = {
    DatasetType.GOLDEN_ANSWERABLE: GoldenCase,
    DatasetType.UNANSWERABLE_REFUSAL: UnanswerableCase,
    DatasetType.SECURITY: SecurityCase,
}


class LoadedSuite(BaseModel):
    manifest: SuiteManifest
    goldens: list[GoldenCase] = Field(default_factory=list)
    unanswerable: list[UnanswerableCase] = Field(default_factory=list)
    security: list[SecurityCase] = Field(default_factory=list)

    def cases(self, dataset_type: DatasetType) -> list[Any]:
        if dataset_type is DatasetType.GOLDEN_ANSWERABLE:
            return list(self.goldens)
        if dataset_type is DatasetType.UNANSWERABLE_REFUSAL:
            return list(self.unanswerable)
        return list(self.security)

    def active(self, dataset_type: DatasetType) -> list[Any]:
        """Only `active` cases. Every other status, `suggested` included, is out."""
        return [
            c for c in self.cases(dataset_type) if c.status == CaseStatus.ACTIVE.value
        ]

    def excluded_by_status(self, dataset_type: DatasetType) -> dict[str, int]:
        """Counts of the non-active cases, by status."""
        counts: dict[str, int] = {}
        for case in self.cases(dataset_type):
            if case.status != CaseStatus.ACTIVE.value:
                counts[case.status] = counts.get(case.status, 0) + 1
        return dict(sorted(counts.items()))
