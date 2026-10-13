# 002 — Document Model and DocumentRepository Design

Status: approved (2026-10-13)

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
            ├── errors.py
            └── validate.py
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

Hash a normalized representation, not absolute path. Use SHA-256 throughout.

There are three hashes. Each has one job:

| Hash | Stored in | Job |
|---|---|---|
| `sha256` | manifest (existing) | file integrity only: the raw file bytes, frontmatter included |
| `body_sha256` | manifest (existing) | the document text alone |
| `content_hash` | `KnowledgeDocument` (computed) | **the only change-detection signal for Spec 003 ingestion** |

### `body_sha256` (existing, reused)

```text
body_sha256 = sha256( utf8( strip( normalize_line_endings( body ) ) ) )
```

- `body` is the text after the closing frontmatter delimiter.
- `normalize_line_endings` converts CRLF and CR to LF.
- `strip` removes leading and trailing whitespace.

This reproduces the values already in the manifest. The loader recomputes it and raises `ManifestValidationError` when it differs from the manifest value.

### `content_hash` (new)

```text
content_hash = sha256( utf8( canonical_json( {
    "hash_contract": "content-hash-v1",
    "body_sha256": <body_sha256>,
    "metadata": { <retrieval-affecting fields> }
} ) ) )
```

`canonical_json` means sorted keys, no insignificant whitespace (`separators=(",", ":")`), `ensure_ascii=False`, dates as ISO `YYYY-MM-DD`, and `null` for absent optional values. `lote_languages` keeps its stored order.

Retrieval-affecting fields included in `metadata`:
- `title`, `knowledge_domain`, `tenant_id`;
- `access_scope`, `owner_user_id`;
- `content_language`, `language_scope`, `lote_languages`;
- `source_authority`, `source_type`, `source_url`;
- `approval_status`, `lifecycle_status`, `retrieval_enabled`, `synthetic`;
- `effective_from`, `effective_to`.

Excluded on purpose:
- `document_id`, `document_version`: identity, not content;
- `last_reviewed_at`, `introduced_in_release`: they change without changing what is retrieved;
- `path`, `sha256`, `schema_version`: storage and bookkeeping details.

Consequences:
- a body edit or a change to who can see the document, or which language it applies to, changes `content_hash`;
- a review-date bump or a file move does not change it;
- changing the field list or the recipe requires a new `hash_contract` value, which forces Spec 003 to treat every document as changed.

The raw `sha256` stays an integrity check only. A mismatch is a validation error, but it is never used to decide whether to re-index.

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

## Security fixtures

Files under `tests/fixtures/security/` carry complete, schema-valid metadata. They are **valid but ineligible** documents:
- `approval_status: test_only` and `synthetic: true` exclude them from the production corpus;
- the staff canary is additionally excluded for guest/public by `access_scope: staff`;
- `introduced_in_release: security-fixtures` marks that they belong to no knowledge release;
- `retrieval_enabled: true` is deliberate, so exclusion is proven by authorization and governance checks, not by a disabled flag.

They are not listed in the knowledge manifest. They are never loaded from the production roots. Tests may load them only through an explicitly configured, isolated test repository.

## `make validate-knowledge`

A thin command-line entry point, `python -m way2australia_rag.repositories.validate`, wrapped by `make validate-knowledge`.

It builds a `LocalDocumentRepository` from explicit repository-relative paths and:
1. loads and validates the manifest (structure, duplicates, missing files);
2. validates each document's frontmatter against the JSON Schema and the Pydantic model;
3. checks manifest/frontmatter metadata and the `sha256` and `body_sha256` hashes;
4. lists the eligible public corpus and fails if any eligible document is synthetic, not approved or not public;
5. prints one line per problem (document ID, field, reason) and a summary count;
6. exits `0` when valid and `1` on any problem.

All logic lives in the repository and validation modules. The command only wires configuration and formats output.

`make verify` runs `validate-knowledge`, because it is deterministic and fast.

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
