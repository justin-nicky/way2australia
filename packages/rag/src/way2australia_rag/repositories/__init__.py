"""Document repository contract and implementations."""

from way2australia_rag.repositories.base import DocumentQuery, DocumentRepository
from way2australia_rag.repositories.eligibility import (
    GUEST_PUBLIC_POLICY,
    EligibilityPolicy,
    list_eligible_documents,
)
from way2australia_rag.repositories.errors import (
    DocumentNotFoundError,
    DocumentRepositoryError,
    DocumentValidationError,
    DuplicateDocumentError,
    ManifestValidationError,
)
from way2australia_rag.repositories.local import (
    DEFAULT_APPROVED_ROOTS,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.manifest import (
    ManifestEntry,
    ValidationProblem,
    load_manifest,
    validate_manifest,
)

__all__ = [
    "DEFAULT_APPROVED_ROOTS",
    "GUEST_PUBLIC_POLICY",
    "DocumentNotFoundError",
    "DocumentQuery",
    "DocumentRepository",
    "DocumentRepositoryError",
    "DocumentValidationError",
    "DuplicateDocumentError",
    "EligibilityPolicy",
    "LocalDocumentRepository",
    "LocalRepositoryConfig",
    "ManifestEntry",
    "ManifestValidationError",
    "ValidationProblem",
    "list_eligible_documents",
    "load_manifest",
    "validate_manifest",
]
