# 002 — Document Model and DocumentRepository Requirements

Status: approved (2026-10-13)

## Goal

Introduce the stable knowledge-document domain model and repository abstraction that all later ingestion code will use.

Phase 1 shall read approved local seed documents through `LocalDocumentRepository`.

The design must preserve a clean path to a future `S3DocumentRepository` without implementing S3 in this specification.

## Dependency

Spec 001 — Project Foundation should be complete first.

## R1 — Stable KnowledgeDocument model

The system shall represent normalized knowledge documents using a typed domain model.

### Acceptance criteria

Each document exposes at least:

- stable `document_id`;
- integer `document_version`;
- title;
- knowledge domain;
- tenant ID;
- access scope;
- content language;
- language scope;
- LOTE applicability;
- source authority;
- source type;
- optional source URL;
- approval status;
- lifecycle status;
- review date where available;
- release/version metadata;
- retrieval-enabled flag;
- synthetic/test flag;
- document body/content.

Invalid or missing required fields must fail clearly.

## R2 — Stable identity and version semantics

Document identity shall be independent of document content and physical storage path.

### Acceptance criteria

- approved edits do not require changing `document_id`;
- approved content changes increment `document_version`;
- physical path is not treated as business identity;
- chunk IDs are not part of document identity.

## R3 — DocumentRepository abstraction

Consumers shall access documents through a repository interface rather than direct filesystem calls.

### Acceptance criteria

The repository supports:
- listing documents;
- getting a document by stable ID;
- optionally requesting a specific version where supported;
- filtering to documents eligible for use;
- clear errors for missing or invalid documents.

The interface shall not expose filesystem-specific concepts to callers.

## R4 — LocalDocumentRepository

Phase 1 shall provide a local-filesystem repository implementation.

### Acceptance criteria

- reads normalized knowledge from approved local knowledge directories;
- parses Markdown frontmatter and body;
- excludes raw sources, evaluation files, docs, experiment files, analytics files, and security fixtures from production loading;
- can return the active/retrieval-enabled public corpus;
- does not hard-code Malayalam as the only language;
- does not treat directory location alone as authorization.

## R5 — Manifest integration

The repository shall use or validate against the knowledge manifest.

### Acceptance criteria

- manifest entries can be loaded;
- every production knowledge document has a stable manifest relationship;
- duplicate document IDs are rejected;
- duplicate `(document_id, document_version)` pairs are rejected;
- missing referenced files are detected;
- manifest/document metadata mismatches are surfaced clearly.

## R6 — Metadata/schema validation

Knowledge metadata shall be validated before documents are considered eligible.

### Acceptance criteria

- required metadata fields are validated;
- lifecycle/approval values are validated;
- access scope values are validated against project policy/config where practical;
- malformed metadata produces actionable errors;
- invalid documents do not silently enter the corpus.

## R7 — Content hashing

The repository/loading layer shall expose a deterministic content hash useful for later idempotent ingestion.

### Acceptance criteria

- identical normalized source content produces the same hash;
- meaningful content changes produce a different hash;
- hash generation is independent of absolute path;
- changes to retrieval-affecting metadata (for example access scope or LOTE applicability) produce a different hash;
- changes to review dates alone do not change the hash;
- exactly one hash is designated for change detection, and its relationship to the manifest's existing `sha256` and `body_sha256` is documented;
- hashing behavior is tested.

## R8 — Retrieval eligibility

The repository shall distinguish stored documents from documents eligible for production RAG ingestion.

### Acceptance criteria

A document is not eligible when, for example:
- `retrieval_enabled` is false;
- approval status is not approved;
- lifecycle status is not active;
- the document is synthetic/test-only;
- its access scope is not allowed by the requested repository query/filter.

Phase 1 normal production corpus is public approved active knowledge only.

## R9 — Language metadata neutrality

The document model/repository shall remain language-neutral.

### Acceptance criteria

- Malayalam uses `ml`;
- global knowledge may use `lote_languages: ["*"]`;
- future languages can be added through data/config without changing repository interfaces;
- language metadata does not grant authorization.

## R10 — Future storage portability

The repository abstraction shall allow a future S3-backed implementation without changing ingestion domain logic.

### Acceptance criteria

- callers depend on the repository interface, not `Path`;
- local file parsing remains inside the local adapter;
- S3 is not implemented in this spec;
- future S3 assumptions are not baked into domain models.

## R11 — Tests

The document model and local repository shall have deterministic automated tests.

### Acceptance criteria

Tests cover at least:
- valid document loading;
- invalid/missing metadata;
- duplicate IDs/versions;
- missing manifest file;
- metadata/manifest mismatch;
- retrieval eligibility filtering;
- language metadata;
- content hashing;
- repository get/list behavior.

Security fixtures must never enter the normal production corpus. They carry complete metadata and are treated as valid but ineligible documents.

## Out of scope

This specification does **not** implement:
- chunking;
- chunk IDs;
- embedding generation;
- Qdrant writes;
- BM25/FTS5 indexing;
- ingestion orchestration;
- change/update processing;
- S3;
- metadata database;
- Knowledge Release Candidate workflow;
- admin UI;
- evaluation impact analysis;
- LLM evaluation suggestions.

## Definition of Done

This specification is complete when:
- typed document model exists;
- `DocumentRepository` exists;
- `LocalDocumentRepository` loads the current seed corpus;
- manifest/schema validation works;
- `make validate-knowledge` runs as part of `make verify`;
- content hashing works;
- eligibility filtering works;
- deterministic tests pass;
- RAG/application code does not need direct filesystem access for source knowledge;
- `make verify` passes;
- `CURRENT_STATE.md` is updated.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | model unit tests (valid/invalid construction) |
| R2 | T1, T3 | model tests; duplicate `(document_id, document_version)` manifest tests |
| R3 | T2, T4 | in-memory fake satisfies the Protocol; repository get/list integration tests |
| R4 | T4 | seed-corpus integration tests; excluded-location assertions |
| R5 | T3, T7 | manifest unit tests (duplicates, missing files, mismatches); `make validate-knowledge` |
| R6 | T3, T7 | metadata/schema validation tests; `make validate-knowledge` |
| R7 | T5 | hashing unit tests (same content, changed content, moved path) |
| R8 | T6, T7 | eligibility unit tests; security fixtures valid but ineligible |
| R9 | T1, T4, T6 | language metadata tests; language does not broaden access |
| R10 | T2, T4 | Protocol/interface review: no `Path` in the public contract |
| R11 | T7, T8 | `make verify` (includes `validate-knowledge`) |

## Change log

<!-- Approved amendments only, one dated line each. -->
