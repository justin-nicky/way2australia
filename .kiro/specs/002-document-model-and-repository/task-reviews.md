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

### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (ruff clean, pyright 0 errors, 90 tests passed, skills mirrors match); `make test-integration` → exit 0, 0 collected (90 deselected); `uv run pytest packages/rag/tests/test_manifest_validation.py` → 16 passed; `git diff --stat 5832054^ 5832054 -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R5] New runtime dependencies `jsonschema` and `pyyaml` are not recorded in `TECH_STACK.md`/`DECISIONS.md` → record them at T9 (design requires JSON Schema validation and frontmatter parsing, so they are in scope).
  - F2 [MINOR, IMPLEMENTATION, R6] `load_schema` lets `jsonschema.SchemaError` escape instead of `ManifestValidationError`; an `OSError` from reading a document file is reported via `str(exc)`, which can include an absolute path (`errors.py` says messages never carry absolute paths) → wrap/neutralise in T4 or T7.
  - F3 [MINOR, IMPLEMENTATION, R6] For nested `required` violations, `schema_problems` reports only the leaf field name, dropping the parent path → prefix with `error.path`. No nested objects in the current schema, so no effect today.
- Summary for user (PASS only):
  - Changed: new `packages/rag/.../repositories/manifest.py` (load manifest, schema-check records and frontmatter, reject duplicate `document_id` and `(document_id, document_version)`, detect missing files, compare manifest to frontmatter) and `frontmatter.py` (YAML frontmatter split, dates kept as strings); 16 unit tests; `jsonschema` + `pyyaml` added to `packages/rag`.
  - Verified by: `make verify` (90 tests, ruff, pyright), the T3 test file (all five required verification cases, plus the real seed manifest validating with 0 problems); no seed/eval/config files touched.
  - Worth your attention: (1) two new dependencies — approve or object; (2) the manifest is treated as a subset of frontmatter: a field only the frontmatter has (e.g. `effective_from`) is not a mismatch, and a `null` manifest value missing from frontmatter is ignored; (3) structural/duplicate errors raise, per-document problems are returned as a list for T7's CLI; (4) a repeated `document_id` with a different version is rejected, so the manifest holds one version per document.
