# 002 — Document Model and DocumentRepository Tasks

Status: implementing (branch spec/002, base 869c37f)

## T1 — Implement document domain model
**State:** approved (2026-10-14) — predates task review

**Requirements:** R1, R2, R9

- [x] Create document enums/value models under `packages/core`.
- [x] Implement `KnowledgeDocument`.
- [x] Validate stable identity/version fields.
- [x] Validate language metadata.
- [x] Validate source/governance metadata.
- [x] Keep chunk/index fields out of the source document model.

### Verification

Unit tests cover valid and invalid model construction.

## T2 — Define repository contract
**State:** approved (2026-10-14) — predates task review

**Requirements:** R3, R10

- [x] Create `DocumentRepository` Protocol.
- [x] Define repository query/filter object if needed.
- [x] Define repository-safe error types.
- [x] Ensure the interface does not expose local filesystem paths.
- [x] Document future S3 compatibility.

### Verification

A fake/in-memory repository can satisfy the interface without local files.

## T3 — Implement manifest and metadata validation
**State:** approved (2026-10-14)

**Requirements:** R2, R5, R6

- [x] Load `knowledge/manifest/document_manifest.jsonl`.
- [x] Validate manifest record structure.
- [x] Reject duplicate `document_id`/version identities.
- [x] Detect missing referenced files.
- [x] Validate frontmatter against required metadata.
- [x] Use `knowledge/schemas/document_metadata.schema.json` where appropriate.
- [x] Surface actionable validation errors.

### Verification

Unit tests prove:
- a valid manifest loads;
- duplicate `document_id` and duplicate `(document_id, document_version)` are rejected;
- a missing referenced file is detected;
- a manifest/frontmatter metadata mismatch is reported clearly;
- a schema violation produces an actionable error naming the document and field.

## T4 — Implement LocalDocumentRepository
**State:** approved (2026-10-14)

**Requirements:** R3, R4, R9, R10

- [x] Implement explicit repository root configuration.
- [x] Parse Markdown frontmatter + body.
- [x] Load only approved production knowledge locations.
- [x] Build `KnowledgeDocument` instances.
- [x] Implement `get_document`.
- [x] Implement `list_documents`.
- [x] Exclude raw sources, evaluations, docs, release manifests and security fixtures.
- [x] Avoid hard-coded Malayalam-only behavior.

### Verification

Integration tests load the expected local seed corpus through the repository abstraction.

## T5 — Implement deterministic content hashing
**State:** approved (2026-10-14)

**Requirements:** R7

- [x] Compute `body_sha256` exactly as defined in design ("Content hashing").
- [x] Verify computed `body_sha256` and raw `sha256` against the manifest; raise `ManifestValidationError` on mismatch.
- [x] Compute `content_hash` (`content-hash-v1`) from `body_sha256` plus the listed retrieval-affecting metadata using canonical JSON.
- [x] Exclude absolute local path, identity/version, review date and release fields from `content_hash`.
- [x] Document the hash contract.

### Verification

Tests prove:
- computed `body_sha256` matches the manifest for every seed document;
- identical logical content → identical `content_hash`, including CRLF vs LF bodies;
- body change → changed `content_hash`;
- `access_scope` or `lote_languages` change → changed `content_hash`;
- `last_reviewed_at` change alone → unchanged `content_hash`;
- path change alone → unchanged `content_hash`;
- a manifest `sha256`/`body_sha256` mismatch raises `ManifestValidationError`.

## T6 — Implement retrieval eligibility filtering
**State:** approved (2026-10-15)

**Requirements:** R8, R9

- [x] Implement production eligibility policy.
- [x] Enforce approval/lifecycle/retrieval-enabled conditions.
- [x] Exclude synthetic documents.
- [x] Enforce allowed access scopes from server-owned policy input.
- [x] Keep language metadata independent from authorization.

### Verification

Tests cover:
- active public document included;
- inactive/deprecated excluded;
- retrieval-disabled excluded;
- synthetic excluded;
- non-public excluded for guest/public;
- language metadata does not broaden access.

## T7 — Add `make validate-knowledge`
**State:** approved (2026-10-15)

**Requirements:** R5, R6, R8, R11

- [x] Implement `way2australia_rag.repositories.validate` as a thin entry point over the repository and validation modules.
- [x] Report every problem with document ID, field and reason, then a summary count.
- [x] Fail if any eligible public document is synthetic, not approved or not public.
- [x] Exit `0` when valid and `1` on any problem.
- [x] Add the `validate-knowledge` Makefile target and include it in `make verify`.
- [x] Update `docs/project/COMMANDS.md` if the behavior differs from what it documents.

### Verification

- `make validate-knowledge` exits `0` on the current seed corpus.
- Tests run the entry point against temporary broken repositories (duplicate ID, missing file, schema violation, hash mismatch) and assert exit code `1` with the document ID in the output.

## T8 — Add complete automated tests
**State:** approved (2026-10-15)

**Requirements:** R11

- [x] Add unit tests for models.
- [x] Add unit tests for manifest loading.
- [x] Add unit tests for hashing.
- [x] Add unit tests for eligibility.
- [x] Add repository integration tests.
- [x] Verify real seed corpus IDs/versions are unique.
- [x] Assert `tests/fixtures/security/` is not in the production corpus.
- [x] Assert both security fixtures parse as valid documents and are ineligible for guest/public (valid-but-ineligible, see design "Security fixtures").

### Verification

```bash
make verify
```

## T9 — Documentation and handoff
**State:** approved (2026-10-15)

**Requirements:** Definition of Done

- [x] Update `docs/project/CURRENT_STATE.md`.
- [x] Update `docs/project/DECISIONS.md` if durable hash/repository decisions were introduced.
- [x] Update `docs/knowledge/SCHEMA_AND_METADATA.md` only if the implemented schema differs from seed documentation.
- [x] Keep Spec 003 concerns out of this implementation.
- [x] Mark task completion accurately.

- [ ] Hand off to `spec-orchestrator` for completion (`all tasks approved`, optional `spec-reviewer`, merge).

### Verification

- `make verify` passes.
- `CURRENT_STATE.md`, `DECISIONS.md` and this task list match the implemented reality.

## Completion gate

Do not implement chunking, embeddings, Qdrant ingestion, or content-update processing in this spec.
