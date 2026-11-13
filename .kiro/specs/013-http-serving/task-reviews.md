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
