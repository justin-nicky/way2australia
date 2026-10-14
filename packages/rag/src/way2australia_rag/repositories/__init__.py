"""Document repository contract and implementations."""

from way2australia_rag.repositories.base import DocumentQuery, DocumentRepository
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
    "DocumentNotFoundError",
    "DocumentQuery",
    "DocumentRepository",
    "DocumentRepositoryError",
    "DocumentValidationError",
    "DuplicateDocumentError",
    "LocalDocumentRepository",
    "LocalRepositoryConfig",
    "ManifestEntry",
    "ManifestValidationError",
    "ValidationProblem",
    "load_manifest",
    "validate_manifest",
]
