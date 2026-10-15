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

### User decision
- 2026-10-14 — approved

## T5 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: see `git log --grep "Spec-Task: 002/T5"`
- Verification run: `make verify` -> pass (126 tests, ruff and pyright clean; 25 new in `test_content_hash.py`); `make test-integration` -> 9 passed (seed corpus through the repository)
- Notes:
  - New `repositories/hashing.py` owns the hash contract (documented in its module docstring and mirrored in design "Content hashing"): `normalize_body`, `compute_body_sha256`, `sha256_hex`, `canonical_json`, `compute_content_hash`, `HASH_CONTRACT = "content-hash-v1"`, `CONTENT_HASH_METADATA_FIELDS` (the 17 fields from the design). Absent optional fields hash as `null`; `lote_languages` keeps stored order.
  - `local.py`: `_provisional_content_hash` and `_normalized_body` removed; `_build` now calls `compute_content_hash(body, frontmatter)` and `normalize_body`. The hash is computed from the validated frontmatter (ISO date strings), not from absolute path.
  - Integrity checks: `manifest.check_manifest_documents` now also calls new `check_integrity_hashes`, comparing the manifest `sha256` (raw bytes) and `body_sha256` to recomputed values. Mismatches are `ValidationProblem`s (document and field only), so the loader raises `ManifestValidationError` and T7's `validate-knowledge` reports them. They run only after schema and manifest/frontmatter checks pass, so other problems are not drowned by hash noise.
  - Existing test helper `record()` in `test_manifest_validation.py` used placeholder hashes; it now computes real hashes when the document file exists (the missing-file test keeps placeholders). No production behavior change beyond the new check.
  - Tests: every seed document's `body_sha256` and `sha256` match the manifest; CRLF/LF/padding equivalence; body change; `access_scope`, `lote_languages` and other retrieval-affecting fields change the hash; `last_reviewed_at`, path, release, id and version do not; recipe re-stated independently in the test; repository hash equals `compute_content_hash`; body edit and raw-only edit raise `ManifestValidationError` without absolute paths; moving a file leaves every `content_hash` unchanged.
  - T4 review F1 resolved (provisional hash replaced). F2/F3 (T7 reporting) untouched.
  - No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies.
### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (ruff clean, pyright 0 errors, skills mirrors match, 126 tests passed); `make test-integration` → pass (9 passed, 117 deselected); `make test-unit` → 117 passed; `git diff --stat a3f1c2f^ a3f1c2f -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R7] `content_hash` is computed from the raw frontmatter mapping (dates kept as YAML strings), not from the validated `KnowledgeDocument` fields. The schema does not constrain the format of `effective_from`/`effective_to`, and Pydantic `date` also accepts forms such as `2026-01-01T00:00:00`, so two documents with the same validated date could hash differently, contrary to the design's "dates as ISO `YYYY-MM-DD`". All seed dates are plain `YYYY-MM-DD` (the integration test confirms model-based and raw-based hashes agree) → compute the hash from validated model values, or have T7/T8 reject non-`YYYY-MM-DD` date strings.
  - F2 [MINOR, IMPLEMENTATION, R7] The Implementation notes say the hash is computed "from the validated frontmatter" and that the contract was "mirrored in design"; the code uses the unvalidated mapping and `design.md` was not changed in T5 (it already held the contract). Narrative only; no code impact.
- Summary for user (PASS only):
  - Changed: new `packages/rag/.../repositories/hashing.py` (the `content-hash-v1` contract: body normalization, `body_sha256`, canonical JSON, the 17 hashed metadata fields, documented in the module docstring); `local.py` now sets `content_hash` with it (T4's placeholder is gone); `manifest.py` checks the manifest's `sha256` and `body_sha256` against each file and reports mismatches as `ManifestValidationError`; 25 tests in `test_content_hash.py`.
  - Verified by: `make verify` (126 tests), `make test-integration` (9). Tests cover every T5 verification item: seed hashes match the manifest, CRLF/LF give the same hash, body/`access_scope`/`lote_languages` changes alter it, review date/path/release/id/version do not, hash mismatches raise without leaking absolute paths, and moving a file keeps every hash.
  - Worth your attention: (1) any edit to a knowledge file, even whitespace, now fails loading until the manifest hashes are updated. This is intended integrity behavior, but editors will need a way to refresh hashes. (2) F1: date strings are hashed as written; harmless for the current seed.

### User decision
- 2026-10-14 — approved

## T6 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: none yet (changes left uncommitted for task review)
- Files changed: new `packages/rag/src/way2australia_rag/repositories/eligibility.py`; `repositories/__init__.py` (exports); new `packages/rag/tests/test_eligibility.py` (22 tests); `tasks.md` (T6 ticks and State)
- Verification run: `make verify` -> pass (148 tests, ruff and pyright clean, skills mirrors match); `make test-integration` -> 10 passed (seed corpus through the repository, includes the new seed-eligibility test)
- Notes:
  - `EligibilityPolicy` (frozen dataclass) holds the server-owned `allowed_access_scopes` (non-empty). `is_eligible(document)` requires approved AND active AND `retrieval_enabled` AND NOT `synthetic` AND scope in the policy. `GUEST_PUBLIC_POLICY` is the Phase 1 policy (`public` only).
  - `policy.query(lote_language=None)` builds the equivalent `DocumentQuery`; the language argument only narrows applicability and never touches the scopes.
  - `list_eligible_documents(repository, policy, lote_language=None)` pushes the query to the repository and then re-applies `is_eligible` and the language check to the result, so a repository that ignores the query still cannot leak ineligible documents (tested with a deliberately leaky repository).
  - Eligibility does not look at paths or directories. The scopes come from the caller's trusted server code; nothing reads them from documents, requests or LLM output.
  - Tests cover: active public included; deprecated/archived/draft excluded; non-approved statuses excluded; retrieval-disabled excluded; synthetic excluded; staff/subscriber/admin/user_private excluded for guest; widening only via an explicit server policy; empty policy rejected; language filters (including `*`, `ml`, `en`) never make a staff document eligible; language narrows eligible documents only; both security fixtures parse as valid documents but are ineligible (`retrieval_enabled: true`, so exclusion is by governance and authorization); all 13 seed documents are eligible.
  - T4 findings F2/F3 (T7 reporting) untouched. No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies.
  - Test-only note: the tests import `_matches` from `local.py` to emulate a filtering repository.


### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (exit 0; ruff clean, pyright 0 errors, skills mirrors match, 148 tests passed); `make test-integration` → pass (10 passed, 138 deselected); `make test-unit` → 138 passed; `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R8] `test_eligibility.py::load_fixture` builds the security fixtures by hand (`split_frontmatter`, keeps only keys in `KnowledgeDocument.model_fields`, skips JSON-schema validation) instead of through "an explicitly configured, isolated test repository" (design "Security fixtures"). It proves ineligibility, but not that the fixtures are schema-valid, and silently drops unknown keys → in T8, load them through an isolated `LocalDocumentRepository`/schema-validated path.
  - F2 [MINOR, IMPLEMENTATION, R9] The language-applicability rule (`"*"` or exact code) is duplicated in `eligibility.list_eligible_documents` and `local._applies_to_language`, and the tests import the private `local._matches`. Behaviour is consistent today → move the rule to one shared helper (e.g. on the model or the query module) when next touched.
  - F3 [MINOR, IMPLEMENTATION, R11] The security-fixture and seed-corpus tests partly anticipate T8 checklist items; no conflict, but T8 should reuse rather than duplicate them.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/repositories/eligibility.py` with `EligibilityPolicy` (server-supplied, non-empty set of allowed access scopes; eligible = approved AND active AND retrieval-enabled AND not synthetic AND scope allowed), `GUEST_PUBLIC_POLICY` (public only) and `list_eligible_documents`, which pushes the filter to the repository and re-checks every result so a faulty repository cannot leak documents; exports in `repositories/__init__.py`; 22 tests in `packages/rag/tests/test_eligibility.py`.
  - Verified by: `make verify` (148 tests), `make test-integration` (10). Tests cover every T6 verification item: active public included; deprecated/archived/draft, non-approved, retrieval-disabled and synthetic excluded; staff/subscriber/admin/user_private excluded for guest; language filters (`*`, `ml`, `en`) never make a staff document eligible; both security fixtures ineligible; all 13 seed documents eligible.
  - Worth your attention: eligibility ignores file location entirely and language only narrows results. Three minor cleanups (F1–F3) are left for T8.

### User decision
- 2026-10-15 — approved

## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: none yet (changes left uncommitted for task review)
- Files changed: new `packages/rag/src/way2australia_rag/repositories/validate.py`; `repositories/local.py` (public `under_root`, new `document_fields` helper shared by the loader and the validator); `repositories/manifest.py` (T3 F3); `Makefile` (`validate-knowledge` target, added to `verify`); `docs/project/COMMANDS.md`; new `packages/rag/tests/test_validate_knowledge.py` (17 tests); `packages/rag/tests/test_manifest_validation.py` (+1 test); `tasks.md` (T7 ticks and State)
- Verification run: `make validate-knowledge` -> exit 0 ("OK, 0 problems") on the seed corpus; `make verify` -> pass (166 tests, ruff and pyright clean, skills mirrors match, validate-knowledge OK); `make test-integration` -> 10 passed
- Notes:
  - `python -m way2australia_rag.repositories.validate --repo-root <path>` (Makefile passes `$(CURDIR)`; default is the current directory). `validate_knowledge(config)` returns all problems; `main` only formats (`ERROR <document_id>: <field>: <reason>` per problem, then a count) and returns 0/1.
  - Stages: schema and manifest load (structural errors and duplicates are fatal at this stage and reported as problems); manifest entries outside approved roots; markdown files under approved roots not in the manifest; per-document frontmatter/schema/manifest-match/`sha256`/`body_sha256` checks; for documents without earlier problems, the Pydantic model (every error listed) and `effective_from`/`effective_to` format; then, only if everything is clean, the corpus check through `LocalDocumentRepository`.
  - Corpus check interpretation: any active, `retrieval_enabled` document in the production roots must be approved, not synthetic and `public`; the guest/public eligible set is then re-checked for the same. A synthetic or draft document with `retrieval_enabled: false` or a non-active lifecycle is not retrievable and does not fail. This is slightly broader than "eligible public document" (which is tautologically safe under the policy), so it catches misplaced staff or draft files in the public roots.
  - Prior findings addressed: T3 F3 (nested `required` now prefixed with the parent path, tested); T4 F2 (outside-root entries and unlisted files are reported); T4 F3 (all Pydantic errors listed); T5 F1 (non-`YYYY-MM-DD` `effective_from`/`effective_to` rejected, so the raw-mapping hash cannot diverge from validated dates). T5 F1's alternative (hash from model values) not taken. T5 F2 is narrative only.
  - Not touched: T6 F1-F3 (assigned to T8). T3 F1 (record deps) stays for T9. No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies.
  - Unrelated formatter churn in `test_content_hash.py` was reverted.
  - COMMANDS.md: added a Behavior list under `make validate-knowledge`; the original expectations were unchanged.

### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make validate-knowledge` → exit 0 (`validate-knowledge: OK, 0 problems` on the seed corpus); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills mirrors match, validate-knowledge OK, 166 tests passed); `make test-integration` → exit 0 (10 passed, 156 deselected); `uv run pytest packages/rag/tests/test_validate_knowledge.py` (inside `make verify`) → 17 passed; `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R5] "Report every problem" is partial: `load_manifest` raises on the first duplicate or structural error, so those stop all later checks, and `_corpus_problems` (synthetic / not approved / not public) runs only when no other problem exists. A stray unlisted file or one hash mismatch therefore hides a retrievable synthetic or staff document until it is fixed. Exit code stays correct (1) → acceptable; optionally run the corpus checks per document from frontmatter so they are reported alongside other problems.
  - F2 [MINOR, IMPLEMENTATION, R6] Design says "All logic lives in the repository and validation modules. The command only wires configuration and formats output." `validate.py` holds the new checks (outside-root entries, unlisted files, date format, all-Pydantic-errors, corpus checks) next to `main`. `main` itself only wires and formats and `validate_knowledge()` is reusable, so the intent holds → consider moving the checks into a validation module if ingestion needs them.
  - F3 [MINOR, IMPLEMENTATION, R7] The `YYYY-MM-DD` date check (T5 F1) exists only in `validate-knowledge`; `LocalDocumentRepository` still loads a document with `effective_from: 2026-01-01T00:00:00` and hashes the raw string. Gated by `make verify`, so harmless for CI → move the check into the loader if the repository is used outside `make verify`.
  - F4 [MINOR, IMPLEMENTATION, R11] The CLI tests cover a repeated `document_id`, not a repeated `(document_id, document_version)` pair; the pair case is covered by the T3 manifest tests → no action needed.
- Summary for user (PASS only):
  - Changed: new `packages/rag/.../repositories/validate.py` (`python -m way2australia_rag.repositories.validate --repo-root <path>`; prints `ERROR <document_id>: <field>: <reason>` per problem and a count, exits 0/1); `Makefile` adds `validate-knowledge` and runs it in `make verify`; `docs/project/COMMANDS.md` documents the behavior; `local.py` exposes `under_root` and a shared `document_fields` helper; `manifest.py` keeps the parent path for nested `required` errors; 18 new tests.
  - Verified by: `make validate-knowledge` (seed corpus: 0 problems), `make verify` (166 tests), `make test-integration` (10). Tests run the CLI against temporary broken repositories (duplicate ID, missing file, schema violation, hash mismatch) and check exit 1 with the document ID and no absolute paths; also synthetic, draft and staff documents in the public roots, entries outside approved roots, unlisted files, bad dates and a missing schema.
  - Worth your attention: (1) the check is broader than the spec's "eligible public document": any active, retrieval-enabled document in the public roots must be approved, public and non-synthetic, so a misplaced staff or draft file fails `make verify`; (2) it also fails on markdown files under the roots that the manifest does not list, and on non-`YYYY-MM-DD` dates (closing earlier review findings); (3) some problems hide others until fixed (F1).

### User decision
- 2026-10-15 — approved
