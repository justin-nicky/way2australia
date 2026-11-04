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

## T3 — round 1

### Implementation
- Model: Composer (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier match not verified against the table.
- Files changed:
  - New: `packages/rag/src/way2australia_rag/lexical/equivalents.py`, `.../evaluation/{script_mix,continuity}.py`; tests `test_script_mix.py`, `test_continuity.py`; fixtures `packages/rag/tests/evaluation/fixtures/continuity_{base,candidate_equal}.json`;
  - Lexical/retrieval: `lexical/{tokenizer,store,build,cli}.py`, `retrieval/{bm25,strategy}.py`, `config/retrieval.yaml` (schema 1.2, default `lexical-v1`);
  - Evaluation: `evaluation/{compare,cli}.py`, `retrieval_eval.py`; `Makefile` (`eval-continuity`); `.gitignore` (`/.local/`);
  - Tests: tokenizer v2/chillu pins, cross-tokenizer compare, applicability over both tokenizers, lexical CLI/build/strategy, strategy_eval 2.4 metrics; `graphify-out/*` refreshed.
- Unicode chillu table: verified against The Unicode Standard v16.0, Malayalam chillu subsection (2026-11-04); six ZWJ legacy pairs only; U+0D54–U+0D56 omitted (no legacy ZWJ sequences in that table).
- Verification run:
  - `make verify` → pass (1224 passed, 2 skipped; ruff, format, pyright clean);
  - `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1224 passed, 2 skipped);
  - `make test-integration` → 27 passed, 1199 deselected;
  - `make eval-security` → PASS (v3 default);
  - `make index-lexical` with `QDRANT_COLLECTION_BASE=w2a-t010-<hex>`, `--embedder fake`, separate `W2A_LEXICAL_INDEX_DIR` for v1 and v2 → settings 1.2, tokenizers `lexical-v1` / `lexical-v2`, same digest; dirs removed after;
  - `make eval-continuity` on committed fixtures → exit 0 (suite/lote/git lines only);
  - `graphify update .` run.
- Notes:
  - `COMMANDS.md` entry for `make eval-continuity` deferred to T6 as specified.
  - BM25 authorization spy doubles gained a `tokenizer` delegate; dropped-lote applicability tests parametrized over both tokenizers (all gated factories).
  - `eval-compare` `--cross-tokenizer` can combine with `--cross-index`; digest and chunk_count mismatches still refuse.
- Usage: ~180K tokens · 85 tool uses · 15:00
- Process (P3): `transcript_metrics.py` on subagent `0b2436c2…` → **`make verify` 12 runs (11 before last code edit)** — verify-budget hook would have blocked after the second run.

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: FAIL
- Commands: `make verify` → pass (1224 passed, 2 skipped; ruff, format check and pyright clean); `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1224 passed, 2 skipped); `make test-integration` → 27 passed, 1199 deselected; `make eval-security` → PASS on all five paths for heading, structure and recursive (92 queries: 5 security, 87 golden; result under `experiments/results/tmp/`); `make index-lexical` with `QDRANT_COLLECTION_BASE=w2a-t010-ec7eff86`, `--embedder fake`, throwaway `W2A_LEXICAL_INDEX_DIR` under `.local/` once per tokenizer → settings 1.2, `lexical-v1 v1` / `lexical-v2 v2`, same digest `1438a2e947e3`, 45 chunks; dirs deleted afterwards; `make eval-continuity` on committed fixtures → exit 0; on a flipped-hit copy the Python module exits 1 (`make` itself exits 2); `git status --porcelain -- evaluation knowledge config` → only `config/retrieval.yaml` (allowed); `graphify update .` not re-run (read-only; `graphify-out/` already refreshed). Unicode chillu pairs: code points match The Unicode Standard v16.0 Malayalam chillu table (six ZWJ legacy sequences; U+0D54–U+0D56 omitted).
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R8] `_identity_problems` always refuses a lexical `source_chunk_digest` or `chunk_count` mismatch, including when `cross_index=True`. D069 says chunk digest is not compared across indexes; Spec 009 `--cross-index` (idx-v1 vs idx-v2) would now exit 2. → Skip digest/chunk_count when `cross_index` is set; still require them for `--cross-tokenizer` without `--cross-index`. Test `--cross-index` allowing a digest/chunk_count difference, and `--cross-tokenizer` still refusing one.
  - F2 [MAJOR, IMPLEMENTATION, R7] Script-mix tests do not match the T3 box or R7. `test_every_v3_query_letter_matches_script_fixture` never calls `script_mix`, checks only the five characters in `SCRIPT_FIXTURE`, and skips every other letter. Virama and vowel signs inside a Malayalam word are not pinned. → For every letter in every v3 query, assert the name prefix equals a committed Unicode `Script` fixture (fail on unmapped letters); pin a virama and a vowel sign as adding no script.
  - F3 [MAJOR, IMPLEMENTATION, R5] Required tokenizer tests are missing: a file is never queried with its own tokenizer (no case that would fail if BM25 used the module-level `lexical-v1` alias); BM25 authorization tests are not parametrized over both tokenizers (only `test_dropped_lote_clause_raises_language_applicability` is). → Add a v2-file query that only matches after chillu replacement; parametrize the BM25 authorization tests over `lexical-v1` and `lexical-v2`.
  - F4 [MINOR, IMPLEMENTATION, R5] `equivalents.py` comments swap NA/NNA on the first two rows (code points are correct). The header names U+0D54–U+0D56 as “CHILLU RR / L / LL” (those are U+0D7C–U+0D7E); the omitted letters are CHILLU M / Y / LLL. → Fix the comments.
  - F5 [MINOR, IMPLEMENTATION, R10] GNU make maps a recipe exit 1 to make exit 2, so `make eval-continuity` cannot surface “cases differ” as exit 1 (same pattern as `eval-compare`). The Python module itself exits 1. → T6 docs should tell operators to read the printed lines, or to invoke the module directly when they need the 0/1/2 split.
- Usage: (orchestrator)

## T3 — round 2

### Implementation
- Model: Composer (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier match not verified against the table.
- Round 2 scope: task-reviews.md T3 round 1 findings F1–F5 only.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/compare.py` — skip lexical digest/chunk_count in `_identity_problems` when `--cross-index`;
  - `packages/rag/src/way2australia_rag/lexical/equivalents.py` — chillu header comment (U+0D54–U+0D56);
  - `Makefile` — `eval-continuity` prints `eval-continuity: exit N` on stderr when the module exits non-zero;
  - Tests: `test_compare.py` (cross-index digest/chunk_count pass), `test_script_mix.py` (full v3 letter fixture, `script_mix` per query, virama/vowel pins), `test_bm25.py` (v2 chillu query via index tokenizer; auth tests over both tokenizers), `test_continuity.py` (make status line);
  - `graphify-out/*` refreshed.
- Verification run:
  - `make verify` → pass (1237 passed, 2 skipped; ruff, format, pyright clean);
  - `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1237 passed, 2 skipped);
  - `make test-integration` → 27 passed, 1212 deselected;
  - `make eval-security` → PASS;
  - `make eval-continuity` on committed fixtures → exit 0; on flipped-hit copy → Python exit 1, stderr `eval-continuity: exit 1`, GNU make exit 2;
  - `make index-lexical` not re-run (round 2 changed no lexical build behaviour; round 1 run still valid).
- Notes:
  - F4 NA/NNA row comments already matched code points; only the U+0D54–U+0D56 header was wrong.
  - F5: GNU make still returns 2 when the module exits 1; the recipe line makes the Python exit code observable on stderr.
- Usage: not measured · ~60 tool uses · ~12:00

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands: `make verify` → pass (1237 passed, 2 skipped; ruff, format check and pyright clean); `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1237 passed, 2 skipped); `make test-integration` → 27 passed, 1212 deselected; `make eval-security` → PASS on all five paths for heading, structure and recursive (92 queries: 5 security, 87 golden; result under `experiments/results/tmp/`); `make index-lexical` with `QDRANT_COLLECTION_BASE=w2a-t010-d23acbcd`, `--embedder fake`, throwaway `W2A_LEXICAL_INDEX_DIR` under `.local/` once per tokenizer → settings 1.2, `lexical-v1 v1` / `lexical-v2 v2`, same digest `1438a2e947e3`, 45 chunks; dirs deleted afterwards; `make eval-continuity` on committed fixtures → exit 0; on a flipped-hit copy → Python exit 1, stderr `eval-continuity: exit 1`, GNU make exit 2; `git status --porcelain -- evaluation knowledge config` → only `config/retrieval.yaml` (allowed); `graphify update .` not re-run (read-only; `graphify-out/` already refreshed). Unicode chillu pairs: code points match The Unicode Standard v16.0 Malayalam chillu table (six ZWJ legacy sequences; U+0D54–U+0D56 omitted). Round 1 F1–F3 closed; F4 header closed; F4 row comments and F5 make-exit remain MINOR.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R5] `equivalents.py` row comments still swap NA/NNA: U+0D23 is NNA → CHILLU NN (U+0D7A) but the comment says NA → CHILLU N; U+0D28 is NA → CHILLU N (U+0D7B) but the comment says NNA → CHILLU NN. Code points are correct. The U+0D54–U+0D56 header is now CHILLU M / Y / LLL. → Fix the two row comments (T6 can catch this).
  - F2 [MINOR, IMPLEMENTATION, R10] GNU make still maps a recipe exit 1 to make exit 2; the new stderr line `eval-continuity: exit 1` makes the Python code visible. → T6 docs should tell operators to read that line, or to invoke the module directly, when they need the 0/1/2 split.
  - F3 [MINOR, IMPLEMENTATION, R5] `BM25Retriever`'s module docstring still says the query is tokenized with `lexical-v1` after retrieve started using `self._lexical.tokenizer.query_terms`. → Update the docstring (T6 can catch this).
- Summary for user (PASS only):
  - Changed: `lexical-v2` (NFC, then generic chillu-sequence replacement, then v1 steps) sits beside unchanged `lexical-v1`. BM25 always queries with the tokenizer recorded in the file. `config/retrieval.yaml` is schema 1.2 with default `lexical.tokenizer: lexical-v1`. Result 2.4 gains a `by_script_mix` slice (romanized Malayalam counts as `latin`). `eval-compare --cross-tokenizer` allows a tokenizer change when digest and chunk count match; `--cross-index` again skips digest/chunk_count (round-1 F1). `make eval-continuity` compares shared goldens without refusing suite/`lote`/case-set differences. Round 2 closed F1–F3: script-mix letter fixture calls `script_mix` and fails on unmapped golden letters; BM25 auth tests run on both tokenizers; a v2 file is queried with its own tokenizer.
  - Verified by: `make verify` (also hub-free), `make test-integration`, `make eval-security` (v3, gate unchanged until T4), throwaway `make index-lexical` per tokenizer, `make eval-continuity` on fixtures.
  - Worth your attention: default tokenizer stays `lexical-v1` until T5. `CURRENT_STATE.md` still says T3 round 2 is implementing. Remaining MINORs: swapped NA/NNA comments (code is right), `make eval-continuity` exits 2 when cases differ, stale BM25 docstring. T6 should document the make exit mapping.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/lexical/cli.py` → `main`: `--tokenizer` (else config default), prints settings 1.2 and tokenizer.
    2. `packages/rag/src/way2australia_rag/lexical/tokenizer.py` → `TOKENIZERS` / `_tokenize_v2`: NFC, `replace_sequences`, then v1 steps; module-level `tokenize` stays v1.
    3. `packages/rag/src/way2australia_rag/lexical/equivalents.py` → `SEQUENCE_EQUIVALENTS`: six Unicode chillu pairs (code points only).
    4. `packages/rag/src/way2australia_rag/lexical/store.py` → `LexicalIndex.tokenizer`: the file's recorded tokenizer; unknown names refused with rebuild advice.
    5. `packages/rag/src/way2australia_rag/retrieval/bm25.py` → `BM25Retriever.retrieve`: `self._lexical.tokenizer.query_terms`.
    6. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `RetrievalConfig` / `LexicalConfig`: schema 1.2; 1.1 files read as `lexical-v1`.
    7. `packages/rag/src/way2australia_rag/evaluation/script_mix.py` → `script_mix`; `retrieval_eval.py` writes `metrics.by_script_mix` and per-case `script_mix`.
    8. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `_identity_problems`: `--cross-tokenizer` relaxes name/version; digest/chunk_count skipped only with `--cross-index`.
    9. `packages/rag/src/way2australia_rag/evaluation/continuity.py` → `compare_continuity`; `Makefile` `eval-continuity`.
    10. Supporting edits: `.gitignore` `/.local/`, `config/retrieval.yaml`, tests (`test_bm25.py`, `test_script_mix.py`, `test_compare.py`, `test_continuity.py`, tokenizer/CLI/strategy).
- Usage: 190K tokens · 78 tool uses · 28:00

### User decision
- 2026-11-04: approved. Verbatim: "T3 approved. Before committing, fix the three MINORs in this commit (no re-review needed): …" Chillu row comments, BM25 module docstring, and T5 continuity command via `uv run python -m way2australia_rag.evaluation.continuity` with module exit code recorded (`COMMANDS.md` in T6). One graph commit per task from now on; do not rewrite pushed T2 graph commits.

## T4 — round 1

### Implementation
- Model: Composer (Cursor subagent); intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md` — tier match not verified against the table.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/security_index.py` (non-applicable `zz` rows, `staff_scope_lote`, `require_non_applicable_lote_inactive`, `active_lote_code` on build);
  - `packages/rag/src/way2australia_rag/evaluation/security_eval.py` (dual `lote` modes, access-only sanity checks, split auth/applicability violations, result 1.4);
  - `packages/rag/src/way2australia_rag/evaluation/cli.py` (`eval-security` resolves active `lote`, summary lines);
  - `packages/rag/tests/evaluation/test_security_eval.py`, `test_security_integration.py` (1.4 coverage, both modes, Docker non-applicable exclusion);
  - `packages/rag/src/way2australia_rag/retrieval/bm25.py` (module docstring line wrap only — unblocks ruff on this branch);
  - `.kiro/specs/010-multilingual-retrieval/tasks.md`, this file; `graphify-out/*` refreshed.
- Verification run:
  - `make verify` → pass (1256 passed, 2 skipped; ruff, format, pyright clean);
  - `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1256 passed, 2 skipped);
  - `make test-integration` → 27 passed, 1231 deselected;
  - `make eval-security` → PASS; `lote modes: none, ml`; three chunkers × five paths × both modes; 92 queries (5 security, 87 golden); result under `experiments/results/tmp/security-evaluation-20261104T094431Z.json`;
  - `graphify update .` run.
- Notes:
  - Non-applicable rows share the query dense vector with forbidden probes but use weaker lexical probe text (`repeats=2`) so unfiltered sanity still finds a forbidden winner among tied scores; access-only sanity requires non-applicable first under the access filter alone.
  - `check_hit` still runs before applicability; dual violations count as authorization.
  - Legacy 1.3 result shape remains readable in tests via an inline fixture; new writes use schema 1.4.
- Usage: not measured · 48 tool uses · 7:00
- Process (P3): `transcript_metrics.py` on subagent `7855b276…` → **`make verify` 8 runs (7 before last code edit)**.

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands: `make verify` → pass (1256 passed, 2 skipped; ruff, format check and pyright clean); `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1 make verify` → pass (1256 passed, 2 skipped); `make test-integration` → 27 passed, 1231 deselected; `make eval-security` → PASS on all five paths for heading, structure and recursive, both lote modes (`lote modes: none, ml`; 92 queries: 5 security, 87 golden; result `experiments/results/tmp/security-evaluation-20261104T095357Z.json`); `git status --porcelain -- evaluation knowledge config` → empty; `graphify update .` not re-run (read-only; `graphify-out/` already refreshed).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R9] `test_each_forbidden_row_type_is_in_the_lexical_file` still parametrizes only `staff_scope`, `other_tenant` and `owned`; the new `staff_scope_lote` variant is covered by `points_per_variant` equality and the bypassed-`check_hit` variants set, not this lexical-id list. → Add `staff_scope_lote` to the parametrize (T6 can catch this).
  - F2 [MINOR, IMPLEMENTATION, R9] `test_security_integration.py` module docstring still describes only forbidden-point isolation; the Docker test now also asserts non-applicable exclusion with a `lote`. → Update the docstring (T6 can catch this).
- Summary for user (PASS only):
  - Changed: `make eval-security` now gates two lote modes (`none` and the active registry code, `ml`) on all five paths and three chunkers. The throwaway corpus adds public eligible `lote_languages: ["zz"]` rows (nearest under the access filter) and a `staff_scope_lote` forbidden variant (`lote_languages: [ml]`). Result schema is 1.4 with `lote_modes`, split authorization/applicability violation lists, and `non_applicable_rows_per_variant`. `zz` as an active code is a harness error (exit 2). Authorization still runs first; a dual failure counts as authorization.
  - Verified by: `make verify` (also hub-free), `make test-integration`, `make eval-security` (v3, both modes, five paths, three chunkers).
  - Worth your attention: non-applicable lexical probes use 2 term repeats vs forbidden 3, so the unfiltered BM25 sanity still finds a forbidden winner; access-only sanity requires the `zz` row first. Protected paths (`evaluation/`, `knowledge/`, `config/`) were not touched. Default tokenizer stays `lexical-v1` until T5. Two MINORs for T6 (parametrize `staff_scope_lote`; Docker test docstring).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_security`: registry `lote`, `zz` guard, `lote_modes` on the 1.4 document, AUTH/APPLIC summary lines.
    2. `packages/rag/src/way2australia_rag/evaluation/security_index.py` → `build_security_index`: `zz` rows, `staff_scope_lote`, `require_non_applicable_lote_inactive`.
    3. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `run_security_evaluation`: per query, unfiltered sanity then access-only sanity, then `_gate` twice (`lote=None` and active code).
    4. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `_gate`: `RetrievalAuthorizationError` vs `LanguageApplicabilityError`; returned forbidden vs non-applicable hits; `passed` needs zero of both.
    5. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `security_document` / `security_run_record`: schema 1.4 keys; `violations` remains the concatenated 1.3 list.
    6. Supporting edits: `bm25.py` docstring wrap (ruff); `test_security_eval.py` and `test_security_integration.py`.
- Usage: not measured · 78 tool uses · (reviewer)

### User decision
- 2026-11-04: approved. Verbatim: "T4 approved. Fix both MINORs in this commit …" Parametrize `staff_scope_lote` in `test_each_forbidden_row_type_is_in_the_lexical_file`; update Docker integration module docstring. No re-review. User stops this orchestrator session; T5 in a fresh session.

## T5 — round 1

### Implementation (user-owned runs + agent wrap-up)
- Model: orchestrator session (Composer); user ran real evals; agent recorded and applied promotion config.
- Lexical rebuilds (2026-11-04, `QDRANT_COLLECTION_BASE=w2a-realcheck`, settings **1.2**):
  - `.local/lexical`: `lexical-v1` v1, **34** chunks, digest `89b30b429b43e689ec41dc4525762f0e217d35b65188d470d3da28e0a677518c`.
  - `.local/lexical-v2`: `lexical-v2` v2, **34** chunks, same digest.
- Pre-run: `git status --porcelain` empty after both lexical builds (before eval arms).
- Four arms (`public-eval-v3`, `lote: ml`, `w2a-realcheck-idx-v2`, `idx-v2`, BGE-M3 @ `5617a9f`, `mps:0`, `top_k` 5, 13 documents, `git_dirty: false`, empty `fallback_counts` on all files):

| Arm | Strategy | Lexical | Result file |
|-----|----------|---------|-------------|
| A | hybrid | lexical-v1 | `experiments/results/retrieval-evaluation-idx-v2-20261104T105123Z.json` |
| B | bm25 | lexical-v1 | `experiments/results/retrieval-evaluation-idx-v2-20261104T105259Z.json` |
| C | hybrid | lexical-v2 | `experiments/results/retrieval-evaluation-idx-v2-20261104T105300Z.json` |
| D | bm25 | lexical-v2 | `experiments/results/retrieval-evaluation-idx-v2-20261104T105321Z.json` |

**Arm A — hybrid lexical-v1**
- Overall (n=87): HitRate@5 **0.9885**, MRR **0.9228** (miss: `g026`).
- `en` (n=54): HitRate@5 0.9815, MRR 0.9321.
- `ml` (n=16): HitRate@5 1.0000, MRR 0.9531.
- `mixed` (n=17): HitRate@5 1.0000, MRR 0.8647.
- `by_script_mix`: `latin` (n=58) 0.9828 / 0.9282; `latin+malayalam` (n=19) 1.0000 / 0.8658; `malayalam` (n=10) 1.0000 / 1.0000.
- Cross-tokenizer flips vs Arm C: **none**.
- Watch ranks (first relevant doc rank): g056 **2** (rr 0.5); g057 **2** (0.5); g061 **5** (0.2); g067 **1** (1.0); g068 **1** (1.0); g069 **1** (1.0).

**Arm B — bm25 lexical-v1**
- Overall: HitRate@5 **0.8391**, MRR **0.7423** (14 misses: `g026`, `g029`, `g061`, `g067`–`g075`, `g076`, `g078`).
- `en` (n=54): 0.9630 / 0.8472.
- `ml` (n=16): **0.3125 / 0.2396** (carry-over for T6 / retrospective: fallback path serves Malayalam users poorly until transliteration exists).
- `mixed` (n=17): 0.9412 / 0.8824.
- `by_script_mix`: `latin` 0.9655 / 0.8578; `latin+malayalam` 0.8947 / 0.7807; **`malayalam` 0.0000 / 0.0000** (n=10).
- Flips vs Arm D: **none**.
- Watch ranks: g056 **2**; g057 **2**; g061 **miss**; g067–g069 **miss**.

**Arm C — hybrid lexical-v2** (promoted v3 hybrid reference)
- Same numbers as Arm A on every slice and watch case (identical case-by-case).

**Arm D — bm25 lexical-v2** (promoted v3 bm25 reference)
- Same numbers as Arm B on every slice and watch case.

**Honest interpretation (for T6 `DECISIONS.md` D072+):** `eval-compare --cross-tokenizer` is a perfect tie (hybrid hits 86→86, MRR 0.9228→0.9228; bm25 hits 73→73, MRR 0.7423→0.7423; zero hit flips). Metrics match case-by-case because **no indexed document or evaluation query contains a legacy Malayalam chillu ZWJ sequence**; `lexical-v2` differs only on those sequences. Promotion under the pre-registered R10 rule (tie promotes) is a **correctness default** exercised by unit tests on chillu pairs, **not** a measured retrieval gain on this corpus.

**Continuity** (Spec 009 hybrid ref `experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json` → Arm A):

```
suite: public-eval-v2 -> public-eval-v3
suite version: 2 -> 3
lote: none -> ml
git_commit: '9d1c12c37daa9cfc672b539acbff567189c56577' -> 'f2d2e20f7f2deeeebba001233f90d88f926d5fe8'
shared goldens: 69
only in CANDIDATE: g070 v1, g071 v1, g072 v1, g073 v1, g074 v1, g075 v1, g076 v1, g077 v1, g078 v1, g079 v1, g080 v1, g081 v1, g082 v1, g083 v1, g084 v1, g085 v1, g086 v1, g087 v1
continuity: no shared-case differences
```

Module exit code: **0** (`python3 -m uv run python -m way2australia_rag.evaluation.continuity …`; not `make eval-continuity`).

**Compare hybrid** (A vs C): `eval-compare: PASS (hits 86 -> 86, MRR 0.9228 -> 0.9228)`; `cross-tokenizer: lexical-v1 v1 -> lexical-v2 v2`.

**Compare bm25** (B vs D): `eval-compare: PASS (hits 73 -> 73, MRR 0.7423 -> 0.7423)`; same cross-tokenizer line.

**Promotion (2026-11-04):** User decision — promote `lexical-v2` (pre-registered rule; tie promotes). Agent set `config/retrieval.yaml` → `lexical.tokenizer: lexical-v2`. Operator rebuilds and smoke test before task commit (commands in orchestrator handoff). No Qdrant change; no new `index_version`.

**File checks (all four arms):** suite `public-eval-v3` v3; `embedder_is_fake: false`; `git_dirty: false`; collection `w2a-realcheck-idx-v2`; `index_version` idx-v2; recursive chunker; embedder pair BGE-M3 @ `5617a9f`; `top_k` 5; document/chunk counts 13 / 34; `lote: ml`; served strategy matches requested; `fallback_counts` {}; tokenizer matches arm.

**Files pending commit:** four result JSONs; `config/retrieval.yaml`; spec task/review docs; `CURRENT_STATE.md`; test promotion pins (`test_strategy.py`, `test_lexical_cli.py`, `test_strategy_eval.py`); ruff fix on `test_security_integration.py` module docstring. Separate graph commit after task commit.

**Post-review fixes (same round, after FAIL F1/F2):** Committed-config and CLI summary pins → `lexical-v2`; eval lexical builders use `TOKENIZERS[RETRIEVAL_CONFIG.lexical.tokenizer]`; E501 docstring wrap. `make verify` → pass (1257 passed, 2 skipped; ruff, format, pyright clean) with `QDRANT_COLLECTION_BASE` unset.

**Operator rebuild/smoke (2026-11-04, post-approval):** Realcheck and production `make index-lexical` both printed settings 1.2, `lexical-v2 v2`, 34 chunks, digest `89b30b429b43`. `make retrieve QUERY="NAATI CCL coaching" RETRIEVE_ARGS="--lote ml"` served hybrid from `way2australia-idx-v2` (5 hits). `make setup` OK.

**Recorded deviation (user-accepted 2026-11-04):** `make retrieve` does not print the lexical tokenizer name, so the smoke test only shows that the hybrid path served from the rebuilt `way2australia-idx-v2` file. Evidence that the promotion is live: the `make index-lexical` output for both files (settings 1.2, `lexical-v2 v2`, 34 chunks, digest `89b30b429b43`).

**Carry-over for T6 and the retrospective (roadmap item 10 — grounded generation / HTTP route spec):** `open_retrieval` does not compare the lexical file's recorded tokenizer with `config/retrieval.yaml` `lexical.tokenizer`, so a stale `lexical-v1` file would keep serving silently. Group with the existing startup policy item for a missing or stale lexical file (Spec 008 hand-off / `CURRENT_STATE.md` Known issues).

- Usage: not measured (user-owned eval runs)

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: FAIL (superseded — F1/F2 fixed; re-review pending)
- Commands: `python3 -m uv run python -m way2australia_rag.evaluation.continuity experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json experiments/results/retrieval-evaluation-idx-v2-20261104T105123Z.json` → exit 0 (shared goldens 69, no shared-case differences); `make eval-compare BASE=…105123Z.json CANDIDATE=…105300Z.json COMPARE_ARGS=--cross-tokenizer` → PASS (hits 86 → 86, MRR 0.9228 → 0.9228); `make eval-compare BASE=…105259Z.json CANDIDATE=…105321Z.json COMPARE_ARGS=--cross-tokenizer` → PASS (hits 73 → 73, MRR 0.7423 → 0.7423); `git diff --name-status main...HEAD -- evaluation knowledge config` → T1 evaluation files + T3 `config/retrieval.yaml` (working tree adds only the T5 tokenizer promotion; `knowledge/` empty); `make verify` → fail (ruff E501, pytest not reached); targeted pytest of the committed-default pins → 2 failed, 1 passed; `make test-integration` not run (not in T5 verification).
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R10] Promotion set `config/retrieval.yaml` to `lexical.tokenizer: lexical-v2`, but tests still pin the committed default as `lexical-v1`: `test_committed_config_loads` (`packages/rag/tests/retrieval/test_strategy.py:58`) and `test_success_summary_and_digest_stability` (`packages/rag/tests/lexical/test_lexical_cli.py:67`, implicit `make index-lexical` with no `--tokenizer`). Confirmed: assert `'lexical-v2' == 'lexical-v1'`; CLI summary now prints `tokenizer lexical-v2 v2`. → Update those two pins to v2 so T5's required `make verify` after promotion can pass.
  - F2 [MAJOR, IMPLEMENTATION, R11] `make verify` fails at lint: ruff E501 on `packages/rag/tests/evaluation/test_security_integration.py:1` (89 > 88). Introduced by the T4 commit's post-review MINOR docstring fix (no re-review); T5 did not touch the file. → Wrap the module docstring. The promotion gate cannot go green until lint is clean.
  - F3 [MINOR, IMPLEMENTATION, R10] Operator rebuild/smoke (`make index-lexical` for realcheck and default `way2australia-idx-v2`, `make retrieve QUERY="..." RETRIEVE_ARGS="--lote ml"` must report `lexical-v2`, then `make setup`) is still pending, while the "If promoted" checkbox is marked `[x]`. Local `.local/` work, not a git artifact; do it before relying on retrieve, not before fixing F1/F2.
- Usage: (orchestrator)

### Review
- Model: Cursor Grok 4.6; matches the BEST tier (`Grok 4.6`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands: `python3 -m uv run python -m way2australia_rag.evaluation.continuity experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json experiments/results/retrieval-evaluation-idx-v2-20261104T105123Z.json` → exit 0 (shared goldens 69, no shared-case differences); `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v2-20261104T105123Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v2-20261104T105300Z.json COMPARE_ARGS=--cross-tokenizer` → PASS (hits 86 → 86, MRR 0.9228 → 0.9228); `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v2-20261104T105259Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v2-20261104T105321Z.json COMPARE_ARGS=--cross-tokenizer` → PASS (hits 73 → 73, MRR 0.7423 → 0.7423); `git diff --name-status main...HEAD -- evaluation knowledge config` → T1 evaluation files + T3 `config/retrieval.yaml` (working tree adds only the T5 tokenizer promotion; `knowledge/` empty); `make verify` → pass (1257 passed, 2 skipped; ruff, format check and pyright clean) with `QDRANT_COLLECTION_BASE` unset; `make test-integration` not run (not in T5 verification); `graphify update .` not re-run (read-only; graph commit after user approval).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R10] Operator rebuild/smoke (`make index-lexical` for realcheck and default `way2australia-idx-v2`, `make retrieve QUERY="..." RETRIEVE_ARGS="--lote ml"` must report `lexical-v2`, then `make setup`) is still pending, while the "If promoted" checkbox is marked `[x]`. Local `.local/` work, not a git artifact; do it before relying on retrieve (prior round-1 F3, still open).
- Summary for user:
  - Changed: Four v3 `lote: ml` result files on `w2a-realcheck-idx-v2` (hybrid/bm25 × lexical-v1/v2). Continuity vs Spec 009 hybrid ref passed (69 shared goldens identical). Both `--cross-tokenizer` compares tied, so R10 promoted `config/retrieval.yaml` to `lexical.tokenizer: lexical-v2`. Prior FAIL F1/F2 fixed: committed-config and CLI pins, eval builders use the config tokenizer, ruff E501 wrap.
  - Verified by: continuity exit 0; hybrid compare PASS 86→86 / MRR 0.9228; bm25 compare PASS 73→73 / MRR 0.7423; `make verify` 1257 passed, 2 skipped, `QDRANT_COLLECTION_BASE` unset. Protected paths: only allowed `config/retrieval.yaml` tokenizer change plus T1 evaluation files already on the branch.
  - Worth your attention: Promotion is a correctness default, not a measured gain (seed corpus has no legacy chillu sequences; case-by-case identity). BM25-only `ml` MRR 0.2396 (n=16) is a T6 carry-over. Operator lexical rebuild/smoke is still pending before you rely on `make retrieve`. Approve, then one commit of the four JSONs + config + tests + spec docs (`Spec-Task: 010/T5`), then a graph commit.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `config/retrieval.yaml` → `lexical.tokenizer`: promoted default `lexical-v2`.
    2. `experiments/results/retrieval-evaluation-idx-v2-20261104T105123Z.json` → Arm A hybrid lexical-v1 (continuity candidate).
    3. `experiments/results/retrieval-evaluation-idx-v2-20261104T105300Z.json` → Arm C hybrid lexical-v2 (promoted v3 hybrid reference).
    4. `experiments/results/retrieval-evaluation-idx-v2-20261104T105259Z.json` and `...T105321Z.json` → BM25 lexical-v1/v2 arms (identical; `ml` MRR 0.2396).
    5. Supporting edits: `test_strategy.py` `test_committed_config_loads`, `test_lexical_cli.py` success summary, `test_strategy_eval.py` config tokenizer, `test_security_integration.py` E501 wrap; `CURRENT_STATE.md` Next step.
- Usage: (orchestrator)

### User decision
- 2026-11-04: approved. Verbatim: "approved for T5, with two record fixes in the same commit (no re-review needed): …" (tasks.md "If not promoted" → `[ ] N/A (promoted)`; T5 deviation on retrieve smoke vs index-lexical output; carry-over for roadmap 10 on tokenizer vs config mismatch). Operator rebuild/smoke completed before commit. Record fixes applied in the T5 commit; no re-review.
