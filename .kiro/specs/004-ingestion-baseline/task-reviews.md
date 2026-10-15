# 004 — Task reviews

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Files changed: `packages/rag/src/way2australia_rag/repositories/manifest.py` (new `DATE_FIELDS` and shared `date_problems()`, called from `check_manifest_documents`); `packages/rag/src/way2australia_rag/repositories/validate.py` (private date check and its constants removed; dates now reported through the shared helper); `packages/rag/tests/test_date_and_policy.py` (new); `.kiro/specs/004-ingestion-baseline/tasks.md`
- Verification run: `make test-unit` → pass (175 passed, 13 deselected); `make test-integration` → pass (13 passed); `make validate-knowledge` → OK, 0 problems; `make verify` → pass (188 tests, ruff and pyright clean)
- Notes: The helper lives in `manifest.py` because both the loader (`_read_all` → `check_manifest_documents`) and `validate-knowledge` already go through it, so the two cannot diverge. Date fields are `last_reviewed_at`, `effective_from`, `effective_to` (the only date-like fields in `document_metadata.schema.json`). A bad date makes the loader raise `ManifestValidationError` with a line `doc_a: <field>: must be a YYYY-MM-DD date` (no absolute path). Tests cover each field with four bad values, valid values, seed corpus load, and `config/access_policy.yaml` vs `GUEST_PUBLIC_POLICY` (guest == ["public"], equal scopes, every named scope is an `AccessScope` member). `make format` briefly reformatted an unrelated test file; that change was reverted. Nothing under `knowledge/`, `config/` or `evaluation/` was touched. Model check: running model matches the intended tier note (no mismatch recorded).
- Usage: 93K tokens · 19 tool uses · 1:39

### Review
- Model: claude-opus-5-5 (matches task-reviewer tier BEST = Opus; implementer was claude-sonnet-5-5)
- Verdict: PASS
- Commands: `make test-unit` → pass (175 passed, 13 deselected; 18 new in `test_date_and_policy.py`); `make validate-knowledge` → OK, 0 problems; `make test-integration` → pass (13 collected, 13 passed); `make verify` → exit 0 (ruff clean, pyright 0 errors, 188 passed, validate-knowledge OK); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R3] The scope check is one-way (`named <= members`): a new `AccessScope` member added without a config entry would not fail the test. R3 says the enum values "match" the configured scopes; the task checklist only asks for the subset. → Optionally assert equality (`named == members`) in a later task.
- Summary for user (PASS only):
  - Changed: one shared strict `YYYY-MM-DD` check (`date_problems`, `DATE_FIELDS` in `repositories/manifest.py`) now runs inside `check_manifest_documents`, which both `LocalDocumentRepository` and `make validate-knowledge` use. The old private check in `validate.py` (which covered only the effective dates) is gone; `last_reviewed_at` is now checked as well. New tests are in `packages/rag/tests/test_date_and_policy.py`.
  - Verified by: the commands above. The tests cover each of the 3 date fields with 4 bad values, plus valid dates, the seed corpus loading unchanged, and `config/access_policy.yaml` against `GUEST_PUBLIC_POLICY`.
  - Worth your attention: the R3 test checks enum values in one direction only (F1). Nothing under `knowledge/`, `config/` or `evaluation/` changed.
- Usage: 74K tokens · 11 tool uses · 27:21

### User decision
- 2026-10-15 — approved
