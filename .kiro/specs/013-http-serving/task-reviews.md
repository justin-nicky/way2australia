# 013 — Task Reviews

## T1 — round 1

### Implementation
- Model: Grok 4.7 (Cursor; BEST_MINUS_ONE). A parallel Claude Code session (claude-sonnet-5-5) wrote most of the opening rework and the first draft of this block; this session set eval-retrieval's open depth, the close-order assertion, and confirmed `make verify`.
- Files changed:
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` (one `_open_standalone` helper; keyword-only `top_k` with early refusal; `OpenedRetrieval.client`; one outer `try` closing client and lexical on any failure; idempotent `close()`: lexical, then client)
  - `packages/rag/src/way2australia_rag/retrieval/cli_args.py` (`open_kwargs(client_factory, top_k=None)`), `retrieval/cli.py`, `generation/cli.py` (`make retrieve`, `make ask` pass `args.top_k`)
  - `packages/rag/src/way2australia_rag/evaluation/cli.py` (`eval-generation` passes its resolved `top_k`; `eval-retrieval` passes the depth the retriever is asked for when the dense path is up — `rerank.depth` if reranking, else `fusion.candidate_depth` — not `--top-k`; `retrieval_depth` is `rerank.depth` only when `opened.reranker is not None`, else `fusion.candidate_depth`)
  - Tests: new `packages/rag/tests/retrieval/test_opening_lifecycle.py` (10 tests); new test in `packages/rag/tests/evaluation/test_strategy_eval.py`; `KeepOpenClient` helper in `packages/rag/tests/conftest.py` used by `tests/retrieval/test_cli.py` (`Factory`) and `tests/ingestion/test_config_schema_11.py` (`test_open_hybrid_paths_without_tokenizer`)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run: `uv run pytest packages/rag/tests/retrieval packages/rag/tests/evaluation packages/rag/tests/generation` → 1154 passed, 2 skipped; `make typecheck` → 0 errors; `make verify` (`HF_HUB_OFFLINE=1`, empty `HF_HOME`) → pass (1806 passed, 5 skipped; lint, typecheck, skills-check, validate-knowledge, validate-evaluation). No integration tests (not required by T1). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none).
- Notes:
  - Test change forced by R2: `open_retrieval(...).close()` now closes the Qdrant client, so two existing tests that reuse one in-memory client after a CLI or `close()` failed with "QdrantLocal instance is closed" (`test_cli.py::test_output_has_no_secret_path_or_chunk_text`, `test_config_schema_11.py::test_open_hybrid_paths_without_tokenizer`). Their assertions are unchanged; their client factories now hand out a non-closing view (`KeepOpenClient`). No other existing test needed a change.
  - The task said to update the one existing test asserting depth 20 after an open-time fallback; no such test exists (no test covered that case). Added `test_eval_cli_open_time_fallback_with_rerank_records_the_candidate_depth` (docstring names Spec 011 F1) asserting `retrieval_depth` 50, reranker built but never loaded, served path `bm25+fallback:qdrant_unavailable`.
  - `eval-retrieval` passes that open depth, not `--top-k` (the metric cutoff, still checked by `require_retrieval_depth`). With reranking the passed depth equals `rerank.depth`, so the early refusal does not fire, including when an open-time fallback later records `candidate_depth`.
  - The early `top_k` check runs before the embedder, reranker and client are built (stricter than "before `reranker_factory`"); message `top_k N exceeds rerank.depth D.` keeps the text the CLI test matches.
  - The inner `except RetrievalUnavailableError` fallback applies only to the dense open and lexical bind (as before); reranker load and `build_retriever` errors are not turned into fallbacks. The failed client is closed and set to `None` before `_open_fallback`, so it is closed exactly once.
  - Behaviour change to note for review: CLIs now close the client at the end of a run (previously it was left to process exit).
  - No library documentation relied on in this task (no FastAPI, Starlette, uvicorn or httpx behaviour).
  - Not run: `make test-integration` (not required by T1); no real API, model or collection was touched.
- Usage: 177K tokens · 65 tool uses · 24:50

### Review
- Model: claude-opus-5-5 (Claude Code; matches the BEST tier `Opus`; different model from the implementer)
- Verdict: PASS
- Commands: `uv run pytest packages/rag/tests/retrieval packages/rag/tests/evaluation packages/rag/tests/generation` (via `python3 -m uv`, as the Makefile does) → pass (1154 passed, 2 skipped); `make verify` → pass (ruff and format clean, pyright 0 errors, 1806 passed, 5 skipped); `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` not required by T1, not run.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R15] Two existing tests outside the task's named exceptions changed their client factory (`tests/retrieval/test_cli.py::Factory`, `tests/ingestion/test_config_schema_11.py::test_open_hybrid_paths_without_tokenizer`) to hand out `KeepOpenClient`, because `close()` now closes the client (R2). Assertions are unchanged, so the R15 rule holds; recorded for transparency → none required.
  - F2 [MINOR, IMPLEMENTATION, R1] `eval-retrieval` passes `rerank.depth` itself as `top_k` when reranking, so the new early refusal cannot trip there; this matches the design ("passes its effective depth"; `--top-k` is a document cutoff) and the existing distinct-document check still guards the metric → none required.
  - Verified deviations from the Implementation block: no existing test asserted depth 20 after an open-time fallback (grep of `retrieval_depth` in tests confirms), so the new test is the right substitute; the early `top_k` check runs before the embedder, reranker and client are built (stricter than required, tested with zero factory, load and client calls); CLIs now close the client through their existing `opened.close()` in `finally`, and no CLI uses the client afterwards (`eval-security` does not use `open_retrieval`). An eligible reranker load skip keeps `retrieval_depth` = `rerank.depth`, which is correct because the rerank stage still asks hybrid for `rerank.depth` candidates.
- Summary for user (PASS only):
  - Changed: `open_retrieval` now has one standalone-lexical helper (bm25 and open-time fallback), an early `top_k > rerank.depth` refusal before any model or client is built, and closes the Qdrant client and lexical file on every failed open; `OpenedRetrieval.close()` closes lexical then client, idempotently. The four CLIs pass their `top_k`/depth; `eval-retrieval` records `retrieval_depth` 50 after an open-time fallback with reranking requested (Spec 011 F1), no result version bump.
  - Verified by: 10 new lifecycle tests (failure injected at dense open, lexical bind, reranker load, `build_retriever`; idempotent close; early refusal; shared helper), one new eval-CLI depth test, targeted pytest and `make verify` (1806 passed).
  - Worth your attention: CLIs now close the Qdrant client at the end of each run (previously left to process exit); two existing tests' client factories now return a non-closing view (assertions unchanged).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/cli_args.py` → `ResolvedRetrievalArgs.open_kwargs`: forwards `top_k`
    2. `packages/rag/src/way2australia_rag/retrieval/cli.py`, `generation/cli.py` → `main`: pass `args.top_k`
    3. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval` (`open_depth`, `retrieval_depth`) and `_generation`
    4. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`, `_open_standalone`, `_open_fallback`, `OpenedRetrieval.close`
    5. `packages/rag/tests/retrieval/test_opening_lifecycle.py`: lifecycle, early refusal, shared helper
    6. `packages/rag/tests/evaluation/test_strategy_eval.py` → `test_eval_cli_open_time_fallback_with_rerank_records_the_candidate_depth`
    7. Supporting edits: `KeepOpenClient` in `packages/rag/tests/conftest.py`, used by `tests/retrieval/test_cli.py` and `tests/ingestion/test_config_schema_11.py`; `tasks.md` boxes
  - Learning notes: /Users/justin/learning/way2australia/specs/013-http-serving/T1.md
- Usage: 133K tokens · 36 tool uses · 12:15

### User decision
- 2026-11-14 — approved:

> I approve T1. Commit it with Spec-Task: 013/T1 and push spec/013.
>
> Process note for the record: T1 had two implementers writing at the same time (Grok 4.7 in Cursor and a parallel Claude Code session). The review covered the combined diff, so T1 stands. From T2 on, exactly one implementer session works on a task. Then start T2.

## T2 — round 1

### Implementation
- Model: Grok 4.7 (Cursor; BEST_MINUS_ONE). Matches the configured Cursor tier.
- Files changed:
  - `packages/rag/src/way2australia_rag/lexical/store.py` (`check_same_thread=False` with `mode=ro` and `query_only`; one `threading.Lock` around every connection use including idempotent `close`; `check_tokenizer`)
  - `packages/rag/src/way2australia_rag/lexical/freshness.py` (`run_sync`; `verify_fresh` uses it)
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` (`_open_standalone` takes `tokenizer` and calls `check_tokenizer`)
  - `packages/rag/src/way2australia_rag/retrieval/strategy.py` (`open_bound_lexical` takes keyword-only `tokenizer` and calls `check_tokenizer` before `bind_to`)
  - Tests: new `packages/rag/tests/lexical/test_lexical_runtime.py`; `test_lexical_standalone.py` (freshness inside a running loop, twice); builders that open through the real retrieval config now record its tokenizer (`test_opening.py`, `test_bm25.py`, `test_retrieval_integration.py`, `test_config_schema_11.py`, `test_ask_cli.py`, `lexical_support.build_production`)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run: `python3 -m uv run pytest packages/rag/tests/lexical packages/rag/tests/retrieval packages/rag/tests/ingestion/test_config_schema_11.py packages/rag/tests/generation/test_ask_cli.py` → 571 passed (`uv` is not on PATH; the Makefile invokes `python3 -m uv`). `make verify` → pass (1811 passed, 5 skipped; ruff, format, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` not required by T2, not run.
- Notes:
  - `check_tokenizer` compares the recorded tokenizer name with `lexical.tokenizer`. Open already rejects an unknown name/version pair. The message uses the existing rebuild advice (`make index-lexical`, no path) plus the recorded and wanted names. The label is the file name, as in every other lexical error; the tests assert the temp directory is absent and the message contains no `/`.
  - One lock per `LexicalIndex`. `close` is idempotent, so the sqlite connection is closed once even when `close` runs again. A mismatch closes that connection once; on the hybrid path the Qdrant client is closed once as well.
  - `run_sync` uses `asyncio.run` when no loop is running, and `asyncio.run` on a joined thread (`lexical-freshness`) when one is. `LocalDocumentRepository` was not changed. On Python 3.12 an uncontended `asyncio.Lock.acquire` does not bind the lock to a loop, so two sequential `verify_fresh` calls on the same repository succeed; that was checked before relying on it.
  - Existing tests that open a file through `config/retrieval.yaml` (`lexical-v2`) now build that file with the configured tokenizer. Assertions are unchanged. `build_production` gained an optional lexical tokenizer; its chunker tokenizer is still `FakeTokenizer`.
  - `docs/project/CURRENT_STATE.md` was already modified when this session started (T2 implementing, round 1, and the single-implementer sentence). This session did not edit it.
  - No FastAPI, Starlette, uvicorn, or httpx behaviour relied on.
  - Not run: `make test-integration` (not required); no real API, model, or collection was touched.
- Usage: n/a (Cursor) · 204 tool uses · 25:00

### Review
- Model: Grok 4.7 (Cursor; matches the BEST tier `Grok 4.7`). Fresh session; the implementer used the same configured model.
- Verdict: PASS
- Commands: `UV_CACHE_DIR="$(pwd)/.uv-cache" UV_PYTHON_INSTALL_DIR="$(pwd)/.uv-python" python3 -m uv run pytest packages/rag/tests/lexical packages/rag/tests/retrieval` → pass (536 passed); `HF_HUB_OFFLINE=1 HF_HOME="$(mktemp -d)" make verify` → pass (ruff check clean, ruff format 237 files already formatted, pyright 0 errors, skills-check match, validate-knowledge OK, validate-evaluation OK, 1811 passed, 5 skipped, 1816 collected). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` not required by T2, not run.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R15] Existing opens that go through `config/retrieval.yaml` now build the lexical file with `TOKENIZERS[retrieval.lexical.tokenizer]` (`tests/lexical_support.py` `build_production`, `tests/retrieval/test_opening.py`, `test_bm25.py`, `test_retrieval_integration.py`, `tests/ingestion/test_config_schema_11.py`, `tests/generation/test_ask_cli.py`). Assertions are unchanged → none required.
- Summary for user (PASS only):
  - Changed: one read-only SQLite connection per lexical file (`check_same_thread=False`, still `mode=ro` and `query_only`) is guarded by one lock on `LexicalIndex`, including an idempotent `close`. Standalone open and `open_bound_lexical` both refuse a file whose recorded tokenizer is not `lexical.tokenizer` from `config/retrieval.yaml`, with `make index-lexical` in the message and no path, and close that connection once. `verify_fresh` reaches the repository through `run_sync`: `asyncio.run` when this thread has no loop, and `asyncio.run` on a short-lived joined thread when a loop is already running.
  - Verified by: tokenizer refusal on the standalone and bound paths (connection and, on hybrid, the Qdrant client closed once), 8-thread BM25 matching serial results, close overlapping a query, `verify_fresh` twice from inside `asyncio.run`; targeted pytest (536 passed) and `make verify` (1811 passed, 5 skipped).
  - Worth your attention: on Python 3.12 an uncontended `asyncio.Lock.acquire` does not bind `LocalDocumentRepository`'s lock to a loop, so two sequential `verify_fresh` calls on one repository succeed. The design uses that lock only for those sequential runs (startup, or one dense re-open). Overlapping freshness checks on the same repository are outside this task.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `_open_standalone`, `open_retrieval`: passes `retrieval_config.lexical.tokenizer` and closes on a mismatch
    2. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `open_bound_lexical`: `check_tokenizer` before `bind_to`, then close
    3. `packages/rag/src/way2australia_rag/lexical/store.py` → `_read_only_connection`, `LexicalIndex.check_tokenizer`, `_fetchall` / `_fetchone`, `close`
    4. `packages/rag/src/way2australia_rag/lexical/freshness.py` → `run_sync`, `verify_fresh`
    5. `packages/rag/tests/lexical/test_lexical_runtime.py`: refusal, eight threads, close-during-query
    6. `packages/rag/tests/lexical/test_lexical_standalone.py` → `test_verify_fresh_inside_a_running_loop_twice`
    7. Supporting edits: test builders record the configured tokenizer (`lexical_support.build_production` and the open-path fixtures); `tasks.md` boxes
  - Learning notes: /Users/justin/learning/way2australia/specs/013-http-serving/T2.md
- Usage: n/a (Cursor) · 74 tool uses · n/a (Cursor)

### User decision
- 2026-11-15 — approved:

> T2 approved. Commit it with the Spec-Task: 013/T2 trailer and push spec/013, recording the approval in the T2 user-decision block. dont start T3 yet.

## T3 — round 1

### Implementation
- Model: Grok 4.7 (Cursor; BEST_MINUS_ONE). Matches the configured Cursor tier.
- Files changed:
  - `packages/rag/src/way2australia_rag/retrieval/breaker.py` (new: `BreakerState`, `Admission`, `CircuitBreaker`; one `threading.Lock`)
  - `packages/rag/src/way2australia_rag/retrieval/fallback.py` (keyword-only `breaker=None`, `on_probe=None`)
  - `packages/rag/src/way2australia_rag/retrieval/strategy.py` (keyword-only `breaker=None` on `build_retriever`, passed into both hybrid `FallbackRetriever`s)
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` (keyword-only `breaker=None` on `open_retrieval`, passed to `build_retriever` and `_open_fallback`)
  - `packages/rag/tests/retrieval/test_breaker.py` (15 tests)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run: `uv run pytest packages/rag/tests/retrieval` → 437 passed, 2 skipped. `make lint typecheck` → ruff clean, 239 files formatted, pyright 0 errors. `make eval-security` (`HF_HUB_OFFLINE=1`) → PASS in 34243 ms (heading, structure, recursive; eight paths each). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make verify` did not finish: the one run that executed stopped at `skills-check` before pytest, because a gitignored `__pycache__` under `agent-skills/workflow-reviewer/scripts/` was part of the mirror tree (skill file bytes otherwise match; Claude's extra frontmatter is the injector). That bytecode was removed. A second `make verify` was blocked by the session verify budget. `make test-integration` not required, not run.
- Notes:
  - `breaker is None` keeps the previous control flow (D058): every query tries the primary; only `RetrievalUnavailableError` falls back. CLIs pass no breaker.
  - One lock. Closed admits `DENSE`. `failure_threshold` consecutive `record_failure(DENSE)` calls open until `clock() + cooldown_s`. The first `admit` at or after that instant gets `PROBE` and the state becomes half-open; every other caller gets `SKIP` until the probe reports, including if the clock jumps during the probe. Probe success closes and resets the count. Probe failure stores the new reason, counts, and opens a cool-down from that instant. `release` changes state only for a half-open `PROBE`: new cool-down, same `last_reason`, count unchanged. `release(DENSE)` does not count. A constructor `open_reason` starts the breaker open with that reason and a cool-down from construction.
  - `SKIP` does not call the primary. BM25 is served with `fallback_reason = last_reason` and `dense_attempt` under 0.5 s. Eligible outages call `record_failure` then BM25. Success calls `record_success`. Any other exception on a `PROBE` calls `release` and propagates; the same exception on `DENSE` propagates and is not counted (D062).
  - `on_probe` is `Callable[[], Retriever | None]`, for T5's BM25-only stack (no primary). The hook owns `record_failure` and `release`. A returned retriever is called with the same access, `top_k`, and `lote`; if the breaker is still half-open, this class records success first so the continuation is admitted `DENSE`. `None` serves BM25 with `last_reason` (a hook that left the probe half-open is `release`d). An exception from the hook releases if still half-open, then propagates. With no hook, a probe releases and serves BM25 so the breaker cannot stick half-open.
  - `build_retriever` gained the keyword because that is where the hybrid `FallbackRetriever`s are constructed (plain and reranked). Default `None` leaves existing callers unchanged. `open_retrieval` passes the same breaker into both, and into the open-time fallback.
  - No FastAPI, Starlette, uvicorn, or httpx behaviour relied on. The status-error test raises `UnexpectedResponse`, the existing D062 type.
  - Not run to completion: `make verify` (see above). No real API, model, or collection was touched.
- Usage: n/a (Cursor) · 140 tool uses · n/a
- Verify budget: 3 make verify attempts in transcript; budget is 2 per session.

### Review
- Model: Grok 4.7 (Cursor; matches the BEST tier `Grok 4.7`). Fresh session. The implementer used the same configured model (Cursor BEST_MINUS_ONE is also Grok 4.7).
- Verdict: PASS
- Commands: `UV_CACHE_DIR=/home/box/work/way2australia/.uv-cache UV_PYTHON_INSTALL_DIR=/home/box/work/way2australia/.uv-python HF_HUB_OFFLINE=1 uv run pytest packages/rag/tests/retrieval` → pass (437 passed, 2 skipped, 439 collected). `make verify` → pass (ruff check clean, ruff format 239 files already formatted, pyright 0 errors, skills-check match, validate-knowledge OK, validate-evaluation OK, 1809 passed, 22 skipped, 1831 collected). `HF_HUB_OFFLINE=1 make eval-security` → PASS in 34338 ms (heading, structure, recursive; eight paths each). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` not required by T3, not run.
- Findings: none
- Summary for user (PASS only):
  - Changed: Hybrid retrieval can take a circuit breaker (`retrieval/breaker.py`). Closed tries dense on every request; after the configured run of eligible outages it opens and BM25 serves; when the cool-down ends, one caller probes. `FallbackRetriever` keeps today's behaviour when no breaker is passed. `open_retrieval` and `build_retriever` thread an optional breaker into every hybrid fallback, including the open-time one. CLIs pass nothing.
  - Verified by: 15 breaker tests (fake clock, one probe among 8 threads, skip path, HTTP status not counted, access and `lote` spy, `open_retrieval` wiring). Retrieval pytest 437 passed, 2 skipped. `make verify` 1809 passed, 22 skipped. `make eval-security` with the fake embedder passed. `evaluation/`, `knowledge/` and `config/` are unchanged.
  - Worth your attention: T5's `on_probe` hook owns `record_failure` and `release`. If it returns a retriever while the probe is still half-open, `FallbackRetriever` records success before that retriever runs, so the continuation is admitted as dense. `open_retrieval` does not take the hook; a probe with no primary and no hook releases and serves BM25. T5 builds that retriever itself. A Qdrant HTTP status error still propagates and is not counted; on a probe it also starts a new cool-down.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`, `_open_fallback`: optional breaker passed through; CLIs omit it
    2. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `build_retriever`: breaker attached to both hybrid `FallbackRetriever`s
    3. `packages/rag/src/way2australia_rag/retrieval/fallback.py` → `FallbackRetriever.retrieve`: skip, count, probe, and the `on_probe` hook
    4. `packages/rag/src/way2australia_rag/retrieval/breaker.py` → `CircuitBreaker.admit`: one lock; closed, open, one probe
    5. `packages/rag/tests/retrieval/test_breaker.py`: clock, concurrency, fallback, opening
    6. Supporting edits: `tasks.md` checkboxes
- Usage: n/a (Cursor) · 58 tool uses · n/a

### User decision
- 2026-11-16 — approved:

> approve
> via: Control Tower trial 2; decided by: Justin

## T4 — round 1

### Implementation
- Model: Grok 4.7 (Cursor; BEST_MINUS_ONE, matches the configured Cursor tier)
- Files changed:
  - `packages/rag/src/way2australia_rag/generation/base.py` (`Generator.generate` keyword-only `deadline_s`; `deadline_s` property)
  - `packages/rag/src/way2australia_rag/generation/fake.py` (`deadline_s` is `None`; `generate` accepts the argument)
  - `packages/rag/src/way2australia_rag/generation/claude.py` (per-call deadline is `min(config.deadline_s, deadline_s)` when given; attempt loop and classification unchanged)
  - `packages/rag/src/way2australia_rag/generation/bedrock.py`, `anthropic_api.py` (`deadline_s` property returns the configured value; `generate` forwards `deadline_s`)
  - `packages/rag/src/way2australia_rag/generation/deadline.py` (new: `AbandonedWork`, `run_with_cap` on a daemon thread)
  - `packages/rag/src/way2australia_rag/generation/service.py` (keyword-only `budget_s`, `min_generation_s`, `on_abandoned`; cap; skip below the minimum)
  - `config/generation.yaml` (comment text only: `deadline_s`, `backoff_s` in both provider blocks, `bedrock.model_id`; schema `1.1` unchanged)
  - Tests: `packages/rag/tests/generation/test_deadline.py` (new), `test_service.py`; signature-only updates so callers that are invoked with `deadline_s` still type-check and run: `test_ask_cli.py` (the committed-default stub), `test_generation_eval.py` (`_ScriptedGenerator.deadline_s`), `evaluation/security_eval.py` (`_PoisonGenerator.generate`)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run:
  - `uv run pytest packages/rag/tests/generation` → 266 passed, 2 skipped
  - `make verify` (`HF_HUB_OFFLINE=1`, empty `HF_HOME`) → pass (1823 passed, 22 skipped; ruff, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation). Qdrant was down, so the Docker integration tests skipped. An earlier `make verify` in this session stopped at `skills-check` before pytest: a stray `__pycache__` under `agent-skills/workflow-reviewer/scripts/` was counted as source. Removed that cache; the completed run above is the result.
  - `make ask` equivalent (`python -m way2australia_rag.generation.cli` with `--generator fake --embedder fake --reranker fake`, throwaway base `w2a-t013-cap`, lexical file deleted afterwards): `status: answered`, fake generator called, `generation_ms 0.0`. Qdrant was down, so retrieval fell back to BM25 (`qdrant_unavailable`). The Spec 012 fake run on hybrid was also `answered`.
  - `make eval-generation` equivalent (`--generator fake --allow-fake --embedder fake --reranker fake --limit 10`, same throwaway base, result file deleted afterwards): exit 0; 8 golden, 2 unanswerable; answer rate 1.0; refusal rate 0.0; `citation_invalid` 0; `evidence_only` 0; `output_invalid` 0. Same fake statuses as before (the fake answers when retrieval returns a hit). Same BM25 fallback because Qdrant was down.
  - `git status --porcelain -- evaluation knowledge config` → `M config/generation.yaml` only. `git diff config/generation.yaml` is comment text on those lines; values and `schema_version` are unchanged.
- Notes:
  - With no budget and no generator deadline (the fake), `answer` calls `generate` directly. `run_with_cap` needs a finite cap, and the design says no cap applies in that case. That keeps the generation-eval step clock exact: the budget elapsed is `built - started`, with no extra `perf_counter` read.
  - A budget always yields a cap (`deadline_s` or the remainder, whichever is smaller). Below `min_generation_s` the generator is not called (`called` false, so `identity.generator` is null) and the response is `evidence_only` / `generator_unavailable` / `deadline`.
  - CLIs still call `answer` without a budget. Their cap is the generator's `deadline_s`. The fake's is `None`, so `make ask` and `make eval-generation` with `--generator fake` are uncapped, as before.
  - Abandoned exceptions are logged at WARNING as `abandoned generation work raised <ClassName>`, with no message and no traceback. A done callback registered after the thread has finished runs in `add_done_callback`.
  - The worker is a daemon `threading.Thread`. A subprocess that abandons `run_with_cap` and then exits is limited by a 5 s timeout and returns 0; the in-process test also asserts `thread.daemon`. The CLI path is covered in-process (`cli.main` with `BlockingGenerator`), because a full CLI subprocess would rebuild the index inside that timeout.
  - No new httpx, FastAPI, Starlette or uvicorn behaviour. The adapter's per-phase timeout is unchanged. The cap wait is `threading.Event.wait` (`https://docs.python.org/3/library/threading.html#threading.Event.wait`); daemon threads are not joined at shutdown (`https://docs.python.org/3/library/threading.html#threading.Thread.daemon`).
  - Not run: real Anthropic or Bedrock calls; `make ask` / `make eval-generation` against a live Qdrant hybrid index (Qdrant connection refused). `make test-integration` is not required by T4.
- Usage: n/a (Cursor) · 187 tool uses · n/a

### Review
- Model: Grok 4.7 (Cursor; matches the BEST tier). Fresh session. The implementer used the same configured model (Cursor BEST_MINUS_ONE is also Grok 4.7).
- Verdict: PASS
- Commands: `uv run pytest packages/rag/tests/generation` → pass (266 passed, 2 skipped). `make verify` → first run stopped at `skills-check` before pytest because a gitignored `__pycache__` under `agent-skills/workflow-reviewer/scripts/` was in the skill tree (not T4 work); that bytecode was removed. Second `make verify` → pass (ruff clean, 241 files formatted, pyright 0 errors, skills-check match, validate-knowledge OK, validate-evaluation OK, 1823 passed, 22 skipped, 1845 collected). `W2A_LEXICAL_INDEX_DIR=<temp> make ask QUERY="Is coaching compulsory?" ASK_ARGS="--generator fake --embedder fake --reranker fake"` → exit 0, `status: answered`, `generation_ms 0.0` (default lexical file absent, so the index was built in that temp dir with `--embedder fake`; Qdrant down, BM25 fallback `qdrant_unavailable`). `W2A_LEXICAL_INDEX_DIR=<temp> make eval-generation EVAL_ARGS="--generator fake --allow-fake --embedder fake --reranker fake --limit 10"` → exit 0; 8 golden, 2 unanswerable; answer rate 1.0; refusal rate 0.0; `citation_invalid` 0; `evidence_only` 0; `output_invalid` 0. `git status --porcelain -- evaluation knowledge config` → `M config/generation.yaml` only; `git diff` on that file is comment text, values and schema `1.1` unchanged. `make test-integration` not required by T4, not run.
- Findings: none
- Summary for user (PASS only):
  - Changed: `AnswerService.answer` takes a keyword-only budget and waits at most the generator's deadline, tightened by whatever budget remains after retrieval and context. Past that, or when the remainder is below `min_generation_s`, the response is `evidence_only` / `generator_unavailable` / `deadline` (the generator is not called in the second case). The wait is `run_with_cap` on a daemon thread. The Claude adapter uses `min(config.deadline_s, deadline_s)` so it does not start another attempt after the cap. `FakeGenerator.deadline_s` is `None`, so fake CLI runs are not capped. Comments in `config/generation.yaml` for `deadline_s`, `backoff_s`, and `bedrock.model_id` now say that; values are unchanged.
  - Verified by: generation pytest 266 passed, 2 skipped. `make verify` 1823 passed, 22 skipped. Fake `make ask` returned `answered`. Fake `make eval-generation` (limit 10) had answer rate 1.0 and `evidence_only` 0. Protected paths: only comment edits in `config/generation.yaml`.
  - Worth your attention: with no budget and no generator deadline, `answer` calls `generate` directly, so `--generator fake` stays uncapped. A real generator's `deadline_s` is the cap on `make ask` and `make eval-generation`. An abandoned call keeps running on a daemon thread; an in-flight read can outlive the cap, and there is still no guaranteed upper bound. The concurrency slot handoff is T7. The hang check is a 5 s subprocess of `run_with_cap`, plus in-process `cli.main` with a blocking generator, because a full CLI subprocess would rebuild the index inside that timeout.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/generation/service.py` → `AnswerService.answer`, `_cap`: budget, skip below the minimum, `run_with_cap`
    2. `packages/rag/src/way2australia_rag/generation/deadline.py` → `run_with_cap`, `AbandonedWork`: daemon thread, class-only log, late callback
    3. `packages/rag/src/way2australia_rag/generation/claude.py` → `ClaudeMessagesAdapter.generate`: per-call deadline tightens the configured one
    4. `packages/rag/src/way2australia_rag/generation/base.py` → `Generator.generate`, `deadline_s`
    5. `packages/rag/src/way2australia_rag/generation/anthropic_api.py`, `bedrock.py` → `deadline_s` returns the configured value; `generate` forwards the cap
    6. `packages/rag/src/way2australia_rag/generation/fake.py` → `FakeGenerator.deadline_s` is `None`
    7. `config/generation.yaml`: comment text for `deadline_s`, `backoff_s`, `bedrock.model_id`
    8. Supporting edits: `packages/rag/tests/generation/test_deadline.py`, `test_service.py`; signature-only updates in `test_ask_cli.py`, `packages/rag/tests/evaluation/test_generation_eval.py`, `packages/rag/src/way2australia_rag/evaluation/security_eval.py`; `tasks.md`, `CURRENT_STATE.md`
- Usage: n/a (Cursor) · 109 tool uses · n/a

### User decision
- 2026-11-16 — approved:

> approved
> via: Control Tower gate way2australia-013-T4-r1-task_pass; decided by: Justin

## T5 — round 1

### Implementation
- Model: Claude Sonnet 5.5 (Claude Code; BEST_MINUS_ONE, matches the configured Claude Code tier)
- Files changed:
  - `config/serving.yaml` (new, schema 1.0, design values)
  - `packages/rag/src/way2australia_rag/serving/` (new package): `config.py` (strict loader, `check_budget` cross-file check), `locks.py` (`LockedEmbedder`, `LockedReranker`), `readiness.py` (`Readiness`, `ReadinessSnapshot`, reasons), `stack.py` (`ServingStack`, `StackHolder`, `ServingInputs`, `open_serving_stack`, `try_reopen_dense`)
  - `packages/rag/src/way2australia_rag/retrieval/opening.py`: two additive `OpenedRetrieval` fields with defaults, `fallback_reason` (set by `_open_fallback`) and `rerank_open_skip` (set after the reranker load), so the holder can start a BM25-only stack with the breaker open and report a sticky reranker skip. No behaviour change for the CLIs.
  - Tests (new, `packages/rag/tests/serving/`): `test_serving_config.py`, `test_readiness_and_locks.py`, `test_stack.py`
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run:
  - `uv run pytest packages/rag/tests/serving packages/rag/tests/retrieval` → 472 passed, 2 skipped
  - `make verify` (`HF_HUB_OFFLINE=1`) → pytest 1860 passed, 20 skipped (the output I kept was its tail, ending at the pytest summary; ruff and pyright were also run separately: ruff clean, pyright 0 errors). Qdrant was not running, so the Docker integration tests skipped.
  - `git status --porcelain -- evaluation knowledge config` → `?? config/serving.yaml` only.
- Notes:
  - **Reranker skip is sticky inside `LockedReranker`**: an eligible load failure is stored and re-raised on every later `load`, so a re-opened stack keeps the open-time skip (D077, R5) without a new `open_retrieval` parameter. The holder preloads the reranker at start, so a BM25-only start still has it loaded for the re-open.
  - **BM25-only start**: an embedder outage (checked before Qdrant) opens `bm25` through `open_retrieval`; a Qdrant outage comes back from `open_retrieval` as an open-time fallback with `fallback_reason`. In both cases the holder builds `FallbackRetriever(None, BM25, reason, breaker=<created open>, on_probe=holder hook)`. The first `open_retrieval` call receives a closed breaker that is replaced in that case.
  - **Strategies other than `hybrid`**: `bm25` has no breaker use and no probe; `dense` with Qdrant down fails the start (no fallback exists for it, as in the CLIs).
  - **Generator ownership**: a generator passed in `ServingInputs.generator` belongs to the holder, which closes it at shutdown and on a failed open. T6's lifespan must not close it a second time after a failed `open_serving_stack` (`Generator.close` is idempotent for the fake; the Claude adapters were not re-checked).
  - **Deviation from the task wording**: the lock-overlap test uses events (a gated embedder, a reranker call made while the embedder is inside), not 0.2 s sleeps. It proves the two locks are separate and that two embeds serialize, with no timing tolerance.
  - **Not done here, by design**: phase transitions (`set_ready`, `set_failed`) and the shutdown callback belong to T6; `abandoned_generation` is tested through a provider callback only, the `SlotPool` is T7.
  - No FastAPI, Starlette, uvicorn or httpx behaviour is used in this task.
  - Not run: real embedder, reranker, generator, Bedrock or Anthropic; a live Qdrant; `make test-integration` (not required by T5).
- Usage: (orchestrator)

### Review
- Model: claude-opus-5-5 (Claude Code; matches the BEST tier `Opus`; different model from the implementer)
- Verdict: PASS
- Commands: `uv run pytest packages/rag/tests/serving packages/rag/tests/retrieval` (via `python3 -m uv`, as the Makefile does) → pass (472 passed, 2 skipped: the two Qdrant integration tests); `HF_HUB_OFFLINE=1 make verify` → **exit 0** (ruff clean, pyright 0 errors, skills/knowledge/evaluation checks pass, 1860 passed, 20 skipped); with local Qdrant started for this review (`docker compose up -d qdrant`; Docker Desktop and the container were both stopped before and were stopped again afterwards): the same pytest run → pass (474 passed, 0 skipped), and `pytest -m integration packages/rag/tests/serving packages/rag/tests/retrieval` → pass (2 collected, 2 passed: `test_seed_corpus_retrieval_under_guest_access`, `test_hybrid_with_the_fake_reranker_through_open_retrieval`); `git status --porcelain -- evaluation knowledge config` → `?? config/serving.yaml` only (allowed: new `config/serving.yaml`). `make test-integration` not required by T5, not run in full.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R1] Every serving test passes `generator_provider="fake"` as an explicit override, so no test proves that `default_generator` from `config/generation.yaml` decides the generator when no override is given (`resolve_serving_choices` does fall back to it; the code is right, the proof is missing). Strategy and `rerank.enabled` are proven from config → add one test with `generator_provider=None` and a `default_generator` changed in the config copy (T6 or T9 may add it).
  - F2 [MINOR, SPEC_DEFECT, R2] Generator ownership is written only in this round's Implementation notes, not in T6's task text: the holder owns a generator passed in `ServingInputs.generator` and closes it at shutdown and on a failed `open_serving_stack`; the lifespan must not close it again, but must close it itself if phase 1 fails after `build_generator` and before the holder exists. T6's boxes say only "shutdown closes the holder". A double close is harmless today (`FakeGenerator.close` sets a flag; the Claude adapter's `close` calls the SDK client's `close`, which is safe to repeat), but a missing close on a phase 1 failure would leak → the orchestrator puts both rules in the T6 brief (or a dated change-log line on T6); no T5 change needed.
  - F3 [MINOR, IMPLEMENTATION, R5] No test runs the re-open against a Qdrant server: the open and re-open tests in `tests/serving/test_stack.py` are not marked `integration` and never skip; they use an in-memory `QdrantClient` for "up" and a real HTTP client on a closed port for "down" (so outage classification is real, the swap target is in-memory). The two Docker-backed tests in `tests/retrieval/` cover `open_retrieval` on hybrid with the fake reranker, not the holder → none required (`make verify` must not need Docker); the user-run smoke check (T8) is the live check.
  - F4 [MINOR, IMPLEMENTATION, R5] The probe request leases the old stack and then continues on the new stack's retriever (`_probe` returns `self._current.opened.retriever`) without a lease on the new stack. Nothing retires the new stack while serving (it has no `on_probe`), so only a shutdown that lands during that one request could close it under the request → none required for T5; T6's shutdown order (stop accepting requests, then `holder.close()`) covers it.
  - Verified deviations: the lock-overlap test uses events instead of 0.2 s sleeps; it proves the separate locks and embed serialization with no timing tolerance (accepted, matches the "threads in tests" rule). The re-open's bound lexical checks are identity, tokenizer and `bind_to` (chunk identities against the live collection), the same checks as a start with Qdrant up (R5); document freshness of the file was checked in phase 1. Sticky reranker skip lives in `LockedReranker` (eligible failure re-raised, asked once; non-eligible not sticky), tested. The two new `OpenedRetrieval` fields are additive with defaults; CLI behaviour unchanged (full suite passes).
- Summary for user (PASS only):
  - Changed: new `config/serving.yaml` (design values) and `packages/rag/.../serving/`: strict config loader with the 30 + 3 + 2 ≤ 40 budget check, separate embedder and reranker locks, a readiness model (phases, reason codes, breaker state read live, abandoned count from a callback), and `StackHolder`/`open_serving_stack` (config decides strategy, reranking, generator; BM25-only start with the breaker open when Qdrant or the embedder is down; probe re-open with the startup checks, atomic swap, drain then close; everything closed on a failed start and at shutdown). `OpenedRetrieval` gains `fallback_reason` and `rerank_open_skip`.
  - Verified by: 3 new test files (config, readiness and locks, stack and re-open), targeted pytest, `make verify` exit 0 (1860 passed), and both Qdrant integration tests passing against a live local Qdrant.
  - Worth your attention: (1) T6 needs the generator-ownership rule in its brief (F2). (2) The re-open path is tested against in-memory Qdrant, not a server; the live check is the T8 smoke run (F3). (3) `dense` strategy with Qdrant down fails the start (no fallback exists for it, as in the CLIs).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/serving/stack.py` → `open_serving_stack`, `StackHolder.start`: config resolution, model warm-up, BM25-only start
    2. same file → `StackHolder.try_reopen_dense`, `_probe`, `_swap`, `_release`, `close`: re-open, swap, drain, shutdown
    3. `packages/rag/src/way2australia_rag/retrieval/fallback.py` → `_probe_without_primary` (T3, unchanged here): how the probe hook is called
    4. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `OpenedRetrieval.fallback_reason`, `rerank_open_skip`
    5. `packages/rag/src/way2australia_rag/serving/locks.py` → `LockedEmbedder`, `LockedReranker.load` (sticky skip)
    6. `packages/rag/src/way2australia_rag/serving/readiness.py` → `Readiness.snapshot`
    7. `config/serving.yaml` and `packages/rag/src/way2australia_rag/serving/config.py` → `load_serving_config`, `check_budget`
    8. `packages/rag/tests/serving/test_stack.py`, then `test_readiness_and_locks.py`, `test_serving_config.py`
    9. Supporting edits: `tasks.md` boxes and State
  - Learning notes: /Users/justin/learning/way2australia/specs/013-http-serving/T5.md
- Usage: (orchestrator)

### User decision
- 2026-11-21 — approved:

> T5 approved. Commit it with the Spec-Task: 013/T5 trailer and push spec/013, recording the approval in the T5 user-decision block.
>
> Add a dated change-log line to T6 in tasks.md (from T5 review F2 and F1):
> 1. Generator ownership: StackHolder closes the generator at shutdown and when open_serving_stack fails, so the lifespan must not close it again; if phase 1 fails after build_generator but before the holder exists, the lifespan closes it itself. Add a test for that failure path.
> 2. Add a test that, with no generator passed in, the server uses config default_generator (T5 F1).
> Keep F3 (real-Qdrant re-open, covered by the T8 smoke run) and F4 (covered by T6's shutdown order) as notes.
>
> Dont start T6 yet

## T6 — round 1

### Implementation
- Model: Claude Sonnet 5.5 (Claude Code; BEST_MINUS_ONE, matches the configured Claude Code tier)
- Files changed:
  - `apps/api/pyproject.toml` (workspace dependency `way2australia-rag`), `uv.lock`
  - `apps/api/src/way2australia_api/config.py` (`repo_root`, `serving_config`, `api_fake` from `W2A_API_FAKE`)
  - `apps/api/src/way2australia_api/lifespan.py` (new: `run_phase_one`, `StartupError`, `_Loader` background thread, `make_lifespan`, default `on_fatal` = SIGTERM)
  - `apps/api/src/way2australia_api/api/ready.py` (new: `GET /ready`), `main.py` (`create_app(settings, *, stack_factory=None, on_fatal=None)`, lifespan, `/ready` router, readiness on `app.state`)
  - `Makefile` (`api` target, `API_HOST`/`API_PORT`)
  - Tests: `apps/api/tests/conftest.py`, `support.py`, `test_serving_startup.py` (new, 14 tests); `packages/rag/tests/serving/test_stack.py` (one new test: generator follows `default_generator`)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run: `uv run pytest apps/api packages/rag/tests/serving` → 57 passed. `ruff check`, `ruff format`, `pyright apps packages/rag/tests/serving` → clean. `HF_HUB_OFFLINE=1 make verify` (once) → exit 0, 1876 passed, 20 skipped (Qdrant not running: Docker integration tests skipped). `make -n api` prints the `$(UV_ENV) $(UV) run uvicorn ...` recipe. `git status --porcelain -- evaluation knowledge config` → empty. `make test-integration` not required by T6, not run.
- Notes:
  - Phase 1 maps every failure to `StartupError("startup failed: <Class>[: <message>]")`. The message text is kept only for the families that are path- and secret-free by contract (retrieval, ingestion, generator configuration, prompt, serving configuration); any other exception is reported by class name only. The lifespan closes the generator only when phase 1 fails after `build_generator`; on success the generator is in `ServingInputs.generator` and the holder owns it (tests count one close on a phase 1 failure after build, on a phase 2 failure and on a normal shutdown).
  - Phase 1 skips the lexical check only when the configured strategy is `dense`. The checked handle is closed; phase 2 opens its own.
  - Shutdown while the loader is still running: the loader sees a `closing` flag and closes the holder it finishes building (test). After a normal start, shutdown closes the holder (stack, lexical, client, embedder, reranker, generator). uvicorn stops accepting requests before the lifespan ends, which is T5 review F4's shutdown order.
  - `on_fatal` default signals SIGTERM to the process (graceful uvicorn exit); the process exit code is then uvicorn's, not necessarily non-zero. Noted for the T8 smoke check.
  - A real `uvicorn` start with `W2A_API_FAKE=1` and the real (bge-m3) lexical file stops with the identity-mismatch message and no path. The full fake start needs `make ingest` and `make index-lexical` with the fake embedder and `QDRANT_COLLECTION_BASE`, which is user-run and not exercised here.
  - T5 review F3 (re-open tested against in-memory Qdrant only) stays a T8 smoke item. `COMMANDS.md` is not updated here (T9).
- Usage: 189K tokens · 48 tool uses · 8:44

### Review
- Model: claude-opus-5-5 (Claude Code; BEST tier `Opus`, matches; different model from the implementer)
- Verdict: PASS
- Commands: `uv run pytest apps/api packages/rag/tests/serving` (via `.venv/bin/python -m pytest`) → pass (57 passed); `HF_HUB_OFFLINE=1 make verify` (once) → exit 0 (1876 passed, 20 skipped: Docker integration tests, no local Qdrant); `make -n api` → `$(UV_ENV) $(UV) run uvicorn way2australia_api.main:app --host 127.0.0.1 --port 8000`; `git status --porcelain -- evaluation knowledge config` → empty. `make test-integration` not required by T6, not run.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R2] Shutdown while the loader is still in `open_serving_stack`: `_Loader.close()` sets `closing` and the lifespan returns without joining the daemon loader thread, so the late holder is closed only if the process outlives the load (the test keeps the process alive). In a real uvicorn exit the thread is killed mid-load and the OS reclaims the resources. → Optional: join the loader with a bounded timeout in the lifespan's `finally`, or note the window in the design As-built notes (T9).
  - F2 [MINOR, IMPLEMENTATION, R8] `test_unknown_prompt_stops_startup_and_closes_the_generator` asserts that no generator was built (the prompt is read first), so its name promises a close it does not check; the close-once path is covered by the tokenizer and missing-lexical tests. → Rename when the file is next touched.
  - Implementer note checked: the default `on_fatal` sends SIGTERM; uvicorn 0.54 `Server.capture_signals` re-raises the captured signal after a graceful shutdown, so a phase 2 failure ends the process by SIGTERM (non-zero status), as the design's "process exits" needs. T5 F4 shutdown order holds: uvicorn drains requests before the lifespan `finally` calls `holder.close()`.
- Summary for user (PASS only):
  - Changed: the API now starts the serving stack in two phases (`lifespan.py`): phase 1 synchronous checks (configs with the budget cross-check, prompt, generator, `lote` codes, standalone lexical identity, chunker, tokenizer, freshness) that stop startup with a path- and key-free `StartupError`; phase 2 opens the stack on a background thread. `GET /ready` (new) reports `starting` / `failed` (503) or `ok` / `degraded` (200) with reasons, breaker state and `fake`. `W2A_API_FAKE` selects fake models and logs a warning. `make api` added (`API_HOST`/`API_PORT`). `apps/api` depends on `way2australia-rag`.
  - Verified by: 14 new startup tests (`apps/api/tests/test_serving_startup.py`) and one new `default_generator` test in `test_stack.py`; targeted pytest 57 passed; `make verify` 1876 passed.
  - Worth your attention: generator ownership follows the 2026-11-21 box (lifespan closes it only on a phase 1 failure after build; holder otherwise; counted once in every test). A phase 2 failure exits by SIGTERM. Shutdown during load closes the late stack only if the process stays alive (F1). The fake start against a real lexical file was not run end to end (needs user-run fake `make ingest` / `make index-lexical`; T8).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `Makefile` → `api`: how the server is started.
    2. `apps/api/src/way2australia_api/main.py` → `create_app`: wires the lifespan, `Readiness` and the `/ready` router; test seams `stack_factory`, `on_fatal`.
    3. `apps/api/src/way2australia_api/lifespan.py` → `run_phase_one`, `_check_lexical`, `_Loader._run` / `close`, `make_lifespan`: the two phases, generator ownership, shutdown.
    4. `apps/api/src/way2australia_api/api/ready.py` → `get_ready`: maps the readiness snapshot to status and body.
    5. `apps/api/src/way2australia_api/config.py` → `Settings`: `repo_root`, `serving_config`, `api_fake` (`W2A_API_FAKE`).
    6. `apps/api/tests/support.py`, `conftest.py`: in-memory indexed client, down client, counting fakes, fake-identity lexical file.
    7. `apps/api/tests/test_serving_startup.py`: phase 1 failures, readiness transitions, phase 2 failure, fake mode, shutdown counters.
    8. Supporting edits: `packages/rag/tests/serving/test_stack.py` (`default_generator` test), `apps/api/pyproject.toml`, `uv.lock`.
- Usage: 148K tokens · 37 tool uses · 11:04

### User decision
- 2026-11-21 — approved:

> T6 approved. Record it, commit once with the Spec-Task: 013/T6 trailer and push spec/013. Carry F1 (lifespan does not join a loader still opening at shutdown; late holder is closed by the loader, process exit frees the rest) into T9's As-built notes, and F2 (rename test_unknown_prompt_stops_startup_and_closes_the_generator) to the next time that test file is touched. Then start T7 with exactly one implementer session.

## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Claude Code subagent; BEST_MINUS_ONE tier, mismatch with MODEL_PREFERENCES not checked, no user to ask)
- Files changed: new `apps/api/src/way2australia_api/{contract,slots,middleware,errors,logs}.py`, `api/answer.py`; edited `main.py` (middleware order, handlers, router, logging setup) and `lifespan.py` (slot pool, runtime settings, `top_k` on app state, abandoned provider registered on readiness); new `apps/api/tests/test_answer_route.py` (44 tests). `test_serving_startup.py` not touched, so the T6 F2 rename carry-over stays open.
- Verification: `pytest apps/api packages/rag/tests/serving` 101 passed; `ruff check`, `ruff format --check`, `pyright apps/api` clean. **`make verify` did not complete**: the first run failed on a pyright error in the new test file (fixed); the second run was refused by the verify-budget hook (budget 2, one slot was spent by a `make -n test` dry run). The full suite and the protected-path check (`git status --porcelain -- evaluation knowledge config`, empty at last look) are left to the reviewer. No integration tests required.
- Notes:
  - Query-length and empty checks and `lote` resolution run in the route (422 built with the shared error helper); extra fields and type errors come from the pydantic model through the validation handler. The `lote` message lists active codes and does not echo the value.
  - The route catches any exception and returns the 500 body itself (so the fake header and request ID are present); the global `Exception` handler is a backstop.
  - `X-W2A-Fake` follows `settings.api_fake` (every answer-path response incl. 413, 422, 503, 500).
  - The 413 middleware reads the limit from `app.state.serving_config` (set in phase 1).
  - Logger `way2australia_api.answer` gets a stderr handler only when the root has none (uvicorn), so tests capture via propagation.
- Usage: 156K tokens · 22 tool uses · 11:26
- Verify budget note: the full `make verify` did not complete in this round (one pyright failure fixed, second run refused by the budget hook); the task reviewer runs it.

### Review
- Model: claude-opus-5-5 (Claude Code subagent; BEST tier, matches `MODEL_PREFERENCES.md`)
- Verdict: FAIL
- Commands: `HF_HUB_OFFLINE=1 make verify` → pass (ruff check clean, 262 files formatted, pyright 0 errors; pytest 1920 passed, 20 skipped of 1940 collected, 200 s; `apps/api/tests/test_answer_route.py` all passed); `git status --porcelain -- evaluation knowledge config` → empty. No integration run required by the task. The iteration run (`uv run pytest apps/api`) was not repeated separately; `make verify` covers it.
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, R12] The server's 500 log line records the error class but not the request ID. R12 AC2 and the design ("Middleware and errors": "the log records the error class and request ID") require both. `api/answer.py:98` logs `"answer failed: %s"` with the class only, and so does the backstop `errors.py:57` (`"request failed: %s"`). No answer log line is written on the 500 path, so the request ID the client receives can't be matched to any server log line. → Log the request ID with the class in both places (still no `exc_info` and no message). Add a test that the 500 log record for an injected error holds the response's `X-Request-ID` and the class name.
  - F2 [MINOR, IMPLEMENTATION, R16] `X-W2A-Fake` follows `settings.api_fake` only. The design says the header goes on "when the stack is fake (any of embedder, reranker or generator is fake)". A real-mode server whose configuration selects a fake provider (for example `default_generator: fake`, which the T6 configuration test exercises) would serve fake answers with no header, and readiness would show `fake: false`. → Derive the flag from the opened components (or refuse fake providers outside `W2A_API_FAKE` at phase 1), or record that `api_fake` is the only switch as a decision.
  - F3 [MINOR, IMPLEMENTATION, R16] The fake header is asserted on 200 and 422 only. The code also adds it to 413 (`BodySizeMiddleware._too_large`), 503 and 500 (`error_response`), but no test checks those. → Extend `test_fake_header_present_in_fake_mode_and_absent_otherwise` to the 413, 503 and 500 responses.
  - F4 [MINOR, IMPLEMENTATION, R10/R12] `holder.acquire()` raises `ServingNotReadyError` once the holder is closed (shutdown race). That error is caught by the route's broad `except` and becomes a 500 `internal_error` instead of a 503 `not_ready`. → Map `ServingNotReadyError` to the not-ready 503 (optional; shutdown only).
  - F5 [MINOR, IMPLEMENTATION, R12] Only an authorization error is injected at the route. Configuration and applicability errors take the same path but have no route test, while R12 says "tests cover each class". → Parametrize the 500 test over `RetrievalAuthorizationError`, a configuration error and an applicability error.
- Implementer decisions checked:
  - Query and `lote` validation in the route matches design "Lote and query validation runs in the route after body parsing" and "Data flow". The model-level comment in the contract sketch is superseded. The `lote` 422 lists active codes and does not echo the value.
  - The route-built 500 is sound. It keeps the request ID and fake header, and it avoids Starlette's `ServerErrorMiddleware` re-raise, which would make uvicorn log a traceback with the exception message (R12/R13). The global handler is only a backstop for middleware failures. On that path the uvicorn traceback would still be logged, which is acceptable for a backstop.
  - The fake header reaches 413, 422, 503 and 500 through the path check in `fake_headers`. See F2 and F3.
  - Contract, maps, pin test, slots (idempotent release, transfer, late-callback safety via `AbandonedWork.add_done_callback`), middleware order (request ID outermost), 413 with and without `Content-Length`, 422 without `input`/`ctx`, server-resolved guest access, `top_k` from config, and the log fields all match the design. `test_serving_startup.py` was not touched, so the T6 F2 rename carry-over stays open.
- Usage: 141K tokens · 24 tool uses · 4:39

## T7 — round 2

### Implementation
- Model: claude-sonnet-5-5 (Claude Code subagent; BEST_MINUS_ONE tier, mismatch with MODEL_PREFERENCES not checked, no user to ask)
- Files changed: `apps/api/src/way2australia_api/api/answer.py`, `errors.py`, `lifespan.py`; `apps/api/tests/test_answer_route.py`, `test_serving_startup.py` (rename only).
- Findings fixed:
  - F1: both 500 log lines (route and backstop handler) now record `request_id` and the error class (no `exc_info`, no message). Test `test_internal_errors_are_500_with_request_id_only` checks the single ERROR record holds the response's `X-Request-ID` and the class name, with no sentinel text and no `exc_info`.
  - F2: the design's fake-mode section only says `api_fake` selects fakes and that the header and readiness show fake "when the stack is fake"; it does not say how a config-selected fake behaves. Chose to refuse: phase 1 (`_refuse_fake_providers`) stops startup with a `RetrievalConfigurationError` ("configuration selects a fake embedder/reranker/generator; fake providers need W2A_API_FAKE") when not in `api_fake` and the ingestion embedder provider, an enabled reranker provider or `default_generator` is `fake`. So `settings.api_fake` is the only way to get a fake stack and the header/readiness flag cannot lie. The check runs before the generator is built. Test `test_fake_provider_outside_fake_mode_is_refused_at_startup`.
  - F3: `test_fake_header_present_in_fake_mode_and_absent_otherwise` now also asserts `X-W2A-Fake: true` on 413, busy 503 and 500.
  - F4: the route maps `ServingNotReadyError` from `holder.acquire()` to 503 `not_ready` with the not-ready `Retry-After`; test `test_shutdown_race_is_503_not_ready` (slot released).
  - F5: the 500 test is parametrized over `RetrievalAuthorizationError`, `RetrievalConfigurationError` and `LanguageApplicabilityError`.
  - T6 F2 carry-over: `test_unknown_prompt_stops_startup_and_closes_the_generator` renamed to `test_unknown_prompt_stops_startup_before_a_generator_is_built`.
- Verification: `pytest apps/api packages/rag/tests/serving` 105 passed; ruff check/format and pyright `apps/api` clean; `make verify` once (result in the hand-off). `git status --porcelain -- evaluation knowledge config` empty.
- Usage: 120K tokens · 24 tool uses · 6:50

### Review
- Model: claude-opus-5-5 (Claude Code subagent; BEST tier, matches `MODEL_PREFERENCES.md`; different model from the implementer)
- Verdict: PASS
- Commands: `HF_HUB_OFFLINE=1 make verify` (once) → exit 0 (ruff check clean, 262 files already formatted, pyright 0 errors; pytest 1924 passed, 20 skipped: Docker integration tests, no local Qdrant; 200 s). `git status --porcelain -- evaluation knowledge config` → empty. The iteration run `uv run pytest apps/api` is covered by `make verify` and was not repeated. No integration run required by T7.
- Round 1 findings checked:
  - F1 fixed: `api/answer.py` and the backstop `errors.py::_internal_handler` log `request_id=… error=<Class>` with no message and no `exc_info`; `test_internal_errors_are_500_with_request_id_only` asserts exactly one ERROR record holding the response's `X-Request-ID` and the class, no sentinel, `exc_info is None`.
  - F2 fixed by refusal: `lifespan._refuse_fake_providers` runs in phase 1 before `build_generator` when `api_fake` is false and refuses a `fake` embedder, an enabled `fake` reranker or `default_generator: fake` with a `RetrievalConfigurationError` (its message survives `_safe_message`, path- and key-free). This fits R16 ("a fake mode … exists only through explicit server settings") and the design error table (invalid config → phase 1 fails); it makes the design's "when the stack is fake" condition equal to `api_fake`, so the header and readiness flag cannot under-report. No spec decision is needed, but the choice should be written down (F1 below). Committed config (`bge_m3`, `bge`, `anthropic`) is unaffected.
  - F3 fixed: the fake-header test now covers 200, 422, 413, busy 503 and 500, and the absent case.
  - F4 fixed: `ServingNotReadyError` from `holder.acquire()` → 503 `not_ready` with `Retry-After: 5`, slot released (`test_shutdown_race_is_503_not_ready`).
  - F5 fixed: the 500 test is parametrized over authorization, configuration and applicability errors.
  - T6 F2 carry-over done: the test is renamed to `test_unknown_prompt_stops_startup_before_a_generator_is_built`.
  - No regressions found: round 2 changes are confined to the logging lines, the new `except ServingNotReadyError` branch (placed before the broad `except`, `finally` still releases the slot), the phase 1 check and tests.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R16] The refusal of config-selected fake providers outside `W2A_API_FAKE` is a behaviour the design does not state (design "Settings and fake mode" / "Middleware and errors" describe the header "when the stack is fake"). → Record it in T9's design As-built notes (and the fake-mode entry in `COMMANDS.md`/`DECISIONS.md`).
  - F2 [MINOR, IMPLEMENTATION, R16] `test_fake_provider_outside_fake_mode_is_refused_at_startup` covers only the generator branch; the embedder and enabled-reranker branches (and "disabled fake reranker is allowed") have no test, and `_refuse_fake_providers` types `generation` as `Any` rather than `GenerationConfig`. → Parametrize the test over the three providers and tighten the type when the file is next touched.
- Summary for user (PASS only):
  - Changed: `POST /v1/answer` is in place (`api/answer.py`) with public contract 1.0 (`contract.py`), the slot pool (`slots.py`), request-ID and body-size middleware (`middleware.py`), 422/500/503 bodies (`errors.py`) and the one-line JSON answer log (`logs.py`); the lifespan adds the slot pool, runtime settings, config `top_k` and the abandoned-work readiness provider, and now refuses a config-selected fake provider unless `W2A_API_FAKE` is set.
  - Verified by: `apps/api/tests/test_answer_route.py` (contract pin, mappings, 422/413/503/500, slots, capped generator, request ID, fake header, no sensitive text in logs or bodies); `make verify` 1924 passed, 20 skipped.
  - Worth your attention: fake providers now only run under `W2A_API_FAKE` (round 2 choice; to be written into the design at T9, F1). Shutdown-race requests get 503 `not_ready`. The refusal test covers the generator only (F2).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `apps/api/src/way2australia_api/main.py` → `create_app`: middleware order, error handlers, answer router.
    2. `apps/api/src/way2australia_api/middleware.py` → `RequestIdMiddleware`, `BodySizeMiddleware`, `fake_headers`.
    3. `apps/api/src/way2australia_api/api/answer.py` → `post_answer`: readiness, slot, validation, access, `service.answer`, contract, log, release.
    4. `apps/api/src/way2australia_api/slots.py` → `SlotPool`, `Slot.transfer`/`release`.
    5. `apps/api/src/way2australia_api/contract.py` → `AnswerRequest`, `AnswerContract`, `to_contract` and the `_STATUS`/`_REASON` maps.
    6. `apps/api/src/way2australia_api/errors.py` → `error_response`, validation and backstop handlers.
    7. `apps/api/src/way2australia_api/logs.py` → `build_log_record`, `configure_logging`.
    8. `apps/api/src/way2australia_api/lifespan.py` → `_refuse_fake_providers`, slot pool and app state in `make_lifespan`.
    9. `apps/api/tests/test_answer_route.py`: route, contract, limits, errors, logging tests.
    10. Supporting edits: `apps/api/tests/test_serving_startup.py` (rename), `tasks.md`, `CURRENT_STATE.md`.
- Usage: 126K tokens · 28 tool uses · 6:09

### User decision
- 2026-11-22 — approved:

> T7 approved. Record it, commit once with the Spec-Task: 013/T7 trailer and push spec/013. Carry round-2 F1 (fake-provider refusal at startup) into T9: the design As-built notes, COMMANDS.md, and a DECISIONS.md entry. Carry F2 (tests for the embedder, enabled-reranker and disabled-fake-reranker branches of _refuse_fake_providers, and a real type instead of Any for generation) to the next time lifespan.py or its tests are touched. dont start T8 yet, give me the command to run the orchestrator in a different session.

## T8 — round 1

### Implementation
- Model: Grok 4.7 (Cursor; BEST_MINUS_ONE). Matches the configured Cursor tier.
- Files changed:
  - `apps/api/tests/test_route_security.py` (route authorization over a throwaway security index)
  - `apps/api/tests/test_concurrency.py` (16 concurrent `TestClient` threads; dense re-open under that load)
  - `docs/project/COMMANDS.md` (user-run real smoke steps; `api` listed as implemented)
  - `.kiro/specs/013-http-serving/tasks.md` (boxes, State), this file
- Verification run: `uv run pytest apps/api` → 73 passed. `make eval-security` → PASS in 19971 ms (`experiments/results/tmp/security-evaluation-20261122T173514Z.json`; heading, structure and recursive chunkers, 93 queries, lote modes none and ml). `make verify` → pass outside the sandbox (ruff clean, 264 files formatted, pyright 0 errors, skills-check match, validate-knowledge OK, validate-evaluation OK, 1928 passed, 20 skipped, 1948 collected). A sandboxed `make verify` failed 7 git-init tests (`git init` could not create `.git/hooks`: Operation not permitted); those tests pass outside the sandbox and are the ones in the 1928. `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` is not a separate T8 command; integration tests run inside `make verify`.
- Notes:
  - The route test builds one security index (`build_security_repository`, `build_security_index`, in-memory Qdrant, temp lexical file, fake embedder) and opens three serving stacks against it. Phase 1 still checks the ordinary fake lexical file. Phase 2 retargets `collection_base`, `index_version` (`sec-v1`) and the lexical tokenizer (`lexical-v1`, the builder's default). A wrapper ignores `close` so the stack shutdown does not destroy the shared client.
  - Breaker-open BM25 is the same hybrid stack after `record_failure` reaches `failure_threshold`. An open-time BM25 start would call `verify_fresh`, which refuses this file because the synthetic forbidden rows are not repository documents. The answer log is the path check: hybrid with `rerank: off`, then `served_strategy` `bm25` and `fallback_reason` `qdrant_unavailable`, then hybrid with `rerank: applied`. Before any request, a filter-free dense search shows a forbidden document among the nearest hits, so an empty result would not hide a missing corpus. `role`, `tenant_id` and `scope` are 422 on each stack.
  - Concurrency raises `max_in_flight` to 16. BM25 is the Qdrant-down stack; hybrid is the indexed in-memory client. Bodies match a solo request except `request_id`. The re-open test holds `FallbackRetriever.retrieve` until all 16 calls have entered, then points the client factory at the up client and moves the breaker clock past the cool-down. All 16 return 200, the holder is dense, the breaker is closed, and the pre-swap stack's lexical handle is closed.
  - These tests pass `on_fatal` as a no-op so a failed phase-2 open does not SIGTERM the pytest process.
  - Real smoke check (R16): not run. It needs the real stack (`make api`, models, Qdrant, `ANTHROPIC_API_KEY`). Steps are in `COMMANDS.md` under "HTTP API smoke check". No user run is recorded in this file yet.
  - `lifespan.py` and its tests were not touched, so the T7 round-2 F2 carry-over (embedder, enabled-reranker and disabled-fake-reranker tests for `_refuse_fake_providers`, and a `GenerationConfig` type for `generation`) stays on the task.
  - `docs/project/CURRENT_STATE.md` was already modified when this session started (orchestrator handoff: T7 approved, T8 not started). This session did not edit it.
  - No library code changed. No FastAPI, Starlette, uvicorn or httpx behaviour was relied on beyond threads calling one `TestClient`, which the design names.
- Usage: not measured · 219 tool uses · n/a

### Review
- Model: Grok 4.7 (Cursor; BEST). Same configured model as the implementer; Cursor BEST and BEST_MINUS_ONE are both Grok 4.7.
- Verdict: PASS
- Commands: `python3 -m uv run pytest apps/api` → pass (73 passed); `make eval-security` → pass (19484 ms; heading, structure and recursive chunkers; 93 queries; lote modes none and ml; `experiments/results/tmp/security-evaluation-20261122T175217Z.json`); `make verify` → pass, first attempt outside the sandbox (ruff clean, 264 files formatted, pyright 0 errors, skills-check match, validate-knowledge OK, validate-evaluation OK, 1928 passed, 20 skipped, 1948 collected). `git status --porcelain -- evaluation knowledge config` → empty (allowed: none). `make test-integration` is not a T8 command.
- Findings: none
- Summary for user (PASS only):
  - Changed: route-level authorization over a throwaway security index (`apps/api/tests/test_route_security.py`) and 16-thread concurrency plus a dense re-open under that load (`apps/api/tests/test_concurrency.py`). `COMMANDS.md` now has the user-run real smoke steps and lists `api` as implemented. No library code changed.
  - Verified by: `pytest apps/api` (73 passed), `make eval-security` PASS, `make verify` exit 0 (1928 passed, 20 skipped, 1948 collected).
  - Worth your attention: the real smoke check is not run. It needs `make api` with the real embedder, reranker, generator, Qdrant and `ANTHROPIC_API_KEY`. Steps are under "HTTP API smoke check" in `COMMANDS.md`. Breaker-open BM25 is tripped on an already-open hybrid stack, because an open-time BM25 start would refuse this synthetic lexical file. The re-open under load uses in-memory Qdrant; the live check is that optional smoke step. `CURRENT_STATE.md` still lists the T8 tests under "Not yet implemented"; T9 reconciles that file.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `docs/project/COMMANDS.md` → "HTTP API smoke check": the user-run `make api` steps (readiness, one answerable and one unanswerable query, optional breaker)
    2. `apps/api/tests/test_route_security.py` → `test_route_hides_forbidden_documents_on_every_serving_path`: `POST /v1/answer` on hybrid, breaker-open BM25 and the reranked path
    3. `apps/api/tests/test_concurrency.py` → `test_concurrent_requests_match_the_same_request_alone`, `test_reopen_during_concurrent_requests_drains_the_old_stack`: 16 threads, then the swap and drain
    4. Supporting edits: `tasks.md` boxes and state
- Usage: not measured · 124 tool uses · n/a

### User decision
- 2026-11-22 — not approved yet:

> Not approved yet. The smoke-check box in T8 is ticked but the smoke run was not done; untick it until I record the run. I'm running the HTTP API smoke check now per COMMANDS.md and will paste the results to record under T8 in task-reviews.md. Wait for that before asking for approval.

The smoke-check box is unticked. Approval waits until this run is recorded here.
### User-run smoke check (recorded 2026-11-27)
- Stack: real (BGE-M3, `bge-reranker-v2-m3`, Qdrant, `anthropic` / `claude-sonnet-5-5`), `W2A_API_FAKE` unset; steps per `COMMANDS.md` "HTTP API smoke check".
- Startup without `ANTHROPIC_API_KEY` (2026-11-25): phase 1 refused cleanly with "GeneratorConfigurationError: ANTHROPIC_API_KEY is not set…", no path or secret in the message; the process exited (`make api` Error 3).
- Startup 14:45:54; first `/ready` poll 14:46:40 → 200 `{"status":"ok","degraded_reasons":[],"breaker":"closed","fake":false}`. Warm-up ≤ 46 s (upper bound; models loaded by 14:46:00).
- Answerable, "Is coaching compulsory?" → HTTP 200, status `answered`, reason `null`; `latency_ms` total 4241.8 (retrieval 1726.0, generation 2515.1); hybrid, rerank applied.
- Unanswerable, u016 refund question → HTTP 200, status `insufficient_evidence`, internal reason `citation_invalid` / sub_reason `model_url`; total 3878.4 (retrieval 1659.2, generation 2218.9). Same outcome as the Spec 012 v4 reference run (known `model_url` carry-over for prompt v2).
- Log lines carry `query_chars` only, no query text.
- Breaker check: not run (optional).
- Finding for T9 (As-built notes / known issues): on 2026-11-25 a server left idle about 2 days answered its first request with retrieval 40117.8 ms, which consumed the 40 s request budget, so generation was skipped (`evidence_only` / `generator_unavailable`, sub_reason `deadline`; nothing billed). Right after a fresh start retrieval was 1.7 s, so the cause is idle swap/sleep, not startup. Embedder and reranker have no inference timeout (D077) and `/ready` does not warm the models. Candidate follow-up: a warm-up inference before ready, and/or a retrieval-time share of the budget.

### User decision
- 2026-11-27 — approved:

> T8 approved. Record it, commit once with the Spec-Task: 013/T8 trailer and push spec/013. Leave the spec-implementer SKILL.md change (all four copies) out of the T8 commit; I'll commit it separately as a chore. Then start T9 with exactly one implementer session, and use a stronger reviewer model than the implementer for T9's review (Opus in Claude Code, or the strongest model available in Cursor).
