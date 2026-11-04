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
