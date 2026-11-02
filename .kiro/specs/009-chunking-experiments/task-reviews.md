# Spec 009 — Task reviews

## T1 — round 1

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/pyproject.toml`, `uv.lock` — base deps `tokenizers`, `huggingface_hub`
  - `packages/rag/src/way2australia_rag/ingestion/tokenization.py` (new), `guard.py` (new)
  - `packages/rag/src/way2australia_rag/ingestion/config.py`, `service.py`, `cli.py`
  - `packages/rag/src/way2australia_rag/lexical/build.py`, `cli.py`, `freshness.py`
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` — `verify_fresh` / `production_entries` need tokenizer (T3 may refine standalone path)
  - `packages/rag/src/way2australia_rag/evaluation/security_index.py`, `security_eval.py`
  - Tests: `tests/ingestion/test_tokenization.py`, `test_guard.py`, `test_service.py`; `tests/lexical/test_lexical_build.py`; caller updates in lexical/retrieval/evaluation tests
  - `packages/rag/tests/ingestion/fixtures/bge_m3/` (tokenizer.json, sentence_bert_config.json)
  - `graphify-out/` (graphify update)
- Verification run:
  - `make verify` → pass (1046 passed, 2 skipped)
  - `uv tree --package way2australia-rag --no-dev` → `huggingface-hub`, `tokenizers` in base; `torch` only under optional `bge-m3` extra
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass
- Notes:
  - `IngestionService` takes `tokenizer` and optional `chunk_token_cap`; heading v1 uses cap `None`.
  - `ChunkTooLongError` reason string is `chunk_too_long: section_id=… position=… tokens=… limit=…` (no chunk text).
  - Standalone BM25 open builds tokenizer via `build_tokenizer` so freshness matches lexical build until T3’s `chunker_identity`-only path.
- Usage: n/a (Cursor) · 169 tool uses · 24:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: FAIL
- Commands: `make verify` with `HF_HOME=/tmp/w2a-t1-empty-hf`, `HF_HUB_CACHE` and `HUGGINGFACE_HUB_CACHE` under that directory, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` → fail (38 failed, 990 passed, 2 skipped, 18 errors; 1048 collected). Lint, pyright, skills-check, validate-knowledge and validate-evaluation passed before pytest. `python3 -m uv tree --package way2australia-rag --no-dev` → `huggingface-hub` and `tokenizers` are base dependencies; `torch` appears only under the `bge-m3` extra. `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4038 nodes). `make test-integration` → pass (24 passed, 1024 deselected).
- Findings: F1 [BLOCKING, IMPLEMENTATION, R1] `ingestion/cli.py`, `lexical/cli.py`, and both standalone paths in `retrieval/opening.py` call `build_tokenizer` on the config file's embedder. `config/ingestion.yaml` has `provider: bge_m3`, so `--embedder fake` and `open_retrieval(..., provider="fake")` still construct `BgeM3Tokenizer`. The fake embedder is then guarded with the BGE-M3 tokenizer, and `fake_max_sequence_length` is unused on those runs. With the Hugging Face cache hidden, `make verify` fails as above (including `test_open_retrieval_bm25_builds_no_embedder_and_no_client` and `test_success_summary_and_digest_stability`). A cache-present run can pass; this machine has the BGE tokenizer cached, which hides the dependency. → Pass `build_tokenizer` an embedder config whose `provider` is the provider selected for that run (`model_copy(update={"provider": provider})` when they differ). `provider` `fake` must yield `FakeTokenizer` and leave the hub untouched. Re-run `make verify` with `HF_HUB_OFFLINE=1` and an empty `HF_HOME`. Keeping a tokenizer on `verify_fresh` until T3 is fine when it follows that same provider.
- Findings: F2 [MAJOR, IMPLEMENTATION, R2] `test_oversized_chunk_refuses_production_entries` expects `ChunkTooLongError` from `production_entries`, then asserts `tmp_path / "lex.sqlite"` is absent. The test never writes that path, and it never calls the lexical CLI or `build_lexical_index`, so exit 2 and "no file written" are unlocked. The CLI returns 2 today because `ChunkTooLongError` is an `IngestionError` and `build_lexical_index` runs only after `production_entries`. → Drive `lexical.cli.main` with an oversized chunk, assert exit code 2, and assert the target file is absent (or unchanged if one was already there).
- Findings: F3 [MINOR, IMPLEMENTATION, R2] The new service tests check the run report for chunk text and for the chunker exception message. They do not capture logs. The service log line is the exception class name. → Assert with `caplog` that the chunk text and the chunker exception message are absent from the log.
- Usage: n/a (Cursor) · 98 tool uses · 10:00

## T1 — round 2

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/tokenization.py` — `embedder_for_run()`; callers pass run-selected provider into `build_tokenizer`
  - `packages/rag/src/way2australia_rag/ingestion/cli.py`, `lexical/cli.py`, `retrieval/opening.py` — use `embedder_for_run(config.embedder, provider)`
  - `packages/rag/tests/lexical/test_lexical_cli.py` — `test_oversized_chunk_refuses_cli_exit_2_and_writes_no_file`
  - `packages/rag/tests/lexical/test_lexical_build.py` — drop vacuous sqlite assertion from production_entries test
  - `packages/rag/tests/ingestion/test_service.py` — `caplog` on chunk-text / chunker-message tests
  - `packages/rag/tests/evaluation/test_strategy_eval.py` — `lexical_env` patches `opening.build_tokenizer` so bm25 eval tests stay hub-free while keeping bge dense identity
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-t1-empty-hf` `HF_HUB_CACHE`/`HUGGINGFACE_HUB_CACHE` under that dir, `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1047 passed, 2 skipped)
  - `uv tree --package way2australia-rag --no-dev` → `huggingface-hub`, `tokenizers` in base; `torch` only under optional `bge-m3` extra
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass
- Notes:
  - F1: `--embedder fake` / `open_retrieval(..., provider="fake")` now construct `FakeTokenizer` and never touch the hub; evaluation bm25 tests still record bge dense identity but patch tokenizer construction in `opening` only within `lexical_env` (eval CLI has no embedder override).
- Usage: n/a (Cursor) · 83 tool uses · 7:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t1-r2-hf` `HF_HUB_CACHE=/tmp/w2a-t1-r2-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t1-r2-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t1-r2-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1049 collected, 1047 passed, 2 skipped). `make test-integration` → pass (24 passed, 1025 deselected). `python3 -m uv tree --package way2australia-rag --no-dev` → `huggingface-hub` and `tokenizers` are base dependencies; `torch` appears only under the `bge-m3` extra. `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4046 nodes).
- Findings: none
- Summary for user (PASS only):
  - Changed: Chunk length is measured with a tokenizer that follows the embedder selected for that run. `--embedder fake` uses `FakeTokenizer` and does not touch the Hugging Face hub. Ingestion counts tokens after chunking and before embedding; a too-long chunk fails that document only, with section, position, token count and limit, and no chunk text in the report or logs. The lexical build uses the same guard and exits 2 without writing the file.
  - Verified by: `make verify` with `HF_HUB_OFFLINE=1` and an empty Hugging Face cache (1047 passed, 2 skipped opt-in BGE-M3 smokes); `make test-integration` (24 passed); `uv tree` shows `tokenizers` and `huggingface-hub` without `torch` in the base set.
  - Worth your attention: Standalone BM25 freshness still builds a tokenizer until T3. Evaluation tests whose config provider is `bge_m3` stub that construction so `make verify` stays offline; a real `eval-retrieval` BM25 run still needs the cached tokenizer files. The security index uses `FakeTokenizer` directly, matching its fake-embedder-only harness.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/ingestion/cli.py` → `main`: builds the tokenizer for the selected provider and passes it into ingestion.
    2. `packages/rag/src/way2australia_rag/ingestion/tokenization.py` → `embedder_for_run`, `build_tokenizer`: `fake` yields `FakeTokenizer`; `bge_m3` loads tokenizer files only.
    3. `packages/rag/src/way2australia_rag/ingestion/guard.py` → `check_chunks`: refuses the first chunk over the limit.
    4. `packages/rag/src/way2australia_rag/ingestion/service.py` → `IngestionService.run`: chunking, the guard and point IDs sit inside the per-document try.
    5. `packages/rag/src/way2australia_rag/lexical/cli.py` → `main`: same tokenizer selection; a violation exits 2 before any file is written.
    6. `packages/rag/src/way2australia_rag/lexical/build.py` → `production_entries`: runs the same guard.
    7. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`: standalone and fallback freshness follow the run's provider.
    8. `packages/rag/src/way2australia_rag/ingestion/config.py` → `EmbedderConfig.fake_max_sequence_length`.
    9. Tests: `test_tokenization.py`, `test_guard.py`, `test_service.py` (`caplog`), `test_lexical_cli.py` (exit 2, no file).
    10. Supporting edits: lexical freshness signature, security index/eval wiring, `pyproject.toml`, `uv.lock`, `graphify-out/`.
- Usage: n/a (Cursor) · 79 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved
