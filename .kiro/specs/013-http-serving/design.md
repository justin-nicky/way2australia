# 013 — HTTP Route and Serving Policy Design

Status: approved (2026-11-13)

## Design summary

One process opens one serving stack and answers guest questions over HTTP.

- **Configuration decides everything.** The server reads `config/retrieval.yaml`, `config/ingestion.yaml`, `config/generation.yaml` and a new `config/serving.yaml`. Strategy, reranking and generator come from them, never from library defaults (R1).
- **Startup has two phases.** The FastAPI lifespan runs the fast checks synchronously: configuration, prompt, generator construction (extra and key), active `lote` codes, and the lexical file (identity, chunker, tokenizer, freshness). Any failure stops the process. It then starts a background loader that builds and warms the embedder and reranker and opens Qdrant. Until the loader finishes, readiness is `starting` (503), because a blocking lifespan would keep uvicorn from answering readiness during the roughly 25 s load (R3, R8).
- **Concurrency model A.** The route is a synchronous `def` on FastAPI's threadpool. Answer work is limited by an in-process slot pool. One lock serializes embedder calls and another serializes reranker calls. One read-only SQLite connection per lexical file is shared behind a lock (R7, R10).
- **Circuit breaker.** A small `CircuitBreaker` is passed into `FallbackRetriever` by the server only. The CLIs pass none, so D058 is unchanged for them (R4).
- **Server start with Qdrant down.** The holder starts BM25-only with the breaker open. The probe request re-opens dense, runs the startup identity and binding checks, and swaps the stack atomically (R5).
- **Hard generation cap.** `run_with_cap` runs `generate` on a daemon thread and waits at most the cap. The generator also receives the cap as its own deadline, so no new attempt starts after it. An abandoned call keeps its slot until its thread ends (R6).
- **Public contract.** `AnswerContract` v1.0 is a separate model with its own public enums, mapped by one function (R11).
- **Request ID.** The server generates one per request. Logs carry no query text and no query hash (R13).

## Package / file placement

```text
config/serving.yaml                                   new, schema 1.0 (server only)
packages/rag/src/way2australia_rag/
  retrieval/opening.py        rework: one standalone-lexical helper, client lifecycle,
                              early top_k/rerank check, tokenizer check (R1, R2, R3)
  retrieval/breaker.py        new: CircuitBreaker (R4)
  retrieval/fallback.py       optional breaker parameter (R4)
  lexical/store.py            shared read-only connection behind a lock; tokenizer check (R3, R7)
  lexical/freshness.py        loop-safe execution (R3)
  generation/base.py          Generator.generate(prompt, *, deadline_s=None); Generator.deadline_s (R6)
  generation/claude.py        honours the per-call deadline (R6)
  generation/deadline.py      new: run_with_cap, AbandonedWork (R6)
  generation/service.py       cap, budget, on_abandoned (R6)
  evaluation/cli.py           retrieval_depth per served path (R1, Spec 011 F1)
  serving/                    new package (reusable serving lifecycle, no HTTP)
    __init__.py
    config.py                 ServingConfig + loader for config/serving.yaml
    locks.py                  LockedEmbedder, LockedReranker (R7)
    stack.py                  ServingStack, StackHolder, open_serving_stack, reopen_dense (R2, R5)
    readiness.py              Readiness state model (R8)
apps/api/
  pyproject.toml              adds the workspace dependency way2australia-rag
  src/way2australia_api/
    config.py                 Settings additions (repo root, config paths, fake mode)
    lifespan.py               new: two-phase startup, shutdown (R2, R8)
    contract.py               new: AnswerRequest, AnswerContract v1.0, public enums, to_contract (R9, R11)
    slots.py                  new: SlotPool, Slot (R10)
    middleware.py             new: request ID, body-size limit (R9, R13)
    logs.py                   new: answer log line builder (R13)
    errors.py                 new: exception handlers (R12)
    api/answer.py             new: POST /v1/answer (R9)
    api/ready.py              new: GET /ready (R8)
    api/health.py             unchanged (liveness)
    main.py                   wires lifespan, middleware, routers
Makefile                      new target: api (R16)
```

`packages/rag/serving/` holds lifecycle code that a later worker or batch runner could reuse. `apps/api` holds only HTTP concerns: routes, request and response models, middleware, slots, logging and wiring (ARCHITECTURE "apps/api").

## Components / boundaries

### `config/serving.yaml` (schema 1.0)

```yaml
schema_version: "1.0"
request:
  max_query_chars: 1000        # characters, after stripping; 1..4000
  max_body_bytes: 16384        # whole JSON body; 1024..1048576
concurrency:
  max_in_flight: 4             # answer slots, including abandoned generation work; 1..64
  retry_after_busy_s: 1
  retry_after_not_ready_s: 5
budget:
  request_s: 40                # per-request budget (retrieval + context + generation)
  min_generation_s: 2          # below this remaining, the generator is not called
breaker:
  failure_threshold: 3         # consecutive fallback-eligible dense outages; 1..20
  cooldown_s: 30               # fixed; 1..600
```

The loader is strict: unknown keys and out-of-range values are refused. A cross-file check refuses a `budget.request_s` below the configured generator's `deadline_s` plus `qdrant.query_timeout_s` plus `min_generation_s`, so the budget leaves room for one bounded retrieval and a full generation deadline. With the committed values that is 30 + 3 + 2 = 35 ≤ 40.

Why the numbers:
- **`max_query_chars` 1000.** The longest suite query is far below this, and 1000 Malayalam characters are about 3 KB of UTF-8.
- **`max_body_bytes` 16 KiB.** It covers 1000 characters even fully `\u`-escaped (6 bytes each) plus `lote` and the JSON overhead.
- **`max_in_flight` 4.** See "Throughput ceiling" below.
- **Budget 40 s.** The generation deadline is 30 s. Worst-case retrieval is the dense timeout (3 s), BM25 (milliseconds) and a reranker queue of at most 3 requests ahead at about 1 s each, which is about 7 s in all.

### Retrieval opening rework (R1, R2, R3)

- **One standalone-lexical helper.** `_open_standalone(...) -> (LexicalIndex, IndexIdentity, DocumentCounter)` replaces the duplicated wiring in the `bm25` branch and in `_open_fallback` (Spec 008 F4).
- **Early depth check.** `open_retrieval` takes an optional `top_k` (and `eval-retrieval` passes its effective depth). With `rerank=True` and `top_k > rerank.depth`, it raises `RetrievalConfigurationError` before `reranker_factory` is called (Spec 011 F3).
- **Client lifecycle.** The client is closed on every failure after it is created: one `try` covers `DenseIndex.open`, the lexical bind, the reranker load and `build_retriever`, with an `except BaseException` that closes the client and any opened lexical file. `OpenedRetrieval` gains a `client` field, and `close()` closes the lexical file and then the client, idempotently (Spec 008 T4).
- **Tokenizer check.** `LexicalIndex.check_tokenizer(expected: str)` compares the file's recorded tokenizer with `lexical.tokenizer`. It is called by the standalone helper and by `open_bound_lexical` (CLIs and server). A mismatch raises `LexicalIndexBindingError` with advice to run `make index-lexical` (Spec 010 T5).
- **`retrieval_depth` per served path (Spec 011 F1).** `eval-retrieval` sets `retrieval_depth` to `rerank.depth` only when the opened stack has a loaded reranker on a dense-capable path. After an open-time fallback (reranker built, not loaded, no dense primary) it uses `fusion.candidate_depth`, as a run without reranking would. A per-query fallback inside a reranked run still asks BM25 for `rerank.depth`; that is unchanged and is noted in COMMANDS, because top-5 distinct-document metrics need at most 17. **No result version bump:** `retrieval_depth` keeps its meaning ("the depth asked of the served path"); the old value 20 in this one case was a defect. `eval-compare` and `eval-continuity` do not read the field, so earlier 2.5 files stay comparable. The correction is recorded in DECISIONS.

### Lexical store and freshness (R3, R7)

- **Shared connection.** `_read_only_connection` opens with `check_same_thread=False` (still `mode=ro` and `query_only`). `LexicalIndex` holds one `threading.Lock` that guards every use of the connection: search, counts, identity reads and close. BM25 queries take milliseconds, so the lock costs nothing measurable, and there is one connection per lexical file to close. The design takes this option over per-thread connections, whose threads are owned by anyio and are hard to enumerate and close, and over a pool, which adds a structure for no measured gain. A later move to a pool stays local to `LexicalIndex`.
- **Loop-safe freshness.** `verify_fresh` calls a `run_sync(coro_factory)` helper. With no running loop it uses `asyncio.run`. Inside a running loop it runs `asyncio.run` on a short-lived thread and joins it. `LocalDocumentRepository`'s `asyncio.Lock` is only ever used within one of these sequential runs, at startup or at a dense re-open; a test covers two sequential runs.

### Circuit breaker (R4)

`retrieval/breaker.py`:

```python
class BreakerState(StrEnum): CLOSED = "closed"; OPEN = "open"; HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int, cooldown_s: float,
                 clock: Callable[[], float] = time.monotonic, open_reason: FallbackReason | None = None): ...
    def admit(self) -> Admission       # DENSE (closed), PROBE (one caller after cool-down), SKIP
    def record_success(self, admission: Admission) -> None
    def record_failure(self, admission: Admission, reason: FallbackReason) -> None
    def release(self, admission: Admission) -> None   # probe ended without an eligible verdict
    @property
    def state(self) -> BreakerState
    @property
    def last_reason(self) -> FallbackReason | None
```

- **Locking and states.** All transitions take one `threading.Lock`. Closed: every call is admitted (`DENSE`). After `failure_threshold` consecutive `record_failure` calls, the breaker is open until `now + cooldown_s`. The first `admit()` after the cool-down gets `PROBE` and the state becomes half-open; every other caller gets `SKIP` until the probe reports. A probe success closes the breaker and resets the count. A probe failure re-opens it for a new cool-down. A success while closed resets the count.
- **`release` (non-eligible errors).** A non-eligible error during a probe (an HTTP status error, a binding error) is not an outage and propagates (D062). `release` then returns the breaker to open with a new cool-down, so the next probe waits and the request fails closed as today.
- **`FallbackRetriever` integration.** It gains `breaker: CircuitBreaker | None = None`; `None` is today's behaviour exactly.
  - On `SKIP`, the primary is not called and BM25 serves with `fallback_reason = breaker.last_reason` and a `dense_attempt` of about 0 ms.
  - On `DENSE` or `PROBE`, the primary is called. `RetrievalUnavailableError` calls `record_failure` and then the fallback serves. Success calls `record_success`. Any other exception calls `release` (probe) and propagates.
  - The fallback reason values are unchanged, so no new `FallbackReason` member is needed. The breaker state reaches logs and readiness, not results.

### Serving stack and holder (R1, R2, R5)

`serving/stack.py`:

```python
@dataclass
class ServingStack:
    opened: OpenedRetrieval            # retriever, identity, lexical, client, reranker
    service: AnswerService
    dense: bool                        # False when serving BM25-only after an open-time outage
    def close(self) -> None            # idempotent; closes opened (lexical, client)

class StackHolder:
    def acquire(self) -> ContextManager[ServingStack]   # ref-counted lease on the current stack
    def try_reopen_dense(self) -> ReopenOutcome         # called only by the probe request
    def close(self) -> None                             # shutdown: close current and drained old stacks
```

- **Shared parts.** One `CircuitBreaker` lives in the holder and is passed to every `FallbackRetriever` the holder builds. The embedder, reranker and generator are built once and shared across stack generations. They are owned by the holder and closed at shutdown only. `open_retrieval` receives them through factories that return the already-built (and locked) instances.
- **`open_serving_stack(...)`**, run by the background loader:
  1. **Lexical first.** The standalone lexical file has already been checked in phase 1 (identity against configuration, chunker, tokenizer, freshness).
  2. **Build and warm the models.** The embedder is wrapped in `LockedEmbedder` and warmed with one `embed_query`. The reranker, when `rerank.enabled`, is wrapped in `LockedReranker` and loaded once. An eligible reranker load failure is the sticky open-time skip (D077) and is reported in readiness. An eligible embedder load failure is treated like a dense outage.
  3. **Open dense** through `open_retrieval` with the server's breaker. On success the lexical file is bound to the live collection (`open_bound_lexical`: identity against the dense index, tokenizer) and the stack is `dense=True`.
  4. **On a fallback-eligible dense outage** the stack is `dense=False`: `FallbackRetriever(None, BM25, reason, breaker)`, with the breaker created open (`open_reason`) so that the first request after the cool-down is a probe.
  5. **On a non-eligible error** (missing collection, settings mismatch, HTTP status error, offline-not-cached reranker) startup has failed. The loader closes everything it opened, sets readiness to `failed` and calls the shutdown callback, which signals the process to exit (R8).
- **Probe in a BM25-only stack.** When the stack is `dense=False` and `admit()` returns `PROBE`, the route's service call goes through `StackHolder.try_reopen_dense()` before retrieval (a holder-level hook in `FallbackRetriever` with no primary):
  1. Open a new Qdrant client and `DenseIndex`.
  2. Bind a **new** lexical connection to it. This runs the startup checks: dense identity and settings, lexical identity against the dense index, tokenizer and freshness.
  3. Build the new retriever with the shared models and breaker.
  4. **Success:** swap the holder's current stack under its lock, `record_success`, and the probe request continues on the new stack.
  5. **Eligible outage:** `record_failure` (breaker re-opens) and the request is served by BM25.
  6. **Mismatch or other non-eligible error:** log the error class with the request ID, `release` (breaker stays open with a new cool-down), set the readiness degraded reason `dense_reopen_refused`, serve BM25. The server never serves dense hits from a collection that fails the checks.

  Every resource the failed attempt opened is closed before the attempt returns.
- **Embedder failure at startup.** If the stack is BM25-only because the embedder failed to build or warm for an eligible reason (`model_unavailable`, D057), the holder records that it has no embedder. `try_reopen_dense` then first retries building the embedder, wrapping it in `LockedEmbedder` and warming it with one `embed_query`, and only then opens Qdrant (step 1 above).
  - An eligible failure of this retry is an outage: `record_failure`, BM25 serves.
  - A non-eligible failure (for example offline mode with nothing cached) is handled like a refused re-open: `release`, `dense_reopen_refused`, BM25 serves.
  - On success the holder keeps the embedder for every later stack generation.

  Recovery therefore needs no restart. The retry runs on the probe request only, so it costs at most one model load (about 10–20 s) per cool-down, on one request. That request is also bounded by its generation budget, which may leave it `evidence_only` / `deadline`; the design accepts this.
- **Atomic swap and drain.** `acquire()` increments the lease count of the current stack. A swap marks the old stack retired. The old stack is closed when its last lease ends. Requests in flight finish on the stack they started with.
- **Shutdown.** `StackHolder.close()` closes the current stack, waits up to 5 s for leases on retired stacks and then closes them anyway, and closes the embedder, reranker and generator. Abandoned generation threads are daemon threads and do not block exit; their slots no longer matter at shutdown.

### Model locks (R7)

`LockedEmbedder` wraps an `Embedder` and holds a `threading.Lock` around `embed_query` (and `embed_documents`, unused by the server). `LockedReranker` wraps a `Reranker` and holds a separate lock around `score` and `load`. `info`, `device` and identity pass through. With two locks, request A can rerank while request B embeds.

**Throughput ceiling (development machine, D079 and D090 figures).**
- Reranking costs about 0.8–1 s per request at p95 and is serialized, so reranked throughput cannot exceed about 1.0–1.25 requests per second, whatever `max_in_flight` is.
- Generation (Sonnet 5.5, direct API) has a total p50 of about 3.9 s per request. At `max_in_flight` 4, generation allows about 1 request per second.

Both ceilings are about 1 request per second on this machine. A fifth concurrent request gets 503 at once instead of queueing behind the reranker lock. With 4 slots, the reranker queue adds at most about 3 s to retrieval, which the budget allows. Deployment (item 14) re-measures on the target device.

### Hard generation cap and budget (R6)

**Generator interface.**
- `Generator.generate(prompt, *, deadline_s: float | None = None)` and a `deadline_s: float | None` property: the configured deadline for Claude generators, `None` for `FakeGenerator`.
- `ClaudeMessagesAdapter.generate` uses `min(config.deadline_s, deadline_s)` as its own deadline, so it never starts or retries an attempt after the cap.

**`generation/deadline.py`.**

```python
class AbandonedWork:
    def add_done_callback(self, fn: Callable[[], None]) -> None   # runs once when the thread ends
def run_with_cap(fn: Callable[[], T], cap_s: float, *,
                 on_abandoned: Callable[[AbandonedWork], None] | None = None,
                 clock=time.monotonic) -> T
```

- **The worker.** `run_with_cap` starts a daemon `threading.Thread` that runs `fn` and stores its result or exception, then waits on an `Event` for at most `cap_s`. If the thread finishes in time, the result is returned or the exception re-raised.
- **On timeout.** It calls `on_abandoned(work)` and raises `GeneratorUnavailableError(UnavailableReason.DEADLINE)`. The thread keeps running. Its eventual result is discarded, and its exception is logged by class only.
- **Why a daemon thread.** A `ThreadPoolExecutor` worker is joined at interpreter exit and would make a CLI hang after a cap.

**`AnswerService.answer(..., budget_s: float | None = None, min_generation_s: float = 0.0, on_abandoned=None)`.**
- **The cap.** `cap = generator.deadline_s`, or the remaining budget when that is `None`. With a budget, `cap = min(cap, budget_s - elapsed)`.
- **No call below the minimum.** If `cap < min_generation_s` (a budget is given), the generator is not called and the response is `evidence_only` / `generator_unavailable` / `deadline`.
- **CLIs.** They pass no budget, so their cap is the generator's `deadline_s`. With no budget and no deadline (fake), no cap applies.
- **The call.** The generator call is `run_with_cap(lambda: generator.generate(prompt, deadline_s=cap), cap, on_abandoned=...)`.
- **`min_generation_s`.** The rule applies only when a budget is given (the server), with `budget.min_generation_s`. The CLIs pass no budget, so they keep the adapter's existing 1 s minimum per attempt.

**Honest bound on an abandoned call.**
- No attempt starts after the cap, because the adapter's own deadline equals the cap. The attempt already in flight was started with `timeout = min(request_timeout_s, remaining)`.
- That is an httpx per-phase timeout: connect, write, pool, and **each** read. A non-streaming Messages response usually arrives in one or a few reads after the model finishes, so in practice the call ends within the cap plus at most one `request_timeout_s` (20 s).
- A peer that trickles bytes can reset the read timeout repeatedly, so **there is no guaranteed upper bound**.
- The slot stays held until the thread really ends, so the cap on concurrent work is never exceeded. Under a pathological provider, capacity shrinks and clients get 503. The answer log line records `abandoned_in_flight` so this is visible.

**Effect on evaluation (accepted).** `make eval-generation` and `make ask` use the same cap, so a later run may record `evidence_only` / `deadline` for cases that took about 32 s in Spec 012 (g021, g022, g040). The generation result schema is unchanged: `deadline` is an existing sub-reason.

**Config comment fixes (Spec 012 F2).**
- `deadline_s`: "hard wall-clock cap per request, all attempts and backoff".
- `backoff_s`: "delay = backoff_s * 2**attempt; an attempt is skipped when the wait leaves no usable time before the deadline".
- `bedrock.model_id`: "null until the Bedrock switch (its own spec)".

### Slots (R10)

`apps/api/slots.py`: `SlotPool(max_in_flight)` with a `threading.Lock` counter.
- **Acquire.** `try_acquire() -> Slot | None` never blocks.
- **Release.** `Slot.release()` is idempotent.
- **Transfer.** `Slot.transfer(work: AbandonedWork)` marks the slot as owned by the abandoned work and registers `release` as the work's done callback. After a transfer, the route's own `release` is a no-op.

The route acquires before any work and releases in `finally`. A synchronous handler is not told that the client disconnected, so its work runs to the end and then releases. `abandoned_in_flight` is the number of transferred slots.

### Readiness (R8)

`serving/readiness.py` holds a thread-safe state.
- **Phase:** `starting`, `ready` or `failed`.
- **Degraded reasons:** a set of `dense_circuit_open`, `dense_circuit_half_open`, `rerank_skipped`, `dense_reopen_refused` and `abandoned_generation`.
  - The breaker reasons are derived from the breaker at read time.
  - `dense_reopen_refused` clears on a successful re-open.
  - `abandoned_generation` is present while `abandoned_in_flight > 0`. `/ready` reads that count from the `SlotPool` through a provider callback registered at startup, so `serving/readiness.py` does not depend on `apps/api`. Its bound is open-ended (see "Honest bound"), so slots held by abandoned work are visible in readiness, not only in logs. The response adds `abandoned_in_flight` as an integer when the reason is present.
- **Fake flag:** `fake: bool`.

`GET /ready` maps the state to a response:
- `starting` → 503, body `{"status": "starting", "fake": …}`;
- `failed` → 503, body `{"status": "failed", "fake": …}`;
- `ready` with no reasons → 200, body `{"status": "ok", "degraded_reasons": [], "breaker": "closed", "fake": …}`;
- `ready` with reasons → 200, body `{"status": "degraded", "degraded_reasons": [...], "breaker": "<state>", "fake": …}`.

The body holds no paths, URLs, collection names or exception text. `GET /health` is unchanged.

### Public contract and request (R9, R11)

`apps/api/contract.py`:

```python
class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    query: str          # stripped; 1..max_query_chars (validator reads serving config from app state)
    lote: str | None = None   # resolve_lote against active codes loaded at startup

class PublicStatus(StrEnum):  ANSWERED = "answered"; INSUFFICIENT_EVIDENCE = "insufficient_evidence"; EVIDENCE_ONLY = "evidence_only"
class PublicReason(StrEnum):  NO_EVIDENCE = "no_evidence"; NOT_ANSWERABLE = "not_answerable"; GENERATOR_UNAVAILABLE = "generator_unavailable"

class PublicCitation(BaseModel):   # frozen, extra=forbid
    source_id: str; document_id: str; document_version: int; section_id: str
    title: str; source_authority: str; source_url: str | None
class PublicEvidence(PublicCitation):
    snippet: str

class AnswerContract(BaseModel):   # frozen, extra=forbid
    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    status: PublicStatus
    reason: PublicReason | None
    answer: str | None
    citations: list[PublicCitation]
    evidence: list[PublicEvidence]
    message: str | None
    message_language: str | None
```

**Mapping.** `to_contract(response: AnswerResponse, request_id: str) -> AnswerContract` is the only mapping. Two explicit dicts, `_STATUS: dict[AnswerStatus, PublicStatus]` and `_REASON: dict[AnswerReason, PublicReason]`, define it:
- `no_evidence` → `no_evidence`;
- `model_declined`, `citation_invalid` and `output_invalid` → `not_answerable`;
- `generator_unavailable` → `generator_unavailable`.

A test asserts that both dicts cover every member of the internal enums, so adding an internal value without a public mapping fails CI rather than a request. Citation and evidence fields are copied field by field, never with `model_dump` passthrough, and `source_url` comes from the block metadata the `Citation` already carries.

**Pin test.** It asserts the exact field names, types and nesting of `AnswerContract`, `PublicCitation` and `PublicEvidence`, the members of both public enums, and the `contract_version`. Changing any of them needs a new contract version.

**Lote and query validation** runs in the route after body parsing:
- **Query:** the length and empty checks from serving config.
- **`lote`:** `resolve_lote` against the active codes cached at startup. A `RetrievalConfigurationError` from it becomes 422 with the list of active codes (no query echo).

### Middleware and errors (R9, R12, R13)

- **Request ID middleware** (pure ASGI):
  - generates `uuid4().hex`, stores it in the request state and adds `X-Request-ID` to every response;
  - ignores any incoming `X-Request-ID` (or similar) header.
- **Body-size middleware** (pure ASGI, `POST /v1/answer` only):
  - a `Content-Length` above `max_body_bytes` gives 413 at once;
  - otherwise it reads the body up to `max_body_bytes + 1` bytes (covering chunked bodies with no length); over the limit gives 413, and nothing reaches the router;
  - within the limit, the buffered body is replayed to the app;
  - the 413 body is `{"request_id", "error": "body_too_large"}`.
- **Exception handlers:**
  - `RequestValidationError` → 422 with `{"request_id", "error": "invalid_request", "fields": [{"loc", "msg"}]}`. FastAPI's default `input` and `ctx` are dropped, so the query is never echoed.
  - Any other exception → 500 with `{"request_id", "error": "internal_error"}`; the log records the error class and request ID, with no `exc_info`.
- **503 bodies:** `{"request_id", "error": "busy" | "not_ready"}` with `Retry-After`.
- **Fake header:** when the stack is fake (any of embedder, reranker or generator is fake), the answer route adds `X-W2A-Fake: true` to every answer response, including errors from the route.

### Logging (R13)

`apps/api/logs.py` builds one line per answer request: JSON on the `way2australia_api.answer` logger at INFO. Fields:
- `request_id`, `status`, `reason`, `sub_reason`;
- `served_strategy`, `fallback_reason`, `rerank` (`applied`, `skipped:<reason>:<stage>` or `off`), `breaker`;
- `generator` (provider, model ID), `fake`;
- `latency_ms` (retrieval, context, generation, total);
- `query_chars`, `script_mix` (from `script_mix.py`);
- `abandoned_in_flight`.

**What is never logged:**
- query text, a query hash, answer text, evidence text;
- URLs from configuration, keys;
- exception messages from client libraries.

Error lines carry the class name only. `httpx` and `anthropic` loggers stay at WARNING (their request lines carry URLs, as in `make ask`). Uvicorn's access log is kept: it holds method, path, status and client address, and no body.

**Decision (D-L):** no raw query text and no query hash in Phase 1 logs. A hash of a short query is guessable. Retention and redaction belong to observability (item 11).

### Settings and fake mode (R16)

`Settings` gains:
- `repo_root` (default: the working directory);
- `serving_config` (default `config/serving.yaml`);
- `api_fake` (`W2A_API_FAKE`, default false).

With `api_fake` the server uses the `fake` embedder provider, the `fake` reranker and the `fake` generator. It needs the same fake-embedder collection and lexical file that `make ingest` and `make index-lexical` build with `QDRANT_COLLECTION_BASE` (COMMANDS), logs a fake warning at startup, reports `fake: true` in readiness and adds `X-W2A-Fake: true` to answer responses.

`make api` runs `$(UV_ENV) $(UV) run uvicorn way2australia_api.main:app --host $(API_HOST) --port $(API_PORT)` (defaults 127.0.0.1 and 8000), like the other targets; never a bare `uv run`, since `uv` is not on the user's PATH. `create_app(settings, *, stack_factory=None)` accepts an injected factory so tests build stacks from fakes and in-memory fixtures without uvicorn.

## Data flow

```text
POST /v1/answer
  → RequestID middleware (server ID) → BodySize middleware (413 before parse)
  → route (sync def, threadpool)
      readiness != ready            → 503 not_ready (Retry-After)
      SlotPool.try_acquire() None   → 503 busy (Retry-After)
      validate query and lote       → 422 (no echo)
      access = resolve_access(guest_access(settings))          (server tenant, C3)
      with holder.acquire() as stack:
          response = stack.service.answer(query, access, top_k=config top_k, lote=lote,
                                          budget_s=budget.request_s, on_abandoned=slot.transfer)
              retriever = FallbackRetriever(primary?, BM25, reason, breaker)
                  admit(): DENSE | PROBE | SKIP   (PROBE on a BM25-only stack → holder.try_reopen_dense())
                  dense leg (LockedEmbedder) + BM25 (locked SQLite) → RRF → rerank (LockedReranker)
              context → pre-gate → run_with_cap(generate, cap) → citation validation
      contract = to_contract(response, request_id)
      log line (no query text)
      slot.release()   (no-op if transferred to abandoned work)
  → 200 AnswerContract (+ X-Request-ID, + X-W2A-Fake in fake mode)
```

Startup:

```text
lifespan phase 1 (sync, fails the process): settings → configs (+ cross-file checks) → prompt
  → build_generator (extra, key) → active lote codes → standalone lexical (identity, chunker,
  tokenizer, freshness via run_sync) → readiness = starting
lifespan phase 2 (background thread): models (locked, warmed) → open_serving_stack
  → readiness = ready (degraded reasons as applicable) | failed + shutdown callback
shutdown: holder.close() (stacks, lexical connections, clients, models, generator)
```

## Interfaces / models

- **`open_retrieval`** keeps its signature and adds keyword-only `top_k: int | None = None` and `breaker: CircuitBreaker | None = None`. `OpenedRetrieval` gains `client: object | None`.
- **`LexicalIndex.check_tokenizer(expected: str) -> None`** is new. `open_bound_lexical` and the standalone helper take the expected tokenizer.
- **`Generator.generate`** gains the keyword-only `deadline_s` (existing callers are unaffected), and `Generator` gains a `deadline_s` property.
- **`AnswerService.answer`** gains keyword-only `budget_s` and `on_abandoned`; the CLIs keep calling it as before.
- **`FallbackRetriever`** gains keyword-only `breaker` and `on_probe` (the holder hook for a BM25-only stack).
- **New types:** `CircuitBreaker`, `Admission`, `BreakerState`, `ServingConfig`, `ServingStack`, `StackHolder`, `Readiness`, `AnswerRequest`, `AnswerContract`, `PublicStatus`, `PublicReason`, `PublicCitation`, `PublicEvidence`, `SlotPool`, `Slot`, `AbandonedWork`.

## Error and failure behavior

| Situation | Behavior |
|---|---|
| Invalid config, missing extra, missing API key, unknown prompt | phase 1 fails; process exits non-zero with a safe message |
| Lexical file missing, foreign, stale, or tokenizer mismatch | phase 1 fails; message names the `make` target (R3) |
| Qdrant or embedding model unavailable at startup (eligible) | ready, degraded (`dense_circuit_open`); BM25 serves; probe re-opens (R5) |
| Non-eligible error in phase 2 (missing collection, settings mismatch, HTTP status, reranker offline-not-cached) | readiness `failed`; everything opened is closed; process exits |
| Reranker eligible load failure | ready, degraded (`rerank_skipped`); plain hybrid hits (D077) |
| Dense outage at query time | breaker counts it; BM25 serves this request; after the threshold, open |
| Probe re-open finds a mismatched collection | refused, breaker stays open, `dense_reopen_refused`, BM25 serves |
| Qdrant HTTP status error at query time | propagates (D062) → 500 with request ID only; breaker not counted |
| Generation passes the cap | `evidence_only` / `generator_unavailable` (public) / `deadline` (log); slot held until the thread ends |
| Too little budget left for generation | same response, generator not called |
| Authorization or applicability error | propagates → 500 (fail closed) |
| Body too large | 413 before parsing |
| Invalid body, query, or `lote` | 422, no echo |
| Not ready | 503 `not_ready`, `Retry-After: 5` |
| All slots busy | 503 `busy`, `Retry-After: 1` |

## Security / authorization

- **Server-resolved access.** Access is resolved only from server settings (`guest_access`, server tenant). `AnswerRequest` forbids extra fields, so `role`, `tenant_id` and `scope` in a body are 422, never silently ignored. The validated `lote` is the only request value that reaches retrieval, and it reaches only the applicability builder (C4).
- **Breaker and re-open.** The breaker and the dense re-open change which leg serves, never the access or applicability arguments. The BM25 path enforces them in SQL and `check_hit` (D058). The re-open refuses a collection that does not match the lexical file.
- **Public contract.** It carries model-generated text only in `answer`, and only after citation validation. Citation metadata comes from the blocks, never the model (D083). No internals leave the server.
- **No sensitive output.** Logs and error bodies carry no secrets and no query text.
- **Route-level authorization test.** It reuses the security corpus builders (`evaluation/security_corpus.py`, `security_index.py`) to build a stack with forbidden rows (staff scope, other tenant, the injection variant). Through the HTTP route, on hybrid, breaker-open BM25 and reranked paths, it asserts that no forbidden `document_id` appears in citations or evidence for queries aimed at those rows.

## Observability

Scope is limited to the R13 log line and readiness. Langfuse traces, metrics and the `fallback_stage` field are item 11. `abandoned_in_flight` and the breaker state in the log line are the signals an operator needs before item 11.

## Testing / evaluation strategy

All tests use fakes (`FakeGenerator`, fake embedder, `FakeReranker`, in-memory Qdrant or a stub client, temporary lexical files). No test calls a real model or API.

- **Opening (R1, R2, R3).**
  - Server config resolution with values opposite to the library defaults.
  - Early `top_k > rerank.depth` refusal with factory and load call counts.
  - Client and lexical closed at each injected failure step; `close()` idempotent.
  - Tokenizer mismatch refused in the CLI and server paths.
  - Freshness inside a running loop.
  - `eval-retrieval` `retrieval_depth` after an open-time fallback with reranking requested.
- **Breaker (R4).**
  - Fake clock: threshold, cool-down, single probe under 8 concurrent threads, probe success and failure, `release` on a non-eligible error.
  - `FallbackRetriever(breaker=None)` reproduces existing results (the Spec 008 tests stay green unchanged).
- **Re-open (R5).**
  - Start with dense down, then probe success with a matching collection: swap, in-flight requests finish on the old stack, old stack closed after drain.
  - Probe with a mismatched collection: refused, breaker open, `dense_reopen_refused`.
  - Probe failure: re-open after the cool-down.
  - Start with an eligible embedder load failure (a fake embedder factory that raises a network-caused error once): the stack is BM25-only. The first probe retries the embedder and swaps to hybrid, with the factory called twice and the embedder warmed once. A second variant fails the retry, and the breaker re-opens with BM25 serving.
- **Cap and budget (R6).**
  - A `BlockingGenerator` that waits on an event far past the cap: the response arrives within cap + 0.5 s, the slot stays held (`abandoned_in_flight` 1), and the slot is released when the event is set.
  - Budget exhausted before generation: no call.
  - The adapter honours the per-call deadline (no new attempt after it).
  - A CLI path test shows the cap applies to `make ask`.
- **Concurrency (R7).** 16 concurrent requests through `TestClient` threads on BM25 and on hybrid with fakes: no error, and each result equals the same request run alone. A lock test shows embed and rerank of two requests overlap: two fakes with sleeps, so total time is less than the serial sum.
- **Readiness (R8).** `starting` before the loader finishes (a loader blocked on an event), `ok`, `degraded` for each reason (including `abandoned_generation` while a `BlockingGenerator` holds a transferred slot, cleared once it ends), `failed` on a phase 2 error with the shutdown callback called, `/health` unchanged.
- **Route (R9–R12).**
  - Each 422 case, 413 with and without `Content-Length` (no answer work ran: the service fake records no call), busy 503, not-ready 503, 500 for an injected authorization error with a body holding only the request ID.
  - The contract pin test, the enum-coverage test, and one mapping test per status and per internal reason.
- **Logging (R13).** Sentinel strings in the query, in `ANTHROPIC_API_KEY`, in `QDRANT_URL` and in a fake client exception message never appear in captured logs or response bodies. A client `X-Request-ID` is not echoed.
- **Security (R14).** The route-level authorization test above. `make eval-security` stays green.
- **Lifecycle (R2).** Startup, then shutdown, asserts that every lexical connection, client, model and generator was closed. This includes a re-open swap and a phase 2 failure.

The user-run real smoke check (R16) is recorded in `task-reviews.md`: readiness transitions with timestamps, warm-up time, one answerable and one unanswerable query, per-request latency.

## Phase 2 compatibility / migration

- **Roles.** `AccessContext` construction moves from `guest_access` to an authenticated resolver. The route's single access line is the seam, and the request model never carries access fields.
- **Contract.** The version allows a 1.1 or 2.0 without breaking 1.0 clients. A RAG Lab internal endpoint (item 16) is a separate route with its own model.
- **S3 repository and Knowledge Releases.** These change what `open_serving_stack` opens, not the route. `StackHolder`'s swap is the natural place for a future release switch.

## Alternatives / deferred decisions

- **Async rewrite (model B), or an async generator only (model C).** Rejected for Phase 1 (Decision Brief). Embedding and reranking are CPU/GPU bound and would still need threads. Revisit if deployment shows I/O-bound limits.
- **Blocking lifespan (load models before uvicorn listens).** Rejected: readiness could not report `starting`.
- **Per-thread SQLite connections or a pool.** Rejected for now: anyio owns the threads, and a pool brings no measured gain. Kept local to `LexicalIndex`.
- **A third-party breaker library, or a `circuit_open` fallback reason.** Rejected: the user asked for a minimal breaker, and a new reason value would touch result formats.
- **`ThreadPoolExecutor` for the cap.** Rejected: its workers are joined at interpreter exit, which would hang the CLIs.
- **A client-supplied request ID, or a query hash in logs.** Rejected (user decision).
- **Result 2.6 for the `retrieval_depth` correction.** Not needed: the meaning is unchanged and no comparison reads the field.
- **Deferred:** streaming, usage on raised outcomes, `fallback_stage`, reranker reload and device pin, rate limiting, internal endpoint, Bedrock switch, prompt v2 (requirements "Out of scope").
