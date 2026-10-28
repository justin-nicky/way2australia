# 007 — Hybrid Retrieval: Retrospective Review

## Round 1 — 2026-10-28

- **Spec:** `007-hybrid-retrieval`
- **Diff reviewed:** `main...spec/007` (head `2cd0aa8`, base `06b1af9`; 30 commits), `graphify-out/` excluded
- **Reviewer host / model:** Claude Code, `claude-opus-5-5` (Opus 5.5), run as a subagent of the orchestrator. Intended tier BEST (`Opus` in `agent-skills/MODEL_PREFERENCES.md`): matches. Fresh session; not the implementer's session (the implementer ran as Sonnet 5.5).
- **Outcome:** `PASS`
- **Usage:** 237K tokens · 55 tool uses · 10:11

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | exit 0 | ruff `All checks passed!`, `145 files already formatted`, pyright 0 errors, skills-check (5 skills), `validate-knowledge: OK, 0 problems`, `validate-evaluation: OK, 0 problems`, pytest 864 passed, 1 skipped (opt-in BGE-M3 smoke test); Qdrant was reachable, so the Docker integration tests ran inside it on throwaway collections |
| `make test-integration` | exit 0 | 22 passed, 843 deselected (includes the R12 three-strategy Docker isolation test) |
| `make eval-security` (twice) | exit 0, `eval-security: PASS` | `strategies: dense, bm25, hybrid`; 74 queries (5 security cases, 69 golden), 5 deferred cases; results in the git-ignored `experiments/results/tmp/` |
| `curl localhost:6333/collections` before and after | unchanged | only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings`; no `w2a-sectest-*` or `w2a-t007-*` left; the reviewer wrote nothing to Qdrant |
| `make eval-compare` committed 1.0 (`retrieval-baseline-idx-v1-20261023T063534Z.json`) vs 2.0 (`retrieval-evaluation-idx-v1-20261024T193140Z.json`) | exit 0, PASS | hits 60 -> 60, MRR 0.8783 -> 0.8783; only a `git_commit` identity line (R10 last bullet) |
| `make eval-compare` T2 dense (`…20261025T134659Z.json`) vs dense 2.1 (`…20261028T122835Z.json`) | exit 0, PASS | hits 66 -> 66, MRR 0.8816 -> 0.8816, no flip (R13 first step) |
| `make eval-compare` T2 dense vs hybrid (`…20261028T123121Z.json`) | exit 0, PASS | hits 66 -> 68, MRR 0.8816 -> 0.9094; identity lines `retrieval_strategy: dense -> hybrid`, `lexical_index: none -> lexical-v1 v1 digest 6045203b…`; flips miss->hit `g004`, `g026` only |
| `make eval-compare` T2 dense vs BM25 (`…20261028T123109Z.json`) | FAIL (informational) | hits 66 -> 64, MRR 0.8816 -> 0.7082; flips miss->hit `g004`, `g026`, hit->miss `g029`, `g067`, `g068`, `g069` |
| `git diff --name-status main...spec/007 -- evaluation knowledge config` | 7 entries | exactly the T10 list (below) |
| `git diff --stat main...spec/007 -- evaluation/datasets/{golden,unanswerable,security}_public.jsonl` | empty | v1 datasets byte-for-byte unchanged |
| Real-embedder commands | not run | by instruction; the R2/R13 numbers come from the committed user-run files |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 suite v2 | `evaluation/suites/public-eval-v2.json`, `evaluation/datasets/v2/*`, v1 manifest `status: replaced`, candidates `review.promoted_as`; `evaluation/validate.py` transcription check; `evaluation/cli.py` default v2 | `test_suite_v2.py`; `validate-evaluation: OK`; protected-path diff; eval-security PASS on v2 | SATISFIED |
| R2 v2 dense baseline | `experiments/results/retrieval-evaluation-idx-v1-20261025T134659Z.json` (user run) | T2 scratch checks and continuity (60 hits / MRR 0.8783 over 63 shared) in `task-reviews.md` T2 and `CURRENT_STATE.md`; self-compare PASS | SATISFIED (user-accepted deviation: `git_commit` `b024f5d`, a docs-only successor of the T1 commit) |
| R3 tokenizer `lexical-v1` | `lexical/tokenizer.py` (`tokenize`, `query_terms`, `QueryTerms`, 64-term cap) | `tests/lexical/test_lexical_tokenizer.py` (Malayalam pins, legacy chillu, no language literal) | SATISFIED |
| R4 `make index-lexical` | `lexical/build.py` (`production_entries` with `GUEST_PUBLIC_POLICY`, atomic `build_lexical_index`), `lexical/cli.py`, `Makefile`, `.gitignore` `/.local/lexical/` | `test_lexical_build.py`, `test_lexical_cli.py`; manual throwaway runs in T3 reviews (digest `6045203bfeec` twice) | SATISFIED (outside a git work tree an un-ignored target is allowed: user-accepted, design As-built note) |
| R5 binding | `lexical/store.py` `LexicalIndex.open` (read-only URI), `bind_to`; `retrieval/index.py` `chunk_identities()` | `test_lexical_bind.py` | SATISFIED |
| R6 BM25 + SQL access | `retrieval/bm25.py`, `retrieval/access.py` `build_sql_access_clause` | `test_bm25.py` (authorization, four forbidden row types, injection with trace callback, zero-term, truncation), `test_access.py` | SATISFIED |
| R7 RRF + hybrid | `retrieval/fusion.py` `rrf_fuse`, `retrieval/hybrid.py` (no catch, sequential legs) | `test_fusion.py` (hand-computed scores, best-rank tie-break pinned after T5 r1 F1), `test_hybrid.py` (fail closed, empty leg incl. Malayalam query) | SATISFIED |
| R8 strategy and config | `config/retrieval.yaml`, `retrieval/strategy.py` (`RetrievalConfig`, strict numerics, `build_retriever`), `retrieval/cli.py` | `test_strategy.py`, CLI tests; dense equivalence | SATISFIED |
| R9 result 2.1 | `evaluation/retrieval_eval.py`, `results.py`; `RetrievalResult.leg_document_ranks` | `test_strategy_eval.py` (dense equivalence against `fixtures/dense_eval_2_0.json`, keys, leg ranks, truncation) | SATISFIED |
| R10 compare identity rules | `evaluation/compare.py` (`_identity_problems`, embedder pair), `results.py` (lexical object required on bm25/hybrid 2.1) | `test_compare.py`; committed 1.0 vs 2.0 compare exit 0 (re-run above) | SATISFIED |
| R11 security gate | `evaluation/security_index.py`, `security_eval.py` (per-leg sanity, three strategies, result 1.1) | `test_security_eval.py`; `make eval-security` PASS (re-run) | SATISFIED |
| R12 Docker isolation | `tests/evaluation/test_security_integration.py` (parametrized over three strategies) | `make test-integration` 22 passed (re-run), no collections left | SATISFIED |
| R13 comparison and default | user-run files `…T122835Z` (dense 2.1), `…T123109Z` (BM25), `…T123121Z` (hybrid); `config/retrieval.yaml` `default_strategy: hybrid`; D055 | compares re-run above; T9 reviewer's independent recomputation of the rule | SATISFIED (user-accepted deviation: `git_dirty: true` in the BM25 and hybrid files, cause recorded) |
| R14 unchanged behavior, protected paths | dense equivalence; legacy characterization test untouched; no `index_version` change | `make verify`; protected-path diff; v1 datasets diff empty | SATISFIED (`retrieval/baseline.py` `git_state` edit approved by change log, see Deviations) |
| R15 docs and decisions | D049–D055; `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `CURRENT_STATE.md` | read against code by the T10 reviewer and this round; the missing "reveals nothing today" half (T10 F1) reconciled here | SATISFIED (after this round's reconciliation) |
| Definition of Done | all of the above; `make verify`, `make test-integration`, `make eval-security` pass | this round | SATISFIED, pending the user's approval and merge |

### Protected-data check

`git diff --name-status main...spec/007 -- evaluation/ knowledge/ config/` →
- `A config/retrieval.yaml`: R8 (T5), `default_strategy: hybrid` by the R13 rule (T9). Required.
- `A evaluation/suites/public-eval-v2.json`, `A evaluation/datasets/v2/golden_public.jsonl`, `unanswerable_public.jsonl`, `security_public.jsonl`: R1 (T1). Required.
- `M evaluation/suites/public-eval-v1.json`: one line, `"status": "active"` -> `"replaced"` (R1). Required.
- `M evaluation/candidates/006-candidates.jsonl`: `review.promoted_as` on six rows (R1; T1 tests prove no other change). Required.
- Nothing under `knowledge/`.

No unrequired change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION (docs) | R15 / T10 | T10 review F1, carried here by the user's instruction: R15 asks the docs to say that only eligible public chunks are indexed today, so corpus-wide BM25/IDF statistics reveal nothing; D050, `ARCHITECTURE.md` and `CURRENT_STATE.md` had only the forward half. **Reconciled in this round** (`ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `CURRENT_STATE.md`), including "a future roles spec needs one lexical file per access scope". D050 is left as written (it also names the accepted-leak alternative). |
| F2 | MINOR | IMPLEMENTATION | none / T6 commit `cfcaeff` | `.claude/settings.json` gained `Read(~/learning/**)`, `Edit(~/learning/**)`, `Write(~/learning/**)` permissions in the T6 commit. No task requires it and `task-reviews.md` does not mention it. It supports the user's learning-notes workflow (allowed by the user's global instructions), touches no product code, protected path or retrieval behavior, so it is not scope drift of the product. The user confirms it stays in the shared project settings or moves it to user-level settings. Recorded under known issues. |
| F3 | MINOR | SPEC_DEFECT (design text) | R14, R3 / T3, T10 | The design's "Not changed" list names `retrieval/baseline.py`, which T10 edited (`git_state`, approved by the 2026-10-28 change-log line); the "Interfaces / models" sketch shows `query_terms -> list[str]`, while the code and the design's R3 section use `QueryTerms(terms, truncated)`. Both now recorded in the design As-built notes; no code change. |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/ARCHITECTURE.md` | Retrieval "Hybrid retrieval" bullet on BM25 statistics rewritten: statistics cover every row of a file; the production file holds only eligible public chunks (`production_entries`, `GUEST_PUBLIC_POLICY`), so they reveal nothing; a roles spec needs one lexical file per access scope | F1 (T10 review F1, R15, user instruction) |
| `docs/project/COMMANDS.md` | `make index-lexical` first bullet: only guest/public eligible chunks go in, statistics reveal nothing about other scopes, one file per scope with roles | F1 |
| `docs/project/TECH_STACK.md` | Lexical store line: built from eligible guest/public chunks only; one file per access scope for roles | F1 |
| `docs/project/CURRENT_STATE.md` | Current goal (retrospective PASS, awaiting approval and merge); finalized decisions (BM25 + RRF now implemented, D055); Spec 007 implemented block (retrospective PASS, re-run counts, statistics note); spec row (T10 approved, retrospective PASS); Next step 5; known issues (statistics note split out and completed; T10 F3 `git_state` scope; this round's F1–F3) | implemented reality; F1; MINOR findings go under known issues |
| `.kiro/specs/007-hybrid-retrieval/design.md` | `## As-built notes`: five retrospective notes (`baseline.py` `git_state` edit; `query_terms` returns `QueryTerms`; 2.1 file without a lexical object refused at read time; `run_security_evaluation` takes the retrieval config; shared `tests/lexical_support.py`) | F3; deviations that had a change-log line or decision but no As-built note |

`DECISIONS.md` unchanged: D049–D055 match the code (checked against `config/retrieval.yaml`, `fusion.py`, `tokenizer.py`, `store.py`, `compare.py`, `results.py`, `security_eval.py` and the committed result files); no durable choice is unrecorded. `requirements.md`, code, tests, `evaluation/`, `knowledge/` and `config/` not edited.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| `make index-lexical` has `--embedder`, `--output`, `--config`; `bind_to` compares `hash_contract`; relative paths resolve against `--repo-root` | change log 2026-10-25 (T3 round 1); design As-built notes |
| `make index-lexical` target guard via `git check-ignore`; outside a git work tree an un-ignored target is allowed | change log 2026-10-26 (T3 round 3 F1) and 2026-10-28 (T10); design As-built notes |
| `LexicalIdentity` in `retrieval/models.py`; BM25 score `-bm25() + 0.0`; non-object `payload_json` fails closed; one latency span ending after `check_hit` (dense clock moved) | change log 2026-10-27 (T4 round 1); design As-built notes |
| `FusionConfig` in `fusion.py`; `HybridRetriever` takes `Retriever` legs | change log 2026-10-28 (T5 round 2); design As-built notes |
| `RetrievalResult.leg_document_ranks` (hybrid only) for document-level 2.1 `leg_ranks` | change log 2026-10-28 (T6 round 2); design As-built notes |
| Embedder compared as a (model, revision) pair; 2.1 bm25/hybrid file without a `lexical_index` object refused | change log 2026-10-28 (T7 round 1); D054; design As-built note added this round |
| `run_security_evaluation` has no built-in fusion default; `_gate` typed `Retriever` | change log 2026-10-28 (T8 round 1); D053; design As-built note added this round |
| `retrieval/baseline.py` `git_state` changed (design "Not changed" list and the tasks.md rule name `baseline.py`) | change log 2026-10-28 (T9 round 1 F1); design As-built note added this round (F3) |
| T2 result `git_commit` is `b024f5d`, not the T1 commit | T2 user decision (`CURRENT_STATE.md`) |
| BM25 and hybrid T9 files have `git_dirty: true` | T9 user decision (`CURRENT_STATE.md`, D055) |
| `.claude/settings.json` learning-notes permissions | not approved in the spec: F2 |

### Cross-task consistency

- One authorization source: both legs take the same `ResolvedAccess`; `build_access_filter` (Qdrant) and `build_sql_access_clause` (SQLite) sit side by side in `retrieval/access.py` and are the only builders; both legs call `check_hit` per hit; `HybridRetriever` has no `try`/`except`, so any leg error fails the query (D040). The security gate and the Docker test run the production retrievers through `build_retriever`, never their own filters (only the unfiltered sanity SELECT is harness SQL).
- One strategy vocabulary: `Strategy` (`StrEnum`) feeds `--strategy` choices, `build_retriever` (value comparison after `Strategy(...)` since T5 round 2), result `retrieval_strategy`, the security result's `strategies` and violations.
- One request check: `validate_request` (`retrieval/base.py`) is shared by dense, BM25 and hybrid; one latency rule (span ends after the last `check_hit`) applies to every leg, so per-leg latency in 2.1 results is comparable.
- One lexical identity: `LexicalIdentity` (label, tokenizer name and version, digest, chunk count) is produced by `BM25Retriever`, carried by hybrid, written to 2.1 results and compared by `eval-compare` (label and chunk count excluded from identity, as D054 says).
- One builder for production and the security gate: `security_index.py` uses `production_entries` and `build_lexical_index`, then the production `LexicalIndex.open` and `bind_to`.
- Defaults read from one place: tests that depend on the default strategy read `config/retrieval.yaml` (T9), and the security gate takes the loaded config (T10).
- No duplicated logic found: metrics still come only from `retrieval/metrics.py` (`dedupe_documents` reused by hybrid).

### Scope-drift review

- No graceful degradation, no BM25 run without Qdrant, no Qdrant sparse vectors, BGE-M3 sparse weights or server-side fusion, no stemming, stopwords or legacy-chillu mapping, no reranker, HTTP route, Langfuse, CI or non-guest role in the diff.
- No Phase 2 work: no "compare shared cases" mode, no new Knowledge Release, no candidate activation beyond the six R1 promotions.
- No speculative abstractions beyond the design: `Retriever` Protocol and `build_retriever` are the designed seams; `leg_document_ranks` was added by an approved amendment.
- All spec-file edits after approval are recorded in the `## Change log` (14 dated lines); `tasks.md` boxes added by amendments match them.
- One unrecorded non-product change: `.claude/settings.json` (F2).

### Patterns in `task-reviews.md`

- 14 review rounds over 10 tasks: 11 PASS, 3 FAIL (T3 round 2: case-insensitive APFS bypass of the protected-folder guard, MAJOR; T5 round 1: best-rank tie-break not pinned, MAJOR; T6 round 1: hybrid `leg_ranks` were chunk positions of the fused top-k only, MAJOR). All three were caught by reviewer probes (an end-to-end write, a mutation of the sort key, a reading of the design's R9 against the data actually written) rather than by the implementer's tests.
- Implementer Sonnet 5.5, reviewer Opus 5.5 on every task. Recorded usage: 27 entries, about 3.36M tokens in total (T8 review not measured after an API error); implementer runs 87K–193K, reviews 104K–161K.
- Findings were deferred as explicit task boxes through planner amendments (T6, T7, T8, T9 and 18 boxes in T10) instead of a running list; this kept each deferral traceable to a change-log line, and every box is closed.
- Real-run hygiene repeated as a theme: the T2 `git_commit` and T9 `git_dirty` deviations both came from run order, and T10 fixed the second in code.

### Remediation required

None. F1 reconciled in this round; F2 and F3 are MINOR and recorded under known issues in `CURRENT_STATE.md` (F3 also in the design As-built notes). No RM tasks; no SPEC_DEFECT that needs `spec-planner` before merge.

### Notes for the next spec

- **Graceful degradation (roadmap 13) starts from here.** BM25 must run without Qdrant and without the `bge-m3` extra before it can be the FTS5 fallback. The lexical file's `dense_identity` copy is the starting point: the Qdrant binding becomes optional on the fallback path only, with the same `ResolvedAccess`, `build_sql_access_clause` and `check_hit`. Today `HybridRetriever` fails the whole query on any leg error by design (D052); a fallback must be an explicit, tested switch, not a catch inside fusion.
- **The lexical file is now a prerequisite of the default.** With `default_strategy: hybrid`, `make retrieve` and `make eval-retrieval` without `--strategy` need `make index-lexical` after every content-changing `make ingest` (a stale file is refused by the chunk digest). An automatic rebuild or a freshness check on ingest is a candidate for the fallback or an ops spec; the HTTP route spec must decide what a missing or stale lexical file does at startup.
- **Roles and BM25 statistics.** Today only eligible guest/public chunks are indexed, so corpus-wide IDF and average length reveal nothing. A roles spec needs one lexical file per access scope (D050 named an accepted statistics leak as the alternative; the user's instruction for this round prefers per-scope files) and must extend the security gate's forbidden lexical rows to the new scopes; the security result's `access.role` is still hard-coded `guest` (D047).
- **Malayalam lexical matching (roadmap 8).** `lexical-v1` has no stemming: BM25 alone lost `g067`–`g069`, and `g064`/`g065` ranked only on the Latin `NAATI`/`CCL`; hybrid keeps every `ml` hit but `ml` MRR drops 0.9167 -> 0.7917 (6 cases, small sample). Legacy chillu sequences stay distinct from atomic chillu (D051). Any analyzer change needs a new tokenizer version and a rebuild (bound in the file).
- **Observation only, no action:** the T6 review F2 idea (a stopword list or a minimum BM25 score / IDF floor) was not triggered: the R13 rule held and none of the four cases where hybrid ranks a relevant document lower than dense (`g006`, `g029`, `g064`, `g065`) had only very common term matches. Keep it as a hypothesis if a larger corpus shows common-term noise from the BM25 leg.
- **Reference results for the next spec.** Suite `public-eval-v2` v2: dense `…20261025T134659Z.json` (T2) and `…20261028T122835Z.json` (2.1), BM25 `…20261028T123109Z.json`, hybrid `…20261028T123121Z.json` (68/69, MRR 0.9094). `g061` misses in all three strategies (dense rank 6, BM25 9): a reranker or chunking spec should look at it first. The v1 2.0 file is a closed reference.
- **Run hygiene.** `git_state` now ignores untracked files under `experiments/results/`; still commit or move results between real runs, and keep the tree (including `graphify-out/`) clean before a run.
- **Still deferred:** the Phase 2 "compare shared cases" mode; `seed-v1` still names suite v1 (Phase 2 releases); device pinning (D038); `relevant_section_ids` (roadmap 7); the shallow-clone skip of the T1 byte-identity tests (CI spec); the open Spec 004 nits and Spec 006 retrospective F1.

### Final handoff

`PASS`. No BLOCKING or MAJOR findings; three MINOR findings (F1 reconciled in this round; F2 and F3 recorded under known issues, F3 also as design As-built notes). Documentation reconciled in `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `CURRENT_STATE.md` and the design As-built notes; `DECISIONS.md` needed no change. No RM tasks. All changes are uncommitted for the orchestrator to commit after the user's approval. Merging `spec/007` into `main` can proceed once the user approves this round (and decides F2). No `Status:` was set to verified.

### User decision (2026-10-28)
- Round 1 approved. F1 and F3 accepted as reconciled. **F2 resolved:** moved to local settings by the user (the three `~/learning/**` permissions are now in the git-ignored `.claude/settings.local.json` and removed from `.claude/settings.json`; that edit is part of the retrospective commit).
