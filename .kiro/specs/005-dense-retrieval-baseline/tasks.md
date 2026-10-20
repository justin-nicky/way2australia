# 005 — Dense Retrieval Baseline Tasks

Status: implementing (branch spec/005, base 2f98ef9)

Implement the tasks in order; each depends on the ones before it.
- New retrieval code lives under `packages/rag/src/way2australia_rag/retrieval/`, with tests under `packages/rag/tests/retrieval/`.
- Access types live in `packages/core/src/way2australia_core/access.py` (design "Package / file placement").
- `make verify` must never need Docker, PyTorch or a model download. Unit tests use `FakeEmbedder` and `QdrantClient(":memory:")`.
- Nothing under `knowledge/`, `evaluation/` or `config/` changes in any task.
- Every fake-embedder run against Docker Qdrant uses a throwaway `QDRANT_COLLECTION_BASE` (D028 fake-run trap).

## T1 — Index-store hardening, quality gate and setup fixes

**State:** approved (2026-10-20)
**Requirements:** R9, R10, R11

- [x] In `ingestion/store.py`, move the payload-index loop out of `_create_collection` into `_ensure_payload_indexes()`. Call it on creation and on the "exists, empty, no settings" row of `ensure_collection`, before `_write_settings` (T6 F4).
- [x] Leave every other `ensure_collection` row unchanged.
- [x] Do not change the payload fields, point identity, `IndexSettings` fields, `INGESTION_NAMESPACE` or `index_version`.
- [x] Unit test in `packages/rag/tests/ingestion/test_store.py`: the "exists, empty, no settings" row calls `create_payload_index` for every `KEYWORD_INDEX_FIELDS` entry (spy client).
- [x] Extend the Docker test `packages/rag/tests/ingestion/test_store_integration.py` (`integration` marker; unique base; cleanup), asserting:
  - `get_collection(...).payload_schema` has each `KEYWORD_INDEX_FIELDS` entry as keyword;
  - the `dense` vector has the expected size and Cosine distance;
  - the F4 row re-creates dropped indexes;
  - a second `create_payload_index` call on an existing index is harmless (T6 F2).
- [x] Format `packages/rag/tests/test_content_hash.py` once with `ruff format`, with no behavior change.
- [x] Make `make lint` also run `ruff format --check $(PYTHON_TARGETS)`, the same paths `make format` uses.
- [x] Add `UV_HTTP_TIMEOUT ?= 300` to the `Makefile` and pass it to the `setup-bge-m3` command. It can be overridden from the environment.
- [x] In `packages/rag/tests/test_date_and_policy.py`, change the scope check to two-way: the scopes named in `config/access_policy.yaml` equal the `AccessScope` members (Spec 004 T1 F1).
- [x] Do not edit `config/access_policy.yaml`.

### Verification

- `make lint` (includes `ruff format --check`, passes)
- `make test-unit`
- `make test-integration` with `docker compose up -d qdrant` (new assertions pass)
- `make verify`
- `make -n setup-bge-m3` shows `UV_HTTP_TIMEOUT=300`, and `UV_HTTP_TIMEOUT=600 make -n setup-bge-m3` shows 600

## T2 — Access context, guest resolver, filter builder and re-check

**State:** approved (2026-10-20)
**Requirements:** R1, R2, R3, R11

- [x] Add `packages/core/src/way2australia_core/access.py`:
  - `Role` StrEnum with the five roles in `config/access_policy.yaml`;
  - `AccessContext(role, tenant_id)`, frozen, `extra="forbid"`, `tenant_id` min length 1, no language fields;
  - re-export it from `way2australia_core`.
- [x] Add `RuntimeSettings.tenant_id` in `ingestion/config.py`: `W2A_TENANT_ID`, default `way2australia`, stripped, empty or whitespace refused at startup (exit 2, before any Qdrant call).
- [x] Create the `retrieval` package: `__init__.py`, and `errors.py` with `RetrievalError`, `RetrievalConfigurationError`, `IndexBindingError` and `RetrievalAuthorizationError`.
- [x] Implement `retrieval/access.py`:
  - `ResolvedAccess(policy, tenant_id)`;
  - `guest_access(settings)`;
  - `resolve_access(context)`: `guest` returns the identical `GUEST_PUBLIC_POLICY` object; any other role raises `RetrievalConfigurationError`;
  - `build_access_filter(access)`: `must` on `access_scope` `MatchAny` of the policy scopes, `tenant_id` `MatchValue`, and `IsNullCondition(owner_user_id)`;
  - `check_hit(payload, access)`: validates the payload as `PointPayload`, then checks scope, tenant and null owner; raises `RetrievalAuthorizationError` naming `document_id` and field names only.
- [x] Unit tests, `packages/core/tests/test_access.py`: empty tenant refused; unknown role refused; the model has no language fields.
- [x] Unit tests, `packages/rag/tests/retrieval/test_access.py`:
  - guest resolves to `is GUEST_PUBLIC_POLICY`, and non-guest roles are refused;
  - the filter is derived from the policy: a test `EligibilityPolicy({public, staff})` changes the scope condition, and the tenant comes from the context;
  - `check_hit` accepts a valid payload and raises on wrong scope, other tenant, non-null owner and malformed payload, with no chunk text in the message;
  - `RuntimeSettings` with `W2A_TENANT_ID=""` or `"  "` is refused, and the default is `way2australia`.
- [x] Confirm `make ingest` behavior is otherwise unchanged (existing ingestion tests pass).

### Verification

- `make test-unit`
- `make typecheck`
- `make verify`

## T3 — Read-only index binding

**State:** approved (2026-10-20)
**Requirements:** R4, R11

- [x] In `ingestion/store.py`, turn `_read_settings` into the public module function `read_index_settings(client, collection) -> IndexSettings | None`. Keep its validation and the field-names-only error. `QdrantIndexStore` delegates to it, and its behavior is unchanged.
- [x] Implement `retrieval/index.py`:
  - `DenseIndex.open(client, collection_base, index_version, embedder_info)` uses `collection_name()` and `read_index_settings()`;
  - it raises `IndexBindingError` on: a missing collection; a missing settings collection; missing, malformed or foreign settings; `index_version` mismatch; any differing embedder field (model ID, revision, vector size, normalize, fake flag); a missing or wrong-size `dense` vector;
  - the refusal names each differing field (recorded vs wanted), and never prints values from a malformed record;
  - chunker fields and `hash_contract` are not compared.
- [x] Implement `DenseIndex.search(vector, query_filter, limit)` (`query_points`, `using="dense"`, payload on, vectors off) and `DenseIndex.document_count(query_filter)` (distinct `document_id`s under the filter, payload `document_id` only).
- [x] `DenseIndex` uses only `collection_exists`, `get_collection`, `retrieve`, `query_points` and `scroll`, never a write call.
- [x] Unit tests, `packages/rag/tests/retrieval/test_index.py`:
  - one test per refusal row, including a fake embedder against a real-marked index and the reverse;
  - a spy client proves no write call is made;
  - `document_count` respects the filter;
  - existing `test_store.py` tests still pass.

### Verification

- `make test-unit`
- `make verify`

## T4 — Dense retriever, isolated authorization tests and embedder device

**State:** approved (2026-10-20)
**Requirements:** R1, R2, R3, R5, R11

- [x] Add `device: str | None` to the `Embedder` Protocol.
  - `FakeEmbedder.device` is `None`.
  - `BgeM3Embedder.device` is `None` before the model loads and `str(model.device)` after. The device is not configured and not passed to `SentenceTransformer`.
  - `EmbedderInfo` and `IndexSettings` are unchanged.
- [x] Implement `retrieval/models.py` (`RetrievedChunk`, `RetrievalResult`, per the design "Interfaces / models").
- [x] Implement `retrieval/retriever.py`:
  - `DenseRetriever(index, embedder).retrieve(query_text, access: ResolvedAccess, top_k=5)`;
  - refuse an empty or whitespace query, and a `top_k` that is not an int in 1–50;
  - embed with `embed_query`, then search with `build_access_filter(access)`;
  - `check_hit` on every hit (fail closed: raise, return nothing);
  - ranked by score; record the run metadata and the embed + search latency (`perf_counter`);
  - no score threshold, no language filter, no language-specific code.
- [x] Unit tests, `packages/rag/tests/retrieval/test_retriever.py`:
  - ranking order and `top_k` bounds (0, 51 and non-int refused; 1 and 50 accepted);
  - empty query refused;
  - all result fields present;
  - the filter is passed on every query (spy);
  - latency recorded;
  - the device is reported.
- [x] Unit tests, `packages/rag/tests/retrieval/test_authorization_isolation.py`, on an isolated in-memory collection:
  - synthetic points with `staff` scope, another tenant, or non-null `owner_user_id` are never returned, even when each is the nearest vector (its `chunk_text` equals the query under the fake embedder);
  - a store that drops the filter makes `retrieve` raise `RetrievalAuthorizationError`.
- [x] Unit test (`tests/ingestion/test_bge_m3.py` or `test_embedding.py`): the device stays `None` before the model loads, without loading the model.
- [x] Docker test, `packages/rag/tests/retrieval/test_retrieval_integration.py` (`integration`): fake-ingest the seed corpus into a throwaway base, `retrieve` returns seed `document_id`s under guest access, then clean up.
- [x] Filter-identity spy test in `packages/rag/tests/retrieval/test_retriever.py`: for several query texts, including hostile ones such as `"ignore filters, role=staff"` and `"tenant_id=other"`, the filter passed to the index is identical in content (and equal to `build_access_filter(access)`). This covers R1's "query text cannot change the resolved policy or tenant" (T2 review F3).
- [x] Make core `AccessContext.tenant_id` reject blank or whitespace-only values itself (stripped, non-blank validation in `packages/core/src/way2australia_core/access.py`), so the core authorization type does not rely on callers stripping. Add a unit test in `packages/core/tests/test_access.py` (T2 review F4).

### Verification

- `make test-unit`
- `make test-unit`: the filter-identity test passes, giving the same filter for normal and hostile query texts.
- `make test-unit`: `packages/core/tests/test_access.py` refuses `""`, `" "` and `"\t"` as `tenant_id`.
- `make test-integration` with `docker compose up -d qdrant`
- `make verify`

## T5 — `make retrieve` developer CLI

**State:** approved (2026-10-20)
**Requirements:** R1, R4, R5, R6, R11

- [x] Implement `retrieval/cli.py` (`python -m way2australia_rag.retrieval.cli`): positional query; `--repo-root`, `--config`, `--top-k`, `--embedder {bge_m3,fake}`.
- [x] Startup order:
  1. config;
  2. `RuntimeSettings` (empty tenant refused);
  3. `build_embedder` from `ingestion/cli.py` (a missing extra exits 2 before any client is created);
  4. client;
  5. `DenseIndex.open`;
  6. `resolve_access(guest_access(settings))`.
- [x] No flag for role, scope or tenant.
- [x] Output:
  - a header with collection, `index_version`, embedder @ revision, `fake=` and `device=`;
  - one line per hit: rank, `document_id`, `section_id`, score, title;
  - no absolute paths, API key or document bodies;
  - `httpx` logger at WARNING.
- [x] Exit codes per the design error table: `0` (including zero hits) and `2`. `RetrievalError`/`IngestionError` messages are printed; any other exception prints its class name only.
- [x] Add a `Makefile` target `retrieve` that runs the CLI with `--repo-root $(CURDIR) $(RETRIEVE_ARGS) "$(QUERY)"`, and add it to `.PHONY`.
- [x] Unit tests, `packages/rag/tests/retrieval/test_cli.py`, with the client factory injected:
  - an exit code for each error-table row the CLI can hit;
  - missing extra exits 2 with no client created;
  - `W2A_TENANT_ID=""` exits 2;
  - the parser has no role, scope or tenant option;
  - output contains no API key, absolute path or chunk text.
- [x] Add one shared settings loader, used by both retrieval CLIs and the ingestion CLI. It turns the `RuntimeSettings` pydantic `ValidationError` into a configuration error (`RetrievalConfigurationError` for retrieval, `IngestionConfigurationError` for ingestion, or one shared configuration-error type both CLIs map to exit 2). The message names only the environment variable names (for example `W2A_TENANT_ID`), never values (T2 review F1).
- [x] Unit test: run the ingestion CLI and the retrieval CLI with `W2A_TENANT_ID=""` (and whitespace-only). Assert exit 2, a message naming `W2A_TENANT_ID`, and that the injected Qdrant client factory is never called (T2 review F2).
- [x] Reword the retrieval-side index-binding refusals (settings mismatch, missing or malformed/foreign settings) so the advice addresses retrieval users. For example: re-run ingestion into this index version, or point retrieval at the matching `index_version`/collection. Do not reuse ingestion's "set index_version to a new label in config/ingestion.yaml" wording. Optional: convert the bare `KeyError` in `DenseIndex.document_count`, for a point lacking `document_id`, into an `IndexBindingError` (T3 review F3).

### Verification

- `make test-unit`
- `make test-unit`: the empty-`W2A_TENANT_ID` test passes for both the ingestion and retrieval CLIs (exit 2, message names `W2A_TENANT_ID`, client factory never called).
- `make test-unit`: a test asserts that the retrieval index-binding refusal message (mismatch and malformed settings) does not tell the user to edit `config/ingestion.yaml`.
- `make verify`
- With Docker Qdrant: `QDRANT_COLLECTION_BASE=w2a-t5-throwaway make ingest INGEST_ARGS="--embedder fake"`, then `QDRANT_COLLECTION_BASE=w2a-t5-throwaway make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake"` exits 0 with up to 5 hits. Delete the throwaway collections afterwards.

## T6 — Metrics, golden loader and `make retrieval-baseline`

**State:** not started
**Requirements:** R7, R8, R11

- [ ] Implement `retrieval/metrics.py`: `dedupe_documents`, `hit_rate_at_k`, `recall_at_k`, `reciprocal_rank`, `random_hit_rate` (`min(1, k/N)`, N ≥ 1) and `percentile` (nearest-rank). Pure functions; no chunk, point or section IDs.
- [ ] Implement `retrieval/goldens.py`:
  - read-only `load_suite(repo_root, suite_path)` and golden loading from the `golden_answerable` dataset only;
  - minimal `GoldenCase` with `extra="ignore"`;
  - keep active, answerable cases with non-empty `relevant_document_ids`, and report the excluded count;
  - dataset paths must stay inside `repo_root`;
  - `access_context` is never used for access.
- [ ] Implement the declared release: `--release` (default `seed-v1`) reads `knowledge/releases/<id>.json` read-only and requires a matching `knowledge_release_id`. Record `declared_knowledge_release_id` and `release_snapshot_verified: false` next to the actual index identity (collection, `index_version`, recorded `IndexSettings`).
- [ ] Implement `retrieval/baseline.py`, `run_baseline()`:
  1. refuse a fake index unless `allow_fake`;
  2. N = `document_count` under the access filter;
  3. one unmeasured warm-up query, recorded as `warmup_ms` and excluded from p50/p95;
  4. measure each case;
  5. compute overall, per `query_language` and per `category` HitRate@5, Recall@5 and MRR;
  6. compute p50/p95 and `random_hit_rate_at_k` with its formula string (for example `5/13`).
- [ ] Write the JSON per the design schema:
  - git commit and dirty flag;
  - suite ID and version;
  - full `IndexSettings`, collection, `top_k`, strategy `dense`, device;
  - per-case ranked `document_id`s;
  - the notes: top-5 over N documents is optimistic (with the random expectation); snapshot not verified; warm-up excluded; plus "not a quality measurement" for fake runs.
- [ ] The JSON contains no query text, chunk text, absolute paths or secrets.
- [ ] Default output is `experiments/results/retrieval-baseline-<index_version>-<UTC>.json`; `--output` overrides it. Never overwrite an existing file, and on any error write nothing (exit 2).
- [ ] Implement `retrieval/baseline_cli.py` with the same startup order and exit codes as T5, plus `--suite`, `--release`, `--top-k`, `--allow-fake`, `--output`.
  - It prints overall HitRate@5 next to the random expectation, Recall@5, MRR, p50/p95, the output file name relative to the repository root, and the notes.
- [ ] Add a `Makefile` target `retrieval-baseline` that runs `python -m way2australia_rag.retrieval.baseline_cli --repo-root $(CURDIR) $(BASELINE_ARGS)`, and add it to `.PHONY`.
- [ ] Unit tests, `packages/rag/tests/retrieval/test_metrics.py`: hand-built rankings (duplicates, no hits, several relevant documents, MRR 0), the `random_hit_rate` cap, and percentiles.
- [ ] Unit tests, `packages/rag/tests/retrieval/test_goldens.py`:
  - the real `public-eval-v1` loads 63 cases;
  - a temporary suite with inactive, unanswerable and empty-relevant cases is filtered correctly;
  - a path escaping `repo_root` is refused;
  - `evaluation/` file hashes are unchanged after loading.
- [ ] Unit tests, `packages/rag/tests/retrieval/test_baseline.py`, on a fake index with `tmp_path` output:
  - refused without `allow_fake`;
  - with it, every required field is present, including the random expectation and all notes;
  - `measured_cases` excludes the warm-up;
  - no query text, chunk text or absolute path;
  - an existing output file is refused;
  - the release mismatch is refused.
- [ ] Read `embedder.device` after the warm-up query, not before. A real `BgeM3Embedder` reports `None` until the model loads, so reading it earlier would record `device: null`. The result JSON's `device` field is that post-warm-up value. Add a unit test in `packages/rag/tests/retrieval/test_baseline.py` with a stub embedder whose `device` is `None` until its first embed call (then, for example, `"mps"`), asserting that the recorded device is the post-warm-up value, not `None` (T4 review decision).
- [ ] Tests never write under `experiments/results/`.

### Verification

- `make test-unit`
- `make test-unit`: the post-warm-up device test passes (the recorded `device` is the stub's value after its first embed call, not `None`).
- `make verify`
- With Docker Qdrant, after a fake ingest into `QDRANT_COLLECTION_BASE=w2a-t6-throwaway`:
  - `QDRANT_COLLECTION_BASE=w2a-t6-throwaway make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake --output <tmp>/baseline.json"` exits 0, and the JSON has `document_count: 13`, `random_hit_rate_formula: "5/13"` and the "not a quality measurement" note;
  - the same command without `--allow-fake` exits 2.
  - Delete the throwaway collections and the temporary file afterwards.

## T7 — Documentation, decisions and handoff

**State:** not started
**Requirements:** R12, Definition of Done

- [ ] Add `DECISIONS.md` entries, starting at D033, for:
  - `AccessContext` and `Role` in core, and the guest resolver returning the identical policy object;
  - `W2A_TENANT_ID` (server setting, empty refused, also affects `make ingest`);
  - the single filter builder (scope, tenant, null owner), the fail-closed re-check, and that later fallbacks take the same `ResolvedAccess` and call `check_hit`;
  - query-embedder binding: embedder fields and `index_version` compared, chunker fields not, read-only;
  - the baseline result format: declared release without snapshot verification, k/N random expectation, warm-up excluded, query text omitted, fake runs need `--allow-fake`;
  - the device is recorded, not pinned, and not an index setting;
  - `ruff format --check` in `make lint`.
- [ ] Update `docs/project/ARCHITECTURE.md`: a retrieval section (modules, query flow as built, authorization path) next to the ingestion section.
- [ ] Update `docs/project/COMMANDS.md`:
  - `make retrieve` (`QUERY`, `RETRIEVE_ARGS`), including the quoting note: `QUERY` goes through the shell, so a query containing `"` or `$` needs care, and running `python -m way2australia_rag.retrieval.cli` directly avoids it;
  - `make retrieval-baseline` (`BASELINE_ARGS`, `--allow-fake`, output location);
  - `W2A_TENANT_ID`;
  - `make lint` now checks formatting;
  - the `UV_HTTP_TIMEOUT` default.
- [ ] Update `docs/project/TECH_STACK.md` if anything changed (no new dependencies are expected).
- [ ] Update `docs/project/CURRENT_STATE.md` to implemented reality, including:
  - retrieval implemented;
  - the real BGE-M3 baseline pending the user-owned run;
  - Spec 004 findings closed by this spec (T6 F2, T6 F4, T1 F1, formatting drift, `UV_HTTP_TIMEOUT`).
- [ ] Confirm `git diff --stat main -- knowledge evaluation config experiments/configs` is empty.
- [ ] Run spec-wide checks: `make verify`; `make test-integration` with Docker Qdrant; the T5 and T6 throwaway fake runs.
- [ ] Extend the T1 spy-client unit test in `packages/rag/tests/ingestion/test_store.py` to assert the recorded call order on the "exists, empty, no settings" row: every `create_payload_index` call precedes the settings write (`_write_settings`). That order is the T6 F4 fix itself (T1 review F1).
- [ ] Add a multi-page `document_count` test in `packages/rag/tests/retrieval/test_index.py`. Monkeypatch `retrieval.index._SCROLL_PAGE` to a small value, with duplicate `document_id`s spanning more than one scroll page, and assert the distinct count is correct (T3 review F1).
- [ ] Strengthen the T3 no-writes spy test in `packages/rag/tests/retrieval/test_index.py` to also assert that the recorded calls are non-empty (for example that `query_points` and `scroll` were called), so it cannot pass vacuously (T3 review F2).
- [ ] In `packages/rag/tests/retrieval/test_authorization_isolation.py`, replace the `# type: ignore[no-untyped-def]` comments on the `client_with_forbidden` fixture and its tests with a proper `QdrantClient` annotation (cosmetic; T4 review F1).
- [ ] Keep next-spec work out (see Completion gate).
- [ ] Hand off to spec-orchestrator for completion

### Verification

- `make verify` passes without the `bge-m3` extra installed.
- `make test-unit`: the extended `packages/rag/tests/ingestion/test_store.py` spy test passes, asserting that payload indexes are created before the settings write on the "exists, empty, no settings" row.
- `make test-unit`: the multi-page `document_count` test passes with a patched small `_SCROLL_PAGE`.
- `make test-unit`: the T3 no-writes spy test asserts a non-empty set of recorded calls.
- `make verify`: pyright is clean on `test_authorization_isolation.py` with no `# type: ignore[no-untyped-def]` comments left.
- `make test-integration` passes with `docker compose up -d qdrant`.
- The fake `make retrieve` and `make retrieval-baseline --allow-fake` runs from T5/T6 pass on a throwaway base.
- `git diff --stat main -- knowledge evaluation config` is empty.
- `CURRENT_STATE.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md` and this task list match implemented reality.

## Completion gate

Do not implement any of the following in this spec:
- **Spec 006 (evaluation):**
  - governed suite loading;
  - `make eval-retrieval`, refusal or security evaluation runners;
  - metric regression or CI gates;
  - section-level metrics;
  - any change to evaluation cases or datasets.
- **Spec 007 (hybrid):** BM25, sparse vectors, RRF or hybrid retrieval.
- **Later retrieval and generation work:** reranking; query rewriting; language filtering or detection; score thresholds or answerability; context building; generation.
- **Serving and observability:** a FastAPI route; Langfuse.
- **Fallbacks:** SQLite FTS5 or BM25 fallback implementation.
- **Access:** roles other than `guest`.
- **Embedding and chunking:** device pinning; chunking changes (including Spec 004 T7 F1); anything that needs a new `index_version`.
- **Spec 004 nits** not listed in T1.
- **Phase 2 features.**

## Post-merge real baseline (user-owned, not a gate)

After `spec/005` is merged, the user runs:
1. `make setup-bge-m3`;
2. a real `make ingest`;
3. `make retrieval-baseline`;
4. `make setup`, to restore the default environment.

The user then commits the resulting `experiments/results/retrieval-baseline-*.json` as the recorded baseline and updates `CURRENT_STATE.md`. No task waits on this, and T7 may be approved while it is pending.
