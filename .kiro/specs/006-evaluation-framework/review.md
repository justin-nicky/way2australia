# 006 — Spec Review (retrospective)

Required end-of-spec retrospective (`agent-skills/spec-reviewer`, D031). Append-only; newest round at the bottom.

## Round 1 — 2026-10-24

- **Spec:** `006-evaluation-framework`
- **Diff reviewed:** `main...spec/006` (base `a400bab`, head `28aa24b`)
- **Reviewer host / model:** Claude Code (subagent, fresh session, did not implement the spec) / `claude-opus-5-5`. Matches the `spec-reviewer` tier BEST = Opus in `agent-skills/MODEL_PREFERENCES.md`; no mismatch.
- **Outcome:** `PASS`
- **Usage:** 226K tokens · 40 tool uses · 9:46

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | exit 0 | ruff check "All checks passed!", `ruff format --check` 123 files formatted, pyright 0 errors, skills-check, `validate-knowledge: OK, 0 problems`, `validate-evaluation: OK, 0 problems`; pytest 609 passed, 1 skipped (local Qdrant was already up, so the Docker tests ran inside it on their own throwaway collections). No `bge-m3` extra. |
| `make test-integration` | exit 0 | 20 passed, 590 deselected, including `test_security_integration.py` (R9). `curl localhost:6333/collections` before and after: only `w2a-realcheck-idx-v1` and `-settings`; no `w2a-sectest-*` left; realcheck not touched; container not started or stopped. |
| `make eval-security` | exit 0 | `PASS in 418 ms`; 5 deferred security cases listed with owners; `fixture_public_poisoned` excluded; result under the git-ignored `experiments/results/tmp/` (the reviewer's file was removed afterwards). |
| `make eval-compare BASE=CANDIDATE=experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` | exit 0 | `PASS (hits 60 -> 60, MRR 0.8783 -> 0.8783)`, no `WARNING` lines, `source_authority` "not compared" note (both files 1.0). Committed file read only. |
| `make eval-retrieval` (no `bge-m3` extra) | exit 2 | `ERROR OptionalDependencyError: ... run make setup-bge-m3.` before any Qdrant contact. The fake-embedder and fake-index refusals are unit-tested (`test_cli.py`, `test_retrieval_eval.py`). |
| Protected paths | as required | `git diff --name-status main...spec/006 -- evaluation knowledge config experiments` → exactly `A evaluation/candidates/006-candidates.jsonl`, `A evaluation/schemas/evaluation_case_types.schema.json`, `A evaluation/schemas/evaluation_suite.schema.json`. |
| `retrieval/` scope | as required | `git diff --stat main...spec/006 -- .../retrieval/ .../ingestion .../repositories packages/core apps` → only `retrieval/access.py`, `errors.py` (T8a `document_id`, message text unchanged) and `goldens.py` (T1 wrapper). `metrics.py`, `baseline.py`, `baseline_cli.py` unchanged. |
| Package boundary | as required | Only `retrieval/goldens.py` imports `way2australia_rag.evaluation` from `retrieval/`, `ingestion/`, `repositories/`. The only filter construction in `evaluation/` is `build_access_filter(access)` for `document_count`. |
| Isolation literals | as required | No `ml` word in `evaluation/*.py`; the only `tests/fixtures/security` literal in library or app code is `cli.py` `DEFAULT_FIXTURE_ROOT`. No `.github/` directory. |
| `git status --porcelain` before reconciliation | empty | The working tree was clean at `28aa24b`. |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 Governed suite loader | `evaluation/models.py`, `suite.py` (T1); `retrieval/goldens.py` wrapper | `test_suite_loader.py` (valid suite with counts from the manifest, unknown type, escaping path, malformed line, ignored `access_context`, hash before and after); legacy `test_goldens.py` | SATISFIED |
| R2 Schemas and `validate-evaluation` | two new schema files, `schemas.py`, `validate.py`, `cli.py validate`, `Makefile` (in `verify`) (T2, T8a) | `test_schemas.py`, `test_validate.py` (every check fails on a temp copy; T8a gaps closed); `make validate-evaluation` exit 0 inside `make verify` | SATISFIED |
| R3 Case status and type handling | `LoadedSuite.active`/`excluded_by_status`; `RETRIEVAL_SIDE_ATTACK_TYPES`, `DEFERRED_OWNERS`, `unclassified` in `security_eval.py`; active golden without documents refused by validation and by the runner | `test_status_handling.py`, `test_security_eval.py` (deferred, unclassified); byte-identity before and after a load (`test_suite_loader.py`) and a validation (`test_validate.py`) | SATISFIED (see F1: no before/after hash around the two runners) |
| R4 `eval-retrieval` | `retrieval_eval.py`, `cli.py retrieval` (startup order as designed), `Makefile` (T3, T8a) | `test_retrieval_eval.py` (fake refusals, binding, read-only, `access_context` spy), `test_cli.py` (non-default `W2A_TENANT_ID` reaches the filter); `make eval-retrieval` exit 2 without the extra | SATISFIED |
| R5 Slices and small-corpus notes | `slices.py`, `_notes` in `retrieval_eval.py` (g004/u001 note only while both active) | `test_slices.py` (keys incl. `naati+owner_approved`, threshold 10, absent languages from a temp registry, no `ml` literal) | SATISFIED |
| R6 Section-level readiness | `sections.py` (`"<document_id>#<section_id>"` keys over unchanged `metrics.py`) | `test_sections.py` (synthetic metrics, zero-measurable block) | SATISFIED |
| R7 Result 2.0 and writing rules | `retrieval_eval.py` document; `results.py` via unchanged `write_result`/`check_output_free` | `test_retrieval_eval.py` (1.0-key superset, no query or chunk text, never overwritten, partial cleanup); tests write only to `tmp_path` | SATISFIED |
| R8 Security hard gate | `security_corpus.py` (explicit fixture list), `security_index.py`, `security_eval.py`, `cli.py security` (T5, T8a, T8b) | `test_security_eval.py` (gate passes, sanity check, filter-dropping store fails exit 1, filter identity incl. `s003`, builder refusals, under-10 s bound, `document_id` from the error attribute via a store, stray/missing/hidden fixture files); `make eval-security` PASS | SATISFIED |
| R9 Docker isolation test | `test_security_integration.py` | `make test-integration` 20 passed; no `w2a-sectest-*` left | SATISFIED (closes Spec 005 retro F3) |
| R10 Unanswerable reporting | `unanswerable_report`, `score_distribution` (T4) | `test_retrieval_eval.py` (marker, distributions, latency excluded, no text) | SATISFIED |
| R11 `eval-compare` | `results.py read_result`, `compare.py`, `cli.py compare`, `Makefile` (T6, T8a) | `test_compare.py` (1 vs 2 lost cases, n=10 and n=3 MRR boundaries with epsilon, flips both ways, each refusal with old -> new and next step, duplicate `case_id`, committed 1.0 self-compare); manual self-compare PASS | SATISFIED |
| R12 Legacy `retrieval-baseline` | `goldens.py` wrapper; `baseline.py`/`baseline_cli.py` untouched; `COMMANDS.md` legacy entry | `test_legacy_baseline_snapshot.py` (byte-exact on the frozen fixture, independence, location); `test_baseline.py`/`test_goldens.py` changed only by live-count consistency checks (allowed by the 2026-10-24 R12 amendment); `retrieval/test_cli.py` unchanged | SATISFIED |
| R13 Index and output isolation | `.gitignore` `experiments/results/tmp/`; read-only `DenseIndex`; `w2a-sectest-<8 hex>` refusal in code | `test_security_eval.py` refusals; `test_retrieval_eval.py` read-only; `git status --porcelain -- experiments` clean after runs; legacy location recorded as a known issue in `CURRENT_STATE.md` (this round) | SATISFIED |
| R14 Candidate cases | `evaluation/candidates/006-candidates.jsonl` (7 rows, all `suggested`; T7, T8a) | `test_validate.py` (real file validates, not loaded, loaded count equals `case_count`, no `suggested` case loaded, owner review on the g004/u001 row) | SATISFIED |
| R15 Protected paths and spec-wide checks | three added files only; docs D042–D046 (+ D047 this round), `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md` | protected-path diff above; `make verify`; `make test-integration`; live-count rule (T8a, reviewer scratch check recorded in `task-reviews.md`); docs reconciled this round | SATISFIED |

Definition of Done:

| Item | Status |
|---|---|
| R1–R15 satisfied and traced to approved tasks | SATISFIED (traceability table in `requirements.md`; T1–T8b approved) |
| `make verify` without extra, Docker or model; runs `validate-evaluation` and the gate | SATISFIED (the gate runs through `test_security_eval.py`) |
| `make test-integration` incl. the Docker isolation test | SATISFIED |
| `make eval-security` passes on the seed corpus | SATISFIED |
| `make eval-retrieval` refuses a fake index | SATISFIED (unit tests; exit 2 without the extra observed) |
| `make eval-compare` tolerance tests and the committed 1.0 baseline | SATISFIED |
| `make retrieval-baseline` behaves as in Spec 005 | SATISFIED (snapshot; the stricter refusal of malformed suites is recorded in the design and `COMMANDS.md`) |
| Candidates file exists, inactive, validated | SATISFIED |
| Protected-path check shows only the three added files | SATISFIED |
| Post-merge real `eval-retrieval` run (user-owned, not a gate) | NOT_VERIFIED (pending, recorded in `CURRENT_STATE.md`, as the DoD allows) |
| `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md` match the code | SATISFIED after this round's reconciliation |

### Protected-data check

`git diff --stat main...spec/006 -- evaluation/ knowledge/ config/` → three added files: `evaluation/schemas/evaluation_suite.schema.json` (+71, R2, T2), `evaluation/schemas/evaluation_case_types.schema.json` (+224, R2, T2), `evaluation/candidates/006-candidates.jsonl` (+7, R14, T7, content edited by T8a under the 2026-10-24 amendment). Nothing under `knowledge/` or `config/`; no existing file under `evaluation/` modified. `experiments/configs/day1_baseline.yaml` and the committed baseline file are unchanged. The frozen copy under `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/` is test data outside the protected paths (T1).

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R3 / T3, T5 | The "dataset files byte-identical before and after a run" test covers the loader (`test_suite_loader.py`) and the validator (`test_validate.py`) only; the design ("A test hashes `evaluation/` before and after each runner") also names the `eval-retrieval` and `eval-security` runners, and neither has a before/after hash test. Risk is low: both runners read evaluation data only through `load_suite`, and the only writes in `evaluation/` code go to `work_dir` (`security_corpus.py`) or the result file. No remediation task; recorded as a known issue. |
| F2 | MINOR | IMPLEMENTATION | R15, DoD / T8b | Documentation drift, reconciled in this round: the T8b review F1/F2 items (user-directed), `COMMANDS.md` describing every evaluation error line as `ERROR <ClassName>:` although `eval-compare` refusals print `not comparable: ...` without it, `CURRENT_STATE.md` still listing Spec 005 retro F3 as open (closed by R9) and describing T8b as "in task review", the R13 legacy-output known issue missing from `CURRENT_STATE.md`, and no decision for the security result format. |
| F3 | MINOR | SPEC_DEFECT | R8, R11 / T5, T6 | Design sketches differ from code approved in task reviews: the keyword-only `schema_source` on `build_security_repository`, seed points written through `IngestionService`, `query-probe` canary point IDs, the flip-line format `g002 v1`, the per-list 10-key cap and the unprefixed `not comparable:` refusal output. All were accepted at task approval; recorded in the design's As-built notes in this round. |

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/CURRENT_STATE.md` | Spec 006 row: findings split into fixed, docs-only and closed by user decision without a fix (T1 F3, T6 F2/F4, T7 F2, T7 owner-review item); duplicated "user-owned post-merge step" sentence removed; status kept as all tasks approved, retrospective pending | User-directed F1 (T8b review F1) |
| `docs/project/CURRENT_STATE.md` | "Current goal", the Spec 006 implemented bullet and "Next step" item 1 no longer say T8b is in task review | Stale after T8b approval |
| `docs/project/CURRENT_STATE.md` | "Next step" item 3: "evaluation runs" dropped (delivered by Spec 006); now points to this round's notes and Spec 007 | User-directed F1 |
| `docs/project/CURRENT_STATE.md` | Known issues: candidates noted on the `ml` gap, zero section-measurable cases, g004/u001 pending owner decision; new "Spec 006 retrospective" block (F1, legacy `--allow-fake` output location per R13, `eval-security` not a `verify` step, hard-coded `guest` role); Spec 005 retro F3 marked closed by Spec 006 T5; D047 named | Implemented reality; R13 requires the legacy location as a documented known issue |
| `docs/project/COMMANDS.md` | `eval-security` exit 2: existing output file is `RetrievalConfigurationError`, a refused fixture folder `EvaluationConfigurationError`, `EvaluationHarnessError` only for the harness | User-directed F2 (T8b review F2); matches `cli.py` and `check_output_free` |
| `docs/project/COMMANDS.md` | `validate-evaluation` problem line shown as `ERROR <file>:<line> <case_id> <field>: <reason>`, plus the closing count line | User-directed F2; matches `cli._validate` and `EvaluationProblem.__str__` |
| `docs/project/COMMANDS.md` | `eval-compare`: refusals print `not comparable:` without the `ERROR` prefix (also stated in the shared error-line sentence), the per-list 10-key cap, and the flip-line format `<case_id> v<case_version>` | F2, F3; matches `compare.py` and `cli._compare` |
| `docs/project/DECISIONS.md` | New D047: security evaluation result format 1.0 and the throwaway output location | Durable format built in T5 with no decision |
| `docs/project/ARCHITECTURE.md` | Evaluation section decisions line D042 to D047 | D047 added |
| `.kiro/specs/006-evaluation-framework/design.md` | As-built notes appended: flip-line format `g002 v1` (T6 F2/F4), per-list cap, unprefixed `eval-compare` refusals, `validate-evaluation` line format, `schema_source` keyword, `IngestionService` seed path and `query-probe` IDs, output-file error class | User-directed; F3 |

`TECH_STACK.md` already records `referencing` (T8b); no other new dependency (`git diff main...spec/006 -- packages/rag/pyproject.toml uv.lock` adds only `referencing`). No code, tests, `evaluation/`, `knowledge/`, `config/` or `requirements.md` edited.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| Tolerant loader models (plain-string `status`, defaults) | Change log 2026-10-23 (T1 review F1); design "Interfaces / models" |
| Legacy `retrieval-baseline` refuses malformed suites it used to ignore | Change log 2026-10-23 (T1 review F2); design; `COMMANDS.md` legacy entry |
| `.gitignore` negation in T1, replaced by `/MANIFEST` in T8b | T1 review F3 (user acknowledgement); change log 2026-10-23 (T8 box) |
| `--repo-root`, `--config` on `eval-retrieval`; `eval-security` options | T3 review F2, T5 review F2; design As-built notes |
| `RetrievalAuthorizationError.document_id` (one `retrieval/` change) | Change log 2026-10-24 (T5 review F1) |
| Explicit security fixture list, hidden files ignored | Change log 2026-10-24 (T5 review F4, T8 split) |
| Duplicate `case_id` refusal in `read_result` | Change log 2026-10-24 (T6 review F5) |
| Live-data counts replaced by consistency checks in existing tests | Change log 2026-10-24 (R12/R15) |
| T8 split into T8a/T8b; T8b test fixes | Change log 2026-10-24 (two lines) |
| `schema_source`, `IngestionService` seed path, `query-probe` IDs, flip-line format, per-list cap, unprefixed refusals | T5 and T6 task reviews (accepted); F3; As-built notes (this round) |
| No before/after hash around the two runners | F1 |

### Cross-task consistency

- One access path throughout: `eval-retrieval` (T3/T4) and `eval-security` (T5) both resolve `resolve_access(guest_access(settings))` once and pass it to `DenseRetriever`; spy tests in both prove a case's `access_context` cannot change the filter, and T8a adds the tenant-from-settings CLI test.
- One writer: 2.0 retrieval results and security results both go through the reused exclusive `write_result`/`check_output_free`, so "never overwritten" and "existing file is exit 2" behave the same in both commands (the error class is `RetrievalConfigurationError` in both, now documented).
- `require_active_suite` is shared by `eval-retrieval` and `eval-security`; the suite status values in the schema enum, D042, `COMMANDS.md` and the design agree.
- Error printing agrees across subcommands (`ERROR <ClassName>: safe_text(...)`, class name only for unexpected exceptions), except the deliberate `not comparable:` refusal format of `compare` (now documented).
- Constants agree with docs: `HIT_TOLERANCE_CASES = 1`, `MRR_EPSILON = 1e-9`, `SMALL_SAMPLE_THRESHOLD = 10`, `MAX_TOP_K = 50`, `SECURITY_FIXTURE_FILES`, `FORBIDDEN_VARIANTS`.
- No duplicated logic found: metrics come only from `retrieval/metrics.py`; the security corpus copier lives only in `security_corpus.py` (`tests/conftest.py` calls it).

### Scope-drift review

- No next-spec work: no BM25, sparse vectors, RRF, reranking, language detection, generation evaluation, LLM-as-judge, score thresholds, CI workflow, FastAPI route or Langfuse code in the diff.
- No Phase 2 work: no approval CLI or UI, no candidate activation, no `public-eval-v2`, no "compare shared cases" mode (recorded as a note only).
- No speculative abstractions beyond the design; the test seams (`client_factory`, `embedder_factory`, optional `repository` in `validate_evaluation`) are used only by tests.
- All spec-file edits after approval are recorded in the `## Change log` (six dated lines).

### Remediation required

None. F1–F3 are MINOR; F2 and F3 were reconciled in this round, F1 is recorded under known issues in `CURRENT_STATE.md`. No RM tasks added; no SPEC_DEFECT needs `spec-planner` before merge.

### Notes for the next spec

- **Phase 2 "compare shared cases" mode (not built in Spec 006).** Release-candidate evaluation will need an `eval-compare` mode that compares only the cases present in both runs with the same `case_version`, reports new, removed and changed (`case_version`) cases separately, and keeps security and authorization regressions a hard fail. Spec 006 `eval-compare` refuses any difference in the case set instead (R11), so the first approved evaluation data change (a new golden, a `case_version` bump, or the activation of a candidate) makes every older result incomparable and needs a fresh baseline.
- **Pending human review of candidates.** The 6 agent-drafted pure-`ml` proposals in `evaluation/candidates/006-candidates.jsonl` need correction by a fluent Malayalam speaker and then owner approval; `cand006_ml_001` keeps "NAATI CCL" in Latin script (T7 F2), left to the speaker. The `cand006_change_g004_u001` proposal needs an owner decision among its four options. Activation is a separate, human-approved, versioned change (new cases or `case_version`s and a suite version bump); until then `g004` remains a counted miss and pure `ml` is reported as an absent query language.
- **User-owned post-merge run.** A real `make eval-retrieval` on `w2a-realcheck-idx-v1` followed by `make eval-compare` against the committed 1.0 baseline should reproduce HitRate@5 0.952 and MRR 0.878. Its 2.0 result is the natural baseline for Spec 007 (hybrid retrieval), which should compare against a 2.0 file so the `source_authority` slice is compared too.
- **Device noise.** The gate tolerates one lost case and a `1/n` MRR drop and lists flips as warnings, because the BGE-M3 device is not pinned (D038). If Spec 007 runs on a different device from the baseline, expect flip warnings on borderline cases (`g004`, `g026`, `g061` were misses).
- **Section-level metrics** stay at zero measurable cases until a chunking spec (roadmap 7) gives documents real sections and humans add `relevant_section_ids` (key form `"<document_id>#<section_id>"`).
- **Roles.** The security result hard-codes `access.role: "guest"` (D047); a spec that adds roles must take it from the resolved access and extend the forbidden variants to the new scopes.
- **R3 runner hash test (F1).** A later spec that touches the runners can add a before/after `evaluation/` hash around one `eval-retrieval` and one `eval-security` run.
- **Pattern from `task-reviews.md`.** Every task passed review in round 1 (T1–T8b, Sonnet implementer, Opus reviewer). Findings were all MINOR; most were test-strength gaps (vacuous or missing assertions) caught by reviewer mutation checks, then batched into a dedicated fix task (T8a). Keeping that "running list, then one fix task" pattern worked, but a live-data-count rule from the start (R15) would have avoided the large T8a test sweep. Implementer runs took 99K–167K tokens, reviews 85K–152K.
- Still deferred: Spec 004 nits, device pinning (D038), the legacy `retrieval-baseline` `--allow-fake` output location (R13).

### Final handoff

`PASS`. No BLOCKING or MAJOR findings; three MINOR findings, two reconciled in this round and one recorded as a known issue. Documentation reconciled (`CURRENT_STATE.md`, `COMMANDS.md`, `DECISIONS.md` D047, `ARCHITECTURE.md`, design As-built notes). All changes are uncommitted for the orchestrator to commit after the user's approval. Merging `spec/006` into `main` can proceed once the user approves this round.

### User decision
- 2026-10-24 — approved. Verbatim: "Approved: the retrospective (round 1 PASS), D047 as written, and the merge. Proceed with all four steps."
