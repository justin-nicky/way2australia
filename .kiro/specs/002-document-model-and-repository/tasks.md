# 002 — Document Model and DocumentRepository Tasks

Status: draft

## T1 — Implement document domain model

**Requirements:** R1, R2, R9

- [ ] Create document enums/value models under `packages/core`.
- [ ] Implement `KnowledgeDocument`.
- [ ] Validate stable identity/version fields.
- [ ] Validate language metadata.
- [ ] Validate source/governance metadata.
- [ ] Keep chunk/index fields out of the source document model.

### Verification

Unit tests cover valid and invalid model construction.

## T2 — Define repository contract

**Requirements:** R3, R10

- [ ] Create `DocumentRepository` Protocol.
- [ ] Define repository query/filter object if needed.
- [ ] Define repository-safe error types.
- [ ] Ensure the interface does not expose local filesystem paths.
- [ ] Document future S3 compatibility.

### Verification

A fake/in-memory repository can satisfy the interface without local files.

## T3 — Implement manifest and metadata validation

**Requirements:** R2, R5, R6

- [ ] Load `knowledge/manifest/document_manifest.jsonl`.
- [ ] Validate manifest record structure.
- [ ] Reject duplicate `document_id`/version identities.
- [ ] Detect missing referenced files.
- [ ] Validate frontmatter against required metadata.
- [ ] Use `knowledge/schemas/document_metadata.schema.json` where appropriate.
- [ ] Surface actionable validation errors.

### Verification

Unit tests prove:
- a valid manifest loads;
- duplicate `document_id` and duplicate `(document_id, document_version)` are rejected;
- a missing referenced file is detected;
- a manifest/frontmatter metadata mismatch is reported clearly;
- a schema violation produces an actionable error naming the document and field.

## T4 — Implement LocalDocumentRepository

**Requirements:** R3, R4, R9, R10

- [ ] Implement explicit repository root configuration.
- [ ] Parse Markdown frontmatter + body.
- [ ] Load only approved production knowledge locations.
- [ ] Build `KnowledgeDocument` instances.
- [ ] Implement `get_document`.
- [ ] Implement `list_documents`.
- [ ] Exclude raw sources, evaluations, docs, release manifests and security fixtures.
- [ ] Avoid hard-coded Malayalam-only behavior.

### Verification

Integration tests load the expected local seed corpus through the repository abstraction.

## T5 — Implement deterministic content hashing

**Requirements:** R7

- [ ] Define canonical hash input.
- [ ] Normalize line endings/selected metadata deterministically.
- [ ] Use SHA-256.
- [ ] Exclude absolute local path.
- [ ] Document the hash contract.

### Verification

Tests prove:
- identical logical content → identical hash;
- content change → changed hash;
- path change alone → unchanged hash.

## T6 — Implement retrieval eligibility filtering

**Requirements:** R8, R9

- [ ] Implement production eligibility policy.
- [ ] Enforce approval/lifecycle/retrieval-enabled conditions.
- [ ] Exclude synthetic documents.
- [ ] Enforce allowed access scopes from server-owned policy input.
- [ ] Keep language metadata independent from authorization.

### Verification

Tests cover:
- active public document included;
- inactive/deprecated excluded;
- retrieval-disabled excluded;
- synthetic excluded;
- non-public excluded for guest/public;
- language metadata does not broaden access.

## T7 — Add complete automated tests

**Requirements:** R11

- [ ] Add unit tests for models.
- [ ] Add unit tests for manifest loading.
- [ ] Add unit tests for hashing.
- [ ] Add unit tests for eligibility.
- [ ] Add repository integration tests.
- [ ] Verify real seed corpus IDs/versions are unique.
- [ ] Assert `tests/fixtures/security/` is not in the production corpus.

### Verification

```bash
make verify
```

## T8 — Documentation and handoff

**Requirements:** Definition of Done

- [ ] Update `docs/project/CURRENT_STATE.md`.
- [ ] Update `docs/project/DECISIONS.md` if durable hash/repository decisions were introduced.
- [ ] Update `docs/knowledge/SCHEMA_AND_METADATA.md` only if the implemented schema differs from seed documentation.
- [ ] Keep Spec 003 concerns out of this implementation.
- [ ] Mark task completion accurately.

- [ ] Hand off to `spec-reviewer` (status `implemented — pending review`).

### Verification

- `make verify` passes.
- `CURRENT_STATE.md`, `DECISIONS.md` and this task list match the implemented reality.

## Completion gate

Do not implement chunking, embeddings, Qdrant ingestion, or content-update processing in this spec.
