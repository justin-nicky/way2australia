# 013 — HTTP Route and Serving Policy: Retrospective

## Round 1 — 2026-11-27

- **Spec:** `013-http-serving`
- **Diff reviewed:** `main...spec/013` (base `1e27909`, head `d042ce5`), excluding `graphify-out/` (rebuilt by `graphify update .` just before this round, uncommitted) and the four uncommitted `spec-implementer/SKILL.md` copies (the user's separate chore, not spec work)
- **Reviewer host / model:** Claude Code subagent / `claude-opus-5-5` (BEST tier `Opus` in `MODEL_PREFERENCES.md`, matches; fresh session that implemented no task)
- **Outcome:** `PASS`
- **Usage:** 206K tokens · 38 tool uses · 8:02

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `HF_HUB_OFFLINE=1 make verify` (once) | exit 0 | ruff check clean; ruff format 264 files already formatted; pyright 0 errors, 0 warnings; skills-check: 6 mirrors match; validate-knowledge OK, 0 problems; validate-evaluation OK, 0 problems; pytest 1948 collected, 1943 passed, 5 skipped, 3 warnings (214.98 s; Docker integration tests ran against a reachable local Qdrant) |
| `HF_HUB_OFFLINE=1 make eval-security` (DoD) | PASS in 19213 ms | `experiments/results/tmp/security-evaluation-20261127T120153Z.json`; deferred s001/s007/s009 (`roadmap-12`), s005/s006 (`roadmap-10`, stale owner label, Spec 012 F3 carry-over) |
| `git status --porcelain -- evaluation knowledge config` | empty | no uncommitted protected-path change |
| Real smoke check (R16, R17) | recorded by the user | `task-reviews.md` T8 "User-run smoke check (recorded 2026-11-27)": ready `ok` ≤ 46 s after start; answerable 200 `answered` 4241.8 ms; unanswerable 200 `insufficient_evidence` 3878.4 ms; optional breaker step not run |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 configured stack | `serving/stack.py` (`resolve_serving_choices`: `default_strategy`, `rerank.enabled`, `default_generator`); `retrieval/opening.py` (`_open_standalone` shared, early `top_k > rerank.depth` refusal); `evaluation/cli.py` (depth per served path) | `test_opening_lifecycle.py`; `test_strategy_eval.py` (depth 50 after open-time fallback); `tests/serving/test_stack.py` (config opposite to defaults, generator from `default_generator`, T6 box) | SATISFIED |
| R2 lifecycle | `OpenedRetrieval.client`, idempotent `close()`; `StackHolder.close()`; lifespan generator ownership | failure-step close tests (T1); lexical close once (T2); stack and shutdown counters (T5, T6); generator closed once on phase 1/2 failure and shutdown (T6) | SATISFIED |
| R3 lexical startup | `LexicalIndex.check_tokenizer` on standalone and bound paths; `run_sync` in `lexical/freshness.py`; phase 1 in `lifespan.py` | `test_lexical_runtime.py` (tokenizer, freshness inside a running loop); `test_serving_startup.py` (missing file, tokenizer mismatch) | SATISFIED |
| R4 circuit breaker | `retrieval/breaker.py`; `FallbackRetriever(breaker=…)`; CLIs pass none | `test_breaker.py` (fake clock, single probe among 8 threads, D062 not counted, access/`lote` spy); `make eval-security` | SATISFIED |
| R5 Qdrant down at start, re-admission | `StackHolder` BM25-only start with a breaker created open; `try_reopen_dense` via `open_retrieval(hybrid)` (identity, settings, tokenizer, `bind_to`); embedder retry; swap and drain | `test_stack.py` (match, mismatch refused, probe failure, embedder retry, drain); `test_concurrency.py` (swap during 16 requests) | SATISFIED (against in-memory Qdrant; see F3; freshness not re-run, As-built note) |
| R6 hard cap and budget | `generation/deadline.py` (`run_with_cap`, daemon thread); `AnswerService` `_cap`, `min_generation_s`; adapter `min(config, call)`; `config/generation.yaml` comments | `test_deadline.py`, `test_service.py` (blocking generator, budget, adapter, CLI cap, no hang); route abandoned-slot test (T7) | SATISFIED (budget bounds generation only; see F2) |
| R7 concurrency | sync `def` route; `LockedEmbedder` / `LockedReranker`; one locked `check_same_thread=False` read-only connection; breaker and holder under locks; D092 | lexical 8-thread test (T2); lock overlap by events (T5); 16 concurrent requests on BM25 and hybrid (T8) | SATISFIED |
| R8 readiness | `serving/readiness.py`; `api/ready.py`; two-phase lifespan; `/health` unchanged | `/ready` `starting`, `ok`, each `degraded` reason, `failed` + `on_fatal`; `abandoned_generation` (T7) | SATISFIED |
| R9 route and validation | `api/answer.py`, `contract.AnswerRequest` (extra forbidden), `BodySizeMiddleware` | 422 cases, 413 with and without `Content-Length`, all three statuses 200 (`test_answer_route.py`) | SATISFIED |
| R10 cap and overload | `slots.py` (`SlotPool`, `Slot.transfer`) | busy and not-ready 503 with `Retry-After`; release on success and error; slot held by abandoned work | SATISFIED |
| R11 public contract | `contract.py` (`AnswerContract` 1.0, `PublicStatus`, `PublicReason`, `_STATUS`/`_REASON`, `to_contract`) | pin test, enum coverage, mapping per status and reason, OpenAPI check | SATISFIED |
| R12 error mapping | `errors.py`; route-built 500 with request ID and class only; `ServingNotReadyError` → 503 | 422 without echo; 500 for authorization, configuration and applicability errors (T7 round 2) | SATISFIED |
| R13 logging | `middleware.py` (uuid4, incoming ID ignored); `logs.py`; D097 | sentinel test (query, `ANTHROPIC_API_KEY`, `QDRANT_URL`, client exception message); client `X-Request-ID` not echoed | SATISFIED |
| R14 authorization through the route | server-resolved `guest_access`; request model forbids access fields | `test_route_security.py` (hybrid, breaker-open BM25, reranked; access-like fields 422); `make eval-security` PASS | SATISFIED (see F4 on how breaker-open is reached) |
| R15 unchanged behaviour | builders, `check_hit`, `rrf_fuse`, `HybridRetriever`, rerank stage, context builder, prompt, citation validation, outage classification untouched (diff checked: `strategy.py` only threads `breaker` and the tokenizer through; `claude.py` only the per-call deadline) | existing tests unchanged except those named in task reviews (T1 F1, T2 F1); protected-path check below | SATISFIED |
| R16 `make api`, fake mode, smoke | `Makefile` `api`; `W2A_API_FAKE`; `X-W2A-Fake`; readiness `fake`; D101 | fake-mode tests (T6, T7); smoke recorded by the user under T8 | SATISFIED (F1 open carry-over) |
| R17 spec-wide verification | — | `make verify` and `make eval-security` above; smoke recorded | SATISFIED |
| R18 documentation | `ROADMAP.md` items 10 and 13; `ARCHITECTURE.md` "HTTP serving (Spec 013)"; `COMMANDS.md` "HTTP API"; `DECISIONS.md` D092–D101; `CURRENT_STATE.md`; design As-built notes | T9 review and this round's reconciliation | SATISFIED |

Definition of Done: every R1–R18 traced (above); every task approved and committed on `spec/013` with a `Spec-Task: 013/T<n>` trailer (`21978c8` … `d042ce5`); `make verify` and `make eval-security` pass; the smoke check is recorded; this retrospective passes with the docs reconciled.

### Protected-data check

`git diff --stat main...spec/013 -- evaluation/ knowledge/ config/` →
- `config/generation.yaml` (10 lines): comment-only changes to `model_id`, `backoff_s` and `deadline_s` in both provider blocks; no value or schema change. Required by R6 / T4 (Spec 012 F2).
- `config/serving.yaml` (new, 15 lines): required by T5 (design values; ranges in comments).
- `evaluation/`, `knowledge/`: no change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R16 / T7 (review round 2 F2) | The carry-over stays open: `test_fake_provider_outside_fake_mode_is_refused_at_startup` covers only the generator branch of `_refuse_fake_providers`; the embedder, enabled-reranker and "disabled fake reranker is allowed" branches have no test, and its `generation` parameter is typed `Any` (`apps/api/src/way2australia_api/lifespan.py:177-181`). It was scoped "the next time `lifespan.py` or its tests are touched", and no later task touched them. Behaviour is correct by reading. → Do it in the next spec that touches `lifespan.py`, or as a small chore; listed in `CURRENT_STATE.md`. |
| F2 | MINOR | SPEC_DEFECT | R6 | The per-request budget is "retrieval + context + generation" (R6, design) but only the generation share is enforced: retrieval has no time limit of its own and the embedder and reranker have no inference timeout (D077). The user's smoke run hit it: an idle server's first request spent 40117.8 ms in retrieval and was answered `evidence_only` / `deadline`. R6's acceptance criteria are met as written (the remaining budget caps generation), so this is a gap in the requirement, already recorded as an As-built note and known issue. → Input for the planner of a follow-up (warm-up inference before `ready` or on a timer, and/or a retrieval time share). |
| F3 | MINOR | IMPLEMENTATION | R5, R16 | No live dense re-open or live breaker cycle has been observed: the re-open tests use in-memory Qdrant (T5 review F3), and the optional breaker step of the smoke check was not run. R5's test criteria are met. → Run the optional smoke step (stop Qdrant, see `degraded` / `dense_circuit_open`, restart, see recovery after the cool-down) before relying on recovery in deployment. |
| F4 | MINOR | IMPLEMENTATION | R14 / T8 | The route-level security test reaches "breaker-open BM25" by recording `failure_threshold` failures on an open hybrid stack, not through a BM25-only start (whose `verify_fresh` refuses the synthetic forbidden rows). The served leg is the same `FallbackRetriever` BM25 path, and the standalone `bm25` open is covered by `make eval-security`, so the authorization claim holds; the open-time BM25-only server start is just not exercised with forbidden rows through HTTP. Recorded in the design As-built notes (T8). → None required. |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/HISTORY.md` | In "Closed by Spec 013", labelled the five moved F-numbered bullets with their source: `Spec 012 F2:` (`config/generation.yaml` comments), `Spec 008 F4:` (duplicated standalone open), `Spec 011 F1:` / `Spec 011 F2:` / `Spec 011 F3:` (`retrieval_depth`, `rerank=False` default, late `top_k` refusal); each source taken from the section header the bullet had in `git show d042ce5~1:docs/project/CURRENT_STATE.md`; the intro now says the bullets are verbatim except for that label | T9 review F1 (user request): no bullet starts with a bare `F<n>:` and the two `F2` bullets are distinguishable |
| `docs/project/TECH_STACK.md` | Added "ASGI server: `uvicorn`, from the existing `fastapi[standard]` dependency; `make api` runs it; `apps/api` depends on the workspace package `way2australia-rag`" | The server and the new `apps/api` → `way2australia-rag` dependency (T6) were not in the stack list |
| `docs/project/CURRENT_STATE.md` | "Last updated", Current goal, "Not yet implemented", spec status row and Next step item 1 now say retrospective round 1 PASS and merge awaits the user; added this round's four MINOR findings to "Spec 013 known issues" | Implemented reality after the retrospective; MINOR findings go under known issues (skill rule) |

Checked and left unchanged (they match the code): `ARCHITECTURE.md` "HTTP serving (Spec 013)" and `apps/api` responsibilities; `COMMANDS.md` "HTTP API" (`make api` recipe and defaults `127.0.0.1:8000`, settings, endpoints, status codes, `config/serving.yaml`, tokenizer refusal, hard cap, `retrieval_depth`); `DECISIONS.md` D092–D101 (no durable choice found without an entry); `ROADMAP.md` items 10 and 13; design `## As-built notes` (14 notes; no further departure found).

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| R8 degraded reasons add `dense_reopen_refused` and `abandoned_generation` | `requirements.md` change log 2026-11-13 |
| `make api` recipe uses `$(UV_ENV) $(UV) run` | change log 2026-11-13 |
| Generator ownership by the holder; generator from `default_generator` test | change log 2026-11-21 (T5 review F1, F2) |
| Config-selected fake providers refused unless `W2A_API_FAKE`; `X-W2A-Fake` and readiness `fake` follow `api_fake` only (D101) | T7 review round 2 F1; As-built note; open test gap is F1 |
| Dense re-open does not re-run `verify_fresh` (design listed it; R5 requires identity, settings and binding only) | T9 review "Worth your attention" (1); As-built note; minor, `bind_to` still checks the file against the live collection |
| Lifespan does not join a loader still opening at shutdown | T6 review F1; As-built note |
| Probe request continues on the new stack without a lease | T5 review F4; As-built note |
| `ServingNotReadyError` from a shutdown race → 503 `not_ready` (not in the error table) | T7 review round 1 F4; As-built note |
| Early `top_k > rerank.depth` refusal before any model or client is built (stricter); `eval-retrieval` passes its effective depth | T1 review F2; As-built note |
| Lock-overlap test uses events, not sleeps | T5 review; As-built note |
| Breaker-open BM25 reached by counted failures in the route security test | T8; As-built note; F4 |
| Budget bounds generation only (retrieval has no share) | As-built note (T8 smoke); F2 |

No material unrecorded deviation.

### Cross-task consistency

- **Breaker → holder → route.** T3's `FallbackRetriever(breaker, on_probe)` contract (hook owns `record_failure`/`release`; the retriever records success only while still half-open) is what T5's `StackHolder._probe` relies on, and T8's concurrency test exercises the swap through the route. The breaker is passed only by `open_serving_stack`/`try_reopen_dense`; every CLI open passes none (`build_retriever(..., breaker=None)` default), so D058 holds for the CLIs.
- **Cap → slots → readiness.** T4's `on_abandoned(AbandonedWork)` is T7's `Slot.transfer`, and `/ready` reads `SlotPool.abandoned_in_flight` through the provider registered at startup (T5 readiness model, T7 wiring); the route's `finally: slot.release()` is a no-op after a transfer. Consistent.
- **Tokenizer and lexical open.** T2's `check_tokenizer` sits in both the standalone helper (T1) and `open_bound_lexical`, used by the CLIs, phase 1 and the re-open; one message family (`LexicalIndexBindingError`, names `make index-lexical`).
- **Error families.** Phase 1 prints only `_SAFE_ERRORS` messages (path- and key-free by contract, as `make ask`); the route returns class-only 500s. No contradiction between tasks.
- **Duplicated logic.** None found: one standalone-lexical helper, one cap implementation shared by CLIs and server, one `to_contract`.

### Scope-drift review

- No Phase 2 work, no streaming, no `fallback_stage`, no rate limiting, no internal endpoint, no reranker reload, no Bedrock switch: all stay deferred as the requirements list.
- New code is confined to `packages/rag/src/way2australia_rag/serving/` (reusable lifecycle, no HTTP), additive keyword-only parameters in the library, and `apps/api` (HTTP only). Package boundaries hold (ARCHITECTURE).
- Unrecorded spec edits: none. `requirements.md` changed only through its change log; `design.md` gained only `## As-built notes` (T9); task boxes added after approval (T6) are in the change log.
- Security: access resolved only from server settings; the request model forbids access fields; the validated `lote` reaches only the applicability builder; the public contract carries model text only in `answer` after citation validation; logs hold no query text or hash (D097); fake providers need an explicit setting (D101).

### Patterns in `task-reviews.md`

- Models: implementers Grok 4.7 (Cursor; T1 with a parallel Sonnet session, T2, T3, T4, T8) and Claude Sonnet 5.5 (T5, T6, T7, T9); reviewers Opus 5.5 (T1, T5, T6, T7, T9) and Grok 4.7 (T2, T3, T4, T8). The Grok-reviewed tasks were reviewed by the same model as the implementer because Cursor's BEST and BEST_MINUS_ONE are both Grok 4.7.
- One FAIL: T7 round 1 (MAJOR F1, the 500 log lacked the request ID), fixed in round 2. Every other task passed in round 1.
- "Next time X is touched" carry-overs do not close by themselves when no later task touches X: T6 F2 (rename) closed in T7, but T7 round 2 F2 is still open at the end of the spec (F1).
- T3's implementer could not finish `make verify` (a gitignored `__pycache__` in a skill mirror broke `skills-check`; the verify budget blocked a retry); the reviewer's run passed. T8's smoke-check box was ticked before the user ran the check and was unticked on the user's instruction; the run was recorded on 2026-11-27.
- Commit trailers: every task commit carries `Spec-Task: 013/T<n>`, but in T6–T9 (`fb0a454`, `4577bce`, `a7e0d3b`, `d042ce5`) a blank line separates it from `Co-Authored-By`, so `git log --format='%(trailers:key=Spec-Task)'` finds only T1–T5. Searching the message text (`git log --grep 'Spec-Task: 013/'`) finds all nine. Workflow note for the orchestrator: keep the two lines in one trailer block.
- Token usage per task is in each round; this round's usage is recorded by the orchestrator.

### Remediation required

None. No RM tasks. F2 is a SPEC_DEFECT (MINOR) for `spec-planner` when the follow-up on retrieval time and model warm-up is planned; no planner action is needed before merge.

### Notes for the next spec

- **Retrieval time is unbounded.** The 40 s budget caps generation only. A follow-up should add a warm-up inference before `ready` (and possibly on a timer, since `/ready` only reads state) and/or a retrieval share of the budget; the reranker and embedder still have no inference timeout (D077). Evidence: idle first request, retrieval 40117.8 ms (T8 smoke, 2026-11-25).
- **Live recovery not observed.** Before deployment (item 14), run the optional smoke step that stops and restarts Qdrant, and confirm `dense_circuit_open` → probe → `ok`. The re-open does not re-run `verify_fresh`; if documents can change under a running server in a later phase (S3, releases), add it to the re-open.
- **Open carry-over (F1):** parametrize the fake-provider refusal test over the embedder, enabled reranker and disabled fake reranker, and type `generation: GenerationConfig` in `_refuse_fake_providers`. Make such carry-overs a task box in the next spec rather than "next time the file is touched".
- **Contract 1.0 is pinned** (`AnswerContract`, `PublicStatus`, `PublicReason`); any new field (for example a safe-redirect flag from prompt v2, or usage) needs contract 1.1 or an internal endpoint (item 16), not a silent addition.
- **Prompt v2** inputs are unchanged and now observable through the route: the smoke's unanswerable query came back `citation_invalid` / `model_url`, as in the Spec 012 v4 run. Also: usage on raised outcomes (Spec 012 F1), marker use, g080 answer language, a deterministic safe-redirect flag.
- **Throughput ceiling** is about 1 request per second on the development machine (reranker lock and generation, D092); `max_in_flight` 4 was sized for it. Deployment re-measures on the target device and should revisit `max_in_flight`, `budget.request_s` and device pinning together.
- **`eval-security` owner labels** s005/s006 still say `roadmap-10` (Spec 012 F3); item 10 is now complete with the route, so retarget them when item 12 or prompt v2 runs those cases through the answer path.
- **Breaker-open authorization** is proven through HTTP only on the counted-failures path; a later security spec could build a fresh-consistent forbidden-row corpus so the BM25-only start path is also covered through the route (F4).

### Final handoff

Outcome `PASS` (four MINOR findings, no BLOCKING or MAJOR, no RM tasks). Documentation reconciled in `HISTORY.md`, `TECH_STACK.md` and `CURRENT_STATE.md`; this `review.md` is new. Nothing is committed: `review.md` and the three doc edits stay uncommitted for the orchestrator, alongside the expected `graphify-out/` changes and the user's four `spec-implementer/SKILL.md` copies, which this round did not touch. Merging `spec/013` into `main` can proceed after the user approves this round.
