# Spec 011 — retrospective reviews

## Round 1 — 2026-11-06

- **Spec:** `011-multilingual-reranking`
- **Diff reviewed:** `main...spec/011` (head `eb24bc5`; base `3b81508`), excluding `graphify-out/`
- **Reviewer host / model:** Claude Code, `claude-opus-5-5` (Opus 5.5), run as a subagent in a fresh session; matches the BEST tier (`Opus`) in `agent-skills/MODEL_PREFERENCES.md`.
- **Outcome:** `PASS` (no BLOCKING or MAJOR finding; four MINOR findings; docs reconciled)
- **Usage:** 260K tokens · 43 tool uses · 12:40

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (the reviewer's single run) | exit 0 | lint, format, typecheck (0 errors), skills-check and validators clean; 1442 passed, 3 skipped in 233.8 s; no extras installed; same counts as the T6 review |
| `make test-integration` (Docker Qdrant) | 28 passed, 1417 deselected | includes the T2 `hybrid` + `FakeReranker` test through `open_retrieval` |
| `make eval-security` (hub-free) | PASS | suite v3, three chunkers × eight paths (`dense`, `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`, `hybrid_rerank`, `hybrid_rerank_skip_open`, `hybrid_rerank_skip_query`), 92 queries per chunker (5 security, 87 golden), skips `model_unavailable` at open / query seen; result in git-ignored `experiments/results/tmp/security-evaluation-20261106T104734Z.json` |
| `git diff --name-status main...HEAD -- evaluation knowledge config` | `M config/retrieval.yaml` | only allowed file |
| Unchanged-code list: `git diff --stat main...spec/011` on `retrieval/{fusion,hybrid,fallback,retriever,bm25,access,applicability,index,baseline}.py`, `lexical/`, `ingestion/`, `config/ingestion.yaml`, `tests/retrieval/test_baseline.py`, `packages/core`, `apps` | empty | `availability.py` changed only by the `_cause_chain` extraction (planned) |
| Language literals / lazy import | none / ok | no `ml`/Malayalam literal in `rerank/` or `retrieval/reranking.py`; `sentence_transformers` imported only inside `BgeRerankerV2M3` loading (`bge.py:76`) |
| `git status --porcelain` at start | clean | |

Not run (user-owned or out of scope): real embedder or reranker, `W2A_RUN_RERANKER_SMOKE`, `make eval-retrieval` on `w2a-realcheck-*`. T5 numbers were recomputed from the result files by the T5 and T6 reviewers and are not re-derived here.

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 Reranker contract and fake | `rerank/base.py`, `rerank/fake.py` | `tests/rerank/test_rerank_fake.py`; T1 review | SATISFIED |
| R2 adapter and extra | `rerank/bge.py`, `rerank/build.py`, `pyproject.toml` `reranker` extra, `Makefile` `setup-bge-m3`, `uv.lock` | `test_rerank_bge.py` (lazy import, revision and missing-extra refusals), opt-in smoke test run by the user (T1 decision); hub-free `make verify` | SATISFIED |
| R3 config and selection | `RerankConfig` in `retrieval/strategy.py`; `config/retrieval.yaml` 1.3; `--rerank`/`--no-rerank` in both CLIs; hybrid-only refusal in `open_retrieval` and `build_retriever` | `test_rerank_config.py`, `test_opening_rerank.py` (incl. the two T6 default-on CLI tests) | SATISFIED |
| R4 stage on `hybrid` | `retrieval/reranking.py` (`_order`, membership `_recheck`), composition in `build_retriever` | `test_reranking.py`; amended R4 wording (change log 2026-11-05) | SATISFIED |
| R5 reranker unavailable | `rerank/errors.py`, `_load_reranker` (sticky open skip), stage `except RerankerUnavailableError` | skip-not-BM25 test through real `FallbackRetriever`; offline-not-cached exit 2; T2 review | SATISFIED |
| R6 result 2.5 | `evaluation/retrieval_eval.py`, `results.py`, `cli.py` | `test_rerank_eval.py`, T4 end-to-end CLI test in `test_strategy_eval.py` | SATISFIED (see F1 for the fallback depth) |
| R7 `eval-compare` / continuity | `compare.py` (`rerank_identity`, `skipped_rerank_problems`, `DISTINCT_VERSIONS`), `continuity.py` | `test_rerank_eval.py`, multi-chunk family tests (T4) | SATISFIED |
| R8 security gate | `security_eval.py` (`RERANK_PATHS`, `_check_rerank_path`), `security_index.py` `injection` variant | `test_security_eval.py`; `make eval-security` PASS (this round) | SATISFIED |
| R9 unchanged behaviour, protected paths | unchanged-code list empty; protected diff only `config/retrieval.yaml` | existing tests changed only by format/flag pins (T2, T3, T5 reviews) | SATISFIED |
| R10 real runs and promotion | three committed result files; `rerank.enabled: true`; D079 | T5 review recomputation; user decision recorded verbatim | SATISFIED |
| R11 spec-wide verification | — | this round: `make verify`, `make test-integration`, `make eval-security`, protected diff | SATISFIED |
| R12 docs and decisions | D075–D079; `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `ROADMAP.md`, `CURRENT_STATE.md` | T6 review plus gaps reconciled in this round (F4) | SATISFIED |
| Definition of Done | all of the above | retrospective `PASS` pending the user's approval and the merge | SATISFIED (merge pending) |

### Protected-data check

`git diff --stat main...spec/011 -- evaluation/ knowledge/ config/` → `config/retrieval.yaml | 10 +++++++++-`: schema `1.2` → `1.3` and the `rerank` block (T1, R3), then `enabled: false` → `true` (T5, R10 promotion; `depth` already 20). Both are required by tasks; nothing else changed. `experiments/configs/rerank/retrieval-depth50.yaml` and three result files under `experiments/results/` are outside the protected paths and required by T3/T5.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R6 / T3 | `evaluation/cli.py` sets `retrieval_depth = rerank.depth` whenever reranking is requested, also when a dense outage makes BM25 serve (open time: `FallbackRetriever(None, bm25)`; per query: the primary raises). BM25 is then asked for 20 chunks instead of `fusion.candidate_depth` 50 and the file records `retrieval_depth` 20 for a BM25-served run. Top-5 distinct-document metrics are unaffected while `required_depth` (17 on idx-v2) ≤ 20, so no recorded number is wrong; it is a latent coupling between the served path and the depth. Not in the design; recorded in the As-built notes and `COMMANDS.md`. → fix with the item 10 `open_retrieval` rework (depth per served path). |
| F2 | MINOR | IMPLEMENTATION | R3 / T2 | `open_retrieval(..., rerank: bool = False)`: the library default is off, and only `retrieval/cli.py` and `evaluation/cli.py` resolve the effective setting from `rerank.enabled`. Consistent with the design ("Effective rerank = flag, else `rerank.enabled`" is a CLI rule), but a new caller (the item 10 HTTP route) that omits the argument silently serves un-reranked hybrid while the config says `enabled: true`. → item 10 resolves it from config, with a test; recorded in Notes and As-built. |
| F3 | MINOR | IMPLEMENTATION | R3 / T2 | `top_k > rerank.depth` is refused inside the stage at query time, after the reranker was loaded at open: `make retrieve --top-k 30` (allowed range 1..50) loads the model and then exits 2. In `eval-retrieval` the distinct-document depth check refuses first, but its advice names `candidate_depth`, not `rerank.depth`. Exit code and outcome are correct (refusal, never a wrong result); only the cost and the advice text are off. → optional: check at open, and name `rerank.depth` in the advice. |
| F4 | MINOR | IMPLEMENTATION | R12 / T6 | Doc gaps outside the T6 edits: `ARCHITECTURE.md` retrieval table said `RetrievalConfig` 1.2 and `cli.py` `--strategy` only, listed neither `reranking.py` nor the `rerank/` package, and the evaluation table said results 1.0–2.4, five security paths, security 1.4; `COMMANDS.md` said `make setup` removes only the `bge-m3` extra and that the last `make retrieve` line is always a `rerank:` line (none is printed when BM25 serves with reranking requested). Reconciled in this round. |

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/ARCHITECTURE.md` | Retrieval heading adds "reranking by Spec 011"; module table: `RetrievalConfig` 1.3 with `RerankConfig`, `build_retriever` rerank composition, `opening.py` rerank load and off-by-default parameter, new `reranking.py` row, `cli.py` rerank flags | F4, F2: table described Spec 010 state |
| `docs/project/ARCHITECTURE.md` | "Reranking" section: module list of the `rerank/` package | F4: new package not described |
| `docs/project/ARCHITECTURE.md` | Evaluation table: results 1.0–2.5 and `--cross-rerank`; eight security paths, security 1.5; Spec 011 summary bullet, D078 | F4 |
| `docs/project/COMMANDS.md` | `make setup` removes both `bge-m3` and `reranker` extras | F4: matches `Makefile` (sync without `--extra`) |
| `docs/project/COMMANDS.md` | `make retrieve`: no `rerank:` line when BM25 serves with reranking requested | F4: matches `rerank_line` |
| `docs/project/COMMANDS.md` | `make eval-retrieval` fallback bullet: reranker built but not loaded, `rerank: requested but not loaded` summary line, `rerank: null`, BM25 asked for `rerank.depth` chunks | F1, F4 |
| `.kiro/specs/011-multilingual-reranking/design.md` | As-built notes: fallback depth (F1), library default `rerank=False` (F2), no `rerank:` line on fallback | deviations / contracts not in the approved design |
| `docs/project/CURRENT_STATE.md` | Header, Current goal, Spec 011 block (verify counts), spec table row, Next step: retrospective `PASS`, awaiting approval and merge; new "Spec 011 retrospective" known-issues block (F1–F4) | implemented reality; MINOR findings go to known issues |

No decision added: every durable choice of the spec is in D075–D079; F1–F3 are minor implementation details recorded as known issues, not new contracts. `TECH_STACK.md` and `ROADMAP.md` already match the code.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| Membership re-check instead of `check_hit` on each returned hit | `requirements.md` change log 2026-11-05 (T2 review F1, user decision) |
| `build_reranker` refuses a mismatched `rerank.model_id` for `bge` | change log 2026-11-05 (T1 review F1) |
| `check_applicable` field-read spy test (T3 box) | change log 2026-11-05 (T2 review F2) |
| T4 test-only boxes (end-to-end `eval-retrieval --rerank`, 2.3/2.4/2.5 multi-chunk compare); compare family `DISTINCT_VERSIONS` | change log 2026-11-05 (T3 review F1, F2); As-built notes |
| Security gate at depth 50 / `top_k` 50 (harness-side) | change log 2026-11-05 (T4 review F3); As-built notes; D078 |
| T6 boxes: two required default-on CLI tests, promotion docs | change log 2026-11-06 (T5 review F1, F6) |
| Hub-offline test fixture also opts out on `W2A_RUN_RERANKER_SMOKE=1` (`tests/conftest.py`, new `test_hub_offline_fixture.py`), added at T1 approval without a task box | `task-reviews.md` T1 "User decision (2026-11-05)"; test-only, minor |
| `eval-retrieval` always refuses a fake reranker (R6 "unless the fake allowance is given") | As-built note recorded at tasks approval (2026-11-04) |
| `rerank:` CLI line printed last, after the hits | As-built notes (T2 implementation note, accepted in T2 review) |
| Query-skip results keep `score_kind: rrf`, no `fused_rank`, and `latency_ms` excludes the failed attempt | `task-reviews.md` T2 implementation notes, accepted in T2 review; minor |
| BM25-served run with reranking requested uses `retrieval_depth` = `rerank.depth` | F1 (recorded now) |
| `open_retrieval` defaults `rerank` to off; callers resolve it from config | F2 (recorded now) |
| `agent-skills/MODEL_PREFERENCES.md` (Cursor BEST tier) changed on this branch | commit `389c456`, workflow metadata, not spec work; no effect on code |

### Cross-task consistency

- One reranker-error mapping (`classify_reranker_error`) is used by `_load_reranker` (open) and by the adapter's `score` wrapping (query); it reuses `retrieval/availability.py`'s `_cause_chain`, so the D057/D062 chain rules cannot drift between the embedder and the reranker. `_OFFLINE_TYPES` is a superset of `_EXCLUDED_TYPES`; hub 5xx is not eligible (tested).
- One composition point: `build_retriever` builds `FallbackRetriever(RerankingRetriever(HybridRetriever))` for the CLIs, `open_retrieval` and the security harness, so the gate exercises the production stage (T4 review).
- `rerank_identity` and `skipped_rerank_problems` live in `compare.py` and are imported by `continuity.py`: the D-C rule and the compare rule cannot disagree. `retrieval_eval.py` has its own `_rerank_identity` writer (document side), read back by `results.py`.
- The hybrid-only refusal exists twice (`open_retrieval` before any factory call, `build_retriever` as the composition guard); same message, both tested (T6 test (b) shows the factory is never called).
- Skip semantics agree across layers: `RerankRecord.stage` → per-case `served_path` (`hybrid+rerank_skipped:<reason>`) → `rerank_skip_counts` (`<reason>:<stage>`) → compare/continuity refusal → `make retrieve` warning.
- Exceptions: F1 (served path and depth are coupled only in the evaluation CLI) and F3 (the `top_k ≤ depth` check runs at query time in `make retrieve`).

### Scope-drift review

- No context building, no blending with RRF, no reranking on `dense`, `bm25` or the fallback, no inference timeout, no device pinning, no HTTP route, no new `index_version`, re-ingestion or lexical rebuild. `rrf_fuse`, `HybridRetriever`, `FallbackRetriever`, access and applicability builders unchanged.
- No Phase 2 work. The `Reranker` Protocol has one real provider and one fake; no speculative registry.
- Every spec edit after approval has a dated change-log line (six lines) citing a `task-reviews.md` user decision; the T1 fixture fix is recorded in `task-reviews.md` only (test-only, minor).
- `lote` stays outside `AccessContext`; no secrets; refusals name fields and codes only.
- Process: T3 skipped the `implementing (round 1)` state (T3 review F4, process only).

### Patterns in `task-reviews.md`

- Models: every implementer was Sonnet 5.5 (BEST_MINUS_ONE), every reviewer Opus 5.5 (BEST), always different models. All six tasks passed task review in round 1; no escalation.
- Repeated pattern: reviews produced test or doc boxes added to later tasks (T1→T2, T2→T3, T3→T4, T4→T6, T5→T6), each routed through `spec-planner` with a change-log line. This worked but moved coverage late: the default-on CLI path was first tested in T6 (T5 review F1), and the `eval-retrieval --rerank` CLI path in T4 (T3 review F2). A next spec that flips a default should plan the default-on CLI tests in the same task as the flip.
- Docs drift recurs at the edges of what a task edits (T6 review F1–F4, this round's F4): tables in `ARCHITECTURE.md` and setup lines in `COMMANDS.md` that the task did not touch. A grep for the previous version numbers (`1.2`, `2.4`, `1.4`, "five paths") before hand-off would have caught them.
- Usage (implementer + reviewer, plus fix subagents): T1 159K + 146K (+ 89K fix); T2 200K + 168K; T3 233K + 174K; T4 218K + 150K (+ 102K fix); T5 101K test fix + 152K review; T6 179K + 178K.
- `make verify` stayed within the two-run budget in every session; T2 used both runs (first found format-only failures).

### Remediation required

None. No RM tasks (all findings MINOR). No SPEC_DEFECT for `spec-planner`.

### Notes for the next spec

- **Item 10 (grounded generation, first HTTP route) inherits these reranking items:**
  - resolve the effective rerank setting from `rerank.enabled` (F2) and make the depth follow the served path (F1); check `top_k ≤ rerank.depth` at open (F3);
  - model and client lifecycle: the reranker is loaded once per `open_retrieval`; the sticky open-time skip (D-A) means a transient hub failure at startup disables reranking for the whole process, so a long-running server needs a reload or health policy;
  - latency: depth 20 costs about 1 s per query at p95 on `mps:0` (rerank leg p95 962 ms; depth 50 about 2×). There is no inference timeout (D077). A binding per-request budget, concurrency on one device, and device choice (CPU vs GPU in `ap-south-1`) must be decided with real hardware; the dev-machine figures are not production numbers;
  - refusal threshold: unanswerable cross-encoder top-1 scores overlap the golden ones (three unanswerable cases above 0, D079), so a fixed reranker-score cut-off is unsafe; any threshold needs more unanswerable cases and its own evaluation;
  - context building (deduplication, budgeting, evidence ordering) moved here from item 9;
  - Spec 008/010 serving carry-overs still apply (lexical startup policy and tokenizer check, circuit breaker, Qdrant client lifecycle, async freshness, 5xx eligibility).
- **Evaluation:** reranking reached MRR 0.9751 and HitRate 1.0 on v3 with `lote: ml`; the suite is now near ceiling for retrieval ranking, so further retrieval gains are hard to measure on 87 goldens. Generation-era cases (grounding, citations, refusals) are the higher-value additions. Residual rank losses `g038`, `g062` (1 → 2) and `g057` (0.5) are the remaining ranking signals.
- **Malayalam:** BM25-only and the hybrid fallback still lose `g067`–`g069` (no BM25 candidates); query translation or transliteration remains the fix, and reranking cannot help the fallback.
- **Corpus size:** 34 chunks; depth 50 reranks everything. Re-measure depth and latency when the corpus grows (FAQ indexing, more documents).
- **Operating change:** default runs need `make setup-bge-m3` and a cached reranker; `--strategy dense|bm25` need `--no-rerank`. Any CI spec must install the extras or pin `--no-rerank` for model-free jobs, and keep `make verify` hub-free.
- **Process:** plan default-flip tests in the flipping task; grep docs for old schema versions and path counts before T6 hand-off; the verify budget (two runs) held for every session.
- Workflow: the saved `chore/workflow-trim` plan comes to the user after the merge and before Spec 012 (`CURRENT_STATE.md` Next step).

### Final handoff

- Outcome `PASS`: no BLOCKING or MAJOR finding; F1–F4 MINOR, recorded under Known issues in `CURRENT_STATE.md`; docs reconciled.
- Nothing committed. Uncommitted: this `review.md`, `docs/project/ARCHITECTURE.md`, `docs/project/COMMANDS.md`, `docs/project/CURRENT_STATE.md`, `.kiro/specs/011-multilingual-reranking/design.md` (As-built notes).
- Merging can proceed after the user approves this round. After the merge, the user runs `/graphify . --update` on `main`.
