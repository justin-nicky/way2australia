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
