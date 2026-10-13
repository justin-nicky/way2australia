"""Repository-safe error types.

Messages identify documents by `document_id` / `document_version` and metadata
field names, never by absolute filesystem paths, so they are valid for any
backing store (local files today, S3 later).
"""


class DocumentRepositoryError(Exception):
    """Base class for all document repository errors."""


class DocumentNotFoundError(DocumentRepositoryError):
    """No document matches the requested identity/version."""

    def __init__(self, document_id: str, version: int | None = None) -> None:
        self.document_id = document_id
        self.version = version
        suffix = "" if version is None else f" version {version}"
        super().__init__(f"Document not found: {document_id}{suffix}")


class DuplicateDocumentError(DocumentRepositoryError):
    """A `document_id` or `(document_id, document_version)` appears more than once."""

    def __init__(self, document_id: str, version: int | None = None) -> None:
        self.document_id = document_id
        self.version = version
        suffix = "" if version is None else f" version {version}"
        super().__init__(f"Duplicate document: {document_id}{suffix}")


class DocumentValidationError(DocumentRepositoryError):
    """A document's metadata or content is invalid."""

    def __init__(self, document_id: str, field: str, reason: str) -> None:
        self.document_id = document_id
        self.field = field
        self.reason = reason
        super().__init__(f"{document_id}: {field}: {reason}")


class ManifestValidationError(DocumentRepositoryError):
    """The document manifest is malformed or disagrees with the documents."""

    def __init__(
        self, reason: str, document_id: str | None = None, field: str | None = None
    ) -> None:
        self.reason = reason
        self.document_id = document_id
        self.field = field
        parts = [p for p in (document_id, field) if p]
        prefix = ": ".join(parts)
        super().__init__(f"{prefix}: {reason}" if prefix else reason)
