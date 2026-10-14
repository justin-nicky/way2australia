# 002 — Task Reviews

Append-only; newest at the bottom.

## T3 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: see `git log --grep "Spec-Task: 002/T3"`
- Verification run: `make verify` → pass (90 tests: 16 new in `test_manifest_validation.py`); `make test-integration` → no integration tests collected
- Notes:
  - New modules in `packages/rag/.../repositories/`: `manifest.py` (`load_manifest`, `check_manifest_documents`, `compare_manifest_to_metadata`, `validate_manifest`, `ValidationProblem`) and `frontmatter.py` (`split_frontmatter`, reused by T4). Both manifest records and file frontmatter are validated against `knowledge/schemas/document_metadata.schema.json` (manifest records additionally require `path`, `sha256`, `body_sha256`; `path` must be repo-relative with no `..`).
  - Error split: structural/JSON/schema failures of the manifest raise `ManifestValidationError` (all records listed); duplicates raise `DuplicateDocumentError` (repeated `document_id`, or repeated `(document_id, document_version)` with the version in the error); per-document findings (missing file, bad frontmatter, manifest/frontmatter mismatch) are returned as `ValidationProblem` lists so T7's CLI can print one line per problem.
  - **Dependencies added** to `packages/rag`: `jsonschema` (the design requires JSON Schema validation; no other option in the stack) and `pyyaml` (frontmatter; already in `uv.lock` transitively). Flag for review as a dependency decision.
  - Deviation/interpretation: the seed manifest omits `effective_from`/`effective_to` while every frontmatter has them. A field only the frontmatter carries is NOT reported as a mismatch (manifest is a subset); a field in both with different values, or a non-null manifest value missing from frontmatter, is. Seed data not edited.
  - Frontmatter YAML timestamps are kept as strings so dates validate against the schema as written.
  - Not done (belongs to later tasks): `sha256`/`body_sha256` verification (T5/T7), Pydantic `KnowledgeDocument` construction from frontmatter (T4), CLI (T7). The real seed manifest validates with zero problems (tested).
