# Spec 010 — task reviews

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; the intended tier is BEST_MINUS_ONE (`agent-skills/MODEL_PREFERENCES.md`), model-tier match not checked against the table.
- Files changed:
  - `evaluation/candidates/010-candidates.jsonl` (new: 21 candidates; each row gained `review` with decision, date and `promoted_as`);
  - `evaluation/schemas/evaluation_case_types.schema.json` (`candidate_row.proposed_case` is now a `oneOf` over `golden_answerable` and `unanswerable_refusal`, the latter with `query_language` required);
  - `evaluation/suites/public-eval-v3.json` (new, `case_count` 112), `evaluation/datasets/v3/{golden,unanswerable,security}_public.jsonl` (new: 87 goldens, 15 unanswerable, 10 security);
  - `evaluation/suites/public-eval-v2.json` (`status: replaced` only);
  - `packages/rag/src/way2australia_rag/evaluation/validate.py` (unanswerable promotion fields `query`, `expected_behavior`, `query_language`), `.../evaluation/cli.py` (`DEFAULT_SUITE` is v3);
  - tests: new `packages/rag/tests/evaluation/test_suite_v3.py`; changed `conftest.py` (`LIVE_SUITE` follows `cli.DEFAULT_SUITE`), `test_cli.py`, `test_security_eval.py`, `test_security_integration.py`, `test_status_handling.py`, `test_suite_loader.py` (follow `LIVE_SUITE`, datasets v3), `test_suite_v2.py` (v2 is `replaced`, default test moved, v2 refusal test added);
  - `.kiro/specs/010-multilingual-retrieval/tasks.md` (boxes, State), this file; `graphify-out/*` refreshed by `graphify update .`.
- User decision (2026-11-04), verbatim: "Approve both". Interpretation given by the coordinator: all 21 candidates approved as drafted (no corrections, no rejections) and the unanswerable-schema amendment approved. So `ml_002` keeps b005 + b002; `ml_006` keeps എഴുതാൻ; `mixed_003` keeps aazhcha; `mixed_005` is kept. No query was changed, so no correction was applied to any `proposed_case`.
- Promotion: goldens `g070`–`g079` (`ml_001`–`ml_010`), `g080`–`g087` (`mixed_001`–`mixed_008`), unanswerable `u013`–`u015` (`unans_001`–`unans_003`), in candidate-file order. Each review: `decision: approved`, `reviewed_on: 2026-11-04`, `reviewer_roles: [fluent_speaker_review, owner_review]`. v3 slices: `ml` 16, `mixed` 17, unanswerable `ml` 3.
- Verification run:
  - `make validate-evaluation` → OK, 0 problems (every suite);
  - `make verify` → pass: 1144 passed, 2 skipped; ruff, format and pyright clean;
  - `make eval-security` → PASS on all five paths, 87 golden queries (v3 default);
  - `git status --porcelain -- evaluation knowledge config` → only the allowed files: the candidates file, the schema, `public-eval-v2.json`, `public-eval-v3.json`, `datasets/v3/` (no `knowledge/` or `config/` change; `git diff main...HEAD` over those paths is empty because nothing is committed);
  - `graphify update .` run.
- Not run: `make test-integration` (not a T1 verification item).
- Notes:
  - Spec amendment during the round: R1 `proposed_case` bullet, a dated `## Change log` line and T1's schema box (user "Approve both").
  - Unanswerable v3 rows carry `query_language: ml` (v2 unanswerable rows have none); the promotion check needs it.
  - The v2 files are pinned by SHA-256 in `test_suite_v3.py` rather than read from git, so the tests run in a shallow clone.
  - `test_suite_v2.py` still holds the v2-specific checks; its v2 suite assertion now expects `replaced`.
  - Other tests that loaded the live suite follow `cli.DEFAULT_SUITE` and do not hard-code a count.
  - The legacy chillu note was optional: no query uses a legacy chillu sequence (no ZWJ U+200D).
- Usage: 116K tokens · 11 tool uses · 1:51 (candidate drafting) + 170K tokens · 25 tool uses · 6:10 (after the user's approval)

### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent; matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands: `make validate-evaluation` → OK, 0 problems; `make verify` → pass (1144 passed, 2 skipped; ruff, format check and pyright clean); `make eval-security` → PASS on all five paths for heading, structure and recursive (92 queries: 5 security, 87 golden; result under `experiments/results/tmp/`); `git status --porcelain -- evaluation knowledge config` → only the candidates file, the schema, `public-eval-v2.json`, `public-eval-v3.json` and `datasets/v3/` (`git diff --name-status main...HEAD` over those paths is empty because nothing is committed yet); `make test-integration` not run (not in T1's verification).
- Reviewer checks (scratch script, read-only): every v2 row of the three datasets equals its v3 copy except `evaluation_suite_id` (same key order; 69/12/10 rows, appended `g070`–`g087`, `u013`–`u015`); v2 dataset files equal `HEAD`; v2 manifest differs from `HEAD` only in `status`; each of the 21 promoted cases equals its candidate's `proposed_case` except `case_id`, `id` and `status`; slices `ml` 16, `mixed` 17, unanswerable `ml` 3; three romanized `mixed` queries (`mixed_001`–`003`); every `expected_facts` item is supported (verbatim or close paraphrase) by a listed document; no legacy chillu (no U+200D). Schema change is confined to `candidate_row.proposed_case`. Spec amendment: dated `## Change log` line, R1 bullet and the new T1 boxes match the change; design has no conflicting text.
- Findings:
  - F1 [MINOR, IMPLEMENTATION (approval record), R1] The user gate rests on a two-word decision, "Approve both", which the coordinator interpreted as: all 21 candidates approved as drafted (including the four reviewer choices the drafts left open: `ml_002` keeps both documents, `ml_006` keeps എഴുതാൻ, `mixed_003` keeps aazhcha, `mixed_005` kept) plus the schema amendment. The recorded `review.reviewer_roles` (`fluent_speaker_review`, `owner_review`) follow from that one decision. → The user confirms this interpretation when approving T1; no code change.
  - F2 [MINOR, IMPLEMENTATION, R1] `test_schema_still_accepts_the_spec_006_rows` asserts `errors(row) == [] or "candidate_id" not in row`; every 006 row has `candidate_id`, so the escape clause is dead and would silently hide a row without one. → Assert `errors(row) == []` directly (can be done in a later task's clean-up).
- Summary for user (PASS only):
  - Changed: new suite `public-eval-v3` (112 cases: every v2 row copied with only `evaluation_suite_id` changed, plus 10 `ml` goldens `g070`–`g079`, 8 `mixed` goldens `g080`–`g087`, 3 `ml` unanswerable `u013`–`u015`) from `evaluation/candidates/010-candidates.jsonl`; v2 manifest set to `replaced`; `candidate_row` schema accepts an unanswerable `proposed_case`; the promotion check compares unanswerable fields; `make eval-retrieval`/`eval-security` default to v3 and refuse v2.
  - Verified by: `make validate-evaluation`, `make verify` (1144 passed, 2 skipped), `make eval-security` (PASS, 87 goldens), reviewer's own row-by-row comparison of v2/v3, candidates and document facts.
  - Worth your attention: your "Approve both" was recorded as approving all 21 drafts unchanged, including the four open choices (`ml_002` two documents, `ml_006` എഴുതാൻ, `mixed_003` aazhcha, `mixed_005` kept) and the schema amendment; confirm that is what you meant. v3 unanswerable rows carry `query_language` (v2 ones do not). One dead clause in a schema test (F2).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `evaluation/candidates/010-candidates.jsonl`: the 21 drafts with `review.decision` and `promoted_as`.
    2. `evaluation/suites/public-eval-v3.json`: the new manifest (`case_count`, `replaces`, notes).
    3. `evaluation/datasets/v3/golden_public.jsonl` and `unanswerable_public.jsonl`: the appended rows at the end.
    4. `evaluation/suites/public-eval-v2.json`: `status: replaced` only.
    5. `evaluation/schemas/evaluation_case_types.schema.json` → `candidate_row.proposed_case`: the `oneOf`.
    6. `packages/rag/src/way2australia_rag/evaluation/validate.py` → `_promotion_problems`: unanswerable field set.
    7. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `DEFAULT_SUITE`: v3.
    8. `packages/rag/tests/evaluation/test_suite_v3.py`: copy, hash, manifest, promotion, slice, eligibility and schema tests.
    9. Supporting edits: `conftest.py` (`LIVE_SUITE` follows `DEFAULT_SUITE`), the other evaluation tests switched to `LIVE_SUITE`/v3 paths, `test_suite_v2.py` (v2 `replaced`, v2 refusal test), `requirements.md` change log and R1 bullet, `tasks.md` boxes.
- Usage: 130K tokens · 23 tool uses · 8:09

### User decision
- 2026-11-04: approved. Verbatim: "F1 confirmed: I approve all 21 drafts as drafted, including the four open choices (`ml_002` keeps both documents, `ml_006` keeps എഴുതാൻ, `mixed_003` keeps aazhcha, `mixed_005` kept). F2: fix it in this commit (remove the dead `or "candidate_id" not in row` clause), run the targeted test, no re-review needed. T1 approved. Commit with the `Spec-Task: 010/T1` trailer, then the graph commit, push, and dont start T2 yest."
- F2 fixed at commit: `test_schema_still_accepts_the_spec_006_rows` now asserts `errors(row) == []`; `pytest packages/rag/tests/evaluation/test_suite_v3.py` → 23 passed.

## T2 — round 1

### Implementation
- Model: Composer (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier match not verified against the table.
- Files changed:
  - New: `packages/rag/src/way2australia_rag/languages.py`, `.../retrieval/applicability.py`, `packages/rag/tests/retrieval/test_applicability.py`;
  - Core: `retrieval/{errors,base,models,retriever,bm25,hybrid,fallback,opening,cli}.py`, `lexical/{store,build}.py`, `evaluation/{slices,results,compare,retrieval_eval,cli}.py`, `evaluation/security_eval.py` (`_UnavailableDense.retrieve` keyword);
  - Tests: applicability suite plus updates to retrieval/evaluation/lexical/ingestion tests for `lote`, result 2.4, lexical 1.2 column, CLI `--lote`, and compare refusal; `graphify-out/*` refreshed.
- Verification run:
  - `make verify` → pass (1173 passed, 2 skipped; ruff, format, pyright clean);
  - `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1173 passed, 2 skipped);
  - `make test-integration` → 27 passed, 1146 deselected;
  - `make eval-security` → PASS (v3 default; gate unchanged for applicability until T4);
  - `git diff main...HEAD -- packages/rag/src/way2australia_rag/retrieval/access.py` → empty;
  - `graphify update .` run (twice: mid-round and after final test edits).
- Notes:
  - `evaluation/slices.active_registry_languages` delegates active product codes to `languages._active_product_support_codes`; registry path constant lives in `languages.py`.
  - Lexical builder writes settings 1.2 only; existing 1.1 files still open without `lote`; `has_lote_column` follows schema version.
  - Result schema bumped to 2.4 with top-level `lote`; readers treat older files as `lote: null`.
  - `test_fallback.test_fusion_and_hybrid_are_unchanged` now diffs `fusion.py` only (hybrid legitimately passes `lote`).
- Usage: not measured · 90 tool uses · 13:00

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: FAIL
- Commands: `make verify` → pass (1173 passed, 2 skipped; ruff, format check and pyright clean); `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1173 passed, 2 skipped); `make test-integration` → 27 passed, 1148 deselected; `make eval-security` → PASS on all five paths for heading, structure and recursive (92 queries: 5 security, 87 golden; result under `experiments/results/tmp/`); `git status --porcelain -- evaluation knowledge config` → empty; `git diff main...HEAD -- packages/rag/src/way2australia_rag/retrieval/access.py` → empty; `graphify update .` not re-run (read-only; `graphify-out/` already refreshed).
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R3/R4] The per-path tests do not match the T2 checkbox or the R3/R4 acceptance criteria. `test_non_applicable_first_hit_excluded` covers dense, standalone bm25, hybrid, and `FallbackRetriever` wrapping a succeeding hybrid — not fallback open (`primary is None`) and not fallback query (primary raises `RetrievalUnavailableError`). Dropped-filter injection (`test_dropped_filter_raises_language_applicability`) is dense-only; BM25 already has `DroppedClauseIndex` for access and it is not reused for lote. → Parametrize the non-applicable first-hit case over fallback open and fallback query; add a dropped-lote-clause store double for BM25 and run `check_applicable` through hybrid and both fallback wrappers as well.
  - F2 [MAJOR, IMPLEMENTATION, R3] Lexical `document_count` with a `lote` on settings 1.1 does not raise `LexicalIndexBindingError`. `BM25Retriever.retrieve` checks `has_lote_column` before SQL; `OpenedRetrieval.document_count` for bm25 and fallback-open (`opening.py` `lexical_count`) concatenates the lote clause and queries immediately. A real 1.1 file (no column) surfaces `sqlite3.OperationalError` on `make eval-retrieval --lote … --strategy bm25`, mapped to a class-name-only exit 2, not the `make index-lexical` advice in the error table. → Mirror the `has_lote_column` refusal in lexical `document_count` (and test it on a file that actually lacks the column, not only a 1.2 file with settings rewritten to 1.1).
  - F3 [MINOR, IMPLEMENTATION, R3] Store parity queries the active code and no `lote`, but not the second code required by the T2 store-parity box. → Query with `ResolvedLote(code=other)` as well and assert both stores return the same set (`star`/`both`/`other`).
  - F4 [MINOR, IMPLEMENTATION, R2/R7] Result 2.4 writes top-level `lote`, but tests never assert `doc["lote"]` on a default eval run; `make eval-retrieval --lote` refusal before opening is untested (retrieve CLI covers `--lote en` only); older files reading `lote` as `None` is only implicit. → Assert the 2.4 `lote` key (null and a code); add an eval-CLI invalid `--lote` before-open case; pin `read_result` on a 2.3 file to `info["lote"] is None`.
- Usage: not measured · 92 tool uses · 15:00

## T2 — round 2

### Implementation
- Model: Composer (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier match not verified against the table.
- Files changed:
  - `packages/rag/src/way2australia_rag/retrieval/opening.py`: `_lexical_document_count` mirrors BM25 `has_lote_column` refusal before SQL for bm25 and fallback-open `document_count`;
  - `packages/rag/tests/retrieval/test_applicability.py`: store parity with second active code; non-applicable first-hit over `fallback_open` and `fallback_query`; `DroppedLoteClauseLexical` + parametrized injection through bm25, hybrid and both fallback wrappers; lexical 1.1 `document_count` + lote test;
  - `packages/rag/tests/evaluation/test_cli.py`, `test_retrieval_eval.py`, `test_strategy_eval.py`: eval `--lote` refusal before open, result 2.4 `lote` null/code, committed 2.3 reads `lote` as null;
  - `.kiro/specs/010-multilingual-retrieval/tasks.md` (State), this file; `graphify-out/*` refreshed.
- Verification run:
  - `make verify` → pass (1182 passed, 2 skipped; ruff, format, pyright clean);
  - `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1182 passed, 2 skipped);
  - `make test-integration` → 27 passed, 1157 deselected;
  - `make eval-security` → PASS (v3 default);
  - `git diff main...HEAD -- packages/rag/src/way2australia_rag/retrieval/access.py` → empty;
  - `graphify update .` run.
- Notes:
  - Round 2 scope only: task-reviews.md T2 round 1 findings F1–F4; no new product behavior beyond F2 opening fix.
  - `_lexical_document_count` is exercised directly for 1.1 settings (same binding rule as `BM25Retriever.retrieve`).
- Usage: 85K tokens · 32 tool uses · 3:30

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands: `make verify` → pass (1182 passed, 2 skipped; ruff, format check and pyright clean); `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1182 passed, 2 skipped); `make test-integration` → 27 passed, 1157 deselected; `make eval-security` → PASS on all five paths for heading, structure and recursive (92 queries: 5 security, 87 golden; result under `experiments/results/tmp/`); `git status --porcelain -- evaluation knowledge config` → empty; `git diff main...HEAD -- packages/rag/src/way2australia_rag/retrieval/access.py` → empty; `graphify update .` not re-run (read-only; `graphify-out/` already refreshed).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R3] `DenseRetriever`'s module docstring still says there is "no language filter or language-specific code" after `retrieve` gained `lote` and `check_applicable`. → Update the docstring (T6 can catch this).
- Summary for user (PASS only):
  - Changed: every retrieval path now takes an optional `lote` (validated against the language registry, never `en`/`*`/unknown). With a `lote`, Qdrant and SQLite filter to applicable chunks inside the query, then `check_applicable` re-checks each hit. Lexical files gain a `lote_languages` column (settings 1.2); a 1.1 file still serves without `--lote` and is refused with one (`make index-lexical` advice). `make retrieve` / `make eval-retrieval` take `--lote`; results are 2.4 with top-level `lote`; `eval-compare` refuses a `lote` mismatch. Round 2 closed F1–F4: fallback-open/query and BM25 lote-injection tests; lexical `document_count` refuses `--lote` on settings 1.1; store parity queries the second code; result/CLI `lote` keys are asserted.
  - Verified by: `make verify` (also hub-free), `make test-integration`, `make eval-security` (v3, gate unchanged until T4).
  - Worth your attention: result 2.4 records `lote` now; the script-mix slice is T3. `CURRENT_STATE.md` still describes T2 round 1 FAIL as the next step. One stale dense-retriever docstring (F1).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/cli.py` → `main`: `--lote`, `resolve_lote` before open, prints `lote: <code|none>`.
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval`: `--lote`, `document_count(access, lote)`, result 2.4.
    3. `packages/rag/src/way2australia_rag/languages.py` → `active_lote_codes`: registry codes without `en`.
    4. `packages/rag/src/way2australia_rag/retrieval/applicability.py` → `resolve_lote`, `dense_query_filter`, `sql_access_with_lote`, `check_applicable`.
    5. `packages/rag/src/way2australia_rag/retrieval/retriever.py` → `DenseRetriever.retrieve`: combined filter, then `check_hit`, then `check_applicable`.
    6. `packages/rag/src/way2australia_rag/retrieval/bm25.py` → `BM25Retriever.retrieve`: 1.1 `has_lote_column` refusal, SQL lote clause, re-check.
    7. `packages/rag/src/way2australia_rag/retrieval/hybrid.py` / `fallback.py`: `lote` on every leg and both fallback paths.
    8. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `_lexical_document_count`: same 1.1 refusal for bm25 and fallback-open counts.
    9. `packages/rag/src/way2australia_rag/lexical/{store,build}.py`: settings 1.2 column; builder refuses `["*", code]`.
    10. Supporting edits: `errors.py` (`LanguageApplicabilityError`), `models.py` / `results.py` / `compare.py`, `tests/retrieval/test_applicability.py` and the CLI/eval/compare additions.
- Usage: 185K tokens · 82 tool uses · 18:20

### User decision
- 2026-11-04: approved. Verbatim: "T2 approved. Fix the stale `DenseRetriever` docstring in this commit (one line, no re-review). Commit with `Spec-Task: 010/T2`, graph commit, push, start T3." DenseRetriever module docstring updated in the T2 commit; no re-review.
