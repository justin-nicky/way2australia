# 008 — Retrieval Fallback Design

Status: approved (2026-10-29)

Implements `requirements.md` (approved 2026-10-29; R1/R6 amended 2026-10-29). Requirement IDs in brackets.

## Design summary

- One retrieval-side error, `RetrievalUnavailableError(reason)`, is the only fallback-eligible failure. Qdrant transport failures are mapped to it inside `DenseIndex`, and model load failures inside `DenseRetriever`. Everything else keeps its current type and fails closed [R1].
- Retrieval builds its own Qdrant client with the timeouts from `config/retrieval.yaml` (schema 1.1). Every `DenseIndex` call is bounded [R2].
- The lexical file gains a standalone open path: identity is checked against configuration, and freshness against a chunk digest recomputed from `LocalDocumentRepository` and the chunker. No Qdrant client and no embedder are involved [R3, R4].
- `BM25Retriever` takes an `IndexIdentity` value instead of a `DenseIndex`. An explicit `bm25` builds neither an embedder nor a Qdrant client [R5].
- New `FallbackRetriever` wraps `HybridRetriever`: BM25 serves the query on `RetrievalUnavailableError`, at open time or per query. `rrf_fuse` and `HybridRetriever` are unchanged and still fail closed (D052) [R6].
- One open function, `open_retrieval`, replaces the duplicated wiring in `make retrieve` and `make eval-retrieval` and decides the fallback at open time [R3–R6].
- Results record requested strategy, served strategy and reason [R7]. Evaluation result 2.2 groups latency by served path [R8]. `eval-compare` compares by served strategy and refuses mixed files [R9]. Security result 1.2 gates two fallback paths [R10].

## Package / file placement

| Path | Change | Req |
|---|---|---|
| `packages/rag/.../retrieval/errors.py` | `RetrievalUnavailableError`, `FallbackReason` | R1 |
| `packages/rag/.../retrieval/availability.py` (new) | `classify_qdrant_error`, `classify_model_error`: the one mapping per source | R1 |
| `packages/rag/.../retrieval/index.py` | every Qdrant call goes through the classifier; `search` passes the query timeout | R1, R2 |
| `packages/rag/.../retrieval/retriever.py` | `embed_query` failures classified (model) | R1 |
| `packages/rag/.../retrieval/qdrant_client.py` (new) | `retrieval_client_factory(settings, timeouts)` | R2 |
| `config/retrieval.yaml` | `schema_version: "1.1"`, `qdrant:` timeouts block | R2 |
| `packages/rag/.../retrieval/strategy.py` | `RetrievalConfig` 1.1 with `QdrantTimeouts`; `build_retriever` takes `IndexIdentity` and wraps hybrid | R2, R5, R6 |
| `packages/rag/.../retrieval/identity.py` (new) | `IndexIdentity` (from `DenseIndex` or from the lexical file plus config) | R3, R5, R8 |
| `packages/rag/.../lexical/store.py` | `LexicalIndex.check_identity(expected)`; chunk-set difference shared by `bind_to` and freshness; `document_count(where, params)` | R3, R4, R8 |
| `packages/rag/.../lexical/freshness.py` (new) | `verify_fresh(lexical, repository, chunker)` | R4 |
| `packages/rag/.../retrieval/bm25.py` | constructor `(identity: IndexIdentity, lexical: LexicalIndex)` | R5 |
| `packages/rag/.../retrieval/fallback.py` (new) | `FallbackRetriever` | R6 |
| `packages/rag/.../retrieval/opening.py` (new) | `open_retrieval(...) -> OpenedRetrieval` | R3–R6 |
| `packages/rag/.../retrieval/models.py` | `RetrievalResult.requested_strategy`, `fallback_reason` | R7 |
| `packages/rag/.../retrieval/cli.py` | uses `open_retrieval`; prints the served strategy and reason | R7 |
| `packages/rag/.../evaluation/cli.py`, `retrieval_eval.py` | uses `open_retrieval`; takes `IndexIdentity` and `document_count`; result 2.2 | R8 |
| `packages/rag/.../evaluation/results.py`, `compare.py` | read 2.2; served strategy; mixed-file refusal; embedder pair from `dense_identity` | R9 |
| `packages/rag/.../evaluation/security_eval.py`, `cli.py` | fallback paths, result 1.2 | R10 |
| `packages/rag/tests/...` | tests per the testing section | R11 |
| `docs/project/*`, `ROADMAP.md`, `DECISIONS.md` | final task | R14 |

Not changed: `ingestion/` (including `bge_m3.py`, `embedding.py`, `default_client_factory` and `cli.py`), `lexical/tokenizer.py`, `lexical/build.py`, `lexical/cli.py`, the lexical file format, `retrieval/fusion.py`, `retrieval/hybrid.py`, `retrieval/access.py`, the legacy `baseline.py`/`baseline_cli.py`, `evaluation/`, `knowledge/`, `config/ingestion.yaml`.

## Components / boundaries

### R1 — Failure classification (`errors.py`, `availability.py`)

```python
class FallbackReason(StrEnum):
    QDRANT_UNAVAILABLE = "qdrant_unavailable"
    QDRANT_TIMEOUT = "qdrant_timeout"
    MODEL_UNAVAILABLE = "model_unavailable"

class RetrievalUnavailableError(RetrievalError):
    reason: FallbackReason   # fixed, path-free message built from the reason only
```

- **Qdrant mapping** (`classify_qdrant_error(exc) -> RetrievalUnavailableError | None`; qdrant-client 1.19.1 over REST and httpx 0.28.1):
  - qdrant-client wraps every exception from `httpx.Client.send` as `ResponseHandlingException(e)` and keeps the original in `.source` (`http/api_client.py`, `send_inner`). It does not use `raise ... from`. It also wraps a pydantic `ValidationError` when parsing a 2xx response.
  - The candidate is `exc.source` when `exc` is a `ResponseHandlingException`, otherwise `exc` itself. Exactly one level is unwrapped, through the known wrapper only. `__cause__` and `__context__` are never followed, so an unrelated error raised while handling a `ConnectError` is never classified as an outage.
  - A candidate that is an `httpx.TimeoutException` (connect, read, write or pool) gives `qdrant_timeout`.
  - A candidate that is an `httpx.ConnectError` or other `httpx.NetworkError` gives `qdrant_unavailable`.
  - Anything else returns `None` and the original exception is re-raised unchanged. That covers `UnexpectedResponse` with any HTTP status (404 and **5xx**, deferred by decision D062), a wrapped `ValidationError`, `ValueError` and unknown types.
- **Model mapping** (`classify_model_error(exc) -> RetrievalUnavailableError | None`):
  - **Rule.** `model_unavailable` only when the explicit cause chain contains a network or timeout error. The chain is `exc`, then `__cause__` repeatedly (set by `raise ... from`), with at most 10 links. `__context__` is never followed.
  - **Network or timeout types:**
    - `httpx.TimeoutException`, `httpx.ConnectError`, `httpx.NetworkError`;
    - `requests.exceptions.ConnectionError`, `requests.exceptions.Timeout` (in case a code path still uses requests);
    - `urllib3.exceptions.NewConnectionError`, `urllib3.exceptions.TimeoutError`;
    - built-in `TimeoutError`, `ConnectionError`, `socket.gaierror`.
  - **Explicit exclusion.** `huggingface_hub.errors.OfflineModeIsEnabled` is a `ConnectionError` subclass, but it means offline mode with a missing cache, which is a configuration state. It, and any chain containing it, is not eligible. The import is guarded: without the extra, the hub cannot be the cause.
  - **Not eligible**, because the chain has no network cause:
    - a plain `OSError`;
    - `RepositoryNotFoundError`, `RevisionNotFoundError`, `GatedRepoError` (hub HTTP status errors whose cause is `httpx.HTTPStatusError`, which is not a transport error);
    - `EntryNotFoundError`, a corrupt-cache `OSError`, `PermissionError`;
    - `OptionalDependencyError` (missing extra or broken install);
    - any other type.
  - **What the pinned stack raises (`uv.lock`: sentence-transformers 6.1.0, transformers 5.20.0, huggingface-hub 1.33.0, httpx 0.28.1, requests 2.34.2, urllib3 2.8.0).** huggingface-hub 1.x uses httpx, not requests. Expected shapes:
    - network down or DNS failure while resolving or downloading an uncached file: the hub raises `LocalEntryNotFoundError` chained (`from`) to the `httpx.ConnectError`/`TimeoutException`. transformers' `cached_file` re-raises it as `OSError("We couldn't connect to ...")` from that error. Result: eligible;
    - unknown model ID: `RepositoryNotFoundError`, re-raised by transformers as `OSError("... is not a local folder and is not a valid model identifier ...")`. Result: not eligible;
    - unknown revision: `RevisionNotFoundError`, re-raised as `OSError("... is not a valid git identifier ...")`. Result: not eligible;
    - gated repository: `GatedRepoError`, re-raised as `OSError`. Result: not eligible.
  - **These shapes are not confirmed against the installed sources.** The `bge-m3` extra is not installed in this environment, and the planner did not download the packages. T1's first subtask confirms them from the pinned sources and records the result in the design As-built notes. The check is a read-only inspection of `huggingface_hub/file_download.py`, `huggingface_hub/errors.py` and `transformers/utils/hub.py`. The sources come either from the user's `make setup-bge-m3` environment or, with the user's permission, from the pinned wheels fetched with `uv pip download --no-deps` into a scratch directory outside the repository; nothing is installed into the project environment. If a shape differs (for example `raise` without `from`, which drops the cause), the rule stays "fail closed" and the gap is recorded: an outage that loses its cause is then not eligible, which is the safe direction.
- **Where the mapping is applied**:
  - `DenseIndex.open`, `search`, `document_count` and `chunk_identities` wrap their client calls in `try/except Exception` and call the classifier: a mapped error is raised, anything else is re-raised unchanged.
  - `DenseRetriever.retrieve` wraps only the `embed_query` call. The model loads lazily on the first `embed_query`, so this covers load and download failures.
  - `bge_m3.py` is not changed, so ingestion behaviour is unchanged.
- **Never eligible, by construction**: a model load failure without a network cause (above), `RetrievalAuthorizationError`, `IndexBindingError`, `LexicalIndexBindingError` (including staleness, R4), `RetrievalConfigurationError`, `OptionalDependencyError`, `IngestionConfigurationError`, request validation errors and `sqlite3.Error`. None of them is `RetrievalUnavailableError`, and `FallbackRetriever` catches only that type.

### R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`)

```yaml
schema_version: "1.1"
default_strategy: hybrid
fusion: {...unchanged...}
qdrant:
  connect_timeout_s: 2   # integer 1..30; bounds every open/binding request
  query_timeout_s: 3     # integer 1..30; bounds each search request
```

- qdrant-client takes one integer `timeout` and applies it to every httpx phase. A separate `httpx.Timeout(connect=..., read=...)` cannot be passed: `timeout` is a named parameter, so it cannot be smuggled through `**kwargs`. Both bounds are still enforced as follows:
  - the client is created with `timeout=connect_timeout_s`. This bounds every request made with the client's default, which covers all `DenseIndex.open`, binding, `document_count` and `chunk_identities` calls, including the TCP connect.
  - `DenseIndex.search` passes `timeout=query_timeout_s` to `query_points`. qdrant-client turns this into that request's httpx timeout (and Qdrant's server-side search timeout), so the search is bounded by the query timeout, connect phase included.
  - integers only, because the client rounds up anyway; the bounds keep a misconfiguration from hiding a hang for minutes.
- `retrieval_client_factory(settings, timeouts)` creates `QdrantClient(location=..., api_key=..., timeout=connect_timeout_s, check_compatibility=False)`.
  - The version check is off because it runs as an extra unbounded call and logs warnings that can carry the URL.
  - Ingestion keeps `default_client_factory`, and the security gate keeps its in-memory client.
- `RetrievalConfig` accepts only schema `1.1`. A missing or invalid `qdrant` block is a `RetrievalConfigurationError` naming the field. Tests that load 1.0 fixtures move to 1.1.
- Results record `qdrant_timeouts` (R8).

### R3 — Standalone lexical open (`identity.py`, `lexical/store.py`)

```python
class IndexIdentity(BaseModel):   # frozen
    collection: str
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_is_fake: bool
    source: Literal["qdrant", "lexical_file"]
```

- `IndexIdentity.from_dense(index)` comes from the recorded `IndexSettings`.
- `IndexIdentity.expected(config, settings, provider)` comes from configuration only:
  - `collection_name(settings.collection_base, config.index_version)`;
  - `embedder_identity(config, provider)`, the existing function from `lexical/cli.py`, moved to `ingestion/identity.py` or imported. It never builds the embedder;
  - `embedder_is_fake` is true when the provider is `fake`.
- `LexicalIndex.open(path, collection, index_version)` stays as it is (it checks the tokenizer, collection and `index_version`). The new `check_identity(expected: IndexIdentity, chunker: Chunker, hash_contract)` compares the file's `dense_identity` (collection, `index_version`, model ID, revision), the chunker fields and `hash_contract`. On a mismatch it raises `LexicalIndexBindingError` with the existing `REBUILD_ADVICE` and field names only.
- The standalone path is `open_standalone_lexical(settings, repo_root, expected, chunker, repository)`: `open`, then `check_identity`, then `verify_fresh` (R4). It creates no Qdrant client.
- `open_bound_lexical` and `bind_to` stay unchanged for `hybrid` when Qdrant is reachable.

### R4 — Freshness from the repository (`lexical/freshness.py`)

- `verify_fresh(lexical, repository, chunker)`:
  1. `asyncio.run(production_entries(repository, chunker))`, the same eligible documents, payloads and point IDs that `make index-lexical` writes;
  2. builds `_identity` tuples and `source_chunk_digest`;
  3. if the digest equals `lexical.settings.source_chunk_digest`, returns;
  4. otherwise raises `LexicalIndexBindingError` with the counts (only in the repository, only in the file, changed) and `REBUILD_ADVICE`.
- The count message comes from a helper extracted from `bind_to`, `chunk_set_difference(expected, mine)`, shared by both checks. The `bind_to` message text is unchanged.
- **Cost, and a note for a large corpus.** Each standalone open reads, parses, chunks and hashes every eligible document. For 13 documents this takes milliseconds. For thousands of documents it would take seconds at every process start, and an HTTP route would pay it on every restart. This needs revisiting for a large corpus. Options: a persisted per-document `content_hash` manifest compared incrementally, or binding to a Knowledge Release snapshot ID (Phase 2). The check stays fail-closed until then.
- The check proves the file matches the repository, not the live Qdrant collection. With Qdrant down there is nothing else to compare against. This is accepted: Spec 004 ingests from the same repository, and the dense side is not used on this path.

### R5 — `bm25` without Qdrant or the extra (`bm25.py`)

- `BM25Retriever(identity: IndexIdentity, lexical: LexicalIndex)`. The result header fields come from `identity`, and the retrieval logic is unchanged.
- For an explicit `bm25`, `open_retrieval` builds no embedder, creates no client and calls `open_standalone_lexical` with `IndexIdentity.expected(...)`.
- Nothing on the `bm25` path imports `bge_m3` or `sentence_transformers`: `build_embedder` is not called and `bge_m3` is imported only inside `build_embedder`'s provider branch, which a test pins.
- A characterization test runs Spec 007's `BM25Retriever` construction (via the in-memory dense fixture) and the new standalone path on the same lexical fixture, and requires equal `hits`.

### R6 — `FallbackRetriever` (`fallback.py`) and `open_retrieval` (`opening.py`)

```python
class FallbackRetriever:          # Retriever Protocol; strategy = Strategy.HYBRID
    def __init__(self, primary: Retriever | None, fallback: BM25Retriever,
                 open_reason: FallbackReason | None) -> None: ...
    def retrieve(self, query_text, access, top_k=DEFAULT_TOP_K) -> RetrievalResult:
        validate_request(query_text, top_k)
        started = perf_counter()
        reason = self._open_reason
        if self._primary is not None:
            try:
                return self._primary.retrieve(query_text, access, top_k)
            except RetrievalUnavailableError as error:
                reason = error.reason
        attempt_ms = (perf_counter() - started) * 1000.0
        served = self._fallback.retrieve(query_text, access, top_k)   # same access, same top_k
        return served.model_copy(update={
            "requested_strategy": "hybrid", "fallback_reason": reason.value,
            "latency_ms": attempt_ms + served.latency_ms,
            "leg_latency_ms": {"dense_attempt": attempt_ms, "bm25": served.latency_ms},
        })
```

- Exactly one `except` clause, for `RetrievalUnavailableError`. A BM25 error, an authorization error or any other error propagates.
- The BM25 leg cannot raise `RetrievalUnavailableError`: SQLite errors are not mapped. A dense failure inside `HybridRetriever` happens before its BM25 leg runs, because the legs are sequential with dense first.
- The fallback result is the plain `BM25Retriever.retrieve(query, access, top_k)` result. Only the marking fields and the latency change, so its hits equal `--strategy bm25`.
- No state is kept between queries: each query tries the primary again, with no circuit breaker.

`open_retrieval(strategy, *, settings, ingestion_config, retrieval_config, provider, repo_root, client_factory, embedder_factory, repository) -> OpenedRetrieval` returns `retriever`, `identity: IndexIdentity`, `document_count(access) -> int` and `close()`. The flow:

| Resolved strategy | Steps |
|---|---|
| `dense` | `embedder_factory` (missing extra raises), client, `DenseIndex.open`, `DenseRetriever`. Unavailable errors are raised (exit 2). |
| `bm25` | `open_standalone_lexical`, `BM25Retriever(expected identity)`. No embedder, no client. |
| `hybrid` (default or flag) | `embedder_factory` (missing extra raises, no fallback), then client, `DenseIndex.open`, `open_bound_lexical` (`bind_to`). On success: `FallbackRetriever(HybridRetriever(...), BM25Retriever(from_dense), None)`. On `RetrievalUnavailableError` during client creation, `DenseIndex.open` or `bind_to`'s scroll: `open_standalone_lexical` (R3, R4), then `FallbackRetriever(None, BM25Retriever(expected identity), reason)`. Any other error is raised. |

- The requested strategy is `--strategy` when given, otherwise `default_strategy`. The fallback applies when the resolved value is `hybrid`, in both cases.
- `build_retriever` keeps the name-to-retriever role. It takes `IndexIdentity` and returns the wrapped hybrid, so `open_retrieval` is wiring only.
- `document_count` uses Qdrant (`build_access_filter`) when the dense side is bound, and otherwise the lexical file (`SELECT COUNT(DISTINCT document_id) FROM chunks WHERE <SQL access clause>`). The digest binds both to the same chunk set, so they agree.

**Worst-case latency (per-query retry, no circuit breaker).**
- **Qdrant hangs after a successful open.** Each hybrid query waits for the dense leg's search request to time out, then runs BM25 (under 1 ms on this corpus). httpx applies the timeout per phase, so in principle a request could spend up to `query_timeout_s` in each of connect, write and read. A hang stalls one phase in practice. So:
  - expected worst case per query: about `query_timeout_s` (default 3 s);
  - theoretical bound: 3 × `query_timeout_s`;
  - for a full `eval-retrieval` (1 warm-up + 69 goldens + 12 unanswerable = 82 queries), about 4 minutes at the default.
- **Model load failure.** Each query retries the load. The wait is bounded by the Hugging Face hub's own network timeouts (about 10 s per request by default), not by this config. A refused connection fails fast.
- **Decision.** This is accepted for CLIs and evaluation. A circuit breaker belongs with the HTTP route spec: after N eligible failures, skip the dense leg for a cool-down period and serve BM25 directly. Request latency budgets and concurrency make that a serving concern, and its state would be shared across requests.

### R7 — Marking (`models.py`, `retrieval/cli.py`)

- `RetrievalResult` gains `requested_strategy: str | None = None` and `fallback_reason: str | None = None`.
- `strategy` stays the served strategy. When not degraded, `requested_strategy` equals `strategy` (set by every retriever) and `fallback_reason` is `None`.
- A fallback result has `strategy="bm25"`, `score_kind="bm25"`, no fusion fields and no `leg_document_ranks`.
- `make retrieve` header: `strategy: bm25 (requested: hybrid; fallback: qdrant_unavailable)`. It also prints one stderr line, `WARNING retrieval fell back to bm25: qdrant_unavailable`. Exit 0.
- Reasons come from `FallbackReason` only. The exception text is never printed (httpx messages can carry the URL).
- An explicit `dense` that hits `RetrievalUnavailableError` now prints `ERROR RetrievalUnavailableError: Qdrant is unavailable (qdrant_unavailable)`, exit 2. Today it prints only the client exception's class name, also exit 2. Exit code and behaviour are unchanged; only the message is clearer.

### R8 — Result format 2.2 (`retrieval_eval.py`)

`run_retrieval_evaluation(retriever, identity: IndexIdentity, document_count: int, embedder: Embedder | None, ...)`:
- `require_real_embedder` applies when an embedder was built (`dense`, `hybrid`).
- `require_real_index` checks `identity.embedder_is_fake` (and, for `source: lexical_file`, the configured provider).

Additions over 2.1:

| Key | Meaning |
|---|---|
| `requested_strategy` | `dense`, `bm25` or `hybrid` |
| `served_strategies` | sorted set over all measured goldens and unanswerable cases (warm-up excluded) |
| `retrieval_strategy`, `score_kind` | the single served strategy and its score kind; **`null` for both when `served_strategies` has more than one entry** |
| `fallback_counts` | `{reason: n}` over measured cases; `{}` when none |
| `warmup_fallback_reason` | the warm-up's reason or `null` (informational) |
| `qdrant_timeouts` | `{connect_timeout_s, query_timeout_s}`, or `null` for `bm25` |
| `dense_identity` | `IndexIdentity` as recorded (including `source`) |
| `index_settings` | as 2.1 when the dense side was bound; **`null`** when the run never reached Qdrant |
| per case `served_strategy`, `fallback_reason` | as in R7 |
| `unanswerable.served_strategies` | set; `score_kind` and the top-1 distribution are `null` when mixed (scores of different kinds are not comparable) |
| `latency_ms.by_served_path` | `{"<served>" or "<served>+fallback:<reason>": {p50, p95, n}}` |
| `latency_ms.p50`, `p95` | the single path's values when all measured cases share one path; **`null` when there is more than one path** |

- **Mixed files and R9.** A mixed file is fully readable, with metrics and slices over all cases, so a person can inspect it. Its top-level `retrieval_strategy`, `score_kind` and `p50/p95` are `null` because no single strategy describes it, and `eval-compare` refuses it (R9).
  - `fusion` is recorded when any case was served by `hybrid`.
  - `lexical_index` is recorded whenever the lexical file was opened, including a fallback-only run.
  - `leg_ranks` are as in 2.1 per case, and `null` for the dense leg of a fallback case.
- **Latency choice: grouped by served path.** I chose this over a "not comparable" flag:
  - A fallback case's latency includes the failed dense attempt, so it is neither hybrid latency nor plain BM25 latency. Grouping by served path plus reason keeps that cost visible and separate, which is useful evidence of what an outage costs.
  - A file served entirely by one path still has meaningful top-level numbers. R12's closed-port run reports the cost of a refused connection plus BM25.
  - Mixed files lose their top-level p50/p95. That matches R9, so no comparison can ever mix paths.
  - A flag alone would keep misleading numbers at the top level.
- **Equivalence.** A run with no fallback produces the same metrics, per-case ranks and leg ranks as 2.1, pinned by a fixture test. `retrieval_strategy` equals `requested_strategy` and `by_served_path` has one entry.

### R9 — `eval-compare` (`results.py`, `compare.py`)

- `SUPPORTED_FORMATS` adds `("retrieval_evaluation", "2.2")`.
- `info["retrieval_strategy"]` is the served strategy. For 2.2 it comes from `served_strategies`. For 1.0 and 2.0 it is `dense`, and for 2.1 its recorded value.
- `info["requested_strategy"]` is the requested strategy for 2.2 and equals the served strategy for older formats.
- **Refusal (exit 2)** when a 2.2 file has more than one entry in `served_strategies`, or a case `served_strategy` disagrees with it:
  `not comparable: <label> file '<name>' mixes served strategies (bm25: 3, hybrid: 78); re-run when the system is stable`.
- The embedder pair comes from `index_settings` when present, otherwise from `dense_identity`. Collection and `index_version` come from the top-level keys. The D054 refusals are unchanged.
- The 2.1 rule "a `bm25`/`hybrid` file needs a `lexical_index` object" applies to 2.2 by served strategy.
- Identity lines show requested and served strategy. Latency lines show the single path's p50/p95 and, for a fallback path, add `(includes failed dense attempt: <reason>)`. Latency stays informational.
- The R12 fallback-only file has served `bm25`, the same collection, `index_version`, embedder pair (from the lexical `dense_identity`), lexical identity and `document_count` 13 as the Spec 007 BM25 reference, so it compares under the D044 gate.

### R10 — Security gate (`security_eval.py`)

- Paths gated, all at `top_k` 50 and against the same throwaway Qdrant collection and lexical file as Spec 007:
  - `dense`;
  - `bm25`, now built through the standalone path. The freshness check runs against the isolated security repository and chunker that built the file, and identity against the throwaway collection;
  - `hybrid`;
  - `hybrid_fallback_open`: `FallbackRetriever(None, bm25, qdrant_unavailable)`;
  - `hybrid_fallback_query`: `FallbackRetriever(HybridRetriever(_UnavailableDense(), bm25, fusion), bm25, None)`.
- `_UnavailableDense` is a harness class inside `security_eval.py` that raises `RetrievalUnavailableError(qdrant_unavailable)`. It is constructed only by the gate. No flag, environment variable or config value reaches it.
- Security result format 1.2:
  - `paths` replaces `strategies` (the 1.1 `strategies` list is still written for readers);
  - each violation names its `path`;
  - `access.role` stays `guest` (D047).
- The sanity checks (dense unfiltered, lexical unfiltered, zero-term skip) are unchanged and run once per query.

## Data flow

```text
CLI args + env (QDRANT_*, W2A_TENANT_ID, W2A_LEXICAL_INDEX_DIR) + config/ingestion.yaml + config/retrieval.yaml (1.1)
  → requested strategy (flag or default)
  → open_retrieval
      dense:  embedder → client(timeouts) → DenseIndex.open                  [unavailable → raise]
      bm25:   expected identity → LexicalIndex.open → check_identity → verify_fresh(repository)
      hybrid: embedder [missing extra → raise] → client(timeouts) → DenseIndex.open → bind_to
                 ok          → FallbackRetriever(Hybrid, BM25(from_dense))
                 unavailable → standalone lexical (as bm25) → FallbackRetriever(None, BM25(expected), reason)
  → resolve_access(guest_access(settings))  (one ResolvedAccess)
  → per query: FallbackRetriever.retrieve
       primary Hybrid: dense leg (embed [network/timeout in __cause__ chain → model_unavailable; else raise]; query_points timeout) → BM25 leg → rrf_fuse
       on RetrievalUnavailableError only → BM25Retriever.retrieve(same query, same access, same top_k)
  → RetrievalResult(strategy = served, requested_strategy, fallback_reason)
  → make retrieve output | eval 2.2 rows → eval-compare (served strategy, mixed refused)
```

## Interfaces / models

- New: `FallbackReason`, `RetrievalUnavailableError`, `classify_qdrant_error`, `classify_model_error`, `QdrantTimeouts` (in `RetrievalConfig`), `retrieval_client_factory`, `IndexIdentity`, `LexicalIndex.check_identity`, `LexicalIndex.document_count`, `chunk_set_difference`, `verify_fresh`, `open_standalone_lexical`, `FallbackRetriever`, `open_retrieval`/`OpenedRetrieval`.
- Changed:
  - `BM25Retriever.__init__(identity, lexical)`;
  - `build_retriever(strategy, identity, dense_index | None, embedder | None, lexical, config)`;
  - `RetrievalResult` (+2 optional fields);
  - `run_retrieval_evaluation` (identity and `document_count` replace `index`);
  - `run_security_evaluation` (paths);
  - `ComparableRun.info` (+`requested_strategy`).
- CLIs keep their options. There is no new flag, environment variable or `make` target.

## Error and failure behavior

| Situation | `dense` | `bm25` | `hybrid` (default or flag) |
|---|---|---|---|
| Qdrant connection refused or failed (open or query) | exit 2, `RetrievalUnavailableError` | n/a (no Qdrant) | BM25 serves, `qdrant_unavailable` |
| Qdrant connect or query timeout | exit 2 | n/a | BM25 serves, `qdrant_timeout` |
| Model load or download failure with a network or timeout cause | exit 2 | n/a (no embedder) | BM25 serves that query, `model_unavailable` |
| Model load failure without a network cause (missing model ID or revision, gated repository, corrupt cache, permissions, offline mode) | exit 2 | n/a | exit 2 (never falls back) |
| Error raised while handling a network error, not through the Qdrant wrapper | exit 2 | n/a | exit 2 (never falls back) |
| `bge-m3` extra missing or broken install | exit 2 | runs | exit 2 (never falls back) |
| Qdrant HTTP error status, missing collection, settings mismatch | exit 2 | n/a | exit 2 |
| Lexical file missing, foreign or stale (R3/R4 or `bind_to`) | n/a | exit 2 | exit 2 (also when Qdrant is down) |
| Authorization violation (`check_hit`) in any leg or the fallback | exit 2 | exit 2 | exit 2 |
| BM25 or SQLite error during fallback | n/a | exit 2 | exit 2 |
| Invalid config (timeouts, schema) or request | exit 2 | exit 2 | exit 2 |

- Exit codes are unchanged (0 success, 2 refused). Messages stay path- and secret-free. Qdrant and model error texts are never printed, only the reason.

## Security / authorization

- The fallback adds no authorization logic. `FallbackRetriever` passes the caller's `ResolvedAccess` object unchanged to `BM25Retriever`, which applies `build_sql_access_clause` inside its query and `check_hit` on every hit (C3, D035, D040). A test asserts it is the same object.
- The fallback is not a retry of the same query on a broader store: the lexical file holds only eligible guest/public chunks (D050).
- `RetrievalAuthorizationError` is never caught by the wrapper, so an authorization failure can never be turned into a fallback.
- Fault injection exists only as constructor parameters in tests and as the harness-only `_UnavailableDense` in the security gate. No production switch can force BM25.
- `check_compatibility=False` and fixed reason strings keep Qdrant URLs and API keys out of output.

## Observability

- Per result: `requested_strategy`, `strategy` (served), `fallback_reason`, `leg_latency_ms.dense_attempt`.
- Per evaluation: `served_strategies`, `fallback_counts`, `warmup_fallback_reason`, `latency_ms.by_served_path`, `qdrant_timeouts`.
- `make retrieve` prints a stderr warning line when the fallback serves a query.
- Langfuse and CloudWatch stay out of scope (roadmap 11). These fields are what a later trace would carry.

## Testing / evaluation strategy

All unit tests run under `make verify` without Docker, the extra or a model.

- **R1 (`test_availability.py`):**
  - Qdrant table over constructed exceptions:
    - `ResponseHandlingException` wrapping `httpx.ConnectError`, `ConnectTimeout`, `ReadTimeout` and `ReadError` (eligible);
    - bare httpx transport errors (eligible);
    - `ResponseHandlingException` wrapping a `ValidationError` or `ValueError` (not eligible);
    - `UnexpectedResponse` 404 and 503 (not eligible).
  - **Unrelated error during handling:** `try: raise httpx.ConnectError(...)`, then `except: raise ValueError(...)`, both bare and wrapped as `ResponseHandlingException(ValueError)`. Not eligible.
  - `DenseIndex` methods with a fake client raising each one.
  - Model table (without the extra; hub classes are stood in by local subclasses when the hub is not importable):
    - `OSError` from `httpx.ConnectError` (eligible);
    - `OSError` from `TimeoutError` (eligible);
    - an `OSError` → `LocalEntryNotFoundError`-like → `httpx.ConnectError` chain (eligible);
    - **missing revision**: an `OSError` → `RevisionNotFoundError`-like → `httpx.HTTPStatusError` chain (not eligible);
    - **missing model ID**: an `OSError` → `RepositoryNotFoundError`-like chain (not eligible);
    - a plain `OSError`, `PermissionError` and an `OfflineModeIsEnabled`-like error (not eligible);
    - an `OSError` raised while handling a `ConnectError` without `from` (not eligible: `__context__` is not followed);
    - `OptionalDependencyError` (not eligible).
  - `DenseRetriever` with a fake embedder raising each. `hybrid` fails closed on the missing-revision and missing-model-ID cases, and serves BM25 with `model_unavailable` on the connection error.
- **R2:**
  - a config validation test (missing block, 0, 31, non-integer);
  - a **stalled fake Qdrant**: a local TCP listener on a thread that accepts and never answers. `DenseIndex.search` with `query_timeout_s: 1` raises `qdrant_timeout` in under 1 s plus a 2 s tolerance, and `hybrid` through `open_retrieval` serves BM25;
  - the same for an open-time call with `connect_timeout_s: 1`.
- **R3/R4:** identity mismatch per field; open needs no client (factory raises if called); freshness passes on the seed copy and refuses after editing one document in a temporary repository copy (counts in the message, no text).
- **R5:**
  - `bm25` with embedder and client factories that raise, and `sys.modules["sentence_transformers"] = None`;
  - characterization: hits equal the Spec 007 path on the same fixture.
- **R6:** the six cases listed in R6, with fake retrievers and fake failing indexes. Also: same `access` object, fallback hits equal `bm25`, and every query retries the primary (call count).
- **R7/R8:**
  - result-model and CLI output tests;
  - 2.2 equivalence with 2.1 on the no-fallback fixture;
  - a fully-fallback fixture (single path, top-level values set);
  - a mixed fixture (`null` top-level strategy, score kind and p50/p95; `by_served_path` has two entries).
- **R9:** reader tests for 1.0, 2.0, 2.1 and 2.2; mixed refused; fallback-only 2.2 vs a 2.1 BM25 fixture compares; embedder pair from `dense_identity`.
- **R10:** `test_security_eval.py`: every path gated, a forbidden hit injected into each path fails the gate, result 1.2 keys present. `make eval-security` passes.
- **R11:**
  - closed port: bind port 0, close, point the client there. `hybrid` serves BM25 with `qdrant_unavailable`, and `dense` exits 2 with `RetrievalUnavailableError`;
  - `make test-integration` (Docker) is unchanged and must pass.
- **R12 (user):**
  - `QDRANT_URL=http://127.0.0.1:<closed port> make eval-retrieval` (default strategy), then `make eval-compare` against `…20261028T123109Z.json` (expect 64 to 64, MRR 0.7082, no flip);
  - with Qdrant up, `make eval-retrieval`, then compare against `…20261028T123121Z.json` (68 to 68, MRR 0.9094);
  - `make setup` (no extra), then `make retrieve QUERY=... RETRIEVE_ARGS="--strategy bm25"` with Qdrant unreachable.

## Phase 2 compatibility / migration

- The lexical file format and `lexical-v1` are unchanged. Existing files need no rebuild. Only `config/retrieval.yaml` moves to schema 1.1.
- `IndexIdentity` and the standalone open are per collection. A roles spec adds one file per access scope (D050) by choosing the path per scope; the open and freshness logic do not change.
- The freshness check is the place to bind a Knowledge Release snapshot ID later (Phase 2), replacing the full recompute for a large corpus.
- `FallbackRetriever` is generic over a primary and a fallback `Retriever`. The roadmap 13 reranker fallback can reuse the pattern. The HTTP route adds the circuit breaker and startup policy around `open_retrieval`.

## Alternatives / deferred decisions

- **Catching inside `HybridRetriever` or `rrf_fuse`:** rejected. D052 keeps fusion fail-closed, and a wrapper keeps the switch explicit and separately tested.
- **Circuit breaker or cached failure state:** deferred to the HTTP route spec (see the worst-case latency above).
- **Health probe before each query:** rejected. It adds a round trip, races with the real call, and is out of scope.
- **Separate httpx connect and read timeouts through a custom transport:** rejected. qdrant-client exposes only an integer `timeout`; injecting an httpx client means relying on private API. The client default plus the per-request override enforce both bounds.
- **Mapping model failures inside `bge_m3.py`:** rejected. It would change ingestion's error types; the mapping lives on the retrieval side.
- **Treating Qdrant 5xx as unavailable:** deferred (proposed decision D062). Only transport errors are eligible now, to keep the eligible set small and certain. A 5xx can be a server bug as well as an outage. Revisit with the HTTP route.
- **Mapping every model `OSError`:** rejected (design review). transformers and the hub raise `OSError` for configuration errors as well, so only a network or timeout cause is eligible.
- **Walking `__context__`:** rejected for both sources. An implicit context can link an unrelated failure to an earlier network error.
- **Trusting the file's recorded digest without a recompute:** rejected by the user (Q3, fail closed).
- **Latency as a "not comparable" flag:** rejected in favour of grouping by served path (see R8).

Proposed decisions (written in the final task): D056 Spec 008 ahead of roadmap 7; D057 failure classification; D058 `FallbackRetriever` policy and worst-case latency; D059 Qdrant timeouts and the client factory; D060 standalone lexical open and repository freshness check (large-corpus caveat); D061 result 2.2, security 1.2 and served-strategy comparison; D062 Qdrant HTTP status errors (including 5xx) are not fallback-eligible in Phase 1 retrieval, revisit with the HTTP route.
