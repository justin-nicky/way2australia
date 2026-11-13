# 013 — HTTP Route and Serving Policy Requirements

Status: approved (2026-11-13)

## Goal

Serve the Spec 012 `AnswerService` over HTTP as a long-running process (the remainder of roadmap item 10), and close the serving items that Specs 008, 011 and 012 deferred to the first HTTP surface. Concretely:

- one retrieval and generation stack is opened once per process, at startup, with every setting resolved from committed configuration, and every resource it holds is closed on every failure path and at shutdown;
- a thin FastAPI answer route validates the request, resolves guest access on the server, calls `AnswerService` and returns a versioned public response contract that hides internals;
- the server is safe under concurrent requests (sync path on FastAPI's threadpool, behind an in-process concurrency cap) and bounded in time (a hard wall-clock generation cap inside a per-request budget);
- a minimal circuit breaker stops a hanging Qdrant from costing every request a timeout, and re-admits dense retrieval only after the same identity and freshness check as startup;
- a readiness endpoint says whether the stack is open and warm, and whether it is serving degraded;
- logs are keyed by a server-generated request ID and hold no secrets and no query text.

Repository facts that shape the scope (checked 2026-11-13 on `main` `1e27909`):

- `apps/api` has only `create_app` and `GET /health`; it does not depend on `way2australia-rag`, and there is no `make` target that runs a server.
- `open_retrieval` (`retrieval/opening.py`) is the one wiring function. Its library default is `rerank=False`; only the CLIs resolve `rerank.enabled` (Spec 011 F2). The `bm25` branch and `_open_fallback` duplicate the standalone open (Spec 008 F4). With reranking requested and a dense outage, BM25 is asked for `rerank.depth` chunks (Spec 011 F1). `top_k > rerank.depth` is refused only at query time, after the reranker loaded (Spec 011 F3). The Qdrant client is not closed on every open failure, and `OpenedRetrieval.close()` closes only the lexical file (Spec 008 T4).
- An open-time dense outage makes the whole run BM25-only, and Qdrant is not tried again until the stack is reopened (D058). That suits a CLI run, not a server.
- `verify_fresh` uses `asyncio.run` (D060); `open_retrieval` does not compare the lexical file's tokenizer with `config/retrieval.yaml` (Spec 010 T5).
- The lexical store opens one read-only SQLite connection with the default `check_same_thread=True` (`lexical/store.py`), so a connection opened at startup cannot be used from a worker thread.
- The BGE-M3 embedder and the `bge-reranker-v2-m3` cross-encoder are synchronous PyTorch models; reranking costs about 0.8–1 s per request at p95 on the development machine (D079). The Anthropic and Qdrant sync clients use thread-safe httpx clients.
- `deadline_s` (30 s) is soft: it is passed to the SDK as a per-phase httpx timeout, and three Spec 012 cases ran about 32 s (D084). An httpx timeout bounds each phase (connect, read, write, pool), not the call as a whole.
- `AnswerResponse` carries `sub_reason`, usage, prompt hash and the full retrieval identity, which are internal.
- First startup loads the embedder and reranker in about 25 s on the development machine.

## Dependencies

- Spec 012 (verified, merged `467b8c8`): `AnswerService`, `AnswerResponse`, `build_generator`, `ClaudeMessagesAdapter`, `GenerationConfig`, the prompt registry, `FakeGenerator`, `make ask` (D081–D091).
- Spec 011: `RerankingRetriever`, `FakeReranker`, the sticky open-time skip (D077), rerank identity.
- Spec 010: `resolve_lote`, `active_lote_codes`, the lexical tokenizer setting (D072).
- Spec 008: `open_retrieval`, `FallbackRetriever`, `open_standalone_lexical`, `verify_fresh`, the eligibility rules (D057, D058, D059, D060, D062).
- Spec 005: `guest_access`, `resolve_access`, `check_hit` (D035, D040), `safe_text`.
- Spec 001: `apps/api` skeleton, `Settings`, `GET /health`.
- Retrospective notes: `.kiro/specs/012-grounded-generation/review.md` "Notes for the next spec" (Spec 013 items), and the Spec 008/011 retrospective findings named above.
- The user-run real smoke check (R16) needs Docker Qdrant, the user's real collection and lexical file, `make setup-bge-m3`, a cached reranker, `make setup-anthropic` and `ANTHROPIC_API_KEY`.

## Decisions resolved before drafting

Approved by the user on 2026-11-13 (Decision Brief and follow-up):

- **In scope:** the route; config-resolved `rerank.enabled` and `default_generator`; the `open_retrieval` rework and resource lifecycle; the lexical startup and tokenizer policy and freshness outside a running event loop; a minimal circuit breaker; readiness reporting of a sticky reranker skip; a hard wall-clock generation cap with a per-request budget and the `config/generation.yaml` comment fixes (Spec 012 F2); request validation and a concurrency cap; a versioned public response contract; request-ID logging; `make api`; the ROADMAP item 10 status fix.
- **Concurrency model A:** a synchronous answer path on FastAPI's threadpool behind the concurrency cap. No async rewrite of the library. One lock for the embedder and a separate lock for the reranker, so requests can overlap the two stages.
- **Circuit breaker:** a consecutive-failure count, a fixed cool-down, one probe request after the cool-down, state reported in readiness. No library, no adaptive tuning. D062 unchanged (a Qdrant HTTP status error is not fallback-eligible and does not count as an outage).
- **Server start with Qdrant down:** the server starts with the breaker open (serving BM25), and the probe retries opening dense. The CLIs keep D058 (open-time fallback for the whole run).
- **Dense re-admission:** when the probe re-opens dense, the same identity and freshness checks as startup run (collection against the lexical file) before dense rejoins fusion; a mismatch is refused and the breaker stays open.
- **Readiness:** not-ready only while the stack is not open or not warm. Breaker open or a reranker skip is ready, degraded, with the reason.
- **Abandoned generation work:** a generation call that passes the hard cap is abandoned by the request but keeps its concurrency slot until its thread really ends. No claim that it ends within `request_timeout_s` (httpx timeouts are per phase).
- **Public response:** its own versioned Pydantic model with `status`, `answer`, `citations` (with `source_url` from document metadata), evidence snippets, `message` and its language, a coarse reason and the request ID. No `sub_reason`, usage, cost, prompt hash, retrieval internals or debug flag. An internal endpoint for the RAG Lab is a later spec (item 16).
- **Limits:** a maximum query length; an empty or whitespace-only query refused; `lote` validated against the registry; `top_k` not client-settable; busy returns 503 with `Retry-After`. No per-client rate limiting (item 12).
- **Logging:** keyed by a server-generated request ID (a client-supplied ID is never accepted); no API keys or other secrets; **no raw query text and no query hash** in Phase 1.
- **Deferred:** streaming (its own design: citations are validated on the full answer and fail closed); usage on raised outcomes (prompt v2, Spec 012 F1); a `fallback_stage` field (observability, item 11, Spec 008 F2); reranker reload and device pinning (deployment, item 14); per-client rate limiting (item 12); the Bedrock switch and prompt changes (their own specs).

## R1 — Configured serving stack

The server opens one stack from committed configuration, through a reworked `open_retrieval`.

### Acceptance criteria

- The server resolves the strategy from `default_strategy`, reranking from `rerank.enabled` and the generator from `default_generator`; no library default decides any of them. A test with a configuration that sets each value differently from the library defaults proves the server follows the configuration (Spec 011 F2).
- The standalone lexical open used by `bm25` and by the hybrid fallback is one helper; `open_retrieval` no longer duplicates it (Spec 008 F4).
- The served path's retrieval depth is set per path: with reranking requested and a dense outage, BM25 is asked for the same depth it would use without reranking, not `rerank.depth` (Spec 011 F1). `eval-retrieval` records the corrected `retrieval_depth`.
- `top_k > rerank.depth` with reranking on is refused before the reranker is built or loaded (Spec 011 F3); a test counts reranker factory and load calls.
- The CLIs (`make retrieve`, `make eval-retrieval`, `make ask`, `make eval-generation`, `make eval-security`) keep their behaviour apart from the two corrections above, including the D058 open-time fallback for the whole run.

## R2 — Resource lifecycle

Every resource the stack holds is closed exactly once, on every failure path and at shutdown.

### Acceptance criteria

- `open_retrieval` closes the Qdrant client on every open failure (dense open, lexical bind, reranker load, retriever build), not only on the fallback path; a test injects a failure at each step and asserts the client and any opened lexical connection were closed.
- Closing an opened stack closes the Qdrant client and every lexical connection, and is idempotent.
- At server shutdown, the stack, every lexical connection the server opened (including any opened for worker threads or a pool), any re-opened dense stack and the generator are closed; a test drives startup and shutdown and asserts every connection was closed.
- A startup that fails part way closes everything it opened before the process reports the failure.

## R3 — Lexical startup policy

A lexical file that cannot serve correctly stops startup.

### Acceptance criteria

- A missing lexical file, a file whose identity, chunker or hash contract differs from configuration, a stale file (freshness check fails) and a file whose recorded tokenizer differs from `lexical.tokenizer` in `config/retrieval.yaml` each stop startup with a path-free, secret-free message naming the problem and the `make` target that fixes it. Startup does not fall back to dense-only.
- The tokenizer check also applies to the CLIs that open a lexical file (it was missing everywhere, Spec 010 T5); a stale `lexical-v1` file under a `lexical-v2` configuration is refused.
- The freshness check runs where no event loop is running (or through an async-safe form), so it works from the FastAPI lifespan; a test runs startup inside a running event loop.
- These rules apply with Qdrant up and with Qdrant down.

## R4 — Circuit breaker

A minimal circuit breaker on the dense leg of `hybrid`.

### Acceptance criteria

- States: closed (dense tried on every request), open (dense not tried; BM25 serves through the existing fallback, marked with the fallback reason) and half-open (one probe request tries dense).
- The breaker opens after a configured number of consecutive fallback-eligible dense outages (`RetrievalUnavailableError`, D057); a success resets the count. A Qdrant HTTP status error, a binding error or any non-eligible error does not count and keeps failing closed (D062 unchanged).
- After a fixed, configured cool-down, exactly one request is the probe; concurrent requests during the probe are served by BM25 without a dense attempt. A probe success closes the breaker; a probe failure re-opens it for another cool-down.
- Thresholds and cool-down are committed configuration, validated at load; no adaptive tuning and no third-party breaker library.
- Requests served while the breaker is open apply the same `ResolvedAccess` and `ResolvedLote` through BM25's own clause and `check_hit` as any fallback (D058); the breaker never changes authorization or applicability.
- Breaker transitions are tested with an injected clock and a fake dense failure, including the single-probe rule under concurrent requests.
- The CLIs are unchanged: the breaker exists in the server only.

## R5 — Server start with Qdrant down and dense re-admission

The server can start without Qdrant and re-admits dense retrieval only after checks.

### Acceptance criteria

- If the dense side is unavailable at startup for a fallback-eligible reason, the server starts with the breaker open and serves BM25; the lexical startup policy (R3) still applies in full.
- The probe in that state tries to open the dense side. Before dense rejoins fusion, the same checks as a startup with Qdrant up run: the dense index identity and settings, and the binding of the open lexical file to the live collection. A mismatch is refused, logged with a safe message, and leaves the breaker open; it never serves dense hits from a collection that does not match the lexical file.
- A re-opened dense stack replaces the BM25-only state atomically for new requests; requests in flight finish on the stack they started on; the replaced resources are closed once no request uses them.
- When reranking is on, the re-opened stack uses the reranker already loaded at startup; a sticky reranker skip from startup stays reported (R8).
- Tests cover: start with Qdrant down, probe success with a matching collection, probe success with a mismatched collection (refused, breaker open), probe failure.

## R6 — Hard generation cap and per-request budget

Generation has a true wall-clock cap inside a per-request budget.

### Acceptance criteria

- The server waits for a generation call for at most its cap, measured on a wall clock; at the cap the request stops waiting and returns `evidence_only` / `generator_unavailable` with the existing `deadline` sub-reason (D085), whatever the generator is still doing.
- The generation cap of each request is the smaller of the configured `deadline_s` and what remains of a configured per-request budget after retrieval and context building. When too little remains for a useful attempt, the generator is not called and the response is `evidence_only` / `generator_unavailable` with the `deadline` sub-reason.
- Abandoned work is counted: a generation call abandoned at the cap keeps its concurrency slot (R10) until its thread actually ends, so the cap on concurrent work is never exceeded. The design states the honest bound on how long an abandoned call can run (httpx timeouts are per phase, not total).
- A test uses a generator that blocks well past its cap: the response arrives within the cap plus a small tolerance, the slot stays held while the generator still runs, and it is released when the generator returns.
- The CLIs and `make eval-generation` use the same hard cap (one implementation), so `deadline_s` means what its comment says. Consequence (accepted 2026-11-13): a later `make eval-generation` run may record `evidence_only` / `deadline` outcomes for cases where Spec 012 recorded answers that took about 32 s (g021, g022, g040).
- `config/generation.yaml` comments are corrected: `deadline_s` (hard wall-clock cap), `backoff_s` (not capped by the deadline), `bedrock.model_id` (null until the Bedrock switch) (Spec 012 F2).
- The per-request budget is committed configuration, validated at load (it must leave room for retrieval and for generation).

## R7 — Concurrency model

A synchronous answer path on FastAPI's threadpool, made thread-safe.

### Acceptance criteria

- The answer route runs the existing synchronous `AnswerService` on FastAPI's threadpool; the library is not rewritten as async.
- Embedder calls are serialized by one lock and reranker calls by a separate lock, so one request can embed while another reranks.
- Lexical (SQLite) access is safe from any worker thread; the design chooses the mechanism (per-thread connections, a pool sized to the cap, or one `check_same_thread=False` read-only connection behind a lock), and every connection is closed at shutdown (R2).
- The breaker state, the stack reference and the concurrency counter are updated under locks or atomically.
- A test sends concurrent requests through the route on BM25 and on hybrid with fakes, with no error and with results equal to the same requests sent one at a time.
- The design states the throughput ceiling that follows from the reranker lock (about 0.8–1 s per reranked request on the development machine), and the decision is recorded.

## R8 — Startup, readiness and liveness

The stack is loaded once, and readiness says whether it can serve.

### Acceptance criteria

- The embedder, the reranker (when reranking is on) and the generator are built and loaded once, in the FastAPI lifespan, before the first answer request is served.
- `GET /health` stays a liveness check (unchanged response and status).
- A new readiness endpoint returns not-ready (503) only while the stack is not open or not warm. Once open and warm it returns ready (200) with a status of `ok` or `degraded`; `degraded` lists its reasons: the breaker is open or half-open (serving BM25), reranking is skipped for the process (sticky open-time skip, D077), a dense re-open was refused (R5), or abandoned generation work still holds slots (R6, R10).
- Readiness exposes no path, URL, key, collection internals or exception text; it reports state names and reason codes only.
- A configuration error at startup (missing extra, missing API key, invalid config, R3 failures) stops the process with a safe message; it is not reported as a not-ready state forever.
- Tests cover not-ready before warm-up, ready `ok`, ready `degraded` for each reason, and liveness unchanged.

## R9 — Answer route and request validation

One thin answer route over `AnswerService`.

### Acceptance criteria

- A request body larger than a configured maximum size is refused with 413 before it is parsed; a test sends an oversized body (with and without a `Content-Length` header) and asserts 413 and that no validation or answer work ran.
- The route accepts a JSON body with `query` and an optional `lote`; any other field is refused (422). No tenant, role, scope, `top_k`, strategy, generator, prompt or model field exists.
- `query` must be non-empty after stripping whitespace and at most a configured maximum length (characters); otherwise 422.
- `lote` is validated with `resolve_lote` against the active registry codes; an unknown, empty or `*` value is 422 with the list of active codes.
- The route resolves access only through `resolve_access(guest_access(settings))`, with the tenant from server settings (C3); nothing in the request reaches the access or applicability builders except the validated `lote`.
- The route holds no RAG logic: it validates, takes a concurrency slot, calls `AnswerService` with the server's `top_k`, maps the response, and releases the slot.
- All three answer statuses (`answered`, `insufficient_evidence`, `evidence_only`) return 200.

## R10 — Concurrency cap and overload

A fixed in-process cap on concurrent answer work.

### Acceptance criteria

- At most a configured number of answer requests (including abandoned generation work, R6) hold a slot at once. A request that cannot take a slot immediately returns 503 with a `Retry-After` header; it is not queued.
- A request that arrives while the server is not ready returns 503 with `Retry-After`.
- A slot is released when the request's work ends, on every outcome (success or any error), including when the client has already disconnected: a synchronous handler is not told about a disconnect, so its work runs to its end and then releases the slot. Abandoned generation work (R6) keeps the slot until that work ends.
- Tests cover the busy 503, the not-ready 503, slot release on error, and the slot held by abandoned generation.

## R11 — Public response contract

The client sees a versioned public model, never `AnswerResponse`.

### Acceptance criteria

- The response is its own Pydantic model, separate from `AnswerResponse`, with a contract version field and: `status` and `reason` (each its own public enum, null `reason` when answered), `answer`, `citations` (source ID, document ID, version, section ID, title, source authority, `source_url` from document metadata), `evidence` (the same fields plus the snippet, for `evidence_only`), `message` and `message_language` (for `insufficient_evidence`) and `request_id`.
- It holds no `sub_reason`, usage, cost, prompt identity or hash, generator identity, response model, retrieval identity, latency, context statistics, score, fused rank or exception text.
- A test pins the exact field set and types of the contract (including nested models), so an internal change cannot add a field silently; a change needs a new contract version.
- The public `status` and `reason` enums are defined by the contract, not reused from `AnswerStatus` and `AnswerReason`. The one mapping function maps every internal value to a public value explicitly; adding an internal reason must not change the public contract (an unmapped internal value fails a test, not a request at random). The pin test covers the enum values.
- The mapping from `AnswerResponse` is one function with a test for each status and each internal reason.
- The contract is in the OpenAPI schema with its version.

## R12 — Error mapping

Failures return safe HTTP errors.

### Acceptance criteria

- Validation errors return 422 with field-level messages that never echo the query text.
- Configuration, authorization and language-applicability errors that propagate from `AnswerService` (fail closed, D085) return 500 with only the request ID and a generic message; the server logs the error class and request ID.
- No response body or header carries a stack trace, a path, a URL from configuration, a key or the exception message of a client library.
- Tests cover each class.

## R13 — Logging and request ID

Logs are keyed by a server-generated request ID and hold no secrets and no query text.

### Acceptance criteria

- Each request gets a server-generated request ID, returned in the response body (R11) and a response header. A client-supplied request ID header is ignored and never echoed or logged as the ID.
- One structured log line per answer request with: request ID, status, reason, server-side `sub_reason`, served path (strategy, fallback reason, rerank applied or skipped), breaker state, generator provider and model ID, latencies (retrieval, context, generation, total), query length in characters and the script mix of the query.
- No log line from the server holds the raw query text, a query hash, the answer text, evidence text, an API key, a URL from configuration or a client library's exception message.
- A test captures the logs of requests whose query, environment and configuration hold sentinel strings and asserts none appears; the decision (no raw query and no hash in Phase 1) is recorded in `DECISIONS.md`.

## R14 — Authorization and untrusted input through the route

The route keeps every Spec 005–012 authorization and untrusted-data rule.

### Acceptance criteria

- A route test against a corpus with forbidden (non-public or other-tenant) rows proves that no forbidden document appears in citations or evidence, on hybrid, on the breaker-open BM25 path and on the reranked path, whatever the request body contains.
- Request fields that look like access controls (for example `role`, `tenant_id`, `scope`) are refused by the request model (R9), and the test proves they cannot widen access.
- Evidence and answers are returned as data; the public contract carries no field the model can set except `answer` text that passed citation validation.
- `make eval-security` stays green with the reworked `open_retrieval`.

## R15 — Unchanged behaviour and protected paths

### Acceptance criteria

- The authorization and applicability builders, `check_hit`, `check_applicable`, `rrf_fuse`, `HybridRetriever`, the rerank membership re-check, the context builder, the prompt, citation validation and the generator outage classification are unchanged.
- D058 (open-time fallback for the whole run) and D062 hold for the CLIs; D062 holds for the server.
- No evaluation data under `evaluation/` and no knowledge under `knowledge/` changes.
- Result format versions change only where R1 changes a recorded value (`retrieval_depth` under fallback with reranking requested); the design names any version bump.

## R16 — `make api` and the real smoke check

### Acceptance criteria

- `make api` runs the server locally with the committed configuration (`uvicorn` from the `apps/api` package).
- A fake mode for local runs without models or keys exists only through explicit server settings (fake embedder, fake reranker, fake generator), and readiness and the response say nothing that could be mistaken for a real answer: the server logs a fake warning at startup, readiness reports `fake: true`, and every answer response carries the header `X-W2A-Fake: true`. The response body contract (R11) is the same in fake and real mode.
- A user-run real smoke check, documented in `COMMANDS.md`: start `make api` with the real stack, watch readiness go from not-ready to ready, send one answerable and one unanswerable query, and record status, readiness transitions, warm-up time and per-request latency in `task-reviews.md`. No test calls the real API.

## R17 — Spec-wide verification

### Acceptance criteria

- `make verify` passes, including the new `apps/api` tests and the reworked library tests.
- `make eval-security` passes.
- The real smoke check (R16) is recorded, or explicitly recorded as not run with the reason.

## R18 — Documentation and decisions

### Acceptance criteria

- `ROADMAP.md` item 10 says it is verified on `main` (`467b8c8`) for the library and done by this spec for the route; item 13 records the circuit breaker.
- `ARCHITECTURE.md` (query flow, `apps/api` responsibilities, serving lifecycle), `COMMANDS.md` (`make api`, the endpoints, the smoke check), `DECISIONS.md` (concurrency model and locks, breaker, server start with Qdrant down and re-admission, hard cap and budget, public contract, request ID and logging, readiness) and `CURRENT_STATE.md` reflect what is implemented.
- The design carries as-built notes for any departure.

## Out of scope

- Streaming responses (its own design; citations are validated on the full answer and fail closed).
- Usage and cost on raised generator outcomes (prompt v2, Spec 012 F1).
- A `fallback_stage` field in results (observability, item 11, Spec 008 F2); Langfuse tracing and metrics.
- Reranker reload after a sticky skip and device pinning (deployment, item 14).
- Per-client or per-IP rate limiting, input cost limits beyond the query length (security, item 12).
- An internal or debug endpoint, and any field beyond the public contract (RAG Lab, item 16).
- An async rewrite of the retrieval or generation library.
- Qdrant HTTP 5xx fallback eligibility (D062 stays).
- The Bedrock switch and any prompt change (their own specs).
- Frontend (`apps/web`), authentication, roles other than guest, CORS policy beyond the framework default, Docker images and deployment.
- Query translation or transliteration.

## Risks

- An abandoned generation call holds a concurrency slot until its thread ends; under a slow provider the effective capacity drops and clients see 503. The bound is stated in the design, and the slot accounting is fail-safe.
- PyTorch thread-safety is avoided by the locks, which serialize each model; reranked throughput is about one request per second on the development machine.
- The breaker's dense re-open swaps resources under load; it is isolated in the server's stack holder and tested with concurrent requests.
- Warm-up (about 25 s) and latency figures are development-machine figures, not deployment figures.
- Fake mode could be mistaken for a real server; it is visible in readiness and in the startup log.

## Definition of Done

- Every requirement R1–R18 is met and traced to a task and a verification.
- Every task is approved by the user and committed on `spec/013`.
- `make verify` and `make eval-security` pass; the real smoke check is recorded or its absence is explained.
- The spec-reviewer retrospective passes and the docs are reconciled.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1, T5 | `test_opening_lifecycle.py` (early depth refusal, shared helper), `eval-retrieval` depth test; serving config-resolution test (T5) |
| R2 | T1, T2, T5, T6 | failure-step close tests (T1); lexical close test (T2); stack and shutdown counters (T5, T6) |
| R3 | T2, T6 | tokenizer refusal on standalone and bound paths; freshness in a running loop (T2); phase 1 startup failures (T6) |
| R4 | T3 | `test_breaker.py` (fake clock, single probe under concurrency, D062 not counted); `make eval-security` |
| R5 | T5, T8 | re-open tests: match, mismatch, probe failure, embedder retry, drain (T5); swap under concurrent requests (T8) |
| R6 | T4, T7 | `test_deadline.py`, `test_service.py` (blocking generator, budget, adapter deadline, CLI cap) (T4); route-level abandoned slot (T7) |
| R7 | T2, T5, T8 | lexical threads (T2); lock overlap (T5); 16 concurrent route requests (T8) |
| R8 | T5, T6, T7 | readiness model (T5); `/ready` states, `/health` unchanged (T6); `abandoned_generation` (T7) |
| R9 | T7 | 422 cases, 413 with and without `Content-Length`, statuses return 200 |
| R10 | T7 | busy and not-ready 503 with `Retry-After`; release on success and error; slot held by abandoned work |
| R11 | T7 | contract pin test, enum coverage test, mapping test per status and reason, OpenAPI check |
| R12 | T7 | 422 without echo, 500 with request ID only, no library message in bodies |
| R13 | T7 | sentinel log test, client request ID not echoed; D-L in `DECISIONS.md` (T9) |
| R14 | T8 | route-level authorization test on hybrid, breaker-open BM25 and reranked paths; `make eval-security` |
| R15 | T1–T4, T9 | existing tests unchanged except the named ones; protected-path checks per task; `make eval-security` |
| R16 | T6, T7, T8 | `make api` target, fake mode readiness and header tests; user-run smoke recorded in `task-reviews.md` |
| R17 | T8, T9 | `make verify`, `make eval-security`, smoke record |
| R18 | T9 | reviewer reads `ROADMAP.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `DECISIONS.md`, `CURRENT_STATE.md`, as-built notes |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-11-13 — R8: degraded reasons also list a refused dense re-open and `abandoned_generation` (slots held by abandoned generation work), at design approval, because the abandoned-call bound is open-ended. No task re-opened (no task had started).
- 2026-11-13 — T6 / design "Settings and fake mode": the `make api` recipe uses `$(UV_ENV) $(UV) run uvicorn …` like the other targets (user note at tasks approval; `uv` is not on the user's PATH). No task re-opened.
