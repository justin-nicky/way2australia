# Task Reviews — 006 Evaluation Framework

Append-only, newest at the bottom.

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no mismatch check possible with a user).
- Files changed:
  - new frozen fixture `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/` (README with source commit `0907676` and sha256 of every file, 13 seed documents, manifest, schema, `seed-v1.json`, `config/ingestion.yaml`, `evaluation/suites/legacy-fixture-suite.json`, `evaluation/datasets/golden_fixture.jsonl`);
  - new `packages/rag/tests/retrieval/test_legacy_baseline_snapshot.py` and snapshots `fixtures/legacy_baseline_snapshot.json`, `fixtures/legacy_baseline_summary.txt`;
  - new `packages/rag/src/way2australia_rag/evaluation/{__init__,errors,models,suite}.py`;
  - modified `packages/rag/src/way2australia_rag/retrieval/goldens.py` (compatibility wrapper);
  - new `packages/rag/tests/evaluation/{__init__,test_suite_loader,test_status_handling}.py`;
  - modified `.gitignore` (one negation line, see notes);
  - `.kiro/specs/006-evaluation-framework/tasks.md` (T1 State and checkboxes); this file.
- Verification run:
  - Fixture copy and snapshot test created first and generated on the unmodified code (no `evaluation/` package, original `goldens.py`); 4 tests green before any other change, and green again after the `goldens.py` change with the snapshot and summary files untouched.
  - Fixture suite: 9 rows (8 copied verbatim, 1 derived deprecated row); the fake run gives 3 hits and 5 misses, includes the two-document cases `g003` and `g062`, `en` and `mixed`; 8 cases kept, 1 excluded.
  - README hashes: all 17 listed sha256 values match the files; the verbatim copies were compared with `cmp` to the live files at the source commit.
  - `make verify` -> exit 0 (ruff lint and format check, pyright 0 errors, validate-knowledge OK, pytest 460 passed, 1 skipped; a user-started Qdrant was reachable so the existing integration tests ran on their own temporary collections; no bge-m3 group, Docker not started or stopped, `w2a-realcheck-idx-v1` not touched).
  - `pytest -m "not integration"` -> 441 passed, 1 skipped, 19 deselected.
  - `git diff --stat` on `metrics.py`, `baseline.py`, `baseline_cli.py` and the legacy tests `test_goldens.py`, `test_baseline.py`, `test_cli.py` -> empty.
  - `git status --porcelain -- evaluation knowledge config experiments` -> empty.
- Notes:
  - Independence test records every opened path (builtins `open`, `io.open`, `Path.open/read_text/read_bytes`); it asserts nothing under live `knowledge/`, `evaluation/` or `config/` was opened, and that every repository data file read is under `legacy_baseline_repo/`. A second test runs from a `tmp_path` copy and gets identical JSON and summary. The output file is written to `tmp_path` as `legacy-result.json`; the clock is fixed by patching `baseline_cli.datetime`.
  - `.gitignore` has `MANIFEST` (a build-artifact rule) that matches the fixture's `knowledge/manifest/` directory on case-insensitive filesystems (the live one is tracked). One negation line was added for the fixture path; without it the fixture's manifest would silently not be committed. Review/commit should confirm `git add -n` lists `.../legacy_baseline_repo/knowledge/manifest/document_manifest.jsonl`.
  - Deviations from the design models (needed so legacy tests pass unchanged): `CaseBase.status` is a plain `str` (the legacy test uses a `retired` status; `CaseStatus` is used for comparison); `evaluation_suite_id` on cases, and `status`, `introduced_in_release`, `case_count` on the manifest, have empty/None defaults because legacy temp suites omit them (T2 schema validation will enforce them). An empty manifest `status` is never `active`.
  - Stricter behavior for T8's COMMANDS legacy entry: `read_manifest` checks every listed dataset's type and path, so a suite that lists an unknown dataset type or a non-golden path escaping the repository is now refused by legacy `retrieval-baseline` where it was previously ignored. The real suite and the fixture suite are unaffected.
  - Error messages preserved: `'x' is not a valid evaluation suite.`, `... line N is not a valid golden case.`, `... resolves outside the repository.`, `cannot read ...`, release messages; the wrapper re-raises `EvaluationConfigurationError` as `RetrievalConfigurationError(str(error))`.
  - Loader tests (`test_suite_loader.py`, `test_status_handling.py`) read or copy the live `evaluation/` data (85 cases: 63, 12, 10); they are not part of the legacy snapshot guarantee. The reference attempt in the scratchpad was adapted for the src and these two test files only; its snapshot test and fixtures were not used.
  - State was set to `in task review (round 1)` at the end.
- Usage: 133K tokens · 32 tool uses · 4:50

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; run as a subagent in a fresh session, different model from the implementer).
- Verdict: PASS
- Commands:
  - `make verify` → pass (ruff check and format check clean, pyright 0 errors, skills-check OK, validate-knowledge OK, pytest 460 passed, 1 skipped; a user-started Qdrant was reachable, so the existing integration tests ran on their own temporary collections; no bge-m3 group, Docker not started or stopped, `w2a-realcheck-*` not touched).
  - `pytest -m "not integration"` → 441 passed, 1 skipped, 19 deselected; `pytest -m integration` → 19 passed (442 deselected).
  - Snapshot, legacy and new evaluation tests (`test_legacy_baseline_snapshot.py`, `test_goldens.py`, `test_baseline.py`, `test_cli.py`, `tests/evaluation/`) → 56 passed.
  - Unmodified-code check: `git archive HEAD` extracted to a scratch dir outside the repo (no `evaluation/` package, original `goldens.py`, confirmed with `cmp`), only the new test and `fixtures/` copied in, run with `PYTHONPATH` pointing at the scratch sources → snapshot test 4 passed, plus the legacy tests (46 passed together). Scratch `fixtures/` is identical (`diff -r`) to the working tree's.
  - Non-vacuity (scratch copy): one byte of the snapshot JSON changed → 3 failed; one value in the summary changed → 2 failed; kept case `g037` dropped from the fixture suite → 4 failed; restored → 4 passed.
  - Independence (scratch copy): `chmod 000` on the scratch repo's live `knowledge/`, `evaluation/`, `config/` → snapshot tests 4 passed; control: legacy `test_cli.py` (uses live data) fails under the same chmod, so the lock was effective. Location test runs from a `tmp_path` copy with identical bytes.
  - Fixture copy: all 19 README sha256 values match (`shasum -c`, 19 listed, 19 files); every file under `config/` and `knowledge/` is byte-identical to `HEAD` (`git show HEAD:<path> | cmp`); the 8 golden rows `g001 g003 g005 g010 g032 g037 g055 g062` are byte-identical to their `golden_public.jsonl` lines; `g001-derived-deprecated` differs from `g001` only in `case_id` and `status` and is labelled derived in the README.
  - `git diff --stat HEAD --` on `metrics.py`, `baseline.py`, `baseline_cli.py`, `test_goldens.py`, `test_baseline.py`, `test_cli.py` → empty. No change to `pyproject.toml`, `uv.lock`, `Makefile`.
  - `git status --porcelain --ignored -- evaluation knowledge config experiments` → empty; sha256 of every file under those paths identical before and after `make verify`.
  - `.gitignore`: in a scratch git repo with `core.ignorecase=true`, the `HEAD` `.gitignore` ignores the fixture's `knowledge/manifest/document_manifest.jsonl` (rule `MANIFEST`, line 39); with the new line it does not. In the repo, `git add -n packages/rag/tests/retrieval/fixtures/` lists all 22 fixture files, the manifest included.
- Findings:
  - F1 [MINOR, SPEC_DEFECT, R1/R3] The design's models say `CaseBase.status: CaseStatus` and require `status`, `introduced_in_release` and `case_count` on `SuiteManifest` and `evaluation_suite_id` on cases; the code uses a plain `str` status and defaults for those fields, so legacy test suites (a `retired` status, minimal manifests) still load. Reasonable for R12, but unrecorded. → Record the deviation in `design.md` ("Interfaces / models") when the spec is next amended or at T8; T2's `validate-evaluation` must enforce the status enum and the required manifest/case fields through the schemas.
  - F2 [MINOR, SPEC_DEFECT, R12] Legacy `retrieval-baseline` is now stricter: a suite listing an unknown dataset type, or a non-golden dataset path escaping the repository, is refused (previously ignored), as is a `null` in a newly typed optional field (`status`, `introduced_in_release`, `case_count` on the manifest; `evaluation_suite_id`, `relevant_section_ids` on golden rows). The real suite and the fixture suite are unaffected (checked: no such values in `evaluation/`). This contradicts the design sentence "a problem there cannot change legacy behavior" for manifest-level problems. → Document in the T8 `COMMANDS.md` legacy entry and in the design.
  - F3 [MINOR, IMPLEMENTATION, R12] `.gitignore` is edited although the design lists `.gitignore` only for `experiments/results/tmp/`. The edit is needed (without it the fixture manifest would silently not be committed on macOS), minimal (one negation scoped to the fixture's `knowledge/manifest/` directory, with a comment) and safe (other ignore rules still apply inside it). → No change needed; user acknowledgement at approval. Pre-existing, not this task: any new untracked file under the live `knowledge/manifest/` is also ignored on case-insensitive filesystems.
  - F4 [MINOR, IMPLEMENTATION, R1] `test_access_context_is_loaded_but_ignored` only checks that no other model field name contains "access"; that `access_context` never affects retrieval is shown only when the runners exist. → Cover it in the retrieval and security runner tests (T4/T5).
- Summary for user (PASS only):
  - Changed: new `evaluation/` package (`errors.py`, `models.py`, `suite.py`: typed suite and case models, read-only loader, `active()` / `excluded_by_status()`); `retrieval/goldens.py` reduced to a compatibility wrapper over it; a frozen miniature repository `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/` (13 seed documents, manifest, schema, release, ingestion config, 9-row golden suite) with byte-exact JSON and summary snapshots of legacy `retrieval-baseline`; loader and status tests; one `.gitignore` line.
  - Verified by: `make verify` (460 passed, 1 skipped); the snapshot generated and passing on the unmodified `HEAD` code in a scratch copy outside the repo; the snapshot fails on a one-byte change and on a dropped case; it passes with live `knowledge/`, `evaluation/` and `config/` made unreadable; fixture hashes and verbatim copies checked against `HEAD`.
  - Worth your attention: legacy `retrieval-baseline` now refuses a suite listing an unknown dataset type, which it used to ignore (F2; to be documented in T8); case `status` is a plain string and some manifest fields default (F1); the `.gitignore` negation is outside the listed files but required for the fixture manifest to be committed (F3).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/goldens.py` → `load_suite`, `load_golden_cases`: the legacy entry, now a wrapper that re-raises as `RetrievalConfigurationError`.
    2. `packages/rag/src/way2australia_rag/evaluation/suite.py` → `read_manifest`, `read_dataset`, `load_suite`: the read-only loader (type and path refusals, file/line-only messages).
    3. `packages/rag/src/way2australia_rag/evaluation/models.py` → `LoadedSuite.active`, `excluded_by_status`: case models and status helpers.
    4. `packages/rag/src/way2australia_rag/evaluation/errors.py` and `__init__.py`: error classes.
    5. `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/README.md`: what was frozen, from which commit, which row is derived.
    6. `packages/rag/tests/retrieval/test_legacy_baseline_snapshot.py` → `run_snapshot`: the byte-exact legacy snapshot, independence and location tests.
    7. `packages/rag/tests/evaluation/test_suite_loader.py`, `test_status_handling.py`: loader and status tests.
    8. Supporting edits: `fixtures/legacy_baseline_snapshot.json`, `legacy_baseline_summary.txt`, `.gitignore` (one negation line), `tasks.md` (T1 State and checkboxes).
- Usage: 129K tokens · 27 tool uses · 5:05

### User decision
- 2026-10-23 — approved. Verbatim: "Approved T1. Acknowledge the `.gitignore` negation line (F3). One spec-planner amendment (Change log lines as needed), then continue to T2: T2: `validate-evaluation` rejects unknown case `status` values and missing required suite/case fields via the new schemas (F1); note the plain-string `status` and defaults in design.md. R12 / design + T8: record that legacy `retrieval-baseline` now refuses malformed suites (unknown dataset type, non-golden path outside the repo, null in newly typed optional fields) it used to ignore; document it in the COMMANDS.md legacy entry (F2). T3: add a behaviour test that a case's `access_context` (e.g. admin / other tenant) never changes the access used for retrieval (F4). T8: anchor the `.gitignore` `MANIFEST` rule to the repo root (`/MANIFEST`) so it can't match `knowledge/manifest/` on case-insensitive filesystems; test with `git check-ignore` that a new file under `knowledge/manifest/` is not ignored."

## T2 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - new `evaluation/schemas/evaluation_suite.schema.json` and `evaluation/schemas/evaluation_case_types.schema.json` (the only changes under `evaluation/`, `knowledge/`, `config/`);
  - new `packages/rag/src/way2australia_rag/evaluation/{schemas,validate,cli}.py`;
  - new `packages/rag/tests/evaluation/{test_schemas,test_validate}.py`;
  - `Makefile`: `validate-evaluation` target, added to `.PHONY` and to `verify` after `validate-knowledge`;
  - `tasks.md`: T2 State and checkboxes.
- Verification:
  - `make verify` -> pass (ruff check and format check, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation OK with 0 problems, pytest 505 passed, 1 skipped); no Docker or bge-m3 needed; Qdrant not started, stopped or touched.
  - `make validate-evaluation` -> exit 0 on the repository.
  - `git status --porcelain -- evaluation knowledge config` -> exactly `?? evaluation/schemas/evaluation_case_types.schema.json` and `?? evaluation/schemas/evaluation_suite.schema.json`. Nothing written under `experiments/results/`.
- Notes and decisions:
  - Schemas resolve locally through a `referencing.Registry` keyed by `$id`; `referencing` is a transitive dependency of `jsonschema`, so `pyproject.toml` and `uv.lock` are unchanged.
  - Allowed suite `status` values (the design says "allowed values" without listing them): `draft`, `active`, `deprecated`, `replaced`. Empty or missing is rejected. Reviewer to confirm.
  - Loader models stay tolerant; case `status` is enforced through the referenced `evaluation_case.schema.json` enum, and `evaluation_suite_id`/`query`/etc. get `minLength: 1` in the type definitions.
  - Reasons never echo values (schema errors are mapped to fixed phrases); document IDs are named in the unknown/ineligible messages.
  - Exit codes: malformed JSON lines and schema/cross-check failures are problems (1); missing schema, unreadable suite/dataset, escaping dataset path, no suites, invalid corpus (advice: `make validate-knowledge`) and unexpected exceptions (class name only) are 2.
  - `validate_evaluation` takes an optional `repository` so the ineligible-document test can inject a stub (a real temp copy would need hash edits); unknown vs not-eligible are reported separately.
  - Extra candidate checks beyond the task list: unique `candidate_id`, `target_suite_id` names a known suite, `target_case_ids` exist in that suite. Candidates dir absent is fine (T7 adds the file).
  - Tests: no `ml` literal or word in `evaluation/*.py` (regex test). One temp-copy test per case added by the 2026-10-23 amendments (unknown status, missing case/manifest `evaluation_suite_id`, missing and empty suite `status`, missing `introduced_in_release`, missing and non-integer `case_count`), each exiting 1 and naming file and field.
- Usage: 139K tokens · 25 tool uses · 44:05

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; run as a subagent, fresh session, different model from the implementer).
- Verdict: PASS
- Commands:
  - `make validate-evaluation` → exit 0 (`validate-evaluation: OK, 0 problems`).
  - `make verify` → pass: ruff check clean, `ruff format --check` 108 files formatted, pyright 0 errors, skills-check 5 skills, validate-knowledge OK, validate-evaluation OK, pytest 505 passed, 1 skipped (no Docker started, no `bge-m3` extra; Qdrant not touched).
  - `pytest packages/rag/tests/evaluation/test_schemas.py packages/rag/tests/evaluation/test_validate.py` → 45 passed.
  - `pytest -m integration --collect-only` → 19 collected (not run; not part of T2 verification).
  - `git status --porcelain --ignored -- evaluation knowledge config experiments` → exactly `?? evaluation/schemas/evaluation_case_types.schema.json` and `?? evaluation/schemas/evaluation_suite.schema.json`; `evaluation_case.schema.json` unchanged vs `HEAD` and referenced by `$ref` (not copied); sha256 of all 41 files under `evaluation/ knowledge/ config/ experiments/` identical before and after the review runs.
  - Mutation check in a scratch copy outside the repo (`PYTHONPATH` pointed at the copy): 21 mutations to the two schemas and `validate.py`; 19 killed by the matching test (suite `status`/`introduced_in_release`/`case_count`/`evaluation_suite_id` required, empty `status` rejected, `case_count` integer, golden `$ref` to the case schema, candidate `status` const, duplicate `case_id`, suite-id mismatch, `case_count` mismatch, duplicate dataset path, unknown vs ineligible separated, candidates path refused, both language-neutral review rules, `target_case_ids`, ineligible ignored, repository error → exit 2); 2 survived (F1, F2).
  - Behaviour probes on temp copies with sockets blocked: real data exit 0 with no network; empty manifest and case `evaluation_suite_id` → exit 1 ("must not be empty"); empty `relevant_document_ids` → exit 1; unknown suite `status` and boolean `case_count` → exit 1; dataset path `../../etc/passwd` → exit 2 naming only the basename; a remote `$ref` added to a schema → exit 2 with class name only and no fetch. No output line contained an absolute path or case text.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R14] `test_case_change_candidate_rules` deletes `options` while `target_case_ids` is still `["zzz"]`, so its final `exit 1` assertion is vacuous: dropping `options` from the `case_change` `then.required` survives the suite. → Restore a valid `target_case_ids` before deleting `options`, and assert the problem names `options`.
  - F2 [MINOR, IMPLEMENTATION, R2/R3] No test for an empty `relevant_document_ids` (R2 "non-empty", R3 "an active golden without `relevant_document_ids` fails validation"): removing `minItems: 1` survives (the field-deletion test only covers a missing field). Likewise no test for an empty-string `evaluation_suite_id` (manifest or case). The behaviour is correct (probed). → Add one temp-copy test each.
  - F3 [MINOR, IMPLEMENTATION, R2/R14] `test_candidate_unknown_and_ineligible_documents` only covers the unknown document; an ineligible candidate document is untested. `test_validate.py` also has no test that a dataset path escaping the repository exits 2 (behaviour correct, probed). → Add both (the ineligible case can reuse the injected-repository stub).
  - F4 [MINOR, SPEC_DEFECT, R2/R4] The design says "a non-empty `status` from the allowed values" but lists none; the implementer chose `draft`, `active`, `deprecated`, `replaced`. Judged safe: the case enum has no suite-level `draft`, but every non-`active` value is refused by T3's `eval-retrieval`, the real suite is `active`, and an empty or missing value is rejected. → Record the list in `design.md` and in the T8 suite-status-refusal decision (D042–D046), no code change.
  - F5 [MINOR, IMPLEMENTATION, R2] `schemas.py` imports `referencing` directly; it is not declared in `packages/rag/pyproject.toml` (it is a hard dependency of `jsonschema>=4.18`, and the design names `referencing.Registry`; `uv.lock` unchanged). → Optional: declare it explicitly in a later approved change; no new dependency was added.
- Judgements on implementer decisions: the optional `repository` argument is test-only (CLI never passes it; the default is `LocalDocumentRepository`, eligibility via `list_eligible_documents(GUEST_PUBLIC_POLICY)`, no file paths). The extra candidate checks (unique `candidate_id`, known `target_suite_id`, existing `target_case_ids`) are consistent with T7's planned rows (`public-eval-v1`, `g004`/`u001` are in the suite) and with R14. Reporting a suite dataset under `evaluation/candidates/` as a validation problem (exit 1) matches design step 6 and R14 ("no suite manifest references the file"). The language-neutral rule (`needs_fluent_speaker_review` + `owner_review`) has no language literal and accepts T7's `["fluent_malayalam_speaker", "owner_review"]`. Loader models (`models.py`, `suite.py`) are unchanged.
- Summary for user:
  - Changed: two new schemas under `evaluation/schemas/` (suite manifest; per-type case definitions that `$ref` the existing case schema, plus `candidate_row`); `evaluation/schemas.py` (local `$id` registry, no network), `evaluation/validate.py` (all R2/R14 checks), `evaluation/cli.py` (`validate` subcommand); `make validate-evaluation`, now part of `make verify`.
  - Verified by: `make validate-evaluation` exit 0, `make verify` (505 passed, 1 skipped), 45 new tests, 21 scratch-copy mutations (19 killed), probes with network blocked; protected paths show only the two new schema files and every pre-existing file hash is unchanged.
  - Worth your attention: allowed suite statuses are `draft/active/deprecated/replaced` (not in the design yet, F4; only `active` will run); three test gaps where the code is right but a test is missing or vacuous (F1–F3); `referencing` is used but undeclared (F5).
  - Reading order:
    1. `Makefile` → `validate-evaluation` target and its place in `verify`.
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `main`, `_validate`: exit codes 0/1/2, class-name-only errors.
    3. `packages/rag/src/way2australia_rag/evaluation/validate.py` → `validate_evaluation`, `_validate_suite`, `_validate_candidates`, `_candidate_rules`: the checks and problem lines.
    4. `packages/rag/src/way2australia_rag/evaluation/schemas.py` → `load_schemas`, `EvaluationSchemas`: local registry by `$id`.
    5. `evaluation/schemas/evaluation_suite.schema.json`: required manifest fields and allowed statuses.
    6. `evaluation/schemas/evaluation_case_types.schema.json`: `golden_answerable`, `unanswerable_refusal`, `security`, `candidate_row`.
    7. `packages/rag/tests/evaluation/test_schemas.py`, `test_validate.py`: schema and temp-copy validation tests.
    8. Supporting edits: `tasks.md` T2 checkboxes and State.
- Usage: 132K tokens · 27 tool uses · 5:57

### User decision
- 2026-10-23 — approved. Verbatim: "Approved T2. Implementer decisions accepted (incl. suite statuses draft/active/deprecated/replaced). Deferred to T8 — keep a running list and add all deferred items as T8 boxes in one spec-planner amendment before T8 starts: F1: fix `test_case_change_candidate_rules` so the missing-`options` row fails only for that reason (no unknown target). F2: tests for empty `relevant_document_ids` and empty-string `evaluation_suite_id`. F3: tests for an ineligible document in a candidate row and an escaping dataset path in `test_validate`. F4: record the allowed suite status values in design.md and T8's suite-status decision. F5: declare `referencing` directly in packages/rag/pyproject.toml (it is imported directly; already locked). Continue to T3."
