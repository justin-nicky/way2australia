# 002 — Document Model and DocumentRepository Design

Status: draft

## Design summary

Introduce a storage-independent knowledge domain model in `packages/core` and a repository abstraction/implementation in `packages/rag`.

Conceptual boundary:

```text
knowledge files
      ↓
LocalDocumentRepository
      ↓
DocumentRepository
      ↓
KnowledgeDocument
      ↓
future ingestion pipeline
```

Later:

```text
S3
 ↓
S3DocumentRepository
 ↓
same DocumentRepository contract
 ↓
same ingestion pipeline
```

## Package placement

Recommended structure:

```text
packages/
├── core/
│   └── src/way2australia_core/
│       └── documents/
│           ├── __init__.py
│           ├── models.py
│           └── enums.py
│
└── rag/
    └── src/way2australia_rag/
        └── repositories/
            ├── __init__.py
            ├── base.py
            ├── local.py
            ├── manifest.py
            └── errors.py
```

## Domain model

Use Pydantic models/enums.

Conceptual `KnowledgeDocument` fields:

```python
class KnowledgeDocument(BaseModel):
    document_id: str
    document_version: int
    title: str
    tenant_id: str
    knowledge_domain: str

    access_scope: str
    owner_user_id: str | None

    content_language: str
    language_scope: str
    lote_languages: list[str]

    source_authority: str
    source_type: str
    source_url: str | None

    approval_status: str
    lifecycle_status: str
    last_reviewed_at: date | None

    introduced_in_release: str
    effective_from: date | None
    effective_to: date | None

    retrieval_enabled: bool
    synthetic: bool

    content_hash: str
    content: str
```

Do not add chunk-related fields to this model.

## Repository interface

Use a Python `Protocol`.

Conceptual interface:

```python
class DocumentRepository(Protocol):
    async def get_document(
        self,
        document_id: str,
        version: int | None = None,
    ) -> KnowledgeDocument:
        ...

    async def list_documents(
        self,
        query: DocumentQuery | None = None,
    ) -> list[KnowledgeDocument]:
        ...
```

`DocumentQuery` may include:
- allowed access scopes;
- approval status;
- lifecycle status;
- retrieval-enabled state;
- language applicability where needed.

Do not expose local paths in `DocumentQuery`.

## Why async?

Keep the interface compatible with future network-backed S3 access.

## Local repository

`LocalDocumentRepository` receives explicit configuration:
- knowledge root;
- manifest path;
- metadata schema path;
- policy/config references where required.

Avoid fragile current-working-directory assumptions.

## Allowed corpus

Normal local production roots:

```text
knowledge/public/business/
knowledge/public/official/
knowledge/public/languages/
```

Do not scan the entire repository recursively.

Exclude:
```text
sources/raw/
evaluation/
tests/fixtures/security/
docs/
experiments/
analytics/
config/
knowledge/releases/
```

## Frontmatter parsing

```text
file
 ↓
frontmatter parser
 ↓
metadata + body
 ↓
metadata validation
 ↓
content normalization
 ↓
content hash
 ↓
KnowledgeDocument
```

## Manifest model

Use:

```text
knowledge/manifest/document_manifest.jsonl
```

Recommended behavior:
1. load manifest;
2. validate unique identity/version;
3. resolve each relative path;
4. reject missing paths;
5. parse document;
6. compare stable metadata;
7. expose valid documents.

Do not persist absolute paths.

## Schema validation

Use:
```text
knowledge/schemas/document_metadata.schema.json
```

JSON Schema validates the seed/content contract.
Pydantic validates the in-code domain model.

## Content hashing

Hash a normalized representation, not absolute path.

Recommended initial definition:

```text
hash input =
canonical selected metadata
+
normalized document body
```

Use SHA-256.

Canonicalization should:
- use deterministic field ordering;
- normalize line endings;
- exclude absolute paths;
- exclude volatile derived fields where appropriate.

The chosen hash contract must be documented/tested because Spec 003 will depend on it.

## Eligibility policy

Provide an explicit eligibility function/policy.

Phase 1 public eligibility conceptually requires:

```text
approval_status == approved
AND lifecycle_status == active
AND retrieval_enabled == true
AND synthetic == false
AND access_scope allowed for guest/public
```

Do not infer authorization from directory placement.

## Language behavior

Global rule:
```yaml
language_scope: "global"
lote_languages: ["*"]
```

Malayalam-specific rule:
```yaml
language_scope: "language_specific"
lote_languages: ["ml"]
```

No Malayalam-specific branch belongs in repository infrastructure.

## Error model

Define clear errors such as:
- `DocumentNotFoundError`
- `DuplicateDocumentError`
- `DocumentValidationError`
- `ManifestValidationError`

## Testing strategy

### Unit tests
- Pydantic model validation;
- enum/value validation;
- hash canonicalization;
- eligibility policy;
- manifest uniqueness;
- path handling.

### Integration tests
Use a temporary fixture repository with:
- one valid public document;
- one inactive/non-retrieval document;
- one malformed document;
- duplicate case when needed.

Also test against the real seed corpus where stable and inexpensive.

Assertions include:
- expected production docs load;
- security fixtures do not load;
- raw sources do not load;
- IDs/versions are unique.

## Phase 2 compatibility

Phase 2 can add:

```text
packages/rag/repositories/s3.py
```

without changing:
- `KnowledgeDocument`;
- ingestion orchestration;
- retrieval architecture.

Phase 2 workflow/database behavior remains out of scope.
