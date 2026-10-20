# Task Reviews — 005 Dense Retrieval Baseline

Append-only, newest at the bottom.

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Files changed: `Makefile`; `packages/rag/src/way2australia_rag/ingestion/store.py`; `packages/rag/tests/ingestion/test_store.py`; `packages/rag/tests/ingestion/test_store_integration.py`; `packages/rag/tests/test_content_hash.py` (ruff format only); `packages/rag/tests/test_date_and_policy.py`; `.kiro/specs/005-dense-retrieval-baseline/tasks.md` (State, checkboxes)
- Verification run: `make lint` (incl. `ruff format --check`) → pass; `make typecheck` → pass (0 errors); `make test-unit` → pass (303 passed, 1 skipped); `make test-integration` against real Docker Qdrant → pass (18 passed, includes 3 new tests); `make verify` → pass (321 passed, 1 skipped, Qdrant was up so integration ran); `make -n setup-bge-m3` shows `UV_HTTP_TIMEOUT=300`, `UV_HTTP_TIMEOUT=600 make -n setup-bge-m3` shows 600
- Notes: `_ensure_payload_indexes()` extracted and called on creation and on the "exists, empty, no settings" row, before `_write_settings`. New unit test uses a `MagicMock(wraps=QdrantClient(":memory:"))` spy. Integration tests assert keyword payload_schema, dense size/Cosine, F4 re-creation after dropping indexes, and repeated `create_payload_index` harmless. Scope check in `test_date_and_policy.py` is now `named == members`. Qdrant container was already running when started; I stopped it afterwards. Collections `w2a-realcheck-idx-v1` (+`-settings`) already existed in the Qdrant volume from the user's earlier Spec 004 manual check; not created by me and left untouched. My test collections were removed by fixtures.
- Usage: 83K tokens · 14 tool uses · 1:27
### Review
- Model: claude-opus-5-5 (matches the BEST tier, Claude Code `Opus`; different model from the implementer)
- Verdict: PASS
- Commands:
  - `make verify` (Qdrant down, no `bge-m3` group: `sentence_transformers` not importable) → pass, exit 0 (316 passed, 6 skipped);
  - `docker compose up -d qdrant`; `make test-integration` → pass (18 passed, 304 deselected), including the 3 new tests `test_collection_has_keyword_indexes_and_cosine_dense_vector`, `test_empty_without_settings_recreates_dropped_indexes`, `test_repeated_create_payload_index_is_harmless`;
  - `make verify` with Qdrant up → pass (321 passed, 1 skipped);
  - `make lint` → pass (`ruff check` all passed; `ruff format --check apps packages tests scripts`: 56 files already formatted). Negative check: `make lint PYTHON_TARGETS=<scratch dir with one unformatted file>` → `1 file would be reformatted`, `make: *** [lint] Error 1`;
  - `make -n setup-bge-m3` → `UV_HTTP_TIMEOUT=300 ... uv sync ... --extra bge-m3`; `UV_HTTP_TIMEOUT=600 make -n setup-bge-m3` → `UV_HTTP_TIMEOUT=600 ...`;
  - `pytest packages/rag/tests/ingestion/test_store.py::test_empty_without_settings_recreates_payload_indexes` → 1 passed;
  - `git status --porcelain -- evaluation/ knowledge/ config/` → empty;
  - Qdrant collections before and after the Docker runs: only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings` (untouched; test collections removed by fixtures, nothing to clean up); `docker compose stop qdrant` done. Real-model smoke test not run (user-owned).
- Checks:
  - `store.py`: the index loop moved verbatim into `_ensure_payload_indexes()`, called on creation and on the "exists, empty, no settings" row, both before `_write_settings`; the other rows (settings match/mismatch, points without settings) are unchanged. No change to `PointPayload`, point IDs, `IndexSettings`, `INGESTION_NAMESPACE`, `KEYWORD_INDEX_FIELDS` or `index_version`, so existing `idx-v1` collections stay valid (settings comparison unaffected).
  - Spy unit test is real: after `reset_mock()`, removing the F4-row call would yield `[]` and fail `fields == list(KEYWORD_INDEX_FIELDS)`.
  - Docker tests are real: keyword `data_type` asserted for every `KEYWORD_INDEX_FIELDS` entry; `dense` size equals `embedder_vector_size` and distance `COSINE`; the F4 test first asserts all keyword indexes are gone, then that they are back; unique `w2a-it-<hex>` base, cleanup in `finally`, `integration` marker, skip when unreachable.
  - Two-way scope check: `named == members` fails on a member without config entry or a config scope without member. `config/access_policy.yaml` unchanged.
  - `test_content_hash.py`: whitespace-only reflow of one dict comprehension (`git diff -w` shows identical tokens); behavior-neutral.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R9] No test asserts the ordering "payload indexes before `_write_settings`" on the F4 row (verified by reading `store.py` only) → optionally assert call order on the spy in a later task.
  - F2 [MINOR, IMPLEMENTATION, R9] `test_repeated_create_payload_index_is_harmless` calls the client directly rather than calling `ensure_collection`'s index path twice; it covers the server behavior the task names but not the store method → acceptable as is.
- Summary for user (PASS only):
  - Changed: `ingestion/store.py` now re-creates the keyword payload indexes when a collection exists, is empty and has no recorded settings (Spec 004 T6 F4); `Makefile` `lint` also runs `ruff format --check`, and `setup-bge-m3` passes `UV_HTTP_TIMEOUT` (default 300, overridable); the scope-vs-config test is two-way; `test_content_hash.py` reformatted only.
  - Verified by: `make verify` with and without Docker Qdrant (316/6 skipped; 321/1 skipped), `make test-integration` (18 passed incl. 3 new server-side layout tests), a negative `make lint` run, `make -n setup-bge-m3` with and without the env var.
  - Worth your attention: no payload, identity, settings or `index_version` change, so your `w2a-realcheck-idx-v1` index stays valid (left untouched). `make lint` will now fail on any unformatted file. Two MINOR test-coverage notes (F1, F2).
- Usage: 88K tokens · 17 tool uses · 2:18

### User decision
- 2026-10-20 — approved. Verbatim: "Approved T1. F1: add an assertion on the spy's recorded call order (payload indexes before `_write_settings` on the empty-no-settings row) in T7's final pass; that order is the fix itself. F2: no change."
