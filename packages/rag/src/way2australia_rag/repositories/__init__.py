"""Document repository contract and implementations."""

from way2australia_rag.repositories.base import DocumentQuery, DocumentRepository
from way2australia_rag.repositories.errors import (
    DocumentNotFoundError,
    DocumentRepositoryError,
    DocumentValidationError,
    DuplicateDocumentError,
    ManifestValidationError,
)

__all__ = [
    "DocumentNotFoundError",
    "DocumentQuery",
    "DocumentRepository",
    "DocumentRepositoryError",
    "DocumentValidationError",
    "DuplicateDocumentError",
    "ManifestValidationError",
]
