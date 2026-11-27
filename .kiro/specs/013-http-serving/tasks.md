# 013 — HTTP Route and Serving Policy Tasks

Status: implementing (branch spec/013, base 1e27909)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-11-13; R8 amended at design approval, see its change log). Design: `design.md` (approved 2026-11-13).

Rules for every task:
- **Protected paths.** `knowledge/` and `evaluation/` never change. `config/` changes only as each task's "Allowed protected-path changes" line says. Every task checks `git status --porcelain -- evaluation knowledge config`, and the reviewer compares the output with the allowed list.
- **Unchanged behaviour (R15).** These are not edited: the access and applicability builders, `check_hit`, `check_applicable`, `rrf_fuse`, `HybridRetriever`, the rerank stage and its membership re-check, `ContextBuilder`, the prompt files, `validate_citations`, `classify_error` / outage classification in `generation/claude.py`, `config/retrieval.yaml`, `config/ingestion.yaml`. Existing tests pass with their assertions unchanged, except where a task names the test it changes and why (the `retrieval_depth` correction, the new tokenizer refusal, the hard cap).
- **CLIs keep D058 and D062.** The circuit breaker and the dense re-open exist in the server only; every CLI constructs `FallbackRetriever` without a breaker.
- **`make verify` needs no Docker, PyTorch, extras, network, API keys or model files**, and passes with an empty `HF_HOME` and `HF_HUB_OFFLINE=1`. New tests use fakes (`FakeGenerator`, fake embedder, `FakeReranker`), in-memory or stub Qdrant clients and temporary lexical files. Tests unset `ANTHROPIC_API_KEY` and `AWS_*` variables they could read (autouse fixture).
- **Agents never call Bedrock or the Anthropic API**, never run the real embedder, reranker or generator, never start `make api` against a real collection, and never write to a `w2a-realcheck-*` or `way2australia-*` collection. Real runs and the smoke check are user-owned.
- **Verify budget.** At most two `make verify` runs per agent session: iterate with targeted `uv run pytest <paths>` and `make lint typecheck`, then run `make verify` once at the end of the task.
- **Threads in tests.** Every test that starts threads joins them or releases their blocking events before it ends, with a timeout; no test sleeps longer than 1 s in total; timing assertions use generous tolerances (at least 0.5 s) or an injected clock.
- **No secrets and no query text** in code, config, fixtures, logs or docs. Messages and log lines name fields, codes, states and class names only, never chunk text, query text, paths, URLs or credentials.
- **Library documentation.** FastAPI, Starlette, uvicorn and httpx behaviour the code relies on (lifespan, threadpool for `def` routes, ASGI middleware, `RequestValidationError` handlers, httpx timeouts) is checked against current documentation; record the URLs and versions in the task hand-off where a task relies on them.
- **`lote` stays outside `AccessContext`** (C4, D072); access is resolved only by `resolve_access(guest_access(settings))`.
- **Graph once per spec (D080).** Tasks do not run `graphify update .`; `spec-orchestrator` runs it once after the last task approval. The graph reflects `main` at the start of the spec, so read files changed earlier in this spec directly.
- **Amendments.** Any task box or design edit added after approval gets a dated `## Change log` line in `requirements.md`.
- **`task-reviews.md`** is edited only by exact, targeted edits.

## T1 — Retrieval opening rework and client lifecycle

**State:** approved (2026-11-14)
**Requirements:** R1, R2, R15

- [x] `retrieval/opening.py` per design "Retrieval opening rework":
  - one `_open_standalone` helper used by the `bm25` branch and `_open_fallback` (Spec 008 F4);
  - keyword-only `top_k: int | None = None`: with `rerank=True` and `top_k > rerank.depth`, raise `RetrievalConfigurationError` before `reranker_factory` is called (Spec 011 F3);
  - `OpenedRetrieval.client`; one `try` around `DenseIndex.open`, lexical bind, reranker load and `build_retriever` that closes the client and any opened lexical file on any exception; `close()` closes lexical then client and is idempotent.
- [x] `make retrieve`, `make eval-retrieval`, `make ask`, `make eval-generation` pass their effective `top_k` (or depth) to `open_retrieval`.
- [x] `evaluation/cli.py`: `retrieval_depth` is `rerank.depth` only when the opened stack has a loaded reranker on a dense-capable path; after an open-time fallback it is `fusion.candidate_depth` (Spec 011 F1). No result version bump (design). Update the one existing test that asserts depth 20 in that case, naming the finding in its docstring.
- [x] Tests (`packages/rag/tests/retrieval/test_opening_lifecycle.py` and existing files): a failure injected at each step (dense open, lexical bind, reranker load, `build_retriever`) closes the client and any lexical file (stub client with a `close` counter); `close()` twice is safe and closes once; `top_k > rerank.depth` refused with zero reranker factory and load calls; the standalone path is shared (one helper; existing `bm25` and fallback tests unchanged); `eval-retrieval` records `retrieval_depth` 50 after an open-time fallback with reranking requested.

Allowed protected-path changes: none.

### Verification

- `uv run pytest packages/rag/tests/retrieval packages/rag/tests/evaluation packages/rag/tests/generation` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T2 — Lexical store: tokenizer check, shared connection, loop-safe freshness

**State:** approved (2026-11-15)
**Requirements:** R3, R7, R2

- [x] `lexical/store.py`: `_read_only_connection` with `check_same_thread=False` (still `mode=ro`, `query_only`); one `threading.Lock` per `LexicalIndex` guarding every connection use including `close`; `check_tokenizer(expected)` raising `LexicalIndexBindingError` with advice naming `make index-lexical` (no path).
- [x] Call `check_tokenizer` with `lexical.tokenizer` from `config/retrieval.yaml` in the standalone helper (T1) and in `open_bound_lexical`, so every CLI and the server refuse a mismatched file (Spec 010 T5).
- [x] `lexical/freshness.py`: `run_sync(coro_factory)` (no running loop: `asyncio.run`; running loop: `asyncio.run` on a short-lived thread, joined); `verify_fresh` uses it.
- [x] Tests (`packages/rag/tests/lexical/`): tokenizer mismatch refused (a `lexical-v1` file under a `lexical-v2` config) on the standalone and bound paths, message names `make index-lexical` and no path; BM25 queries from 8 threads on one `LexicalIndex` return the same results as serial calls; close while another thread queries is safe (lock); `verify_fresh` inside a running event loop (an `asyncio.run` test that calls it synchronously) and twice in sequence; the connection is closed exactly once.

Allowed protected-path changes: none.

### Verification

- `uv run pytest packages/rag/tests/lexical packages/rag/tests/retrieval` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T3 — Circuit breaker

**State:** approved (2026-11-16)
**Requirements:** R4, R15

- [x] `retrieval/breaker.py`: `BreakerState`, `Admission` (`DENSE`, `PROBE`, `SKIP`), `CircuitBreaker(failure_threshold, cooldown_s, clock, open_reason)` with `admit`, `record_success`, `record_failure`, `release`, `state`, `last_reason`, all under one lock, per design "Circuit breaker".
- [x] `retrieval/fallback.py`: keyword-only `breaker=None` and `on_probe=None` (holder hook used by T5 for a BM25-only stack). With `breaker=None` behaviour is exactly today's (D058). `SKIP` serves BM25 with `fallback_reason = breaker.last_reason`; `RetrievalUnavailableError` → `record_failure`; success → `record_success`; any other exception during a probe → `release`, then propagates (D062).
- [x] `retrieval/opening.py`: keyword-only `breaker: CircuitBreaker | None = None`, passed to every `FallbackRetriever` it builds (including the open-time fallback); CLIs pass nothing.
- [x] Tests (`packages/rag/tests/retrieval/test_breaker.py`): with a fake clock — threshold reached opens; success while closed resets the count; cool-down then exactly one `PROBE` among 8 concurrent `admit` calls (threads, barrier); probe success closes; probe failure re-opens with a new cool-down; `release` re-opens without counting; a breaker created open admits a probe only after the cool-down. `FallbackRetriever` with a breaker: skip path serves BM25 with the last reason and calls no primary; a Qdrant HTTP status error propagates and is not counted; access and `lote` reach BM25 unchanged (spy). All existing `FallbackRetriever` tests pass unchanged.

Allowed protected-path changes: none.

### Verification

- `uv run pytest packages/rag/tests/retrieval` (iteration), then `make verify` once.
- `make eval-security` with fakes as documented in `COMMANDS.md` passes (CLIs unchanged).
- `git status --porcelain -- evaluation knowledge config` is empty.

## T4 — Hard generation cap and per-request budget

**State:** approved (2026-11-16)
**Requirements:** R6, R15

- [x] `generation/base.py`: `Generator.generate(prompt, *, deadline_s: float | None = None)` and a `deadline_s` property; `FakeGenerator` returns `None` and accepts the argument; the Claude generators return their configured `deadline_s`.
- [x] `generation/claude.py`: the adapter's own deadline is `min(config.deadline_s, deadline_s)` when given; no other change to the attempt loop or classification.
- [x] `generation/deadline.py`: `AbandonedWork`, `run_with_cap(fn, cap_s, *, on_abandoned, clock)` on a daemon thread per design; a late exception from abandoned work is logged by class only; a done callback added after the work ended runs at once.
- [x] `generation/service.py`: keyword-only `budget_s`, `min_generation_s`, `on_abandoned`; cap per design; below `min_generation_s` with a budget, no generator call and `evidence_only` / `generator_unavailable` / `deadline`; the generator call goes through `run_with_cap`. CLIs keep calling `answer` without a budget.
- [x] `config/generation.yaml`: comment fixes for `deadline_s`, `backoff_s`, `bedrock.model_id` in both provider blocks (Spec 012 F2); no value changes; schema version unchanged.
- [x] Tests (`packages/rag/tests/generation/test_deadline.py`, `test_service.py`): a `BlockingGenerator` (waits on an event, `deadline_s` 0.3) returns `evidence_only` / `deadline` within 0.3 s + 0.5 s; `on_abandoned` is called once; its done callback runs only after the event is set; budget leaving less than `min_generation_s` → no call; the adapter with a fake client and fake clock starts no attempt after the per-call deadline; `make ask`'s path (CLI `main` with a blocking fake generator injected) applies the cap; a CLI process does not hang on an abandoned daemon thread (subprocess test with a 5 s timeout, or an equivalent thread-daemon assertion if a subprocess is too slow for the budget).

Allowed protected-path changes: comments only in `config/generation.yaml` (the reviewer checks `git diff config/generation.yaml` shows comment lines only).

### Verification

- `uv run pytest packages/rag/tests/generation` (iteration), then `make verify` once.
- `make ask` and `make eval-generation` with `--generator fake` and fakes as in `COMMANDS.md` produce the same statuses as before.
- `git status --porcelain -- evaluation knowledge config` lists only `config/generation.yaml`.

## T5 — Serving package: config, locks, stack holder, re-open, readiness model

**State:** approved (2026-11-21)
**Requirements:** R1, R2, R5, R7, R8

- [x] `config/serving.yaml` (schema 1.0) with the design values; `serving/config.py` strict loader and the cross-file budget check (`budget.request_s >= generator deadline_s + qdrant.query_timeout_s + min_generation_s`).
- [x] `serving/locks.py`: `LockedEmbedder`, `LockedReranker` (separate locks; identity, `info`, `device` pass through).
- [x] `serving/readiness.py`: thread-safe phase (`starting`, `ready`, `failed`), degraded reasons (`dense_circuit_open`, `dense_circuit_half_open`, `rerank_skipped`, `dense_reopen_refused`, `abandoned_generation`), breaker reasons derived at read time, `abandoned_in_flight` from a registered provider callback, `fake` flag.
- [x] `serving/stack.py`: `ServingStack`, `StackHolder` (ref-counted `acquire`, atomic swap, drain then close, `close` at shutdown with a 5 s drain wait), `open_serving_stack` (strategy, `rerank.enabled` and `default_generator` from config; shared locked models and one breaker; Qdrant down at start → BM25-only with the breaker created open; non-eligible error → everything opened is closed and the error propagates to the caller), `try_reopen_dense` per design (embedder retry first when it failed at startup; new client, `DenseIndex`, new bound lexical connection with identity, tokenizer and freshness checks; swap on success; `record_failure` on an eligible outage; `release` plus `dense_reopen_refused` on a mismatch or other non-eligible error; every resource of a failed attempt closed).
- [x] Tests (`packages/rag/tests/serving/`): config loader (unknown key, out-of-range values, budget cross-check); config resolution with values opposite to the library defaults (rerank off, a non-default strategy, `fake` generator) is followed; lock overlap (fake embedder and reranker that sleep 0.2 s each: two requests' embed and rerank overlap, total below the serial sum); start with dense down → BM25-only and breaker open; probe success with matching collection → swap, a request leased before the swap finishes on the old stack, the old stack closes after its lease ends; probe with a mismatched collection → refused, breaker open, `dense_reopen_refused`; probe failure → breaker re-opens; embedder eligible failure at start → first probe retries the embedder (factory called twice, warmed once) and swaps; failing retry → breaker re-opens; startup failure part way and shutdown close every client, lexical connection, model and generator (counters); readiness reasons including `abandoned_generation` from the provider.

Allowed protected-path changes: new `config/serving.yaml`.

### Verification

- `uv run pytest packages/rag/tests/serving packages/rag/tests/retrieval` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` lists only `config/serving.yaml`.

## T6 — API startup, readiness endpoint, fake mode and `make api`

**State:** approved (2026-11-21)
**Requirements:** R8, R16, R2

- [x] `apps/api/pyproject.toml`: workspace dependency on `way2australia-rag`; `uv lock` updated.
- [x] `config.py`: `repo_root`, `serving_config`, `api_fake` (`W2A_API_FAKE`).
- [x] `lifespan.py`: phase 1 synchronous (configs and cross-file checks, prompt, `build_generator`, active `lote` codes, standalone lexical identity, chunker, tokenizer and freshness; any failure stops startup with a safe message); phase 2 background thread (`open_serving_stack`; readiness `ready` with degraded reasons, or `failed` plus the shutdown callback, which signals the process to exit); shutdown closes the holder. `create_app(settings, *, stack_factory=None, on_fatal=None)` for tests.
- [x] `api/ready.py`: `GET /ready` per design (503 `starting` / `failed`; 200 `ok` / `degraded` with reasons, breaker state, `abandoned_in_flight` when present, `fake`); `GET /health` unchanged.
- [x] Fake mode: fake embedder, reranker and generator; startup warning log; readiness `fake: true`.
- [x] `Makefile`: `api` target whose recipe is `$(UV_ENV) $(UV) run uvicorn way2australia_api.main:app …` like the other targets, never a bare `uv run` (`uv` is not on the user's PATH); host and port variables, default `127.0.0.1:8000`; `make api` is not part of `make verify`.
- [x] Tests (`apps/api/tests/`): phase 1 failures stop startup (invalid serving config, unknown prompt, tokenizer mismatch, missing lexical file) with messages free of paths and keys; readiness `starting` while a stack factory blocks on an event, then `ok`; `degraded` for a breaker-open start and for a reranker skip; `failed` plus `on_fatal` called on a phase 2 non-eligible error, with everything opened closed; `/health` response unchanged; fake mode readiness `fake: true` and the warning logged; shutdown closes every connection (counters).
- [x] Generator ownership (added 2026-11-21, T5 review F2): the generator built in phase 1 is passed to the holder through `ServingInputs.generator`; `StackHolder` closes it at shutdown and when `open_serving_stack` fails, so the lifespan never closes it a second time. If phase 1 fails after `build_generator` and before the holder exists, the lifespan closes the generator itself. Test: a phase 1 failure after `build_generator` (for example a tokenizer mismatch) closes the generator exactly once; a phase 2 failure and a normal shutdown also close it exactly once (counter).
- [x] Generator from configuration (added 2026-11-21, T5 review F1): a test in `packages/rag/tests/serving/` opens the stack with no generator and no generator override passed in, and asserts the generator follows `default_generator` from the generation config (set in the config copy to a value different from the committed one, for example `fake`).

Notes from the T5 review (no box): F3, the dense re-open is tested against in-memory Qdrant only; the live check is the user-run smoke check in T8. F4, the probe request finishes on the new stack without a lease on it; T6's shutdown order (stop accepting requests, then `holder.close()`) covers it.

Allowed protected-path changes: none.

### Verification

- `uv run pytest apps/api packages/rag/tests/serving` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T7 — Answer route, public contract, limits, errors and logging

> Carry-over (T6 review F2, user 2026-11-21): when `apps/api/tests/test_serving_startup.py` is next touched, rename `test_unknown_prompt_stops_startup_and_closes_the_generator` (it asserts no generator was built).

**State:** approved (2026-11-22)
**Requirements:** R9, R10, R11, R12, R13, R16

- [x] `contract.py`: `AnswerRequest` (extra forbidden), `PublicStatus`, `PublicReason`, `PublicCitation`, `PublicEvidence`, `AnswerContract` 1.0, `to_contract` with explicit `_STATUS` and `_REASON` maps, per design.
- [x] `slots.py`: `SlotPool`, `Slot` with idempotent `release` and `transfer(work)`; `abandoned_in_flight` registered as the readiness provider.
- [x] `middleware.py`: server-generated request ID (`X-Request-ID` on every response; incoming ID ignored); body-size limit for `POST /v1/answer` (413 before parsing, with and without `Content-Length`).
- [x] `errors.py`: 422 handler without `input`/`ctx` echo; 500 handler with request ID only; 503 bodies with `Retry-After`.
- [x] `api/answer.py`: `POST /v1/answer` as a sync `def`, per design "Data flow": readiness check, slot, query and `lote` validation, server-resolved guest access, `holder.acquire()`, `service.answer(..., top_k from config, budget_s, min_generation_s, on_abandoned=slot.transfer)`, `to_contract`, log line, release; `X-W2A-Fake: true` on every answer response in fake mode.
- [x] `logs.py`: one JSON line per answer request with the design fields and none of the forbidden ones; `httpx` and `anthropic` loggers at WARNING.
- [x] Tests (`apps/api/tests/`): contract pin (exact field names, types, nesting, both enum member sets, `contract_version`); enum coverage (every `AnswerStatus` and `AnswerReason` member mapped); one mapping test per status and per internal reason; 422 for empty, whitespace-only, too long, extra field (`role`, `tenant_id`, `scope`, `top_k`), bad `lote` (`*`, empty, unknown) with no query echo in the body; 413 with and without `Content-Length` and no service call; busy 503 with `Retry-After: 1`; not-ready 503 with `Retry-After: 5`; 500 for an injected authorization error, body holding only `request_id` and `error`; slot released on success and on error; with a `BlockingGenerator`, the response is `evidence_only` / `generator_unavailable` within the cap plus 0.5 s, the slot stays held, `/ready` shows `abandoned_generation` and `abandoned_in_flight: 1`, and both clear when the generator ends; a client `X-Request-ID` is not echoed; sentinel strings in the query, `ANTHROPIC_API_KEY`, `QDRANT_URL` and a fake client exception message never appear in captured logs or bodies; `X-W2A-Fake: true` present in fake mode and absent otherwise; the OpenAPI schema lists `AnswerContract` with `contract_version`.

Allowed protected-path changes: none.

### Verification

- `uv run pytest apps/api` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T8 — Route-level security and concurrency, real smoke check

> Carry-over (T7 review round 2 F2, user 2026-11-22): the next time `lifespan.py` or its tests are touched, add tests for the embedder, enabled-reranker and disabled-fake-reranker branches of `_refuse_fake_providers` and give its `generation` parameter the `GenerationConfig` type instead of `Any`.

**State:** approved (2026-11-27)
**Requirements:** R14, R7, R16, R17

- [x] Route-level authorization test (`apps/api/tests/test_route_security.py`): build a stack from the security corpus builders (`evaluation/security_corpus.py`, `security_index.py`; in-memory Qdrant, temporary lexical file, fakes) with forbidden rows (staff scope, other tenant, injection variant); through `POST /v1/answer` on hybrid, on breaker-open BM25 and on the reranked path, queries aimed at forbidden rows never return a forbidden `document_id` in citations or evidence; bodies with access-like fields are 422.
- [x] Concurrency test (`apps/api/tests/test_concurrency.py`): 16 concurrent requests (threads over `TestClient`, `max_in_flight` raised for the test) on BM25 and on hybrid with fakes: no error, each result equal to the same request sent alone; a dense re-open swap during the run leaves no request failed and closes the old stack after drain.
- [x] `make eval-security` passes with the reworked opening (fakes, as in `COMMANDS.md`).
- [x] User-run real smoke check, documented in `COMMANDS.md` by this task and recorded by the user in `task-reviews.md`: `make api` with the real stack; `/ready` from `starting` to `ok` (timestamps, warm-up time); one answerable and one unanswerable query (status, public reason, per-request latency from the log line); optionally stop Qdrant to see `degraded` / `dense_circuit_open`, then start it and see recovery after the cool-down. The agent prepares the steps and does not run them.

Allowed protected-path changes: none.

### Verification

- `uv run pytest apps/api` (iteration), then `make verify` once.
- `make eval-security` (fakes) passes.
- The smoke check is recorded in `task-reviews.md` by the user, or recorded as not run with the reason.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T9 — Documentation, decisions and handoff

**State:** not started
**Requirements:** R18, R17, Definition of Done

- [ ] `ROADMAP.md`: item 10 status (library verified on `main` `467b8c8`; route done by Spec 013); item 13 records the circuit breaker and server-start policy.
- [ ] `ARCHITECTURE.md`: query flow (route, limits, slots, breaker), `apps/api` responsibilities, serving lifecycle (two-phase startup, stack holder, re-open, shutdown), concurrency model and locks.
- [ ] `COMMANDS.md`: `make api`, `W2A_API_FAKE`, `GET /health`, `GET /ready`, `POST /v1/answer` (request, contract 1.0, status codes), `config/serving.yaml`, the tokenizer refusal, the hard cap's effect on `make ask` / `make eval-generation`, the `retrieval_depth` correction, the smoke-check steps (if not already added by T8).
- [ ] `DECISIONS.md`: concurrency model A with two model locks and the shared SQLite connection; circuit breaker; server start with Qdrant down, dense re-admission and embedder retry; hard cap, abandoned work and budget; public contract 1.0 and reason mapping; request ID and logging (D-L: no raw query, no hash); readiness semantics; `retrieval_depth` correction without a version bump; tokenizer check in the CLIs.
- [ ] `design.md` as-built notes for any departure; `CURRENT_STATE.md` reflects the implemented reality and the deferred items (streaming, usage on raised outcomes, `fallback_stage`, reranker reload and device, rate limiting, internal endpoint, Bedrock switch, prompt v2).
- [ ] As-built note, DECISIONS.md entry and `COMMANDS.md` fake-mode entry (T7 review round 2 F1, user 2026-11-22): startup refuses a config-selected fake provider (ingestion embedder, enabled reranker or `default_generator`) unless `W2A_API_FAKE` is set (`_refuse_fake_providers` in `lifespan.py`), so `X-W2A-Fake` and readiness `fake` follow `api_fake` only.
- [ ] As-built note and known issue (T8 smoke check, user 2026-11-27): a server idle about 2 days answered its first request with retrieval 40117.8 ms, consuming the 40 s budget so generation was skipped (`evidence_only` / `generator_unavailable`, `deadline`); a fresh start gave 1.7 s retrieval. Embedder and reranker have no inference timeout (D077) and `/ready` does not warm the models. Candidate follow-up: a warm-up inference before ready and/or a retrieval-time share of the budget.
- [ ] As-built note (T6 review F1, user 2026-11-21): the lifespan does not join a loader thread still opening the stack at shutdown; a late-built holder is closed by the loader, and process exit frees the rest.
- [ ] Spec-wide checks: `make verify`, `make eval-security` (fakes).

Allowed protected-path changes: none.

### Verification

- `make verify` and `make eval-security` pass; results recorded in the implementer hand-off.
- `git status --porcelain -- evaluation knowledge config` is empty.
