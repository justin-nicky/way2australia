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

## T3 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - new `packages/rag/src/way2australia_rag/evaluation/{slices,sections,results,retrieval_eval}.py`;
  - `evaluation/cli.py`: `retrieval` subcommand (startup order as in the design; `validate` unchanged);
  - `Makefile`: `eval-retrieval` target (`EVAL_ARGS`) and `.PHONY`;
  - new tests `packages/rag/tests/evaluation/{test_slices,test_sections,test_retrieval_eval,test_cli}.py`;
  - `tasks.md`: T3 State and checkboxes.
- Verification:
  - `make verify` -> exit 0 (ruff check and format, pyright 0 errors, skills-check, validate-knowledge OK, validate-evaluation OK, pytest 540 passed, 1 skipped); no Docker, no bge-m3 extra, Qdrant not started, stopped or touched; no `w2a-realcheck-*` collection touched.
  - `make eval-retrieval` without the extra -> exit 2, `ERROR OptionalDependencyError: BGE-M3 needs the optional 'bge-m3' dependency group; run make setup-bge-m3.` (before any Qdrant contact).
  - The T1 legacy snapshot test passes unchanged inside `make verify`; `git diff --stat` on `retrieval/` is empty.
  - `git status --porcelain`: nothing under `evaluation/`, `knowledge/`, `config/` or `experiments/`.
- Usage: 167K tokens · 29 tool uses · 8:20
- Notes and decisions:
  - Added `--config` (and `--repo-root`) to `eval-retrieval`, as in the other CLIs; it cannot select a fake embedder (a fake provider is refused). Options otherwise: `--top-k`, `--suite`, `--release`, `--output`.
  - `main` takes injectable `client_factory` and `embedder_factory` (defaults `default_client_factory`, `build_embedder`) so tests need no model; a stub embedder with `is_fake=False` stands in for BGE-M3.
  - Active goldens with no `relevant_document_ids` or `answerable: false` are refused (exit 2, naming `case_id`, advising `make validate-evaluation`) rather than silently dropped (R3).
  - `relevant_section_ids` entries are `"<document_id>#<section_id>"` keys (design says section keys; no case uses them yet). Reviewer to confirm.
  - A relevant document missing from the eligible map gives source_authority key `unknown`.
  - The 2.0 document has no `unanswerable` block (T4). `excluded_case_count` = golden cases not run.
  - Fake-index refusal in the CLI is reached as a binding mismatch (D036) first; the explicit `require_real_index` is tested at runner level.
  - `access_context` behavior test: a spy index records every search filter (warm-up included) for goldens with hostile contexts; all equal `build_access_filter(guest())`.

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; run as a subagent, fresh session, different model from the implementer).
- Verdict: PASS
- Commands:
  - `make verify` → pass: ruff check clean, `ruff format --check` 116 files formatted, pyright 0 errors, skills-check, validate-knowledge OK, validate-evaluation OK, pytest 540 passed, 1 skipped (the local `way2australia-qdrant` container was already running, so the 19 integration tests ran inside `make verify` on their own `w2a-it-*` throwaway collections; no `w2a-realcheck-*` collection touched, no manual Qdrant call).
  - `make test-unit` → 521 passed, 1 skipped, 19 deselected. `make test-integration` → 19 passed.
  - `make eval-retrieval` (no `bge-m3` extra) → exit 2, `ERROR OptionalDependencyError: BGE-M3 needs the optional 'bge-m3' dependency group; run make setup-bge-m3.`; nothing written (embedder is built at step 5, before the client factory; `test_missing_extra_exits_2_before_qdrant` asserts `factory.calls == 0`).
  - `pytest packages/rag/tests/retrieval/test_legacy_baseline_snapshot.py test_retrieval_eval.py::test_case_access_context_never_widens_access` → 5 passed.
  - `git diff --stat HEAD -- packages/rag/src/way2australia_rag/retrieval/` → empty. `git status --porcelain -- evaluation knowledge config experiments` → empty.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R4] The `access_context` behaviour test is meaningful at runner level (golden rows with `admin`/other-tenant and `staff`-scope contexts plus `None`; the spy sees 4 searches, warm-up included, each equal to `build_access_filter(guest())`; a runner that derived access from `case.access_context` would fail it). But the access is supplied by the test, so CLI step 7 (`resolve_access(guest_access(settings))`) is not covered: a CLI that ignored `W2A_TENANT_ID` or hard-coded a tenant would still pass. → Add a CLI test with a spy `search` and a non-default `W2A_TENANT_ID`, asserting every filter equals `build_access_filter(resolve_access(guest_access(settings)))` for that tenant.
  - F2 [MINOR, IMPLEMENTATION, R4] `--config` (and `--repo-root`) are options beyond the task's list (`--top-k`, `--suite`, `--release`, `--output`). Judged safe: a fake provider in a custom config is refused at step 5, and `--repo-root` is required by the `make` target. → Record both in the design's As-built notes and `COMMANDS.md` at T8.
  - F3 [MINOR, SPEC_DEFECT, R6] The `relevant_section_ids` entry form `"<document_id>#<section_id>"` is stated only in the T3 checklist; `evaluation_case.schema.json` allows any string and the design speaks of pairs. No case uses the field today. → Record the key form in `design.md` and the T8 docs (no schema change; `evaluation/` is protected).
- Judgements on implementer decisions: `--config` accepted (F2). Injectable `client_factory`/`embedder_factory` with defaults `default_client_factory`/`build_embedder` are test seams only; the CLI has no `--embedder`/`--allow-fake` (tested). Refusing an active golden that is unanswerable or has no relevant documents (exit 2, naming `case_id`) matches R3 "never silently excluded". `"<document_id>#<section_id>"` keys confirmed against the T3 checklist (F3 for docs). `unknown` authority key is safe: `validate-evaluation` already refuses unknown or ineligible relevant documents. No `unanswerable` block is correct for T3 (R10 is T4). `excluded_case_count` = golden rows not run keeps the 1.0 meaning. Fake-index refusal reached as a D036 binding mismatch in the CLI is what design step 9 anticipates; `require_real_index` is tested at runner level with a real-reporting embedder.
- Summary for user:
  - Changed: new `evaluation/{slices,sections,results,retrieval_eval}.py` (slices with `n`/`small_sample`, absent languages from the registry, section metrics over `doc#section` keys, 2.0 result document, writing via the unchanged `retrieval.baseline.write_result`); `retrieval` subcommand in `evaluation/cli.py`; `make eval-retrieval`.
  - Verified by: `make verify` (540 passed, 1 skipped, integration included), `make eval-retrieval` exit 2 without the extra, legacy snapshot and `access_context` tests, `retrieval/` diff empty, protected paths clean.
  - Worth your attention: the `access_context` test proves the runner ignores case contexts, but not that the CLI resolves access from server settings (F1); extra `--config` option (F2); section-key form is undocumented outside `tasks.md` (F3).
  - Reading order:
    1. `Makefile` → `eval-retrieval` target.
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval`: startup order 1–7, refusals, `format_summary`.
    3. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation`, `require_*`, `_notes`: one access for all cases, rows and the 2.0 document.
    4. `packages/rag/src/way2australia_rag/evaluation/slices.py` → `slice_by`, `source_authority_key`, `active_registry_languages`.
    5. `packages/rag/src/way2australia_rag/evaluation/sections.py` → `section_report`: zero-measurable note.
    6. `packages/rag/src/way2australia_rag/evaluation/results.py` → constants, `default_output_path`, `write_document`.
    7. `packages/rag/tests/evaluation/test_retrieval_eval.py` (incl. `test_case_access_context_never_widens_access`), `test_cli.py`.
    8. `packages/rag/tests/evaluation/test_slices.py`, `test_sections.py`; supporting edit: `tasks.md` T3 checkboxes and State.
- Usage: 132K tokens · 24 tool uses · 6:59

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T3. Implementer decisions accepted. Add to the T8 running list: F1: CLI test for `eval-retrieval` with a non-default `W2A_TENANT_ID`, asserting the search filter carries that tenant (access resolved from server settings, not passed in). F2: record `--config` / `--repo-root` in design As-built notes and COMMANDS.md. F3: record the section-key form `"<document_id>#<section_id>"` in design.md and T8 docs. Also: show me T3's reading order and token usage table — both should be in the summary. If the reviewer didn't produce the reading order, note it so T4's review includes it."

## T4 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py`: `score_distribution`, `unanswerable_report`, constants `UNANSWERABLE_STATUS`/`UNANSWERABLE_OWNER`; the 2.0 document gains the `unanswerable` block;
  - `packages/rag/src/way2australia_rag/evaluation/cli.py`: `_unanswerable_line` in `format_summary` (one informational line);
  - tests: `packages/rag/tests/evaluation/test_retrieval_eval.py` (7 new tests), `test_cli.py` (block and summary-line assertions in the success test);
  - `tasks.md`: T4 State and checkboxes; this file.
- Verification run:
  - `make verify` -> exit 0 (ruff check and format, pyright, skills-check, validate-knowledge OK, validate-evaluation OK, pytest 547 passed, 1 skipped). No Docker started, Qdrant not started, stopped or touched; no `w2a-realcheck-*` collection touched; no `bge-m3` extra.
  - `git status --porcelain -- evaluation knowledge config experiments` -> empty; `git diff --stat` on `retrieval/` -> empty.
- Notes and decisions:
  - Unanswerable cases run after the golden cases with the same server-resolved access (a spy test checks the filter, including a hostile `access_context`). Only the top-1 score is kept; the `latency_ms` of those retrievals is neither recorded nor in p50/p95 (test inflates their latency).
  - Distributions use the existing nearest-rank `percentile`, rounded to 4 decimals. With no scores (zero active unanswerable cases, or a case with no hits) the value is `null`; a no-hit case has `top1_score: null` and is skipped in the distribution.
  - The block is always present, also with `n: 0`. It has no `hit`, threshold or pass/fail key (asserted).
  - Warm-up still uses the first golden query; no extra search for unanswerable cases.
  - No query text is written (test scans the written file).
- Usage: 110K tokens · 15 tool uses · 2:10

### Review
- Model: claude-opus-5-5 (intended tier BEST, Claude Code `Opus`: matches; run as a subagent; implementer used a different model).
- Verdict: PASS
- Commands: `make lint` → exit 0; `make typecheck` → exit 0 (0 errors); `make test-unit` → exit 0 (528 passed, 1 skipped, 19 deselected); `make verify` → exit 0 (547 passed, 1 skipped; the 19 Docker integration tests ran against the reachable local Qdrant on their own temporary collections; no `w2a-realcheck-*` collection or `experiments/results/` touched); `git status --porcelain -- evaluation knowledge config experiments` → empty; `git diff --stat HEAD -- packages/rag/src/way2australia_rag/retrieval/` → empty.
- Checks: all four T4 boxes backed by code and tests. R10: block marked `not_evaluable_before_generation`, owner `roadmap-10`, `n`, min/p50/p95/max for unanswerable and golden top-1 scores, per-case `case_id`/`case_version`/`top1_score`; no threshold, pass/fail or hit key (asserted). Unanswerable latencies not recorded and not in p50/p95 (test inflates them). Deprecated cases excluded. Same server-resolved `ResolvedAccess` for unanswerable queries; a hostile `access_context` cannot widen the filter (spy test). R7: block added to the 2.0 document; no query text written (file scan). Scope: no T5–T8 work, no new dependency, no Phase 2 drift.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R10] `run_retrieval_evaluation` docstring still says "Run the active golden cases"; it now also runs the active unanswerable cases → update the docstring (can ride with T8).
- Summary for user (PASS only):
  - Changed: `retrieval_eval.py` gains `score_distribution` and `unanswerable_report`; the runner calls it after the golden loop and adds an `unanswerable` block to the 2.0 result. `cli.py` prints one informational line (`_unanswerable_line`). 7 new runner tests, CLI success test extended.
  - Verified by: `make lint`, `make typecheck`, `make test-unit` (528 passed), `make verify` (547 passed, 1 skipped); protected paths and `retrieval/` unchanged.
  - Worth your attention: a case with no hits gets `top1_score: null` and is skipped in the distribution; with zero active cases all four values are `null` and the block is still present. The block is never a gate; real numbers appear only on the user-owned real run.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation`: where `unanswerable_report` is called after the golden loop (after `latencies` is taken) and where the `unanswerable` key enters the document.
    2. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `unanswerable_report`: runs active unanswerable cases with the same access, keeps only top-1 score; constants `UNANSWERABLE_STATUS`/`UNANSWERABLE_OWNER`.
    3. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `score_distribution`: nearest-rank min/p50/p95/max, `None` handling.
    4. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_unanswerable_line` (used by `format_summary`): the one printed informational line.
    5. `packages/rag/tests/evaluation/test_retrieval_eval.py`: the 7 new tests from `test_unanswerable_block_is_marked_not_evaluable` to `test_no_unanswerable_query_text_in_the_document`.
    6. Supporting edits: `packages/rag/tests/evaluation/test_cli.py` (block and summary-line asserts), `tasks.md` State/checkboxes.
- Usage: 85K tokens · 12 tool uses · 5:27

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T4. Add F1 (docstring) to the T8 list. For T5: include the access_context check in the security runner's tests, as flagged earlier."

## T5 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - new `packages/rag/src/way2australia_rag/evaluation/security_corpus.py` (`build_security_repository`), `security_index.py` (`build_security_index`, `delete_security_index`, `SecurityIndex`, base and collection refusals, variant constants), `security_eval.py` (`RETRIEVAL_SIDE_ATTACK_TYPES`, `DEFERRED_OWNERS`, `FORBIDDEN_VARIANTS`, `select_security_queries`, `run_security_evaluation`, `security_document`);
  - `evaluation/errors.py`: `EvaluationHarnessError`; `evaluation/cli.py`: `security` subcommand, `DEFAULT_FIXTURE_ROOT`, `format_security_summary`;
  - `packages/rag/tests/conftest.py`: `security_repository` fixture now calls the library builder;
  - new tests `packages/rag/tests/evaluation/test_security_eval.py` (25 tests incl. CLI) and `test_security_integration.py` (1, `integration`);
  - `.gitignore` (`experiments/results/tmp/`), `Makefile` (`eval-security`, `.PHONY`), `tasks.md` (T5 State and checkboxes), this file.
- Verification run:
  - `make verify` -> exit 0 (ruff check and format, pyright, skills-check, validate-knowledge OK, validate-evaluation OK, pytest 572 passed, 1 skipped; the Docker integration tests ran because local Qdrant was reachable).
  - `make eval-security` -> exit 0, PASS in about 450 ms, 68 queries (5 security cases, 63 golden), 5 deferred; JSON landed in `experiments/results/tmp/` (git-ignored).
  - The new test file ran in about 5 s together with the integration test; the in-memory gate test asserts under 10 s.
  - `git status --porcelain -- evaluation knowledge config experiments` -> empty. Qdrant container not started or stopped; `w2a-realcheck-*` untouched; `curl localhost:6333/collections` after the run lists only the two `w2a-realcheck-idx-v1*` collections (no `w2a-sectest-*` left behind).
- Notes and decisions:
  - `build_security_repository(fixture_root, work_dir, *, schema_source)`: a keyword-only `schema_source` was added to the design signature because library code must not know where the metadata schema lives; fixtures are discovered as `*.md` under `fixture_root` (no file names or fixture path in library code; the only `fixtures/security` literal is the CLI default, asserted by a test).
  - Seed points are written by running the production `IngestionService` against the new collection (it calls `ensure_collection` and `replace_document`), instead of re-implementing the loop.
  - Canary probe points use `point_id(canary, "query-probe", i)` so they cannot collide with the canary's own chunk-0 point ID; their payload is the canary payload with `chunk_position = i`.
  - A `RetrievalAuthorizationError` is a violation; its document ID is parsed from the error message (names document ID and fields only) to fill `document_id` and variant. If the store drops the filter, `check_hit` raises first, so a second test bypasses `check_hit` (monkeypatch) to prove the forbidden-document path also fails the gate.
  - The result is written on exit 0 and exit 1 (violation) and not on exit 2; documents hold IDs, counts, verdicts, deferred cases and `excluded_fixtures`, never query or chunk text (test scans).
  - access_context check (user decision): `test_case_access_context_never_changes_the_filter` runs golden and security cases whose own `access_context` claims staff/admin/another tenant, with a spy index on `search`; every filter equals `build_access_filter(<server guest access>)` and carries only the server tenant. The CLI failure test also covers exit 1 with ids only.
  - `eval-security` takes `--config`, `--suite`, `--repo-root` like `eval-retrieval`; the suite must be active.
  - The in-memory missing-owner point is excluded by the filter as on Docker (the gate passes in memory and on Docker).
- Deferred items: record `--fixture-root`, `--config`, `EvaluationHarnessError` and the security result document shape in T8 docs and design As-built notes.
- Usage: 159K tokens · 35 tool uses · 18:00

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; implementer was Sonnet, so a different model).
- Verdict: PASS
- Commands: `make verify` → exit 0 (ruff check + format check, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation; pytest 572 passed, 1 skipped; Docker integration tests ran, since local Qdrant was reachable); `make test-integration` → exit 0 (20 passed, 553 deselected, including `test_server_filter_keeps_every_forbidden_point_out`); `make eval-security` → exit 0, PASS in 425 ms, 68 queries (5 security, 63 golden), 5 deferred, JSON in `experiments/results/tmp/`; `curl -s localhost:6333/collections` before and after → only `w2a-realcheck-idx-v1` and `-settings` (no `w2a-sectest-*` left, realcheck untouched, container not started or stopped); `git status --porcelain -- experiments evaluation knowledge config packages/rag/src/way2australia_rag/retrieval` → empty; `grep -rn fixtures/security packages/*/src apps` → only the `cli.py` `DEFAULT_FIXTURE_ROOT` default.
- Reviewer mutation checks (scratch script outside the repo, no file edited): with production `retriever.build_access_filter` patched to return an empty `Filter()`, `cli.main(["security", ...])` → exit 1 with VIOLATION lines (`owned`, `missing_owner`, `other_tenant`, ...); with the filter cut to its first condition and `check_hit` bypassed, each of `other_tenant`, `owned` and `missing_owner` is still reported. So the gate fails per dropped condition, not just when everything is removed. The `access_context` spy test is meaningful: cases claim staff/admin/another tenant, the spy records the filter actually passed to `DenseIndex.search`, and each filter must equal `build_access_filter(<server guest access>)` and contain neither `staff` nor `other-tenant`. A runner that built access from the case would fail it.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R8] `security_eval.py` gets the violating `document_id` by parsing the `RetrievalAuthorizationError` message (regex `hit for document '...'`), which ties it to the message wording in `retrieval/access.py`. If the wording changes, the case still fails closed (variant `check_hit_failed`), but `document_id` is empty → optional: a test that pins the parse, or a structured attribute in a later retrieval spec.
  - F2 [MINOR, IMPLEMENTATION, R8] The checklist item puts "the collection is deleted at the end" in `security_eval.py`, but deletion happens in the CLI's `finally` (`delete_security_index`), not in `run_security_evaluation`. The effect is equivalent for the CLI and for the Docker test (which also cleans up by name in `finally`) → record it in the T8 design As-built notes.
  - F3 [MINOR, IMPLEMENTATION, R8] `security_document` hard-codes `"role": "guest"` instead of taking it from the resolved access. This is correct for Phase 1 only → record it, or take it from access when roles arrive.
  - F4 [MINOR, IMPLEMENTATION, R8] `build_security_repository` now discovers fixtures by `*.md` glob instead of the fixed `FIXTURE_IDS` names, so a new `.md` dropped into `tests/fixtures/security/` would enter the security corpus (the directory holds only the two fixtures today; the Spec 002 tests pass unchanged) → nothing needed now; note it in T8 docs.
- Summary for user (PASS only):
  - Changed: new `evaluation/security_corpus.py`, `security_index.py` and `security_eval.py` build a throwaway `w2a-sectest-<8hex>` in-memory index (seed corpus through production ingestion, staff canary, four forbidden variants nearest by construction) and run every retrieval-side security case and golden query through `DenseRetriever` with the server guest access. `make eval-security` (`cli.py security`) exits 0/1/2. `.gitignore` ignores `experiments/results/tmp/`. A Docker test proves the real server applies the filter (closes Spec 005 retro F3).
  - Verified by: `make verify` (572 passed, 1 skipped), `make test-integration` (20 passed), `make eval-security` (PASS, 425 ms), Qdrant collection listing before and after (clean), protected-path and `retrieval/` checks empty, and reviewer mutation runs (an empty or partial filter makes the gate exit 1).
  - Worth your attention: `build_security_repository` gained a keyword-only `schema_source` and discovers fixtures by glob (F4). The builder runs the production `IngestionService` for seed points. Violations parse the document ID from the error message (F1). Deletion lives in the CLI, not in the runner (F2). T8 must document `--fixture-root`, `--config`, `EvaluationHarnessError` and the security result shape.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `Makefile` → `eval-security`, then `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_security`: in-memory client, random base, build, run, write, delete in `finally`; `format_security_summary`.
    2. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `select_security_queries`: retrieval-side vs deferred/unclassified split.
    3. `packages/rag/src/way2australia_rag/evaluation/security_index.py` → `build_security_index`: base/existing refusals before any write, seed ingestion, canary probes, raw forbidden upserts (`_forbidden_payload`); `delete_security_index`.
    4. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `run_security_evaluation` and `_sanity_check`: unfiltered rank-1 check, guarded retrieval, violation recording; `security_document` (IDs only).
    5. `packages/rag/src/way2australia_rag/evaluation/security_corpus.py` → `build_security_repository`: isolated copy of the fixtures with a generated manifest.
    6. `packages/rag/src/way2australia_rag/evaluation/errors.py` → `EvaluationHarnessError`.
    7. `packages/rag/tests/evaluation/test_security_eval.py`: `SpyIndex`, the filter-dropping and `check_hit`-bypass tests, `test_case_access_context_never_changes_the_filter`, refusals, the 10 s bound, CLI exit codes.
    8. `packages/rag/tests/evaluation/test_security_integration.py`: Docker run with cleanup by name in `finally`.
    9. Supporting edits: `packages/rag/tests/conftest.py` (fixture now calls the library builder), `.gitignore`, `tasks.md` State and checkboxes.
- Usage: 124K tokens · 23 tool uses · 7:29

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T5. Implementer decisions confirmed (schema_source, --config/--suite/--repo-root, --fixture-root as CLI-only default). Add to the T8 list: T5 F1: give `RetrievalAuthorizationError` a `document_id` attribute and read it in the security runner instead of regex-parsing the message; test that a violation report names the document. T5 F4: `build_security_repository` uses an explicit list of fixture files and refuses unexpected files in the fixture folder (e.g. a stray README.md); test both. T5 F3: no code change; record in As-built notes that `security_document` hard-codes role `guest` (Phase 1) and must change when other roles are added. (If not already added) the hard-coded live counts item: replace ~20 tests asserting 13 / 85 / 63 / 12 / 10 with consistency checks against live sources; exact-number tests use the frozen fixture; verify by adding one document and one golden in a scratch copy and running `make test-unit`."

## T6 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - new `packages/rag/src/way2australia_rag/evaluation/compare.py` (`HIT_TOLERANCE_CASES`, `mrr_tolerance`, `compare`, `Comparison`);
  - `evaluation/results.py`: `read_result`, `ComparableRun`, `CaseRow`; `evaluation/errors.py`: `NotComparableError`; `evaluation/cli.py`: `compare` subcommand (`--base`, `--candidate`);
  - `Makefile`: `eval-compare` (usage error and exit 2 when BASE or CANDIDATE is missing), added to `.PHONY`;
  - new `packages/rag/tests/evaluation/test_compare.py` (22 tests incl. CLI exit codes); `tasks.md` (T6 State and checkboxes); this file.
- Verification run:
  - `make verify` -> exit 0 (ruff check and format, pyright, skills-check, validate-knowledge, validate-evaluation, pytest 594 passed, 1 skipped).
  - `make eval-compare BASE=<committed 1.0> CANDIDATE=<same>` -> exit 0, `eval-compare: PASS (hits 60 -> 60, MRR 0.8783 -> 0.8783)`, no WARNING lines (read-only use of the committed file).
  - Manual: a scratch copy (scratchpad, outside the repo) with `document_count` 14 -> exit 2 and `not comparable: document count changed 13 -> 14; run `make eval-retrieval` on the current system to set a new baseline.`
  - `make eval-compare` with no variables -> usage message, exit 2.
  - `git status --porcelain -- evaluation knowledge config experiments` -> empty. Qdrant not touched.
- Notes and decisions:
  - Refusals raise `NotComparableError` (new `EvaluationError` subclass); the CLI prints the message as-is (it already starts with `not comparable:`), through `safe_text`, to stderr, exit 2. All differences are named in one message; case differences are capped at 10 keys then "and N more"; the same case_id with a different version is reported as "case_version changed for gNNN 1 -> 2".
  - Unreadable files, unknown `kind`/`schema_version` and malformed rows name the file by name only and suggest `make eval-retrieval` (or `make retrieval-baseline` for 1.0). Label BASE/CANDIDATE is passed to `read_result` as an optional second argument.
  - Fake runs: message names which file and suggests a real-embedder run; combined with other differences, both next steps are given.
  - Hits and MRR come from per-case rows, unrounded. Slices follow BASE's labels over the shared case keys; `source_authority` is compared only when both files are 2.0, otherwise a note says so. Flips are sorted by case_id and never fail the gate.
  - Test for "pass at exactly 1/n" uses n=10 and two cases moving rr 1.0 -> 0.5 (hits unchanged).
- Deferred items: none. The Phase 2 "compare shared cases" mode is not built (per the amendment).
- Usage: 116K tokens · 19 tool uses · 6:29

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; implementer was Sonnet, so a different model).
- Verdict: PASS
- Commands: `make verify` → exit 0 (ruff check + format check, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation; pytest 594 passed, 1 skipped; Docker integration tests ran, local Qdrant reachable); `make test-integration` → exit 0 (20 passed, 575 deselected); `pytest packages/rag/tests/evaluation/test_compare.py` → 22 passed; `make eval-compare BASE=<committed 1.0> CANDIDATE=<same>` → exit 0, `eval-compare: PASS (hits 60 -> 60, MRR 0.8783 -> 0.8783)`, no WARNING lines, source_authority "not compared" note; manual scratchpad copy (outside the repo) with `document_count` 14 → exit 2, `not comparable: document count changed 13 -> 14; run `make eval-retrieval` on the current system to set a new baseline.`; `make eval-compare BASE=x` → usage line, exit 2; `git status --porcelain -- evaluation knowledge config experiments packages/rag/src/way2australia_rag/retrieval` → empty. No `w2a-realcheck-*` collection touched, container not started or stopped, nothing written under `experiments/results/`.
- Reviewer mutation checks (scratch script outside the repo, module constants patched in memory, no file edited): `HIT_TOLERANCE_CASES` 0 or 2 → the one-lost/two-lost test fails; `mrr_tolerance` 1/n − 1e-6 or 1/n + 0.002 → `test_mrr_boundary` fails. Refusal tests checked one by one: suite ID, suite version, `top_k`, `document_count`, `case_version` and missing case each assert the reason, old -> new values and `make eval-retrieval`; BASE/CANDIDATE fake assert the file name and the real-embedder step; unknown `kind`/`schema_version` assert file name, value found and both commands; the shared `refusal()` helper asserts the `not comparable:` prefix and that neither the synthetic query text nor `tmp_path` appears. Messages carry file names only (`Path.name`), the CLI prints refusals through `safe_text` and unexpected errors as class name only.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R11] The "pass at exactly 1/n" case (n=10, two rr 1.0 -> 0.5) computes a drop of 0.09999999999999998, below 1/n, so neither `MRR_EPSILON` nor the strict `>` is pinned: removing the epsilon, or using `>=` with it, still passes the test. At n=3 (one rr 1.0 -> 0.0) the float drop is 0.33333333333333337 > 1/3, where the epsilon matters → optional: add an n=3 boundary case.
  - F2 [MINOR, IMPLEMENTATION, R11] The case-key cap applies per list (`case_version changed`, `only in BASE`, `only in CANDIDATE` each up to 10), so one message can list up to 30 keys; the task says "up to 10 differing keys, then and N more" → optional: cap the total, or record the per-list reading in T8 As-built notes.
  - F3 [MINOR, IMPLEMENTATION, R11] The "extra case" half of `test_case_set_missing_and_extra` asserts only `only in CANDIDATE: g009 v1`, not the `9 -> 10` counts or the next step (the code emits both; the missing-case half asserts them) → optional: add the two assertions.
  - F4 [MINOR, IMPLEMENTATION, R11] Flip lines read `WARNING flipped hit->miss: g002 v1`; the design example shows `g026 (v1)`. Sorting is by the `"<case_id> v<version>"` string, so by `case_id` as required → align the design example or the format in T8.
  - F5 [MINOR, IMPLEMENTATION, R11] A file holding the same `case_id` twice with different `case_version`s is accepted (keys are unique per pair), and `_refusals` then collapses those versions in a dict, so the "case_version changed" detail can name only one of them. Unreachable with today's writers (one row per case) → note only.
- Summary for user (PASS only):
  - Changed: `make eval-compare BASE=... CANDIDATE=...` (new `evaluation/compare.py`, `read_result` in `results.py`, `compare` subcommand in `cli.py`, `NotComparableError`) reads 1.0 and 2.0 result files, refuses unlike or fake runs with one `not comparable:` message naming every difference (old -> new) and the next step, and otherwise applies the fixed gate: fail only if more than 1 hit is lost or MRR drops by more than 1/n. It prints overall and per-slice deltas, latency, identity differences and flip warnings; exit 0/1/2.
  - Verified by: `make verify` (594 passed, 1 skipped), `make test-integration` (20 passed), 22 `test_compare.py` tests, the committed baseline compared with itself (PASS, no warnings), the manual 13 -> 14 refusal (exit 2), and reviewer mutation runs on both gate constants.
  - Worth your attention: the "exactly 1/n" test does not exercise the float epsilon (F1); the 10-key cap is per list, not per message (F2). Slices use BASE's labels over the shared case keys. All five findings are MINOR and optional.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `Makefile` → `eval-compare` (usage error when BASE or CANDIDATE is missing), then `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_compare`: read both, compare, print, exit 0/1/2.
    2. `packages/rag/src/way2australia_rag/evaluation/results.py` → `read_result` and `_build_run`: accepts only 1.0/2.0, builds `ComparableRun` with per-case `CaseRow`s; `_unreadable` messages.
    3. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `_refusals`: every difference in one message with old -> new and the next step.
    4. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `compare`: unrounded hits/MRR, the gate (`HIT_TOLERANCE_CASES`, `mrr_tolerance`), slice/latency/identity lines, sorted flip warnings.
    5. `packages/rag/src/way2australia_rag/evaluation/errors.py` → `NotComparableError`.
    6. `packages/rag/tests/evaluation/test_compare.py`: `doc()`/`case()` builders and the `refusal()` helper, the boundary tests, one test per refusal, the committed-baseline self-compare and CLI exit codes.
    7. Supporting edits: `.PHONY` in `Makefile`, `tasks.md` State and checkboxes.
- Usage: 117K tokens · 21 tool uses · 5:53

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T6. Implementer decisions accepted. Add to the T8 list: T6 F1: boundary test with n=3 — an MRR drop of exactly 1/n passes, the next representable value above fails (exercises the epsilon and strict `>`). T6 F3: the extra-case refusal test asserts the `9 -> 10` counts and the next-step text. T6 F5: `read_result` rejects a file with a duplicate `case_id` (any version); test it. No change for F2 and F4 (retrospective records the flip-line format in As-built notes)."

## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - new `evaluation/candidates/006-candidates.jsonl` (7 rows: 6 pure-`ml` `new_case` proposals, 1 `case_change` for `g004`/`u001`); the only change under `evaluation/`;
  - `packages/rag/tests/evaluation/test_validate.py`: `test_real_candidates_file_validates_and_is_not_loaded`;
  - `tasks.md` (T7 State and checkboxes); this file.
- Verification run:
  - `make validate-evaluation` -> exit 0, `OK, 0 problems`.
  - `make verify` -> exit 0 (ruff check and format, pyright, skills-check, validate-knowledge, validate-evaluation, pytest 595 passed, 1 skipped).
  - `make eval-security` -> PASS (candidates not loaded; result written under the ignored `experiments/results/tmp/`).
  - `git status --porcelain -- evaluation knowledge config` -> exactly `?? evaluation/candidates/`.
  - Qdrant container, `w2a-realcheck-*` collections and committed `experiments/results/` files not touched.
- Notes and decisions:
  - Each `ml` row: `status: suggested`, `target_suite_id: public-eval-v1`, `proposed_by: spec-006`, `drafted_by: agent`, `needs_fluent_speaker_review: true`, `requires_review: [fluent_malayalam_speaker, owner_review]`, a `rationale` stating the query is an agent draft. Candidate IDs `cand006_ml_001` to `006`; `proposed_case` is `case_version` 1, `category: multilingual`, with `expected_facts` taken from the document text and the guest `access_context` used by existing cases.
  - Queries are written in Malayalam script and deliberately differ from existing goldens (for example refund on cancellation, test-day equipment, recording of coaching sessions, price of the three-mock package, English numerals policy, total marks and pass mark); none has `relevant_section_ids`.
  - The `case_change` row lists four options (keep both, reword `u001`, retire `g004` as answerable, merge) without choosing; `requires_review: [owner_review]`, `needs_fluent_speaker_review: false`.
  - The new test asserts the shared row rules, that the real file validates, that no candidate or proposed case ID appears among the suite's loaded cases, and that the suite manifest does not mention candidates.
- Deferred items: none. Malayalam wording needs fluent-speaker correction before any approval (outside this spec).
- Usage: 99K tokens · 19 tool uses · 2:05

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; implementer was Sonnet, so a different model).
- Verdict: PASS
- Commands: `make validate-evaluation` → exit 0, `OK, 0 problems`; `make verify` → exit 0 (ruff check + format check, pyright, skills-check, validate-knowledge, validate-evaluation; pytest 595 passed, 1 skipped; Docker integration tests ran, local Qdrant reachable); `make test-unit` → 575 passed, 1 skipped, 20 deselected; `make lint` → exit 0; `make test-integration` → 20 passed, 576 deselected; `pytest test_validate.py -k real_candidates` → 1 passed; `make eval-security` → PASS (68 queries, result under the ignored `experiments/results/tmp/`); `git status --porcelain -- evaluation knowledge config experiments` → exactly `?? evaluation/candidates/`; `git diff HEAD -- packages/rag/src/way2australia_rag/retrieval/` → empty; `load_suite` on `public-eval-v1` → 63/12/10 cases (85, matches `case_count`), query languages `en` and `mixed` only. `task-reviews.md` diff has no removed lines. No `w2a-realcheck-*` collection touched, container not started or stopped.
- Reviewer content check: all 7 rows read against the schema (`candidate_row`) and the six cited documents. Every row: `status: suggested`, `target_suite_id: public-eval-v1`, `proposed_by: spec-006`, `drafted_by: agent`, a `rationale`. The six `new_case` rows: `query_language: ml`, `needs_fluent_speaker_review: true`, `requires_review: [fluent_malayalam_speaker, owner_review]`, one eligible document each, no `relevant_section_ids`; each query asks what its document answers (total and pass marks; allowed and banned equipment; 75% refund on cancellation; ₹8,499 materials + three mocks; no live-session recordings; numbers rendered in Malayalam), and the `expected_facts` are in the document text. The `case_change` row targets `g004` and `u001` (both exist), lists four options without choosing, `requires_review: [owner_review]`, and has `needs_fluent_speaker_review: false`, which the spec allows (R14 and the design require `true` only for non-`en` proposed queries).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R14] `cand006_ml_003` ("ടെസ്റ്റ് ബുക്ക് ചെയ്തശേഷം റദ്ദാക്കിയാൽ പണം തിരികെ കിട്ടുമോ?") does not say NAATI or the official test, so on a Way2Australia assistant it also matches `business_007_payments_account_support` ("Payments are non-refundable"); its rationale's "no existing golden covers the refund rule" overlooks `g032` (Way2Australia refunds). `cand006_ml_002` ("ടെസ്റ്റ് എഴുതാൻ ...") has the same, milder ambiguity with the mock test setup → optional: name NAATI / the official test in both queries and say "the NAATI refund rule" in the rationale; otherwise leave for the fluent-speaker and owner review.
  - F2 [MINOR, IMPLEMENTATION, R14] `cand006_ml_001` keeps "NAATI CCL" in Latin script; the other five use only Malayalam script (with Malayalam-script loanwords). Proper-noun acronyms are reasonable in a pure-`ml` query, but they give a lexical anchor the others lack → note for the fluent speaker; no change needed.
  - F3 [MINOR, IMPLEMENTATION, R14] The new test proves non-loading by ID disjointness and by the manifest not containing "candidates"; it does not assert the loaded case count equals the manifest `case_count` (85) or that no loaded case has `status: suggested` → optional: add one of those assertions.
- Summary for user (PASS only):
  - Changed: new `evaluation/candidates/006-candidates.jsonl` (7 inactive rows: 6 agent-drafted pure-Malayalam golden proposals, one per required document, and one `case_change` listing four options for the `g004`/`u001` conflict without choosing), plus one test in `test_validate.py`. No active case, dataset, schema or suite manifest changed.
  - Verified by: `make validate-evaluation` (0 problems), `make verify` (595 passed, 1 skipped), `make test-integration` (20 passed), `make eval-security` (PASS), protected-path check (only `?? evaluation/candidates/`), the suite still loads 85 cases with no `ml` case.
  - Worth your attention: the Malayalam queries are agent drafts and match their documents, but must be corrected by a fluent speaker before any approval; the refund query may also hit the Way2Australia "non-refundable" policy unless it names NAATI (F1). The `case_change` row has `needs_fluent_speaker_review: false` (allowed: English-only owner decision). All three findings are MINOR and optional.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `evaluation/candidates/006-candidates.jsonl`: the six `new_case` rows (`cand006_ml_001`–`006`), then `cand006_change_g004_u001` and its `options`.
    2. `packages/rag/src/way2australia_rag/evaluation/validate.py` → `_validate_candidates` and `_candidate_rules` (unchanged, T2): how `make validate-evaluation` checks these rows.
    3. `packages/rag/tests/evaluation/test_validate.py` → `test_real_candidates_file_validates_and_is_not_loaded`.
    4. Supporting edits: `tasks.md` T7 State and checkboxes.
- Usage: 107K tokens · 28 tool uses · 6:04

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T7. Add to the T8 list: T7: set `owner_review: true` on the `cand006_change_g004_u001` row (business decision). Edits evaluation/candidates/006-candidates.jsonl — name the file explicitly in the T8 box. T7 F1: in the same file, correct `cand006_ml_003`'s rationale (g032 covers the refund rule) and make the query name NAATI to avoid matching business_007; review `cand006_ml_002` for the same ambiguity. T7 F3: the test asserts the loaded count equals the suite manifest's `case_count` (not a literal 85) and that no loaded case has status `suggested`. F2: no change (for the fluent-speaker review)."

## T8a — round 1

### Implementation
- Model: claude-sonnet-5-5 (intended tier BEST_MINUS_ONE; run as a subagent, no user to ask).
- Files changed:
  - `evaluation/candidates/006-candidates.jsonl` (scope exception): `cand006_ml_003` rationale corrected (g032 covers the Way2Australia refund rule; this is the NAATI rule) and query now names the official NAATI CCL test and NAATI; `cand006_ml_002` query now names the official NAATI CCL test and its rationale says why. Both rows keep their status, flags, `requires_review` and `relevant_document_ids`; no other row changed.
  - `retrieval/errors.py` and `retrieval/access.py` (scope exception): `RetrievalAuthorizationError(message, *, document_id)`; both `check_hit` raise sites pass `document_id`; message text unchanged.
  - `evaluation/security_eval.py`: reads `error.document_id`; `_HIT_DOCUMENT` regex and `import re` removed.
  - `evaluation/security_corpus.py`: explicit `SECURITY_FIXTURE_FILES`; `_fixture_files` refuses stray visible entries and missing files before any copy, ignores dot-prefixed entries.
  - `evaluation/results.py`: `read_result` refuses a repeated `case_id` (any version, 1.0 and 2.0) with a `not comparable:` message naming the file and `case_id`.
  - `evaluation/retrieval_eval.py`: docstring of `run_retrieval_evaluation` only.
  - `packages/rag/pyproject.toml` (`referencing>=0.35.0`) and `uv.lock` (two added lines, `way2australia-rag` entry only).
  - Tests: `evaluation/test_validate.py`, `test_cli.py`, `test_security_eval.py`, `test_compare.py`, `test_suite_loader.py`, `test_status_handling.py`; `retrieval/test_baseline.py`, `test_goldens.py`; `ingestion/test_chunking.py`, `test_service.py`, `test_cli_config.py`; `test_content_hash.py`, `test_eligibility.py`, `test_local_repository.py`, `test_manifest_validation.py`; `conftest.py` (helpers `manifest_document_count`, `live_suite_rows`).
  - `tasks.md` (T8a State and checkboxes); this file.
- Verification run:
  - `make verify` -> exit 0 (ruff, format check, pyright, skills-check, validate-knowledge, validate-evaluation; pytest 609 passed, 1 skipped, Docker tests ran).
  - `make test-integration` -> 20 passed; `make eval-security` -> PASS (result under the ignored `experiments/results/tmp/`); `make lint`, `make typecheck` clean; `make validate-evaluation` OK.
  - T1 legacy snapshot test passes unchanged (snapshot and summary files untouched, no diff under `retrieval/tests/fixtures`).
  - `git diff --stat main -- retrieval/` lists only `access.py`, `errors.py`, `goldens.py`; `metrics.py`, `baseline.py`, `baseline_cli.py` unchanged.
  - `make setup` ran; `git diff uv.lock` = two added lines in the `way2australia-rag` entry; a second `make setup` changed nothing.
  - Live-count grep (`== 5|10|12|13|63|85` and `13|63|85 documents|cases`) finds only constants, synthetic data, the frozen fixture and the committed 1.0 file tests.
  - Scratch-copy live-data check, in a copy under the session scratchpad: added a valid public document (manifest entry with correct hashes) and an active golden `g900` with `case_count` +1; `make validate-knowledge` OK, `make validate-evaluation` OK, `make test-unit` 589 passed, 1 skipped (the committed 1.0 result file was copied in read-only, because the copy excluded `experiments/results`). The copy was deleted.
  - `git status --porcelain -- evaluation knowledge config experiments` -> exactly ` M evaluation/candidates/006-candidates.jsonl`. Qdrant container and `w2a-realcheck-*` collections not touched.
- Notes and decisions:
  - T2 F1/F2/F3: the ineligible-candidate-document test uses a stub repository (as the existing ineligible-document test does), not an edited manifest; the escaping-path test asserts exit 2 and that no absolute path appears.
  - T2 F4 is a no-op here (the DECISIONS.md text belongs to T8b).
  - T3 F1: spies `DenseIndex.search`; the test index is built for `tenant-eval-x`, and every filter equals `build_access_filter(resolve_access(guest_access(...)))`.
  - T6 F1: the n=3 pass case asserts the float fact (`0.33333333333333337`) and the fail case the 61/180 drop.
  - T6 F5: the duplicate refusal is raised from `_build_run` (given the label) so it names BASE or CANDIDATE like other refusals.
  - Hard-coded counts: tests now read the live manifest and datasets through two small `conftest.py` helpers; `test_validate.py` no longer sets a literal case count. Counts in the frozen fixture, constants and the committed 1.0 file tests are unchanged.
  - T7 owner review: test-only assertion that the `g004`/`u001` row's `requires_review` contains `owner_review` (no data change).
- Deferred items: none.
- Usage: 165K tokens · 50 tool uses · 48:20

### Review
- Model: claude-opus-5-5 (intended tier BEST = Opus; matches; implementer was Sonnet, so a different model).
- Verdict: PASS
- Commands: `make verify` → exit 0 (ruff check, `ruff format --check` 123 files, pyright 0 errors, skills-check, `validate-knowledge` OK 0 problems, `validate-evaluation` OK 0 problems; pytest 609 passed, 1 skipped; Docker integration tests ran, local Qdrant already up); `make test-integration` → 20 passed, 590 deselected; `make eval-security` → PASS (68 queries: 5 security + 63 golden; 5 deferred; result under the ignored `experiments/results/tmp/`, `git check-ignore` confirms); `uv lock --check` → consistent (123 packages), `git diff uv.lock` = two added lines in the `way2australia-rag` entry (`referencing`, `>=0.35.0`; locked 0.37.0 unchanged); `make setup` was not re-run in the repository (it would reset the user's environment), the lock check stands in for the "second setup changes nothing" claim. `git diff --stat main -- retrieval/` → only `access.py`, `errors.py`, `goldens.py` (T1); `metrics.py`, `baseline.py`, `baseline_cli.py`, the legacy fixture folder, `legacy_baseline_snapshot.json`, `legacy_baseline_summary.txt` and `test_legacy_baseline_snapshot.py` unchanged against HEAD (4 snapshot tests pass). `git status --porcelain -- evaluation knowledge config experiments` → exactly ` M evaluation/candidates/006-candidates.jsonl` (plus the ignored `tmp/`); a field-level diff of that file shows only `cand006_ml_002` and `cand006_ml_003` changed, and only `rationale` and `proposed_case.query`. Live-count grep (`== ?(5|10|12|13|63|85)\b` and bare `13|63|85` in tests) → only `SMALL_SAMPLE_THRESHOLD == 10`, the UUID version `== 5`, `random_hit_rate(5, 13)` (synthetic), the committed 1.0 file and synthetic docs in `test_compare.py`, the frozen-fixture docstring and the `"85"` non-integer string. `test_local_repository.py` `SEED_IDS` is read from the live manifest. Reviewer's own scratch check (copy of the repository outside it, in the session scratchpad, fresh `.venv`): added `official_005_scratch_check` (file, manifest entry with sha256 and body_sha256) and active golden `g999` referencing it, `case_count` 85 → 86; `make validate-knowledge` OK, `make validate-evaluation` OK, `make test-unit` 589 passed, 1 skipped, 20 deselected; `pytest -m integration test_local_repository.py` 8 passed; copy deleted, repository `knowledge/` and `evaluation/` unchanged. `tests/fixtures/security/` holds exactly the two listed fixtures. `task-reviews.md` diff has no removed lines. No `w2a-realcheck-*` collection touched, Qdrant container not started or stopped.
- Box check: T2 F1 (`target_case_ids` restored to `g001`, asserts `options`, no `unknown case`), T2 F2 (empty `relevant_document_ids`, empty `evaluation_suite_id`), T2 F3 (ineligible candidate document reported as not eligible and not unknown; `../outside.jsonl` exit 2, no absolute path), T2 F4 (no code), T2 F5 (`referencing>=0.35.0`), T3 F1 (`W2A_TENANT_ID=tenant-eval-x`, spy on `DenseIndex.search`, every filter equals the resolved guest filter and carries the tenant), T4 F1 (docstring only), T5 F1 (keyword-only `document_id`, both raise sites, message text unchanged; regex and `import re` removed; quote-containing ID test fails with the old regex), T5 F4 (explicit tuple, hidden entries ignored, stray/missing refused before any copy, name only), T6 F1 (pass asserts `0.33333333333333337` and the epsilon; fail 61/180), T6 F3, T6 F5 (2.0 same and other version, 1.0; `not comparable:`, file name, `case_id`, `make eval-retrieval`, CLI exit 2), T7 owner review (test-only), T7 F1 (both queries name NAATI; flags and documents unchanged), T7 F3 (`case_count` from the manifest, no `suggested`), live counts, scratch check: all backed by the diff.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R11] The T5 F1 test (`test_violation_names_the_document_from_the_error_attribute`) asserts the `document_id` in `report.violations` only, not in the JSON from `security_document` or the printed `VIOLATION` line the box names, and it injects the unauthorized point by wrapping `check_hit` (rewriting `document_id` and `access_scope`) rather than through a store. Both outputs are built from the same violation dict, so the risk is low → optional: also render `security_document(...)` and the CLI summary lines and assert the `safe_text` ID appears in each.
  - F2 [MINOR, IMPLEMENTATION, R2] `test_candidate_ineligible_document_is_not_unknown` calls `validate_evaluation` with a stub repository and checks the problem texts; it does not assert the CLI exit code 1 the box names (non-empty problems map to exit 1 in the CLI) → optional: assert the problem count or run the CLI path.
- Summary for user (PASS only):
  - Changed: the deferred T2–T7 review items. `RetrievalAuthorizationError` now carries `document_id` (message text unchanged) and the security gate reads it instead of parsing the message; the security corpus builder copies only the two named fixtures, ignores hidden files and refuses anything else; `read_result` refuses repeated `case_id`s; `referencing` declared directly; two Malayalam candidate queries now name NAATI. Tests no longer assert today's document or case counts; they read the live manifest and suite.
  - Verified by: `make verify` (609 passed, 1 skipped), `make test-integration` (20 passed), `make eval-security` (PASS), `uv lock --check`, the protected-path and `retrieval/` scope checks, and the reviewer's own scratch copy with one extra document and golden (validators OK, 589 unit tests pass).
  - Worth your attention: two MINOR, optional test gaps (F1, F2). `make setup` was not re-run by the reviewer; `uv lock --check` confirms the lock is consistent.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/evaluation/security_corpus.py` → `_fixture_files`, `build_security_repository`: which fixture files the `make eval-security` corpus may contain.
    2. `packages/rag/src/way2australia_rag/retrieval/access.py` → `check_hit`, with `retrieval/errors.py` → `RetrievalAuthorizationError.document_id`: the fail-closed error now carries the hit's ID.
    3. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `run_security_evaluation` (the `except RetrievalAuthorizationError` branch): uses `error.document_id`.
    4. `packages/rag/src/way2australia_rag/evaluation/results.py` → `_build_run`: duplicate `case_id` refusal for `make eval-compare`.
    5. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation` docstring.
    6. `evaluation/candidates/006-candidates.jsonl`: rows `cand006_ml_002` and `cand006_ml_003`.
    7. `packages/rag/tests/conftest.py` → `live_suite_rows`, `manifest_document_count`: the live-count helpers.
    8. `packages/rag/tests/evaluation/test_security_eval.py`, `test_compare.py`, `test_validate.py`, `test_cli.py`: the new review tests.
    9. The remaining test edits (`test_suite_loader.py`, `test_status_handling.py`, `retrieval/test_baseline.py`, `test_goldens.py`, `ingestion/*`, `test_content_hash.py`, `test_eligibility.py`, `test_local_repository.py`, `test_manifest_validation.py`): literal counts replaced.
    10. Supporting edits: `packages/rag/pyproject.toml`, `uv.lock`, `tasks.md` T8a State and checkboxes.
- Usage: 141K tokens · 28 tool uses · 9:35

### User decision
- 2026-10-24 — approved. Verbatim: "Approved T8a. `make setup` confirmed: no changes ("Checked 80 packages"), so the referencing/uv.lock update is consistent. Add to T8b via a small planner amendment: F1: the T5 F1 test also asserts the violation JSON entry and the printed `VIOLATION` line name the document_id (inject the forbidden point through a store, not by wrapping check_hit). F2: the ineligible-candidate test asserts exit code 1. Then start T8b."
