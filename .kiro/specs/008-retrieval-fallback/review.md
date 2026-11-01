# 008 — Retrieval Fallback: Retrospective Review

## Round 1 — 2026-11-01

- **Spec:** `008-retrieval-fallback`
- **Diff reviewed:** `main...spec/008` (head `c5ad39f`, base `f25b552`; 16 commits), `graphify-out/` excluded; plus the orchestrator's uncommitted `Status:` edits to `tasks.md` and `CURRENT_STATE.md`
- **Reviewer host / model:** Claude Code, `claude-opus-5-5` (Opus 5.5), run as a subagent of the orchestrator. Intended tier BEST (`Opus` in `agent-skills/MODEL_PREFERENCES.md`): matches. Fresh session; not the implementer's session (the implementer ran as Sonnet 5.5).
- **Outcome:** `PASS`
- **Usage:** 274K tokens · 60 tool uses · 45:24 (wall clock includes a 600 s stall and a resume)

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | exit 0 | ruff `All checks passed!`, `156 files already formatted`, pyright 0 errors, skills mirrors match (5 skills), `validate-knowledge: OK, 0 problems`, `validate-evaluation: OK, 0 problems`, pytest 1026 passed, 2 skipped (no `bge-m3` extra); Qdrant reachable, so the Docker integration tests ran inside it on throwaway collections |
| `make test-integration` (300 s alarm) | exit 0 | 24 passed, 1004 deselected, 32 s (security integration test parametrized over the five paths) |
| `make eval-security` (twice) | exit 0, `eval-security: PASS` | `paths: dense, bm25, hybrid, hybrid_fallback_open, hybrid_fallback_query`; 74 queries (5 security cases, 69 golden), 5 deferred; results in the git-ignored `experiments/results/tmp/` |
| `make eval-compare` BM25 reference `…20261028T123109Z.json` vs fallback run `…20261101T070658Z.json` | exit 0, PASS | hits 64 -> 64, MRR 0.7082 -> 0.7082; identity line `requested hybrid and was served by bm25`; latency marked `candidate includes failed dense attempt: qdrant_unavailable` (see F2) |
| `make eval-compare` hybrid reference `…20261028T123121Z.json` vs Qdrant-up run `…20261101T070736Z.json` | exit 0, PASS | hits 68 -> 68, MRR 0.9094 -> 0.9094; only a `git_commit` identity line |
| read-only field check of `…T070658Z.json` | as recorded | `fusion` null, `leg_ranks.dense` null per case, `latency_ms.legs.dense_attempt` p50/p95 0.0, `by_served_path` one entry |
| `git diff --stat main...spec/008 -- evaluation/ knowledge/ config/` | 1 file | `config/retrieval.yaml` only (below) |
| `grep` of both CLIs' arguments and `packages/rag/src` for a fallback or fault switch | none | R11: no flag, environment variable or config key forces a fallback |
| `curl localhost:6333/collections` before and after | unchanged | only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings`; the reviewer wrote nothing to Qdrant |
| Real-embedder commands | not run | by instruction; R12 numbers come from the committed user-run files |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 failure classification | `retrieval/errors.py` (`FallbackReason`, `RetrievalUnavailableError` with reason-only message), `retrieval/availability.py` (one `ResponseHandlingException.source` unwrap; explicit `__cause__` only, 10 links, `OfflineModeIsEnabled` excluded), `index.py` `raise_if_unavailable` in `open`/`search`/`document_count`/`chunk_identities`, `retriever.py` wraps only `embed_query` | `test_availability.py` (tables, unrelated-error-during-handling bare and wrapped, missing revision/model ID), `test_index.py`, `test_retriever.py`; design As-built T1 (pinned HF shapes confirmed from wheels) | SATISFIED |
| R2 Qdrant timeouts | `config/retrieval.yaml` 1.1 `qdrant` block, `strategy.py` `QdrantTimeouts` (1..30), `qdrant_client.py` (`timeout=connect_timeout_s`, `check_compatibility=False`), `search(timeout=query_timeout_s)` | `test_strategy.py` validation; stalled-socket tests in `test_index.py` (search and open) and through `open_retrieval` (`test_fallback.py`, 2 s tolerance after T4 F2); `test_qdrant_client.py` | SATISFIED |
| R3 standalone lexical open | `retrieval/identity.py` (`IndexIdentity.expected` without building the embedder), `lexical/store.py` `check_identity`, `opening.py` `open_standalone_lexical` | `test_lexical_standalone.py` (each identity field; constructors patched to raise) | SATISFIED |
| R4 freshness from the repository | `lexical/freshness.py` `verify_fresh` (`production_entries`, `source_chunk_digest`, counts only) | `test_lexical_standalone.py` (fresh passes, edited and removed documents refused); D060 large-corpus caveat | SATISFIED |
| R5 `bm25` without Qdrant or the extra | `bm25.py` `BM25Retriever(identity, lexical)`; `opening.py` `bm25` branch; lazy `bge_m3` import in `ingestion/cli.py` (As-built T3) | `test_bm25.py` characterization; `test_opening.py` (subprocess import pin); `test_strategy_eval.py` CLI with raising factories; T7 Run 3 (user-reported) | SATISFIED |
| R6 hybrid fallback policy | `retrieval/fallback.py` (one `except RetrievalUnavailableError`), `strategy.py` `build_retriever` wraps `hybrid`, `opening.py` open-time `except` (re-raises for `dense`); `fusion.py`/`hybrid.py` unchanged | `test_fallback.py` (21 tests: open, per-query, retry count, same `access` object, hits equal `bm25`, non-eligible, BM25 error, authorization in either leg, closed port, stalled port); `git diff main...spec/008` of `fusion.py`/`hybrid.py` empty | SATISFIED (open-time outage lasts for the run: F1; `bind_to` scroll path untested end to end: F5) |
| R7 marking | `models.py` `requested_strategy`, `fallback_reason`; `retrieval/cli.py` `_strategy_line` and stderr `WARNING` | CLI tests; T4 manual throwaway runs | SATISFIED (header only on fallback, As-built T4 (a)) |
| R8 result 2.2 | `evaluation/retrieval_eval.py` (2.2 keys, `by_served_path`, `index_settings=None` only for served `bm25`) | `test_retrieval_eval.py`, `test_strategy_eval.py`, `dense_equivalence.py`; T7 files | SATISFIED (open-time vs per-query not distinguishable: F2) |
| R9 `eval-compare` by served strategy | `evaluation/results.py` (served strategy, mixed refusal with `served_strategies`, embedder pair from `dense_identity`), `compare.py` | `test_compare.py` (mixed incl. unanswerable-only, standalone `bm25` vs 2.1, revision refusal, committed reference); both T7 compares re-run above | SATISFIED (requested/served line only when they differ, As-built T5 (a)) |
| R10 security gate | `evaluation/security_eval.py` five paths, `_UnavailableDense` harness-only, result 1.2; `security_index.py` carries chunker and seed repository | `test_security_eval.py`, `test_security_integration.py`; `make eval-security` PASS (re-run) | SATISFIED (standalone `bm25` path uses a seed-subset check, As-built T6 (a)–(c)) |
| R11 fault injection and isolation | constructor/factory seams only; closed-port and stalled-socket tests | grep above; `make verify` without Docker dependence for unit tests, extra or model; `make test-integration` 24 passed | SATISFIED |
| R12 real runs | `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json`, `…T070736Z.json` (committed in `3403261`) | compares re-run above; T7 review field checks; Run 3 user-reported | SATISFIED (closed port and Run 3 not file-backed, recorded as user-reported) |
| R13 unchanged behavior, protected paths | ingestion only the two recorded moves; lexical format and `lexical-v1` unchanged; dense/hybrid ranks unchanged (equivalence fixture, T7 run 2) | `make verify`; protected-path diff; legacy snapshot test untouched | SATISFIED |
| R14 docs and decisions | D056–D062, ROADMAP item 13 note, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `CURRENT_STATE.md` | read against the code by the T8 reviewer and this round; F1/F2 wording reconciled here | SATISFIED (after this round's reconciliation) |
| Definition of Done | all of the above | this round | SATISFIED, pending the user's approval and merge (F3 change-log lines are the user's call) |

### Protected-data check

`git diff --stat main...spec/008 -- evaluation/ knowledge/ config/` → `config/retrieval.yaml | 5 ++++-` only: `schema_version` `"1.0"` → `"1.1"` and the `qdrant` block (`connect_timeout_s: 2`, `query_timeout_s: 3`). Required by R2 (T1) and allowed by R13. Nothing under `evaluation/` or `knowledge/`. No unrequired change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION (docs) | R6, R14 / T4, T8 | An open-time outage lasts for the whole run: `open_retrieval` returns `FallbackRetriever(None, BM25Retriever(expected), reason)` (exactly the design's `hybrid` open row), so no later query tries Qdrant again. D058 ("every query tries the primary again"), `ARCHITECTURE.md` and `COMMANDS.md` ("Every query tries Qdrant again") stated the per-query retry without that condition. **Reconciled in this round**; D058 gets a clarifying sentence, the policy is unchanged. For a server this is a startup/reopen question (Notes). |
| F2 | MINOR | SPEC_DEFECT | R8, R9 / T5 | Result 2.2 cannot tell an open-time fallback from a per-query one: both write the `bm25+fallback:<reason>` path, and after an open-time fallback `leg_latency_ms.dense_attempt` is about 0 ms because nothing was attempted, while `eval-compare` still prints "includes failed dense attempt". `CURRENT_STATE.md` item 6 read the 0 ms as "the cost of a refused connection". The doc wording is corrected here (`CURRENT_STATE.md`, `COMMANDS.md`); a field such as `fallback_stage: open | query` is left to the HTTP route or observability spec. |
| F3 | MINOR | SPEC_DEFECT (process) | WORKFLOW / T1, T3, T4, T5, T6 user decisions | Post-approval amendments have no dated `## Change log` line in `requirements.md` (WORKFLOW.md "Approved amendments are recorded as dated lines"; the change log holds only the 2026-10-29 pre-task line): the T3 box (retrieval integration tests use `retrieval_client_factory`, T1 F3), two T5 boxes (T3 F2/F3), T8 boxes (T3 F1, T2 F3, T4 F4 and the lifecycle item, T5 F3, T6 F1), the design "Not changed" list correction and the two design R8 bullets. Each rests on a verbatim user decision in `task-reviews.md`, and the edited texts cite their review IDs, so nothing is unrecorded; only the change-log convention was skipped (Spec 007 kept 14 lines). The reviewer may not edit `requirements.md`. **Resolved 2026-11-01 (user decision):** `spec-planner` added eight dated change-log lines to `requirements.md`, each citing its `task-reviews.md` decision. |
| F4 | MINOR | IMPLEMENTATION | R3–R6 / T3, T4 | `open_retrieval`'s `bm25` branch and `_open_fallback` duplicate the standalone open, the `IndexIdentity.expected` call and the lexical `document_count` closure. Behavior agrees today; fold them into one helper when the HTTP route reworks `open_retrieval` (with the client-lifecycle fix). |
| F5 | MINOR | IMPLEMENTATION (test gap) | R6 / T4 | Design R6 lists "`bind_to`'s scroll" as an open-time fallback trigger. The code covers it (`bind_to` calls `DenseIndex.chunk_identities()`, which maps transport errors since T1, inside the `try` of `open_retrieval`), but no test drives that path through `open_retrieval`; the T4 implementation note even calls `bind_to` "file-only", which is inaccurate. Composition holds; add the test when `open_retrieval` is next touched. |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/DECISIONS.md` | D058: one clarifying sentence (marked as the retrospective's): the per-query retry applies after a successful open; an open-time outage serves the whole run by BM25 with `dense_attempt` about 0 ms | F1; D058 is this spec's own decision, policy unchanged |
| `docs/project/ARCHITECTURE.md` | "Retrieval fallback" policy bullet: open-time outage lasts for the opened retriever; startup and reopen policy for the HTTP route | F1 |
| `docs/project/COMMANDS.md` | fallback paragraph: retry only after a successful open; `make retrieve` "needs Qdrant" bullet: only `dense`/`hybrid` need Qdrant, `bm25` only the lexical file; `eval-compare` latency label: about 0 ms after an open-time fallback, 2.2 does not record the stage | F1, F2; the "needs Qdrant" bullet contradicted R5 |
| `docs/project/CURRENT_STATE.md` | Current goal, finalized-decisions line, Spec 007 block (merged, not "on `spec/007`"), Spec 008 block (T1–T8 approved, retrospective `PASS`, re-run counts, open-time note), Spec 007 row tail (merged), Spec 008 row (retrospective `PASS`, T8 approved), Next step item 6 (`dense_attempt` explanation), new item 8, known issues (this round's F1–F5) | implemented reality; F1, F2; MINOR findings go under known issues |
| `.kiro/specs/008-retrieval-fallback/design.md` | `## As-built notes` → "Retrospective round 1": open-time fallback lasts for the run and 2.2 does not record the stage; `bind_to` scrolls Qdrant (T4 note inaccurate, path untested end to end); duplicated wiring; the two post-approval design edits and where they were approved | F1, F2, F3, F4, F5 |

`TECH_STACK.md` and `ROADMAP.md` unchanged: they match the code (no new dependency; `qdrant-client` usage through `retrieval_client_factory` and the item 13 note are correct). `requirements.md`, code, tests, `evaluation/`, `knowledge/` and `config/` not edited.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| `ingestion/cli.py`: `bge_m3` import moved inside `build_embedder` (tasks rule said `ingestion/` not edited) | T3 review F1, user decision 2026-10-31; design As-built T3; "Not changed" list corrected (F3: no change-log line) |
| `run_retrieval_evaluation(index_settings=...)`; `None` only for a served `bm25` | T3 review F2, user decision; T5 box; design R8 bullet and As-built T3 |
| `make retrieve` prints the `strategy:` fallback line only on fallback; `requested_strategy` set by `FallbackRetriever`; `fallback` typed `Retriever` | T4 review F4, user decision 2026-10-31; As-built T4 |
| `eval-compare` prints requested-vs-served only when they differ; mixed-refusal message shape | T5 review F1/F3, user decision 2026-11-01; As-built T5 |
| Security `bm25` path: seed-subset check instead of `verify_fresh`, separate handle, `from_dense` identity; `security_index.py` edited (not in the placement table) | T6 review F1, user decision 2026-11-01; As-built T6 |
| Plain `hybrid` security path asserts no fallback (harness error otherwise) | T6 review F3, user decision (fix at commit) |
| Retrieval integration tests use `retrieval_client_factory` (T3 box) | T1 review F3, user decision 2026-10-31 (F3: no change-log line) |
| Qdrant client not closed on every open failure nor in `OpenedRetrieval.close()` | T4 user decision: carried to the HTTP route spec (design hand-off, `CURRENT_STATE.md`) |
| Open-time fallback serves the whole run (no per-query retry) | not a deviation (design `hybrid` open row); docs overstated: F1 |

### Cross-task consistency

- **One eligible error, one catch site per layer.** `RetrievalUnavailableError` is raised only by `classify_qdrant_error`/`classify_model_error` (through `raise_if_unavailable` and the `embed_query` wrap) and caught only twice: `FallbackRetriever.retrieve` (one `except`) and `open_retrieval` (one `except`, re-raised unless `hybrid`). The `except Exception` clauses in `index.py` and `retriever.py` re-raise after classification; `_close_quietly` swallows only errors from closing a failed client; `retrieval/cli.py` catches only to print a class name and exit 2. No path catches a broader exception for fallback, and `__context__` is never followed (grep). The retrospective notes in `tasks.md` asked for exactly these two checks.
- **One open path.** `open_retrieval` serves both CLIs; the security gate builds the same retrievers through `build_retriever` and the production `bind_to`/`check_identity`. The only duplication is inside `opening.py` (F4).
- **One identity value.** `IndexIdentity` (`from_dense` or `expected`) feeds `BM25Retriever` headers, `require_real_index`, the 2.2 `dense_identity` block and `eval-compare`'s embedder pair; `check_identity` and `bind_to` share `chunk_set_difference` and keep separate messages.
- **One authorization source on every path.** The fallback BM25 is the plain `BM25Retriever` with the caller's `ResolvedAccess` object (asserted with `is`), `build_sql_access_clause` and `check_hit`; the security gate proves it on both fallback paths at `top_k` 50 with forbidden rows nearest.
- **One reason vocabulary.** `FallbackReason` values appear unchanged in results, CLI output, 2.2 `fallback_counts`/`by_served_path` keys and the security gate's vacuity check; no exception text reaches output.
- **Record accuracy.** The T4 implementation note says `bind_to` is file-only; it scrolls Qdrant (F5). The T7 note on `dense_attempt` misread an open-time 0 ms (F2). Both corrected in docs.

### Scope-drift review

- No circuit breaker, retry loop, health probe, cached failure state or fallback from BM25 to anything (R6, out of scope list).
- No HTTP route, Langfuse, metrics, reranker, generation, stemming, tokenizer change, chunking change, new `index_version` or re-ingestion.
- No Phase 2 work, no new evaluation cases, no new dependency (`pyproject.toml`, `uv.lock` unchanged).
- `ingestion/` touched only by the two recorded moves; `fusion.py`, `hybrid.py`, `access.py`, `baseline*.py`, `lexical/build.py`, `lexical/tokenizer.py` unchanged.
- Spec-file edits after approval are all traceable to verbatim user decisions in `task-reviews.md`, and, since 2026-11-01, to dated change-log lines (F3 resolved).

### Patterns in `task-reviews.md`

- 8 tasks, 8 review rounds, all `PASS` on round 1 (Spec 007: 14 rounds, 3 `FAIL`). 28 MINOR findings in total; none BLOCKING or MAJOR. Resolution mix: fixed at commit (T1 F2, T3 F4, T4 F1/F2, T5 F1/F2, T6 F3, T7 F1/F2, T8 F1–F3), moved into later task boxes (T1 F3, T3 F1–F3, T4 F4, T5 F3, T6 F1), accepted (T1 F1, T2 F2/F3, T4 F3, T6 F2/F4), and carried to the next spec (T2 F2 `asyncio.run`, T4 client lifecycle).
- Repeated finding: `graphify update .` not run by the implementer after code changes (T2 F1, T3 F5, T4 F5, T6 note, T8 F3); the orchestrator ran it before each separate graph commit. The task rule and the actual division of labour disagree; consider moving the rule to the orchestrator.
- Repeated theme: live counts and record accuracy (T3 F4 literal 13, T7 F1 user-reported facts stated as file-checked, T8 F1 stale "untracked"), all caught by reviewers reading the files rather than the implementer's summary.
- Implementer Sonnet 5.5, reviewer Opus 5.5 on every task. Recorded usage: implementer runs 136K–190K (6 of 8 measured; T6 ended with an API error, T7 not recorded), reviews 118K–164K (8 measured); about 2.14M tokens over the 14 measured entries.
- One unexplained 14-minute hang of `make test-integration` (T1), not reproduced since; the T3 box made retrieval integration clients time out, and every later integration run (including this round, 32 s) finished normally.

### Remediation required

None. F1 and F2 reconciled in docs this round; F3–F5 are MINOR and recorded under known issues in `CURRENT_STATE.md` and the design As-built notes. No RM tasks. F3 was for the user (resolved 2026-11-01: change-log lines added): accept the `task-reviews.md` record, or have the orchestrator/`spec-planner` add the missing dated change-log lines before the merge.

### Notes for the next spec

The next spec on the roadmap path that consumes this one is the HTTP retrieval route (or whichever spec first runs retrieval in a long-lived process). Carry-overs:

- **Open once, then what? (startup and reopen policy).** Today an open-time outage makes BM25 serve the whole process (F1), which is right for a CLI run and wrong for a server: Qdrant may come back. The route spec must decide whether to reopen the dense side (on a timer, or lazily after a cool-down) and how that interacts with the circuit breaker below. It must also decide what a missing or stale lexical file does at startup: refuse to start, start dense-only, or start degraded.
- **Circuit breaker.** No circuit breaker exists (D058): with Qdrant hanging after a successful open, each hybrid query waits about `query_timeout_s` (3 s; theoretical bound 3 times that), and a model load failure retries on every query. A server needs a breaker (after N eligible failures, skip the dense leg for a cool-down and serve BM25 directly) whose state is shared across requests, with a test using the stalled-socket helper.
- **Qdrant client lifecycle.** `open_retrieval` closes the client only on the hybrid fallback path, not on every open failure (for example a `dense` `RetrievalUnavailableError`, an `IndexBindingError`, a stale lexical file under `bind_to`), and `OpenedRetrieval.close()` closes only the lexical handle. A long-running server leaks a connection pool per failed open. Fix both, with a test; fold the duplicated standalone wiring (F4) in at the same time and add the `bind_to`-scroll fallback test (F5).
- **Async freshness.** `verify_fresh` uses `asyncio.run` around `production_entries`, so it cannot run inside an event loop (FastAPI). Either run the check at startup outside the loop or add an async variant; do not call it per request.
- **Freshness cost.** Each standalone open rereads, chunks and hashes every eligible document (D060): milliseconds for 13 documents, seconds for thousands, paid at every start. Options: a persisted per-document `content_hash` manifest compared incrementally, or binding to a Knowledge Release snapshot ID (Phase 2).
- **Fallback stage and observability.** Result 2.2 and `RetrievalResult` do not record whether a fallback happened at open time or per query (F2). When traces arrive (roadmap 11, Langfuse), carry `requested_strategy`, served `strategy`, `fallback_reason` and a stage field; a served fallback should be visible to operators, not only in a stderr line.
- **Qdrant 5xx eligibility (D062).** Only transport failures are eligible. Revisit with the route and the breaker: a 503 from a restarting Qdrant is an outage in practice, but a 500 can be a bug; whatever is chosen, keep the single mapping site (`classify_qdrant_error`) and the fail-closed default.
- **API surface.** The route must keep the fixed reason vocabulary in responses (never exception text, which can carry the Qdrant URL), keep exit-2-style refusals as typed errors, and resolve access on the server only (no client-supplied role, scope or tenant). The security gate's five paths are the model for the route's own authorization tests.
- **Authorization invariant for any later fallback** (reranker, generation): take the same `ResolvedAccess`, filter inside the fallback's own query, `check_hit` every hit, and never catch `RetrievalAuthorizationError` (ARCHITECTURE "Retrieval fallback"). `FallbackRetriever` is generic over two `Retriever`s and can be reused for the reranker path of roadmap 13.
- **Reference results for the next spec** (suite `public-eval-v2` v2, `w2a-realcheck-idx-v1`, BAAI/bge-m3 @ `5617a9f`): fallback-only 2.2 `…20261101T070658Z.json` (64/69, MRR 0.7082, equal to the Spec 007 BM25 reference) and Qdrant-up 2.2 `…20261101T070736Z.json` (68/69, MRR 0.9094, equal to the Spec 007 hybrid reference; latency p50 86.2 ms vs 80.3 ms, informational).
- **Process.** Record every post-approval task box or design edit as a dated `## Change log` line in `requirements.md` (F3). Decide who runs `graphify update .` after code tasks (the implementer rule was skipped in five tasks and done by the orchestrator each time).
- **Still deferred from earlier specs:** per-scope lexical files (roles spec, D050); Malayalam stemming and the legacy chillu sequence (roadmap 8, D051); `g061`, a miss in every strategy (reranking or chunking); `relevant_section_ids` and chunking (roadmap 7, now behind this spec, D056); `freshness.py`'s private `_identity` import from `build.py` (make public when `build.py` is next touched); device pinning (D038); the open Spec 004 nits and Spec 006 retrospective F1.

### Final handoff

`PASS`. No BLOCKING or MAJOR findings; five MINOR findings (F1 and F2 reconciled in docs this round; F3–F5 recorded under known issues in `CURRENT_STATE.md` and in the design As-built notes). Documentation reconciled in `DECISIONS.md` (D058 clarification), `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md` and the design As-built notes; `TECH_STACK.md` and `ROADMAP.md` needed no change. No RM tasks. All changes are uncommitted for the orchestrator to commit after the user's approval. Merging `spec/008` into `main` can proceed once the user approves this round (and decides F3). No `Status:` was set to verified.
