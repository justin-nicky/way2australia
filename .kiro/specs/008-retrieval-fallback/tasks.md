# 008 — Retrieval Fallback Tasks

Status: implementing (branch spec/008, base f25b552)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-10-29; R1/R6 amended 2026-10-29). Design: `design.md` (approved 2026-10-29).

Rules for every task:
- **Protected paths.** `evaluation/` and `knowledge/` never change in this spec. `config/` changes only in T1 (`config/retrieval.yaml`: schema 1.1 plus the `qdrant` block). Every task checks `git status --porcelain -- evaluation knowledge config` and the reviewer compares the output with the task's allowed list.
- **Unchanged code.** `ingestion/` (including `bge_m3.py`, `embedding.py`, `default_client_factory`), `lexical/tokenizer.py`, `lexical/build.py`, the lexical file format, `retrieval/fusion.py`, `retrieval/hybrid.py`, `retrieval/access.py`, `retrieval/metrics.py`, `retrieval/baseline.py` and `retrieval/baseline_cli.py` are not edited. The single exception is moving `embedder_identity` out of `lexical/cli.py` (T2), with behavior unchanged. The legacy snapshot test passes untouched (D046).
- **Dense and hybrid rankings stay identical** when nothing fails. Existing tests may change only where a signature changes (`BM25Retriever`, `build_retriever`, `run_retrieval_evaluation`, `RetrievalConfig` 1.1 fixtures). Ranks, scores, document IDs and ordering in their assertions never change.
- **No production fault switch.** Failures are injected only through constructor or factory parameters in tests, and through the harness-only `_UnavailableDense` in the security gate (T6). No CLI flag, environment variable or config key forces a fallback.
- **`make verify` never needs Docker, PyTorch, the `bge-m3` extra or a model download.** Unit tests use `FakeEmbedder`, `QdrantClient(":memory:")`, SQLite files under `tmp_path`, local stalled or closed TCP sockets, and constructed exceptions. Timing tests use 1 s timeouts with a tolerance of at most 2 s.
- **No live-count literals in new tests.** Counts come from the data being tested; literal counts only in synthetic fixtures the test builds.
- **Real systems.** Agents never write to, delete or re-ingest a `w2a-realcheck-*` collection and never run the real model. Docker runs use throwaway bases (`w2a-t008-<8 hex>`, `w2a-sectest-<8 hex>`) and delete them afterwards.
- **Results.** Tests never write under `experiments/results/` (use `tmp_path`). Throwaway CLI output goes to `experiments/results/tmp/`. Committed result files are never modified.
- **Messages.** Messages and output never contain Qdrant URLs, API keys, exception texts from httpx, qdrant-client or the Hugging Face stack, or chunk text. Reasons come from `FallbackReason` only.
- After code changes, run `graphify update .` (D048).
- **`task-reviews.md`** is edited only by exact, targeted edits.
- **Review reading order.** Each task lists the order in which the task reviewer reads the change.

## T1 — Failure classification and Qdrant timeouts

**State:** not started
**Requirements:** R1, R2, R13

- [ ] **Confirm the Hugging Face error shapes first** (design R1, "What the pinned stack raises"). Inspect the pinned sources read-only:
  - versions: sentence-transformers 6.1.0, transformers 5.20.0, huggingface-hub 1.33.0;
  - source: the user's `make setup-bge-m3` environment or, only with the user's permission, `uv pip download --no-deps` into a scratch directory outside the repository;
  - record the four shapes (network down, unknown model ID, unknown revision, gated repository) and whether each uses `raise ... from` in the design's `## As-built notes`;
  - if a shape differs, adjust only the type list. The rule stays "eligible only with a network or timeout cause in the explicit `__cause__` chain".
- [ ] `retrieval/errors.py`: `FallbackReason` (`qdrant_unavailable`, `qdrant_timeout`, `model_unavailable`) and `RetrievalUnavailableError(reason)` with a fixed, path-free message.
- [ ] New `retrieval/availability.py`:
  - `classify_qdrant_error`: unwraps one level, through `ResponseHandlingException.source` only; never follows `__cause__` or `__context__`;
  - `classify_model_error`: follows the explicit `__cause__` chain only, at most 10 links; the network and timeout type list; the guarded `OfflineModeIsEnabled` exclusion;
  - both return `None` for anything else.
- [ ] `retrieval/index.py`:
  - every client call in `open`, `search`, `document_count` and `chunk_identities` goes through `classify_qdrant_error`; a mapped error is raised from the original, and anything else is re-raised unchanged;
  - `search` passes `timeout=query_timeout_s` to `query_points` (the value is given to `DenseIndex`).
- [ ] `retrieval/retriever.py`: wrap only the `embed_query` call with `classify_model_error`.
- [ ] `retrieval/strategy.py`: `RetrievalConfig` schema `1.1` with `QdrantTimeouts(connect_timeout_s, query_timeout_s)`, integers from 1 to 30. A missing or invalid block is a `RetrievalConfigurationError` naming the field.
- [ ] `config/retrieval.yaml`: `schema_version: "1.1"`, `qdrant: {connect_timeout_s: 2, query_timeout_s: 3}`; the other keys are unchanged.
- [ ] New `retrieval/qdrant_client.py`: `retrieval_client_factory(settings, timeouts)` with `timeout=connect_timeout_s` and `check_compatibility=False`.
- [ ] `make retrieve` and `make eval-retrieval` use the new factory. Their existing `client_factory` test parameter keeps working. Ingestion is not changed.
- [ ] Tests:
  - `packages/rag/tests/retrieval/test_availability.py`: the Qdrant and model tables from the design testing section, including:
    - the unrelated-error-during-handling case, bare and wrapped;
    - missing revision and missing model ID fail closed;
    - a connection error during load gives `model_unavailable`;
    - `__context__` without `from` is not eligible;
  - `test_index.py` additions: a fake client raising each error type through each `DenseIndex` method;
  - **stalled fake**: a local TCP listener thread that accepts and never answers. `DenseIndex.search` with `query_timeout_s: 1` raises `qdrant_timeout` within 1 s + 2 s, and an open-time call with `connect_timeout_s: 1` likewise;
  - `test_retriever.py` additions: `DenseRetriever` with a fake embedder raising each model case;
  - `test_strategy.py`: config 1.1 validation (missing block, 0, 31, non-integer, 1.0 refused); existing fixtures moved to 1.1;
  - the factory sets the timeout and `check_compatibility=False`, checked with a recording fake constructor.

Allowed protected-path changes: `config/retrieval.yaml` (schema version and `qdrant` block only).

### Verification

- `make verify` passes (new tests included).
- `git diff -- config/retrieval.yaml` shows only `schema_version` and the `qdrant` block.
- `git status --porcelain -- evaluation knowledge config` lists only `config/retrieval.yaml`.
- `git diff --stat -- packages/rag/src/way2australia_rag/ingestion packages/rag/src/way2australia_rag/retrieval/hybrid.py packages/rag/src/way2australia_rag/retrieval/fusion.py` is empty.
- The As-built note on the Hugging Face error shapes is present in `design.md`.

Review reading order: design As-built note → `retrieval/errors.py` → `retrieval/availability.py` → `test_availability.py` → `retrieval/index.py`, `retriever.py` → `strategy.py`, `config/retrieval.yaml`, `qdrant_client.py` → remaining tests.

## T2 — Index identity, standalone lexical open and freshness check

**State:** not started
**Requirements:** R3, R4, R13

- [ ] New `retrieval/identity.py`:
  - `IndexIdentity` (`collection`, `index_version`, `embedder_model_id`, `embedder_revision`, `embedder_is_fake`, `source`);
  - `from_dense(index)`;
  - `expected(ingestion_config, settings, provider)`, which never builds an embedder.
- [ ] Move `embedder_identity` from `lexical/cli.py` to `ingestion/identity.py` (or a new shared module named in the As-built notes) with behavior unchanged; `lexical/cli.py` imports it.
- [ ] `lexical/store.py`:
  - `LexicalIndex.check_identity(expected, chunker, hash_contract)`, refusing with field names and `REBUILD_ADVICE`;
  - `chunk_set_difference(expected, mine)`, extracted from `bind_to`, which keeps its exact message;
  - `LexicalIndex.document_count(where, params)`: distinct `document_id` under the SQL access clause.
- [ ] New `lexical/freshness.py`: `verify_fresh(lexical, repository, chunker)`. It recomputes the digest from `production_entries`; on a mismatch it raises `LexicalIndexBindingError` with counts and `REBUILD_ADVICE`, never text.
- [ ] `open_standalone_lexical(settings, repo_root, expected, chunker, repository)` (in `retrieval/opening.py`, created here): `open`, then `check_identity`, then `verify_fresh`.
- [ ] Tests (`packages/rag/tests/lexical/test_lexical_standalone.py`):
  - each identity field mismatch is refused, and the message has no path or text;
  - the standalone open passes a Qdrant client factory and an embedder factory that raise if called;
  - freshness passes on a `tmp_path` copy of the seed repository with a file built from it;
  - freshness refuses after one document's body is edited in the copy (counts in the message), and after one document is removed;
  - `document_count` honors the access clause (synthetic forbidden rows);
  - `bind_to` message unchanged (existing `test_lexical_bind.py` passes untouched).

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `git diff -- packages/rag/tests/lexical/test_lexical_bind.py` is empty.
- `git status --porcelain -- evaluation knowledge config` is empty.

Review reading order: `retrieval/identity.py` → `lexical/store.py` diff → `lexical/freshness.py` → `retrieval/opening.py` → tests.

## T3 — `bm25` without Qdrant or the `bge-m3` extra; one open path

**State:** not started
**Requirements:** R5, R13

- [ ] `retrieval/bm25.py`: `BM25Retriever(identity: IndexIdentity, lexical: LexicalIndex)`. Header fields come from `identity`; retrieval logic is unchanged.
- [ ] `retrieval/strategy.py`: `build_retriever(strategy, identity, dense_index | None, embedder | None, lexical, config)`. `hybrid` builds `HybridRetriever` as today (no wrapper yet).
- [ ] `retrieval/opening.py`: `open_retrieval(...) -> OpenedRetrieval(retriever, identity, document_count, close)` for `dense` (as today), `bm25` (standalone open, no embedder, no client) and `hybrid` (embedder, client, `DenseIndex.open`, `open_bound_lexical`; no fallback yet).
- [ ] `retrieval/cli.py` and `evaluation/cli.py` use `open_retrieval`. `run_retrieval_evaluation` takes `identity: IndexIdentity`, `document_count: int` and `embedder: Embedder | None` instead of `index`. Result format stays 2.1 in this task, with byte-equal values for `dense` and `hybrid` runs, and an `index_settings` value unchanged when the dense side is bound.
- [ ] `require_real_index` uses `identity.embedder_is_fake`.
- [ ] Tests:
  - `test_bm25.py`: a characterization test. On one lexical fixture the Spec 007 construction (dense fixture binding) and the standalone path return equal `hits`;
  - `bm25` through `open_retrieval` and both CLIs with raising embedder and client factories and `sys.modules["sentence_transformers"] = None`;
  - a test pins that the `bm25` path never imports `way2australia_rag.ingestion.bge_m3`;
  - `test_strategy_eval.py` and `dense_equivalence.py` pass with the new signature and unchanged values.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make test-integration` (Docker Qdrant running) passes.
- `make index-lexical LEXICAL_ARGS="--embedder fake"` and `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --strategy bm25"`, run against a throwaway `QDRANT_COLLECTION_BASE=w2a-t008-<8 hex>` after `make ingest INGEST_ARGS="--embedder fake"`, return hits. The bm25 call is repeated with `QDRANT_URL` pointing at a closed port and still returns hits. The throwaway collection and lexical file are removed afterwards.
- `git status --porcelain -- evaluation knowledge config` is empty.

Review reading order: `bm25.py` → `strategy.py` → `opening.py` → `retrieval/cli.py`, `evaluation/cli.py`, `retrieval_eval.py` → tests.

## T4 — Fallback policy for `hybrid` and result marking

**State:** not started
**Requirements:** R6, R7, R2, R11

- [ ] New `retrieval/fallback.py`: `FallbackRetriever(primary, fallback, open_reason)` exactly as in design R6:
  - a single `except RetrievalUnavailableError`;
  - the same `access` and `top_k`;
  - latency includes the failed attempt, recorded in `leg_latency_ms.dense_attempt`;
  - no state between queries.
- [ ] `build_retriever` wraps `hybrid` in `FallbackRetriever`. `open_retrieval` implements the hybrid open-time fallback:
  - on a `RetrievalUnavailableError` from client creation, `DenseIndex.open` or `bind_to`, it falls back to `open_standalone_lexical` and `FallbackRetriever(None, BM25(expected), reason)`;
  - a missing extra and every other error are raised.
- [ ] `retrieval/models.py`: `requested_strategy`, `fallback_reason` (optional). Every retriever sets `requested_strategy`.
- [ ] `make retrieve`:
  - header `strategy: bm25 (requested: hybrid; fallback: <reason>)` and a stderr `WARNING` line; exit 0;
  - an explicit `dense` with an unavailable Qdrant prints `ERROR RetrievalUnavailableError: ...` and exits 2.
- [ ] Tests (`packages/rag/tests/retrieval/test_fallback.py`, CLI tests):
  - Qdrant down at open;
  - dense-leg failure on one query of several (the others stay hybrid);
  - model load failure with a network cause (falls back);
  - a missing revision or missing model ID (raised);
  - a non-eligible dense error (raised);
  - a BM25 error during fallback (raised);
  - `RetrievalAuthorizationError` from either leg (raised);
  - an explicit `dense` with Qdrant down (exit 2);
  - the same `access` object is passed to the fallback;
  - fallback hits equal `--strategy bm25` hits;
  - the primary is retried on every query (call count);
  - `fusion.py` and `hybrid.py` are unchanged (`git diff` empty);
  - **closed port** (R11): bind port 0, close it, point the factory there. `hybrid` serves BM25 with `qdrant_unavailable`; `dense` exits 2;
  - **stalled fake through `open_retrieval`** (R2): `hybrid` with `query_timeout_s: 1` serves BM25 with `qdrant_timeout` within the bound plus tolerance.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make test-integration` passes.
- With a throwaway fake-embedder collection and lexical file (as in T3), `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake"` prints `strategy: hybrid`. With `QDRANT_URL` pointing at a closed port it prints the fallback header, and with `--strategy dense` it exits 2. Clean up afterwards.
- `git diff --stat -- packages/rag/src/way2australia_rag/retrieval/fusion.py packages/rag/src/way2australia_rag/retrieval/hybrid.py` is empty.

Review reading order: `fallback.py` → `opening.py` diff → `models.py` → `retrieval/cli.py` → `test_fallback.py` → CLI tests.

## T5 — Evaluation result 2.2 and `eval-compare` by served strategy

**State:** not started
**Requirements:** R8, R9

- [ ] `evaluation/retrieval_eval.py`, result `retrieval_evaluation` 2.2, per design R8:
  - top level: `requested_strategy`, `served_strategies`, `retrieval_strategy`/`score_kind` (`null` when mixed), `fallback_counts`, `warmup_fallback_reason`, `qdrant_timeouts`, `dense_identity`, `index_settings` (`null` when Qdrant was never reached);
  - per case: `served_strategy`, `fallback_reason`;
  - `unanswerable.served_strategies` (with `score_kind`/distribution `null` when mixed);
  - `latency_ms.by_served_path`, with top-level `p50`/`p95` `null` when there is more than one path;
  - `fusion` when any case was served by hybrid; `lexical_index` whenever the file was opened;
  - `document_count` from `OpenedRetrieval`.
- [ ] `evaluation/cli.py` summary: prints requested and served strategies, fallback counts and latency per path.
- [ ] `evaluation/results.py`, `compare.py`:
  - read 2.2; `info["retrieval_strategy"]` is the served strategy and `info["requested_strategy"]` is added;
  - refuse a mixed file (exit 2, per-strategy counts in the message);
  - embedder pair from `dense_identity` when `index_settings` is `null`;
  - the lexical-object rule applies by served strategy;
  - latency lines labelled for fallback paths;
  - 1.0, 2.0 and 2.1 reading unchanged.
- [ ] Tests:
  - `test_retrieval_eval.py`: 2.2 keys; a no-fallback run equals the 2.1 metrics, ranks and leg ranks on the fixture (`dense_equivalence.py`, `test_strategy_eval.py`); a fully-fallback fixture (single path, top-level set); a mixed fixture (nulls, two paths);
  - `test_compare.py`: mixed file refused; a fallback-only 2.2 file vs a 2.1 BM25 fixture compares under the gate; 2.1 vs 2.2; the committed 1.0 vs 2.0 compare still exits 0; the embedder pair comes from `dense_identity`.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v1-20261028T123109Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v1-20261028T123121Z.json` still runs (exit 0 or 1 by the gate, as before; no refusal).
- A throwaway fake run is refused by `eval-retrieval` as before (fake embedder), unchanged.
- `git status --porcelain -- evaluation knowledge config` is empty.

Review reading order: `retrieval_eval.py` → `evaluation/cli.py` → `results.py` → `compare.py` → tests.

## T6 — Security gate over the fallback paths

**State:** not started
**Requirements:** R10, R13

- [ ] `evaluation/security_eval.py`:
  - paths `dense`, `bm25` (standalone open; freshness against the isolated security repository and chunker; identity against the throwaway collection), `hybrid`, `hybrid_fallback_open` and `hybrid_fallback_query`;
  - `_UnavailableDense` as a harness-only class;
  - sanity checks unchanged.
- [ ] Security result 1.2: `paths` added, `strategies` still written; each violation names its `path`; `access.role` stays `guest`.
- [ ] `evaluation/cli.py` security summary lists the paths.
- [ ] Tests (`test_security_eval.py`):
  - every path is gated;
  - a forbidden hit injected into each path fails the gate and names the path;
  - 1.2 keys;
  - a sanity failure is still a harness error (exit 2);
  - `_UnavailableDense` is not importable from `retrieval/`.
- [ ] `test_security_integration.py` (Docker) covers `hybrid_fallback_query` on Docker Qdrant.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make eval-security` → PASS for all five paths on `public-eval-v2` (result under `experiments/results/tmp/`).
- `make test-integration` passes.

Review reading order: `security_eval.py` → `evaluation/cli.py` → tests.

## T7 — Real runs (user-owned gate)

**State:** not started
**Requirements:** R12

T1–T6 must be approved, committed and pushed on `spec/008` first. The tree, including `graphify-out/`, must be clean before each run. The agent prepares the instructions and checks the files; the user runs every command.

- [ ] **User, Qdrant unreachable:**
  - `make setup-bge-m3`;
  - `QDRANT_COLLECTION_BASE=w2a-realcheck QDRANT_URL=http://127.0.0.1:<closed port> make eval-retrieval`;
  - `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v1-20261028T123109Z.json CANDIDATE=<new file>`.
  - Expected: every case served by `bm25` with `qdrant_unavailable`; PASS with hits 64 → 64, MRR 0.7082 → 0.7082, no flip.
- [ ] **User, Qdrant up:**
  - `QDRANT_COLLECTION_BASE=w2a-realcheck make eval-retrieval`, then `make eval-compare` against `…20261028T123121Z.json`.
  - Expected: no fallback; PASS with hits 68 → 68, MRR 0.9094 → 0.9094, no flip.
- [ ] **User, no extra:**
  - `make setup`, then `QDRANT_COLLECTION_BASE=w2a-realcheck QDRANT_URL=http://127.0.0.1:<closed port> make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--strategy bm25"` returns hits;
  - then `make setup-bge-m3` again if needed.
- [ ] **Agent:**
  - check each result file: `served_strategies`, `fallback_counts`, `requested_strategy`, `dense_identity`, `lexical_index`, `git_commit`, `git_dirty`, `latency_ms.by_served_path`;
  - record the numbers and any deviation in `CURRENT_STATE.md`;
  - the user commits the two result files.

Allowed protected-path changes: none. New files under `experiments/results/` only (committed by the user's approval).

### Verification

- Both `eval-compare` outputs are PASS with the expected numbers, and the scratch field checks above are recorded in the handoff.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T8 — Documentation, decisions and final verification

**State:** not started
**Requirements:** R14, R13, Definition of Done

- [ ] `DECISIONS.md`:
  - D056 Spec 008 ahead of roadmap 7;
  - D057 failure classification (wrapper-only Qdrant unwrapping; model network-cause rule);
  - D058 `FallbackRetriever` policy and worst-case latency (circuit breaker deferred to the HTTP route);
  - D059 Qdrant timeouts and the retrieval client factory;
  - D060 standalone lexical open and repository freshness check (large-corpus caveat);
  - D061 result 2.2, security 1.2, served-strategy comparison and latency by served path;
  - D062 Qdrant HTTP status errors (including 5xx) are not eligible.
- [ ] `ROADMAP.md`: note that retrieval graceful degradation (part of item 13) was done before item 7, and that the reranker and model-failure paths remain in item 13.
- [ ] `ARCHITECTURE.md` ("Retrieval", "Retrieval fallback"), `COMMANDS.md` (fallback behavior, `bm25` needs neither Qdrant nor the extra, `config/retrieval.yaml` 1.1, new refusals, result 2.2, security 1.2), `TECH_STACK.md` and `CURRENT_STATE.md` describe the code as built.
- [ ] `design.md` As-built notes: every deviation found in T1–T7.
- [ ] Spec-wide checks: `make verify`, `make test-integration`, `make eval-security`; the protected-path check over the branch.
- [ ] `graphify update .`.

Allowed protected-path changes: none.

### Verification

- `make verify`, `make test-integration` and `make eval-security` pass; counts recorded in `CURRENT_STATE.md`.
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists only `config/retrieval.yaml`.
- The reviewer reads the docs against the code, D056–D062 are present, and the ROADMAP note is present.

Review reading order: `DECISIONS.md` → `ROADMAP.md` → `ARCHITECTURE.md` → `COMMANDS.md`, `TECH_STACK.md` → `CURRENT_STATE.md` → design As-built notes.

## Notes for the retrospective

- Check that no path catches a broader exception than `RetrievalUnavailableError` for fallback, and that `__context__` is never followed.
- Check that the Hugging Face error-shape As-built note matches the pinned versions.
- Carry to the HTTP route spec: circuit breaker, startup policy for a missing or stale lexical file, 5xx eligibility (D062), the cost of the freshness check on a large corpus.
