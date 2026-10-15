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

## T8 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: none yet (changes left uncommitted for task review)
- Files changed: `packages/rag/src/way2australia_rag/repositories/base.py` (new `DocumentQuery.matches`); `repositories/local.py` (private `_matches`/`_applies_to_language` removed); `repositories/eligibility.py` (uses `DocumentQuery.matches`); new `packages/rag/tests/conftest.py`; new `packages/rag/tests/test_seed_corpus.py` (3 integration tests); `packages/rag/tests/test_eligibility.py`; `packages/rag/tests/test_repository_contract.py` (+1 test); `tasks.md` (T8 ticks and State)
- Verification run: `make verify` -> pass (170 tests, ruff and pyright clean, skills mirrors match, validate-knowledge OK); `make test-integration` -> 13 passed
- Notes:
  - T6 F1: new `security_repository` fixture (`conftest.py`) copies the schema and the two security fixtures into `tmp_path` under an isolated approved root, generates a manifest (sha256, body_sha256), and returns a `LocalDocumentRepository`. `test_eligibility.py` loads fixtures through it, so they are schema- and hash-validated, and also asserts `list_eligible_documents` over that repository returns nothing.
  - T6 F2: the language rule now lives only in `DocumentQuery.matches` (public method; same behavior). `LocalDocumentRepository` and `list_eligible_documents` both call it; tests no longer import a private helper. This adds a public method to `DocumentQuery`; no field or Protocol change.
  - T6 F3: no eligibility/fixture tests were copied. Existing tests from T1-T7 already cover models, manifest loading, hashing, eligibility, repository get/list; T8 added only the missing checks: seed (id) and (id, version) uniqueness, fixtures absent from manifest/production roots/guest-eligible set, and a `matches` contract test.
  - Seed uniqueness is also enforced by the loader; the test asserts it on the real corpus explicitly.
  - Not touched: T3 F1 (deps, T9); T7 F1-F3 (accepted/deferred). No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies. Unrelated formatter churn in `test_content_hash.py` reverted.

### Review
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (ruff clean; pyright 0 errors; skill mirrors match (5 skills); `validate-knowledge: OK, 0 problems`; 170 tests passed); `make test-integration` → pass (13 passed, 157 deselected); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R11] Tests import shared constants with `from conftest import ...` (`test_eligibility.py`, `test_seed_corpus.py`). This relies on pytest's default `prepend` import mode putting `packages/rag/tests` on `sys.path`; a second `conftest.py` elsewhere (e.g. `apps/api/tests/`) or a switch to `importlib` mode would break or shadow it → optionally move the constants into a small helper module and keep only the fixture in `conftest.py`.
  - F2 [MINOR, IMPLEMENTATION, R10] T8 adds a public `DocumentQuery.matches` to the T2 contract module (`base.py`). It resolves T6 F2 without changing fields or the Protocol and is covered by a contract test, but it is a source change inside a tests task → note only.
  - F3 [MINOR, IMPLEMENTATION, R11] `test_no_fixture_file_sits_under_a_production_root` matches by file name only; a renamed copy of a fixture under `knowledge/public/` would pass it. The ID-based checks in `test_security_fixtures_are_not_in_the_production_corpus` and `validate-knowledge` cover that case → no action needed.
- Summary for user (PASS only):
  - Changed: new `packages/rag/tests/conftest.py` (isolated `security_repository` fixture: copies the schema and both security fixtures to `tmp_path` with a generated manifest) and `packages/rag/tests/test_seed_corpus.py` (seed ID/version uniqueness, security fixtures absent from manifest, production roots and guest-eligible set). `test_eligibility.py` now loads the fixtures through that repository (schema- and hash-validated) and asserts they are ineligible. The language/scope filter rule moved into one public `DocumentQuery.matches` (`base.py`), used by `local.py` and `eligibility.py`; private helpers removed.
  - Verified by: `make verify` (170 tests, lint, types, skills check, validate-knowledge) and `make test-integration` (13 tests). All R11 acceptance items are covered across the T1–T8 test files.
  - Worth your attention: `DocumentQuery` gained a public `matches` method (behaviour unchanged; closes T6 F2). Tests import constants from `conftest.py`, which works but is fragile (F1). No protected data touched, no new dependencies.

### User decision
- 2026-10-15 — approved

## T9 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Commits: none yet (changes left uncommitted for task review)
- Files changed: `docs/project/CURRENT_STATE.md`; `docs/project/DECISIONS.md` (new D024); `docs/project/TECH_STACK.md`; `tasks.md` (T9 ticks and State)
- Verification run: `make verify` -> pass (170 tests, ruff, pyright, skills check, validate-knowledge)
- Notes:
  - T3 F1: `jsonschema` and `pyyaml` recorded in `TECH_STACK.md` and in D024.
  - D024 records the durable decisions: repository Protocol, `content-hash-v1` as the only change-detection signal, single `EligibilityPolicy`, language rule in `DocumentQuery.matches`, `make validate-knowledge`.
  - `CURRENT_STATE.md`: Spec 002 implemented reality added, "not yet implemented" list trimmed, status row and next step updated (merge after T9 approval).
  - `docs/knowledge/SCHEMA_AND_METADATA.md` not edited: no schema difference was found or needed (box ticked as "only if differs" not triggered). Not independently diffed against the schema by this task.
  - Left unticked: "Hand off to `spec-reviewer` (status `implemented — pending review`)". That status is retired (D023); the task-gated flow replaces it. Needs a spec decision (reword or drop via planner); I did not edit the checkbox text.
  - Spec status in `tasks.md` header not changed; the orchestrator/user decide on merge and "verified".
  - No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies.

### Review
- Model: claude-opus-5-5
- Verdict: FAIL
- Commands: `make verify` → pass (exit 0: ruff all checks passed; pyright 0 errors; skills check 5 mirrors match; `validate-knowledge: OK, 0 problems`; 170 tests passed); `make test-integration` → pass (13 passed, 157 deselected); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MAJOR, SPEC_DEFECT, DoD] The checklist item "Hand off to `spec-reviewer` (status `implemented — pending review`)" is unticked and cannot be satisfied: that status is retired (D023; `WORKFLOW.md` "Retired values"), and a spec is now verified by all tasks approved + merge. The Spec 003 migration of Spec 002 `tasks.md` kept the old text. → user/`spec-planner`: reword (e.g. "orchestrator sets `all tasks approved`; optional `spec-reviewer` retrospective") or drop, with a `## Change log` line; then re-review T9.
  - F2 [MAJOR, IMPLEMENTATION, DoD] `CURRENT_STATE.md` does not match reality, which T9's verification requires: "Last updated" is still 2026-10-14; "Current goal" still says to resume Spec 002 from T3 under the new flow, although T3–T8 are approved. → update the date and rewrite "Current goal" to the actual goal (finish Spec 002 T9, merge `spec/002`, then Spec 003 T9/T10).
  - F3 [MINOR, IMPLEMENTATION, DoD] `CURRENT_STATE.md` contradicts itself on Spec 003: the status row says "T9 dry run (needs the user) and T10 pending" while "Next step" 1 says "Spec 003 T9 dry run done", and Spec 003 `tasks.md` has T9 `not started`. Both lines predate this task, but the handoff file should be consistent → state Spec 003 T9 accurately in `CURRENT_STATE.md` only (do not edit Spec 003 files in this task).
  - Open items checked: `SCHEMA_AND_METADATA.md` box — reviewer compared the doc against `AccessScope`, `LanguageScope`, `lote_languages`/`["*"]` and `owner_user_id` rules in `packages/core/.../documents`; no difference, so ticking it without a diff is correct (no finding). `make test-integration` — run by reviewer, 13 passed. `TECH_STACK.md` + D024 resolve T3 F1; D024 claims (no paths exposed, `CONTENT_HASH_METADATA_FIELDS` exclusions, `HASH_CONTRACT`, single language rule in `DocumentQuery.matches`) match the code.

### Implementation (round 2)
- Model: claude-sonnet-5-5
- Commits: none yet (changes left uncommitted for task review)
- Files changed: `docs/project/CURRENT_STATE.md`; `tasks.md` (T9 State only)
- Verification run: `make verify` -> pass (170 tests, ruff, pyright, skills check, validate-knowledge)
- Notes:
  - F1 (spec defect): fixed by the planner (reworded last Definition-of-Done item). That item is the orchestrator's action after approval (`all tasks approved`, optional `spec-reviewer`, merge), so it is not the implementer's to perform and its box stays unticked; checkbox text not edited.
  - F2: `CURRENT_STATE.md` "Last updated" set to 2026-10-15; "Current goal" rewritten (finish Spec 002 T9 and merge `spec/002`, then Spec 003 T9/T10).
  - F3: `CURRENT_STATE.md` now states Spec 003 T9 accurately in the status row and "Next step": `not started` in its `tasks.md`, dry run performed on Spec 002 T3 but not yet recorded. No Spec 003 files edited.
  - No files under `knowledge/`, `evaluation/` or `config/` touched. No new dependencies. `make test-integration` not re-run this round (no code changes).

### Review (round 2)
- Model: claude-opus-5-5
- Verdict: PASS
- Commands: `make verify` → pass (exit 0: ruff all checks passed; pyright 0 errors; skills check 5 mirrors match; `validate-knowledge: OK, 0 problems`; 170 tests passed); `make test-integration` → pass (13 passed, 157 deselected); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - Round 1 F1 resolved: the planner reworded the last DoD item to "Hand off to `spec-orchestrator` for completion (...)", with a dated `## Change log` line and requirements `Status:` re-dated `approved (2026-10-15)`. No remaining reference to `spec-reviewer` handoff / `implemented — pending review` in Spec 002 `tasks.md`.
  - Round 1 F2 resolved: `CURRENT_STATE.md` "Last updated" is 2026-10-15; "Current goal" now states finish Spec 002 T9 → merge `spec/002` → Spec 003 T9/T10.
  - Round 1 F3 resolved: status row and "Next step" consistently say Spec 003 T9 is `not started` in its `tasks.md` while the dry run was performed on Spec 002 T3; matches Spec 003 `tasks.md` (T1–T8 `in task review (round 1)`, T9/T10 `not started`). No Spec 003 files edited.
  - F1 [MINOR, IMPLEMENTATION, DoD] The reworded last item "Hand off to `spec-orchestrator` for completion" is unticked. This is correct: it describes the orchestrator's post-approval actions (`all tasks approved`, optional retrospective, merge), so ticking it now would be inaccurate → the orchestrator ticks it when it performs the completion step; no implementer action.
  - Observations (no finding): the amendment changed checkbox text, which `WORKFLOW.md` forbids for Kiro's `tasks.meta.json`, but Spec 002 has no `tasks.meta.json`; and the change log keeps T9's round count instead of resetting to `not started` (WORKFLOW rule for re-opened tasks), an explicit, recorded choice. Reviewer cannot verify the user approval behind the re-dated `Status:` line; the orchestrator should confirm it.
- Summary for user (PASS only):
  - Changed: `docs/project/CURRENT_STATE.md` (Spec 002 implemented reality, current goal, spec status rows, next steps, date); `docs/project/DECISIONS.md` new D024 (repository Protocol, `content-hash-v1`, single `EligibilityPolicy`, language rule location, `validate-knowledge`, `jsonschema`/`pyyaml`); `docs/project/TECH_STACK.md` records the two dependencies; Spec 002 `tasks.md` T9 ticks; planner rewording of T9's last item plus change-log line in `requirements.md`.
  - Verified by: `make verify` (170 tests, ruff, pyright, skills mirrors, validate-knowledge), `make test-integration` (13 passed); round 1 findings re-checked against the files; no seed/eval/config changes.
  - Worth your attention: (1) the last T9 box ("Hand off to `spec-orchestrator`") stays unticked until the orchestrator does completion and merge; (2) confirm you approved the requirements amendment (Status re-dated 2026-10-15); (3) after approval, merge `spec/002` into `main`, then record the Spec 003 T9 dry-run outcome.

### User decision
- 2026-10-15 — approved
