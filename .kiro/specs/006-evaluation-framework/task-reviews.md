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
