# Spec 011 — task reviews

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md`, tier match not checked against the table.
- Files changed:
  - New `packages/rag/src/way2australia_rag/rerank/`: `__init__.py` (no exports), `base.py`, `fake.py`, `errors.py`, `bge.py`, `build.py`;
  - `retrieval/availability.py` (chain walk extracted into private `_cause_chain`; `classify_model_error` output unchanged), `retrieval/strategy.py` (`RerankConfig`, schema 1.3, `rerank` default off for 1.1/1.2);
  - `config/retrieval.yaml` (schema 1.3, `rerank` block, `enabled: false`, pinned revision), `packages/rag/pyproject.toml` (`reranker` extra), `uv.lock`, `Makefile` (`setup-bge-m3` also installs `reranker`);
  - Tests: new `packages/rag/tests/rerank/{test_rerank_fake,test_rerank_errors,test_rerank_bge,test_rerank_config}.py`; `retrieval/test_strategy.py` (committed schema now 1.3); `graphify-out/*` refreshed.
- Pinned revision: `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`, read 2026-11-05 from `https://huggingface.co/api/models/BAAI/bge-reranker-v2-m3` (field `sha`); the user should check it on the model page.
- Verification run:
  - targeted `pytest packages/rag/tests/rerank packages/rag/tests/retrieval` → 437 passed, 1 skipped; `make lint typecheck` clean;
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (the single run) → 1337 passed, 3 skipped (no extra, no Docker, no network); the 3 skips include the new opt-in `W2A_RUN_RERANKER_SMOKE` test (never run);
  - `git diff --name-status -- evaluation knowledge config` → only `config/retrieval.yaml`; `graphify update .` run.
  - Not run: `make test-integration` (T1 does not require it), the real reranker, the smoke test.
- Notes:
  - `classify_reranker_error` excludes real hub `OfflineModeIsEnabled` and `LocalEntryNotFoundError` anywhere in the chain; the existing `classify_model_error` still excludes only `OfflineModeIsEnabled` (unchanged output). `BgeRerankerV2M3.load()` turns an offline-not-cached chain into `RetrievalConfigurationError` with `make setup-bge-m3` advice, an eligible network/timeout chain into `RerankerUnavailableError` (`raise ... from`), and re-raises anything else unchanged; `score()` does the same wrapping.
  - `RerankConfig.revision` is optional when `enabled: false` (1.1/1.2 files have none) and required when enabled; `provider` is `bge | fake`. A 1.3 file must carry the `rerank` block; 1.1/1.2 files must not. Cross-field and block errors report `rerank...` text via `_model_error_text` in the loader (pydantic gives model validators no precise location).
  - `build_reranker(config, provider=None)`: the optional `provider` argument is the `--reranker fake` override for T2/T3.
  - Raw logits: `predict(..., activation_fn=torch.nn.Identity())`, `torch` imported only inside `load()`.
  - Not run against the real model, so the `CrossEncoder` call signature (`activation_fn`, `.tokenizer`, `.device`) is unverified until the user runs the smoke test.
- Usage: 159K tokens · 24 tool uses · 7:00

### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent; matches the BEST tier (`Opus`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands:
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) uv run pytest packages/rag/tests/rerank packages/rag/tests/retrieval -q` → 437 passed, 1 skipped;
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (the reviewer's single run) → pass, 1337 passed, 3 skipped (no extra, hub-free);
  - `git status --porcelain -- evaluation knowledge config` → only ` M config/retrieval.yaml` (allowed); `git diff --name-status main...HEAD -- evaluation knowledge config` → empty (work uncommitted);
  - unchanged-code list: `git diff HEAD --name-only` under `retrieval/`, `lexical/`, `ingestion/`, `config/ingestion.yaml` → only `retrieval/availability.py` (chain walk moved into `_cause_chain`, `classify_model_error` logic identical; its tests untouched) and `retrieval/strategy.py`; legacy baseline test untouched;
  - pinned revision: `curl https://huggingface.co/api/models/BAAI/bge-reranker-v2-m3` (metadata only) → `sha` `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`, 40-hex, equals `config/retrieval.yaml`;
  - `grep sentence_transformers packages/rag/src` → only `find_spec` checks; the import is inside `BgeRerankerV2M3._load_model` (called from `load()`); subprocess test confirms the module stays out of `sys.modules`.
  - Not run (not required by T1): `make test-integration`; the real reranker and `W2A_RUN_RERANKER_SMOKE` (never run by agents).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R3] `build_reranker` passes no `model_id` to `BgeRerankerV2M3`, which hard-codes `BAAI/bge-reranker-v2-m3`; a different `rerank.model_id` with `provider: bge` is neither refused nor used (ingestion refuses a mismatched `embedder.model_id`, `ingestion/cli.py:70`). Results would record the true adapter ID, so nothing is mislabelled. → refuse a non-matching `rerank.model_id` for `bge` (config load or `build_reranker`), with a test; can land in T2.
  - F2 [MINOR, IMPLEMENTATION, R1] `rerank/errors.py` imports `_NETWORK_TYPES`, `_cause_chain` and `_optional_types` from `retrieval/availability.py` with `reportPrivateUsage` ignores. Matches the design's "private helper reused", but the cross-module private imports are brittle. → optional: leave, or note in the design As-built notes.
- Summary for user (PASS only):
  - Changed: new `rerank/` package (Protocol, deterministic fake, error classifier, pinned `bge-reranker-v2-m3` adapter, factory); `RetrievalConfig` schema 1.3 with a validated `rerank` block (1.1/1.2 load with reranking off); `config/retrieval.yaml` 1.3, `enabled: false`, revision `953dc6f6…d41e`; `reranker` extra, installed by `make setup-bge-m3`. Nothing calls the reranker yet (T2).
  - Verified by: targeted pytest (437 passed), one hub-free `make verify` (1337 passed, 3 skipped), protected-path and unchanged-code checks, SHA re-read from the hub API (matches).
  - Worth your attention: please confirm the SHA on the model page (`BAAI/bge-reranker-v2-m3`, last modified 2024-06-24). The `CrossEncoder` calls (`activation_fn=nn.Identity()`, `.tokenizer`, `.device`) are untested against the real library until you run `W2A_RUN_RERANKER_SMOKE=1` after `make setup-bge-m3`. Offline-not-cached (`LocalEntryNotFoundError`/`OfflineModeIsEnabled`) is a configuration error for the reranker; `classify_model_error` for the embedder is deliberately unchanged (still excludes only `OfflineModeIsEnabled`). Two MINOR findings (F1 `model_id` ignored for `bge`; F2 private imports).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `config/retrieval.yaml` → `rerank` block: the reviewed values, off by default.
    2. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `RerankConfig`, `RetrievalConfig.rerank_block_matches_schema` / `rerank_depth_within_fusion`, `load_retrieval_config` (key-naming errors).
    3. `packages/rag/src/way2australia_rag/rerank/build.py` → `build_reranker`: config to `fake` or `bge`.
    4. `packages/rag/src/way2australia_rag/rerank/base.py` → `Reranker`, `RerankerInfo`, `RerankScores`: the contract.
    5. `packages/rag/src/way2australia_rag/rerank/bge.py` → `BgeRerankerV2M3.load` / `score` / `_wrap`: lazy import, raw logits, error wrapping.
    6. `packages/rag/src/way2australia_rag/rerank/errors.py` → `classify_reranker_error`, `is_offline_not_cached`.
    7. `packages/rag/src/way2australia_rag/retrieval/availability.py` → `_cause_chain`: shared chain walk.
    8. `packages/rag/src/way2australia_rag/rerank/fake.py` → `FakeReranker`: deterministic test double and hooks.
    9. `packages/rag/tests/rerank/` (`test_rerank_errors.py`, `test_rerank_bge.py`, `test_rerank_config.py`, `test_rerank_fake.py`) and `tests/retrieval/test_strategy.py`.
    10. Supporting edits: `packages/rag/pyproject.toml` (`reranker` extra), `uv.lock`, `Makefile` (`setup-bge-m3`).
- Usage: 146K tokens · 23 tool uses · 5:43

### User decision (2026-11-05)
- Approved, with one fix in the same commit (verbatim): "BUG (test-only): `packages/rag/tests/conftest.py` `hub_offline_empty_cache` opts out only on `W2A_RUN_BGE_M3_SMOKE=1`, so `W2A_RUN_RERANKER_SMOKE=1` alone still forces offline with an empty cache and the reranker smoke test fails with "weights are not cached". Make the fixture also opt out on `W2A_RUN_RERANKER_SMOKE=1`, update its docstring, and add a unit test that each of the two variables lifts the offline setup. Run targeted pytest on the conftest/rerank tests only; no extra `make verify`."
- Fix applied after the decision (Sonnet 5.5 subagent, 89K tokens · 8 tool uses · 0:49): helper `apply_hub_offline_empty_cache` and `HUB_OPT_OUT_VARIABLES` in `packages/rag/tests/conftest.py`; new `packages/rag/tests/rerank/test_hub_offline_fixture.py`. `make lint typecheck` clean; targeted pytest 77 passed, 2 skipped (smoke tests). No extra `make verify`.
- User checks (verbatim): "Revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` matches the HF API (last modified 2024-06-24, Apache-2.0)." Real smoke test, run by the user with both variables set as a workaround, on sentence-transformers 6.1.0 / torch 2.14.1 / transformers 5.20.0: `test_rerank_bge.py` 16 passed, including `test_real_model_orders_an_obvious_pair` (1:33 including the weight download).
- F1: fix in T2 by refusing a `rerank.model_id` that differs from the adapter's model, with a test. F2: leave it; note the private imports from `availability.py` in the design As-built notes in T6.

## T2 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5), run as a subagent; intended tier BEST_MINUS_ONE per `agent-skills/MODEL_PREFERENCES.md`, tier match not checked against the table.
- Files changed:
  - New: `retrieval/reranking.py` (`RerankingRetriever`), tests `tests/retrieval/test_reranking.py`, `tests/retrieval/test_opening_rerank.py`;
  - `retrieval/models.py` (`RerankRecord`, `RetrievedChunk.fused_rank`, `RetrievalResult.rerank`), `retrieval/strategy.py` (`build_retriever(..., reranker, rerank_open_skip)`), `retrieval/opening.py` (`open_retrieval(..., rerank, reranker_factory, reranker_provider)`, `OpenedRetrieval.reranker`, `_load_reranker`), `retrieval/cli.py` (`--rerank` / `--no-rerank` / `--reranker`, rerank line, skip warning), `rerank/build.py` (T1 review F1: `rerank.model_id` refusal for `bge`);
  - Tests adjusted for format/field changes only: `test_retriever.py` (`fused_rank: None` in the hit dump), `test_cli.py` and `evaluation/test_strategy_eval.py` (the new last output line `rerank: off`; hit lines now `lines[3:-1]`; parser option set gains the three flags); new tests in `rerank/test_rerank_config.py` (F1), `test_retrieval_integration.py` (Docker test);
  - Spec files: `tasks.md` (T2 boxes ticked, F1 box added), `requirements.md` (dated Change log line for F1, citing the T1 user decision of 2026-11-05); `graphify-out/*` refreshed.
- Verification run:
  - targeted `pytest` on `retrieval/`, `rerank/`, `evaluation/test_strategy_eval.py` → 513 passed, 1 skipped; `make lint typecheck` clean;
  - `make verify` used 2 runs in total: run 1 (hub-free) found 6 failures from the format/field changes above (fixed; no behaviour change with reranking off); run 2, `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` → 1378 passed, 3 skipped;
  - `make test-integration` (Docker Qdrant) → 28 passed, including the new `hybrid` + `FakeReranker` test through `open_retrieval` on a throwaway `w2a-t011-<8 hex>` base; the collection was deleted (checked: none left);
  - `git status --porcelain -- evaluation knowledge config` → empty; `graphify update .` run.
  - Not run: the real reranker and embedder; `w2a-realcheck-*` / `way2australia-*` collections never touched.
- Notes and deviations:
  - **Re-check wording.** `RetrievedChunk` carries no `tenant_id`, `access_scope` or `owner_user_id`, so `check_hit` cannot be run on a returned hit. The stage re-check instead requires every returned hit to equal (apart from `rank`, `score`, `fused_rank`, `leg_ranks`) exactly one candidate that the hybrid legs already passed through `check_hit` (unknown, duplicated or altered hits raise `RetrievalAuthorizationError`), then runs the real `check_applicable` (via `PointPayload.model_construct`) when `lote` is set. This runs on the reranked path and on both skip paths. The design/task text says "`check_hit` on every returned hit"; the reviewer and user should confirm this reading, or ask `spec-planner` to amend (alternative: carry the authorization fields on `RetrievedChunk`, a wider model change).
  - Output: the `rerank:` line is printed after the hits (so existing line-position assertions keep their meaning); with reranking off it prints `rerank: off`, which is the only change to existing CLI output.
  - Dense outage at open with `--rerank`: the reranker is constructed (missing extra still exits 2) but not loaded; BM25 serves with `rerank: null`.
  - `top_k > depth` is checked in the stage, so it exits 2 on a hybrid run and does not apply when BM25 serves a dense outage.
  - Skipped results keep the plain hybrid hits (`fused_rank` unset, `score_kind: rrf`); `latency_ms` is not extended by the failed attempt.
  - The empty-candidate case does not call the reranker and records `candidates: 0`.
- Usage: 200K tokens · 49 tool uses · 22:29

### Review
- Model: claude-opus-5-5 (Opus 5.5), run as a subagent; matches the BEST tier (`Opus`) in `agent-skills/MODEL_PREFERENCES.md`.
- Verdict: PASS
- Commands:
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) uv run pytest packages/rag/tests/retrieval/test_reranking.py packages/rag/tests/retrieval/test_opening_rerank.py packages/rag/tests/rerank -q` → 103 passed, 1 skipped (smoke test);
  - `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d) make verify` (the reviewer's single run) → pass, 1378 passed, 3 skipped;
  - `make test-integration` (Docker Qdrant) → 28 passed (1353 deselected), including `test_hybrid_with_the_fake_reranker_through_open_retrieval`; afterwards no `w2a-t011-*` collection remains (Qdrant `/collections` listing);
  - `git status --porcelain -- evaluation knowledge config` → empty (allowed: none); `git diff --name-status main...HEAD -- evaluation knowledge config` → `M config/retrieval.yaml` (T1, committed);
  - unchanged-code list: `git status --porcelain` on `retrieval/{fusion,hybrid,fallback,retriever,bm25,access,applicability,index,availability}.py`, `lexical/`, `ingestion/`, `config/ingestion.yaml`, `tests/retrieval/test_baseline.py` → empty;
  - existing-test edits read in the diff: `test_retriever.py` (`fused_rank: None` in the field dump), `test_cli.py` and `evaluation/test_strategy_eval.py` (trailing `rerank: off` line, hit slice `[3:-1]`, three new parser flags); no rank, score, document ID or ordering assertion changed.
  - Not run: the real embedder and reranker; no `w2a-realcheck-*` / `way2australia-*` collection touched.
- Specific checks requested:
  - Reranking off never builds or loads: `open_retrieval` calls `reranker_factory` only under `if rerank`; `_load_reranker(None)` returns at once; `build_retriever` without a reranker returns the pre-spec `FallbackRetriever(hybrid, bm25, None)`. Tested with config off and with `enabled: true` plus `rerank=False` (fail-on-load fake, call-counting factory: 0 calls, 0 loads) and through the CLI with `--no-rerank` (`FakeReranker.load` patched to fail).
  - Query-time reranker failure serves hybrid through the real `FallbackRetriever` (`strategy` hybrid, `fallback_reason` None, BM25 leg never called, hits equal plain hybrid, next query reranks); open-time skip sticky (`load_calls == 1` through `open_retrieval`, three queries all `stage: "open"`); dense outage at open and per query serves BM25 with `rerank: null` and no load or score call.
  - F1 refusal (`rerank/build.py`): `bge` with a non-matching `rerank.model_id` → `RetrievalConfigurationError` naming `rerank.model_id`; `fake` still builds. Tested.
- Findings:
  - F1 [MINOR, SPEC_DEFECT, R4] The R4 criterion, the T2 box and design "Data flow" step 7 say every returned hit passes `check_hit`. `RetrievedChunk` carries no `tenant_id`, `access_scope` or `owner_user_id`, so `check_hit` cannot run on it, and adding them would mean editing `retriever.py` / `bm25.py`, which the "Unchanged code" rule forbids: the spec cannot be met literally. The implementation (`RerankingRetriever._recheck`) requires each returned hit to equal, apart from `rank`/`score`/`fused_rank`/`leg_ranks`, exactly one candidate the hybrid legs already passed through `check_hit`, with no duplicates, then runs the real `check_applicable` when `lote` is set; it runs on the reranked path and both skip paths. Because the stage only reorders and never fetches, this gives the same guarantee for any stage defect, which is what the design "Security / authorization" section asks of the re-check ("defence in depth against a stage defect"); tests cover a foreign, a duplicated and a tampered hit, and the non-applicable row on all three paths. A "forbidden row" (other tenant/scope) cannot be expressed as a `RetrievedChunk`, so the foreign-hit case stands in for it. Not a security gap. → user to accept this reading; `spec-planner` adds a dated `## Change log` line amending R4 / design step 7 / the T2 box ("membership in the leg-checked candidate set, then `check_applicable`"). Does not need code changes; T4's harness-only defective stage should use the same wording.
  - F2 [MINOR, IMPLEMENTATION, R4] With `lote` set, the stage's `check_applicable` uses `PointPayload.model_construct(document_id=..., lote_languages=...)`, an unvalidated partial payload. Correct today (`check_applicable` reads only those two fields), but a future field read there would fail with `AttributeError` rather than closed. → optional: leave, or note in the design As-built notes in T6.
- Summary for user (PASS only):
  - Changed: new `retrieval/reranking.py` (`RerankingRetriever`: depth request, cross-encoder ordering with fused-rank ties, fail-closed output check, sticky open / per-query skip, post-stage re-check, `RerankRecord`); `open_retrieval` builds and loads the reranker once only when reranking is on; `build_retriever` puts the stage inside `FallbackRetriever`; `make retrieve` gains `--rerank` / `--no-rerank` / `--reranker` and a `rerank:` line (`rerank: off` by default); `build_reranker` refuses a mismatched `rerank.model_id` (T1 F1).
  - Verified by: 103 targeted tests, one hub-free `make verify` (1378 passed, 3 skipped), `make test-integration` 28 passed (throwaway base deleted), protected-path and unchanged-code checks empty.
  - Worth your attention: F1, the re-check is "returned hit must be one of the leg-checked candidates" instead of a literal `check_hit` (impossible on `RetrievedChunk` without editing frozen files); please accept it so `spec-planner` can record a Change log line. With reranking off, the only visible change is the new last CLI line `rerank: off`. On a dense outage at open with `--rerank`, the reranker is built (so a missing extra still exits 2) but never loaded.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/retrieval/cli.py` → `main`, `rerank_line`: flags, effective rerank, skip warning.
    2. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`, `_load_reranker`: hybrid-only refusal, build/load once, sticky open skip.
    3. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `build_retriever`: `FallbackRetriever(RerankingRetriever(HybridRetriever))`.
    4. `packages/rag/src/way2australia_rag/retrieval/reranking.py` → `RerankingRetriever.retrieve`, `_order`, `_skipped`, `_recheck`: the stage.
    5. `packages/rag/src/way2australia_rag/retrieval/models.py` → `RerankRecord`, `RetrievedChunk.fused_rank`, `RetrievalResult.rerank`.
    6. `packages/rag/src/way2australia_rag/rerank/build.py` → `build_reranker`: `rerank.model_id` refusal.
    7. `packages/rag/tests/retrieval/test_reranking.py`: ordering, malformed output, re-check defects, skip vs fallback.
    8. `packages/rag/tests/retrieval/test_opening_rerank.py`: wiring, never-built-when-off, sticky skip, CLI.
    9. `packages/rag/tests/retrieval/test_retrieval_integration.py` → `test_hybrid_with_the_fake_reranker_through_open_retrieval` (Docker).
    10. Supporting edits: `tests/rerank/test_rerank_config.py` (F1 test), format-only edits in `test_retriever.py`, `test_cli.py`, `evaluation/test_strategy_eval.py`; `tasks.md` boxes and `requirements.md` Change log line.
- Usage: 168K tokens · 27 tool uses · 6:54


### User decision (2026-11-05)
- Approved (verbatim): "T2 approved. F1: accepted. The membership re-check (every returned hit equals exactly one fused candidate that the legs passed through `check_hit`, ignoring only rank/score fields, no duplicates, then `check_applicable` with a `lote`) replaces "run `check_hit` on every returned hit". Route it to `spec-planner` now, before T3: one dated change-log line amending R4, design step 7 and the T2 box, citing this decision. T4's defective-stage harness uses the same wording. F2: leave the code. Note it in the T6 As-built notes with T1 F2, and add a box to T3: a unit test that fails if `check_applicable` reads any `PointPayload` field besides `document_id` and `lote_languages`."
