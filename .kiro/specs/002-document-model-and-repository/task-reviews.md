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

### User decision
- 2026-10-14 — approved

## T4 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: see `git log --grep "Spec-Task: 002/T4"`
- Verification run: `make verify` -> pass (101 tests; 11 new in `test_local_repository.py`, 8 marked `integration`); `make test-integration` -> 8 passed (seed corpus loaded through the repository abstraction)
- Notes:
  - New `repositories/local.py`: `LocalDocumentRepository`, `LocalRepositoryConfig` (explicit `repo_root`; manifest path, schema path and approved roots are repo-relative, no CWD dependence; a test runs from a different CWD) and `DEFAULT_APPROVED_ROOTS` (business, official, languages). Async methods wrap a one-time cached load run via `asyncio.to_thread`.
  - Loading is manifest-driven (per design): entries whose path is not under an approved root are skipped, so raw sources, evaluation, docs, config, releases and security fixtures are never read even if listed (tested with a manifest listing each). Validation reuses T3 (`check_manifest_documents`); any problem fails the whole load with `ManifestValidationError` naming document and field.
  - `get_document` returns latest version unless pinned; `list_documents` sorts by `(document_id, version)` and applies all `DocumentQuery` filters. `lote_language` matches explicit codes or `*`; it never touches access scope. No Malayalam-specific code; directory placement is not used for authorization.
  - **Interim `content_hash`**: T5 owns `content-hash-v1`, but `KnowledgeDocument` requires a hash now. `_provisional_content_hash` hashes the normalized body only; T5 must replace that single call. Not the final contract.
  - T3 finding F2 fixed (in `manifest.py`, a T4-touched file): `load_schema` wraps `SchemaError` in `ManifestValidationError`; new `describe_error` replaces `str(exc)` for OS/JSON errors so messages carry no absolute paths. Tests added. F1 (record deps) stays for T9; F3 (nested `required` path prefix) not fixed, no effect with the current schema, deferred to T7.
  - No files under `knowledge/`, `evaluation/` or `config/` touched.
  - Not done: real `content_hash`, sha256/body_sha256 verification (T5), eligibility policy (T6), CLI (T7).

### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (ruff clean, pyright 0 errors, skills mirrors match, 101 tests passed); `make test-integration` → pass (8 passed, 93 deselected; the 8 load the real seed corpus through `DocumentRepository`); `make test-unit` → 93 passed; `git diff --stat 42b9775^ 42b9775 -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R7] `content_hash` is a provisional body-only SHA-256 (`_provisional_content_hash`), not `content-hash-v1` → T5 replaces it; until then the value must not be relied on for change detection.
  - F2 [MINOR, IMPLEMENTATION, R5] Manifest entries outside the approved roots are dropped silently, and files under the roots that are not in the manifest are ignored silently → have T7's `validate-knowledge` report both so a misplaced or unlisted document is visible.
  - F3 [MINOR, IMPLEMENTATION, R6] On a Pydantic `ValidationError`, `_build` reports only the first error → acceptable (JSON Schema problems are already listed in full first); consider listing all in T7.
- Summary for user (PASS only):
  - Changed: new `packages/rag/.../repositories/local.py` (`LocalDocumentRepository`, `LocalRepositoryConfig` with explicit `repo_root` and repo-relative manifest/schema/approved-root paths, `DEFAULT_APPROVED_ROOTS` = business, official, languages); `manifest.py` errors no longer leak absolute paths and an invalid schema raises `ManifestValidationError` (T3 F2 fixed); 11 tests in `test_local_repository.py`.
  - Verified by: `make verify` (101 tests), `make test-integration` (8 seed-corpus tests: all 13 seed documents load, get/list by ID and version, language filter is data-driven and never widens access, entries pointing at security fixtures/evaluation/docs/raw/releases are never loaded, no CWD dependence).
  - Worth your attention: (1) `content_hash` is a placeholder until T5; (2) loading is manifest-driven and filtered by approved roots; entries outside them are skipped rather than reported (T7 should surface them); (3) any invalid document fails the whole load, not just that document.
