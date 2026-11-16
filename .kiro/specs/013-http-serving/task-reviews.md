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
