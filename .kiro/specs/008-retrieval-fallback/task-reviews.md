## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: 162K tokens · 47 tool uses · 14:12
- Files changed:
  - new `packages/rag/src/way2australia_rag/retrieval/availability.py`, `qdrant_client.py`;
  - `retrieval/errors.py` (`FallbackReason`, `RetrievalUnavailableError`), `index.py`, `retriever.py`, `strategy.py` (`QdrantTimeouts`, schema 1.1), `retrieval/cli.py`, `evaluation/cli.py`;
  - `config/retrieval.yaml` (`schema_version` and `qdrant` block only);
  - new tests `retrieval/test_availability.py`, `test_qdrant_client.py`; additions to `test_index.py`, `test_retriever.py`, `test_strategy.py`;
  - `.kiro/specs/008-retrieval-fallback/design.md` (new `## As-built notes`: Hugging Face error shapes), `tasks.md` (boxes, State).
- Verification run: `make verify` -> pass (955 passed, 2 skipped); `git diff -- config/retrieval.yaml` shows only `schema_version` and the `qdrant` block; `git status --porcelain -- evaluation knowledge config` lists only `config/retrieval.yaml`; `git diff --stat` of `ingestion/`, `hybrid.py`, `fusion.py` is empty; `graphify update .` ran. Docker integration tests were not run in this round.
- Notes:
  - Hugging Face shapes confirmed from the pinned wheels (user permission): the downloaded `pip download --no-deps --only-binary=:all: --python-version 3.12` into the scratch directory (`uv pip download` does not exist, system pip is 3.9), unzipped and read only, nothing installed or run. All four shapes and offline mode match R1; the eligible type list is unchanged. Details are in the design As-built notes.
  - `DenseIndex.open` gained an optional `query_timeout_s` (default `None`, so existing callers are unchanged); the constructor takes it too. Public `raise_if_unavailable` helper in `index.py` is shared by the four methods.
  - `retrieval_client_factory` lives in `retrieval/qdrant_client.py`; both `make retrieve` and `make eval-retrieval` default to it (`client_factory=None`); a test-supplied `client_factory` still wins. The retrieval config is now loaded before the client is built in `retrieve`, so a bad config is refused before Qdrant contact.
  - The legacy `baseline_cli.py` and the ingestion CLI still use `default_client_factory` (unchanged, per the task rules).
  - Qdrant transport errors are classified with isinstance on `httpx.TimeoutException` / `httpx.NetworkError` only; optional-package types (`requests`, `urllib3`, hub `OfflineModeIsEnabled`) are imported guarded.
  - Timeout tests use a local TCP listener thread (1 s bound, 2 s tolerance); a closed-port test covers `qdrant_unavailable`.
  - `ruff format` reformatted only files this task touched.

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`
- Usage: 147K tokens · 32 tool uses · 47:33
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright 0 errors; 955 passed, 2 skipped);
  - `make test-integration` → pass (22 passed, 935 deselected; Docker Qdrant running). A first run, chained after a broken shell redirect, hung over 14 minutes in `test_retrieval_integration.py` and was killed; that test alone then passed in 1.7 s and the full re-run passed in 27 s (see F3);
  - `make eval-security` → PASS (675 ms; result under `experiments/results/tmp/`);
  - `git diff -- config/retrieval.yaml` → only `schema_version` 1.0 → 1.1 and the `qdrant` block;
  - `git status --porcelain -- evaluation knowledge config` → only `config/retrieval.yaml`;
  - `git diff --stat` of `ingestion/`, `retrieval/hybrid.py`, `retrieval/fusion.py` → empty;
  - design `## As-built notes` → "T1: Hugging Face error shapes" present (four required shapes plus offline, local-only and hub 5xx).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R1] `test_availability.py::test_qdrant_cause_and_context_are_not_followed` asserts only the `__cause__` case; the `__context__` case is covered by `test_unrelated_error_raised_while_handling_a_network_error_is_not_eligible` → rename or add the `__context__` assertion when convenient.
  - F2 [MINOR, IMPLEMENTATION, R11] the new tests in `test_index.py` and `test_retriever.py` add imports mid-file with `# noqa: E402` → move them to the top of each module in a later touch.
  - F3 [MINOR, IMPLEMENTATION, R13] one hung `make test-integration` run (above) was not reproduced; the integration test path passes `query_timeout_s=None`, which is qdrant-client's default, so behavior there is unchanged. The killed run left the throwaway collections `w2a-it-ret-8bf72e323182-idx-v1` and `w2a-it-ret-8bf72e323182-idx-v1-settings` in the local Qdrant (not deleted by the reviewer) → watch for a recurrence; the user may delete those two collections.
- Summary for user:
  - Changed: failure classification for the coming fallback. `FallbackReason` and `RetrievalUnavailableError` (fixed, path-free messages); `availability.py` maps Qdrant transport errors (one `ResponseHandlingException.source` unwrap only) and model load errors (explicit `__cause__` chain only, at most 10 links, offline mode excluded); `DenseIndex` maps every client call and passes `timeout=query_timeout_s` to search; `DenseRetriever` wraps only `embed_query`. Config schema 1.1 with `qdrant.connect_timeout_s: 2`, `query_timeout_s: 3` (integers 1..30); new `retrieval_client_factory` (`check_compatibility=False`) used by `make retrieve` and `make eval-retrieval`. No fallback behavior yet (T4).
  - Verified by: `make verify` (955 passed), `make test-integration` (22 passed), `make eval-security` PASS, protected-path and scope checks; stalled-socket and closed-port tests prove the timeout and unavailable mappings within 1 s + 2 s.
  - Worth your attention: the Hugging Face shapes were confirmed from wheels downloaded with your permission (As-built note); an outage re-raised without `from` is not eligible (safe direction). `make retrieve` now loads the retrieval config before contacting Qdrant. Three MINOR findings, including one unreproduced integration hang and two leftover throwaway collections.
  - Reading order:
    1. `.kiro/specs/008-retrieval-fallback/design.md` → `## As-built notes`: the confirmed error shapes.
    2. `packages/rag/src/way2australia_rag/retrieval/errors.py` → `FallbackReason`, `RetrievalUnavailableError`.
    3. `packages/rag/src/way2australia_rag/retrieval/availability.py` → `classify_qdrant_error`, `classify_model_error`.
    4. `packages/rag/src/way2australia_rag/retrieval/index.py` → `raise_if_unavailable`, `DenseIndex.open`/`search`.
    5. `packages/rag/src/way2australia_rag/retrieval/retriever.py` → `DenseRetriever.retrieve` (`embed_query` wrap).
    6. `packages/rag/src/way2australia_rag/retrieval/strategy.py`, `config/retrieval.yaml` → `QdrantTimeouts`, schema 1.1.
    7. `packages/rag/src/way2australia_rag/retrieval/qdrant_client.py` → `retrieval_client_factory`; used in `retrieval/cli.py` `main` and `evaluation/cli.py` `_retrieval`.
    8. `packages/rag/tests/retrieval/test_availability.py`: the classification tables.
    9. Remaining tests: `test_index.py` (transport mapping, stalled socket, closed port), `test_retriever.py`, `test_strategy.py`, `test_qdrant_client.py`; `tasks.md` boxes.

### User decision
- 2026-10-31 — approved. Verbatim: "T1 approved. F1: accepted. The `__context__` case is covered in another test. F2: fix at commit. Move the imports in `test_index.py` and `test_retriever.py` to the top and remove the `noqa: E402` markers. F3: add a task box (planner amendment) to T3 or T4, whichever reworks retrieval opening: the retrieval integration tests must build their Qdrant clients with `retrieval_client_factory`, so a hang fails within seconds. Do not add a pytest-timeout dependency. Record the unexplained 14-minute hang in task-reviews.md as observed and not reproduced. Delete exactly these two collections and nothing else: `w2a-it-ret-8bf72e323182-idx-v1` and `w2a-it-ret-8bf72e323182-idx-v1-settings`. Then list the collections and confirm only `w2a-realcheck-idx-v1` and its settings collection remain. Commit with the `Spec-Task: 008/T1` trailer and push, then commit the graph separately. Then start T2."
- F3 record: the 14-minute hang of one `make test-integration` run in `test_retrieval_integration.py` is unexplained: observed once, not reproduced (that test alone passed in 1.7 s, the full re-run in 27 s). Follow-up: planner amendment adds a T3 box (retrieval integration tests use `retrieval_client_factory`; no `pytest-timeout`). Two leftover collections from the killed run were deleted on 2026-10-31; only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings` remain.

## T2 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: 136K tokens · 32 tool uses · 7:22
- Files changed:
  - new `packages/rag/src/way2australia_rag/retrieval/identity.py` (`IndexIdentity`, `from_settings`, `from_dense`, `expected`), `retrieval/opening.py` (`open_standalone_lexical`), `lexical/freshness.py` (`verify_fresh`);
  - `lexical/store.py` (`ChunkSetDifference`, `chunk_set_difference`, `check_identity`, `document_count`, public `chunk_identities`; `bind_to` message unchanged);
  - `ingestion/identity.py` (`embedder_identity` moved here, behavior unchanged) and `lexical/cli.py` (imports it);
  - new test `packages/rag/tests/lexical/test_lexical_standalone.py`; `design.md` As-built note; `tasks.md` boxes and State.
- Verification run: `make verify` -> pass (971 passed, 2 skipped; ruff, format and pyright clean); `git diff -- packages/rag/tests/lexical/test_lexical_bind.py` empty; `git status --porcelain -- evaluation knowledge config` empty. `make test-integration` not run (no integration-relevant change). `graphify update .` not run (the orchestrator commits the graph).
- Notes:
  - Freshness tests use a `tmp_path` copy of `knowledge/`; the edit test rewrites the manifest `sha256`/`body_sha256` so the loader accepts the edit and the digest check is what refuses.
  - "No client / no embedder" is proven by patching `QdrantClient.__init__` and `FakeEmbedder.__init__` to raise, and by checking that no torch/transformers module is imported. `open_standalone_lexical` takes no factories, as in the task signature.
  - `ingestion/identity.py` is the one edit under `ingestion/` (the task's named exception).

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`
- Usage: 121K tokens · 22 tool uses · 6:41
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, 153 files formatted, pyright clean; 971 passed, 2 skipped);
  - `make test-integration` (under a 300 s alarm; Docker Qdrant running) → pass (22 passed, 951 deselected, 16 s; no hang);
  - `git diff -- packages/rag/tests/lexical/test_lexical_bind.py` → empty;
  - `git status --porcelain -- evaluation knowledge config` → empty;
  - `git diff --stat` of `lexical/build.py`, `lexical/tokenizer.py`, `retrieval/` (tracked files), `pyproject.toml`, `packages/rag/pyproject.toml`, `uv.lock` → empty (no dependency, no edit to unchanged code); the only `ingestion/` edit is the allowed `embedder_identity` move.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R13] `graphify update .` was not run after the code change (`graphify-out/graph.json` unchanged; only cache files are untracked), against the task rule "After code changes, run `graphify update .`" → the orchestrator runs it before the separate graph commit, as after T1.
  - F2 [MINOR, IMPLEMENTATION, R4] `lexical/freshness.py` imports the private `_identity` from `lexical/build.py` (which may not be edited in this spec) → acceptable here; make it public when `build.py` is next touched. `verify_fresh` uses `asyncio.run` as the design says, so it cannot be called from inside a running event loop (a future HTTP route) → note for the route spec.
  - F3 [MINOR, IMPLEMENTATION, R3] the task box asks for a test where "a Qdrant client factory and an embedder factory raise if called"; `open_standalone_lexical` takes no factories (as its task signature says), so the test patches `QdrantClient.__init__` and `FakeEmbedder.__init__` to raise and checks no torch/transformers import → equivalent proof; no change needed.
- Summary for user:
  - Changed: a lexical file can now be opened and checked without Qdrant or the model. `IndexIdentity` (from the dense index or from configuration only); `LexicalIndex.check_identity` (dense identity, chunker fields, `hash_contract`), `document_count` under the SQL access clause and a shared `chunk_set_difference` (the `bind_to` message is unchanged); `verify_fresh` recomputes the chunk digest from the repository and refuses a stale file with counts only; `open_standalone_lexical` chains open, identity and freshness and closes the file on refusal. `embedder_identity` moved unchanged to `ingestion/identity.py`.
  - Verified by: `make verify` (971 passed), `make test-integration` (22 passed), protected-path and unchanged-code checks; new tests cover every identity field, body edit and document removal (stale), the real corpus (fresh), access-filtered counts and no client/embedder construction.
  - Worth your attention: nothing is wired into the CLIs yet (T3). Freshness reads and chunks every eligible document on each open (D060 large-corpus caveat). Three MINOR findings: graph not refreshed yet, a private import from `build.py`, and the factory test done by patching constructors.
  - Reading order:
    1. `packages/rag/src/way2australia_rag/retrieval/identity.py` → `IndexIdentity.expected`, `from_dense`.
    2. `packages/rag/src/way2australia_rag/lexical/store.py` → `chunk_set_difference`, `LexicalIndex.check_identity`, `document_count`, `bind_to` (refactor only).
    3. `packages/rag/src/way2australia_rag/lexical/freshness.py` → `verify_fresh`.
    4. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_standalone_lexical`.
    5. `packages/rag/tests/lexical/test_lexical_standalone.py`: identity, freshness, access-count and no-client tests.
    6. Supporting edits: `ingestion/identity.py` and `lexical/cli.py` (`embedder_identity` move), `design.md` As-built note, `tasks.md` boxes.


### User decision
- 2026-10-31 — approved. Verbatim: "T2 approved. F1: run `graphify update .` before the separate graph commit, as you said. F2: accept both parts, no code change. Record in the design's As-built notes: `freshness.py` imports the private `_identity` from `build.py`, because this spec doesn't edit `build.py`; `verify_fresh` uses `asyncio.run`, so it can't be called inside a running event loop. Add a T8 box: carry the `asyncio.run` limitation into the next-spec notes for the HTTP route spec (it needs an async freshness check, or a check at startup outside the loop). F3: accepted. Patching the constructors to raise, plus the no-torch/transformers import check, proves the same thing. Commit with the `Spec-Task: 008/T2` trailer and push, then commit the graph separately. Then start T3."

## T3 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: 181K tokens · 47 tool uses · 10:32
- Files changed:
  - `retrieval/bm25.py` (`BM25Retriever(identity, lexical)`; header fields from `IndexIdentity`, logic unchanged); `retrieval/strategy.py` (`build_retriever(strategy, identity, dense_index | None, embedder | None, lexical, config)`); `retrieval/opening.py` (`open_retrieval`, `OpenedRetrieval`, `EmbedderFactory`); `retrieval/cli.py` and `evaluation/cli.py` (use `open_retrieval`); `evaluation/retrieval_eval.py` (`run_retrieval_evaluation` takes `identity`, `document_count`, `embedder | None`, plus `index_settings | None`; `require_real_index(identity)`); `evaluation/security_eval.py` (passes `IndexIdentity.from_dense`); `ingestion/cli.py` (the `bge_m3` import moved into `build_embedder`'s provider branch, so no other path loads it);
  - tests: new `tests/retrieval/test_opening.py`; `test_bm25.py` (characterization test); `test_strategy_eval.py` (configured-identity `bm25` file helper, `bm25` CLI test with raising factories); `test_strategy.py`, `test_hybrid.py`, `test_retrieval_eval.py`, `dense_equivalence.py` (new signatures); `test_retrieval_integration.py` (client via `retrieval_client_factory`).
- Verification run: `make verify` -> pass (976 passed, 2 skipped; ruff, format, pyright clean); `make test-integration` (300 s alarm, Docker Qdrant) -> 22 passed, 956 deselected, 27 s; `grep -rn "QdrantClient(" packages/rag/tests/retrieval` -> only `:memory:` clients and the T1 stalled-fake helper; no dependency changes (`git diff` on the three dependency files is empty); `git status --porcelain -- evaluation knowledge config` empty. Manual: throwaway `QDRANT_COLLECTION_BASE=w2a-t008-394150fa`, `make ingest --embedder fake`, `make index-lexical`, `make retrieve ... --strategy bm25` returned 5 hits, and again with `QDRANT_URL=http://127.0.0.1:1`; collections and lexical file removed afterwards (the `w2a-realcheck` collections and its lexical file were not touched). `graphify update .` not run (the orchestrator commits the graph).
- Notes:
  - `bge_m3` import: `ingestion/cli.py` imported it at module top, so even `bm25` loaded the adapter module. It is now imported inside `build_embedder` (design R5 says it is imported only there). A subprocess test pins that importing `retrieval.opening` and `retrieval.cli` loads neither `bge_m3` nor torch/sentence_transformers.
  - `OpenedRetrieval` also carries `embedder`, `index_settings` and the lexical handle; `document_count` is a callable of the access, as in the design.
  - Result stays 2.1. For `bm25` through `eval-retrieval`, `index_settings` is `null` (Qdrant never contacted), `device` is `null`, and `format_summary` prints "n/a (Qdrant not contacted)". Consequence for later: `eval-compare` reads the embedder pair from `index_settings`, so a standalone `bm25` 2.1 file does not carry it until `dense_identity` arrives in 2.2 (T7/T8 scope).
  - The fake-embedder refusal still happens when the embedder is built (the CLI wraps its factory), before any Qdrant contact; for `bm25` a fake configured provider is refused by `require_real_index(identity)`.
  - `eval-retrieval --strategy bm25` now needs a lexical file built with the configured (real) dense identity from the real repository; the CLI tests build one.
  - `eval-security` still builds `bm25` from the dense fixture identity; its move to the standalone path is T-later (R10).

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`
- Usage: 163K tokens · 32 tool uses · 7:59
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright clean; 976 passed, 2 skipped);
  - `make test-integration` (under a 300 s perl alarm; Docker Qdrant running) → pass (22 passed, 956 deselected, 23 s; no hang);
  - `grep -rn "QdrantClient(" packages/rag/tests/retrieval` → only `:memory:` clients plus the T1 stalled-fake helper `http_client` in `test_index.py`; `test_retrieval_integration.py` now uses `retrieval_client_factory`;
  - `git diff --stat -- pyproject.toml packages/rag/pyproject.toml uv.lock` → empty (no dependency);
  - `git status --porcelain -- evaluation knowledge config` → empty;
  - `git diff --stat HEAD` of `ingestion/`, `lexical/`, `retrieval/{hybrid,fusion,access,baseline,baseline_cli}.py`, `test_legacy_baseline_snapshot.py`, `test_lexical_bind.py` → only `ingestion/cli.py` (see F1);
  - manual, throwaway base `w2a-t008-2880c013` with `W2A_LEXICAL_INDEX_DIR` in a scratch directory: `make ingest INGEST_ARGS="--embedder fake"` (added 13), `make index-lexical LEXICAL_ARGS="--embedder fake"` (13 chunks, digest `6045203bfeec`), `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --strategy bm25"` → 5 hits, exit 0; the same with `QDRANT_URL=http://127.0.0.1:1` → the same 5 hits, exit 0; controls: `--strategy hybrid` with Qdrant up → 5 hits; `--strategy dense` on the closed port → exit 2, `RetrievalUnavailableError ... (qdrant_unavailable)`, no URL. Both throwaway collections and the lexical file deleted; only `w2a-realcheck-idx-v1` and its settings collection remain.
- Findings:
  - F1 [MINOR, SPEC_DEFECT, R5/R13] `ingestion/cli.py` moves the `bge_m3` import from module top into `build_embedder`'s non-fake branch. The tasks rule ("`ingestion/` ... not edited") and the design's "Not changed" list (which names `ingestion/cli.py`) forbid it, but design R5 requires "`bge_m3` is imported only inside `build_embedder`'s provider branch, which a test pins"; before T3 the import was at module top, so R5 cannot hold without this edit (the CLIs import `ingestion.cli` for `ClientFactory`). The edit is a 4-line move with no behavior change: `bge_m3` itself imports only light modules and loads `sentence_transformers` lazily, nothing patches `ingestion.cli.BgeM3Embedder`, and ingestion tests pass. Judgment: accept; the alternative (a second `build_embedder` under `retrieval/`) would be worse → record in the design As-built notes (T8) that `ingestion/cli.py` had this one edit, and correct the "Not changed" list.
  - F2 [MINOR, IMPLEMENTATION, R8/R13] the extra optional `index_settings: IndexSettings | None = None` on `run_retrieval_evaluation`. Judgment: needed and accepted. `IndexIdentity` (T2) carries only six fields, so the task's "an `index_settings` value unchanged when the dense side is bound" can only be met by passing the full `IndexSettings`; the dense-equivalence fixture and the 2.1 CLI tests pass with byte-equal values. Risk: with a `None` default, a future caller that forgets it on a `dense`/`hybrid` run writes `"index_settings": null` silently → make it a required keyword (no default), or refuse `None` when the strategy is not `bm25`; record it in the design's interface list (T8).
  - F3 [MINOR, IMPLEMENTATION, R5] interim consequence of F2: a standalone `bm25` 2.1 file has `index_settings: null`, so `read_result` gives an embedder pair `(None, None)` and `eval-compare` refuses it against any Spec 007 `bm25`/`hybrid` file ("embedder changed ..."). This fails safe (refusal, never a wrong PASS) and R9 (T5) moves the pair to `dense_identity` → T5 must cover a standalone `bm25` result in its compare tests.
  - F4 [MINOR, IMPLEMENTATION, R13] two new tests assert the live corpus count: `test_opening.py` (`opened.document_count(access) == 13`) and `test_strategy_eval.py::test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder` (`doc["document_count"] == 13`), against the tasks rule "No live-count literals in new tests" → derive the count from the entries the fixture builds (distinct `document_id` of `production_entries`).
  - F5 [MINOR, IMPLEMENTATION, R13] `graphify update .` not run after the code change (cache files only) → the orchestrator runs it before the separate graph commit, as after T1 and T2.
- Summary for user:
  - Changed: one open path, `open_retrieval` (`retrieval/opening.py`), now serves `make retrieve` and `make eval-retrieval`. `bm25` opens the lexical file standalone (identity from config, freshness from the repository) with no embedder, no Qdrant client and no `bge_m3` import; `dense` and `hybrid` open as before (no fallback yet). `BM25Retriever` and `build_retriever` take an `IndexIdentity`; `run_retrieval_evaluation` takes `identity`, `document_count`, an optional embedder and the full `index_settings`. Retrieval integration tests use `retrieval_client_factory`.
  - Verified by: `make verify` (976 passed, 2 skipped), `make test-integration` (22 passed, 23 s), grep/dependency/protected-path checks, and a throwaway fake-embedder run where `--strategy bm25` returned the same 5 hits with Qdrant up and with `QDRANT_URL` on a closed port.
  - Worth your attention: the `bge_m3` import moved inside `build_embedder` in `ingestion/cli.py` (an `ingestion/` edit the spec forbids but design R5 needs; accepted, F1). The optional `index_settings` parameter is justified but should lose its `None` default (F2). A `bm25` eval file now has `index_settings: null` and is refused by `eval-compare` until T5 (F3). `eval-retrieval --strategy bm25` now checks the lexical file against `config/ingestion.yaml` rather than the live Qdrant index. Two tests hard-code 13 documents (F4).
  - Reading order:
    1. `packages/rag/src/way2australia_rag/retrieval/cli.py` → `main`: now calls `open_retrieval` and closes `opened`.
    2. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`, `OpenedRetrieval`: the `bm25` standalone branch, then the `dense`/`hybrid` branch.
    3. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `build_retriever`: identity parameter, `bm25` needs no dense side.
    4. `packages/rag/src/way2australia_rag/retrieval/bm25.py` → `BM25Retriever.__init__`, `retrieve` header fields.
    5. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval`, `format_summary` (null `index_settings`).
    6. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation`, `require_real_index`.
    7. `packages/rag/src/way2australia_rag/ingestion/cli.py` → `build_embedder` (lazy `bge_m3` import).
    8. `packages/rag/tests/retrieval/test_opening.py`: no embedder, no client, no `bge_m3` import (subprocess check).
    9. `packages/rag/tests/retrieval/test_bm25.py` → `test_standalone_path_returns_the_hits_of_the_spec_007_construction`; `test_strategy_eval.py` → `test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder`.
    10. Supporting edits: signature updates in `test_strategy.py`, `test_hybrid.py`, `test_retrieval_eval.py`, `dense_equivalence.py`, `security_eval.py`; `test_retrieval_integration.py` client factory; `tasks.md` boxes.

### User decision
- 2026-10-31 — approved. Verbatim: "T3 approved. F1: T8 box. Add a design As-built note on the `bge_m3` import move in `ingestion/cli.py` (required by R5) and correct the "Not changed" list. F2: T5 box (T5 rewrites `run_retrieval_evaluation` anyway): refuse `index_settings=None` for any strategy other than `bm25`, with a test, and record it in the design. F3: T5 box, explicit: a standalone `bm25` result (no Qdrant) must compare against the Spec 007 BM25 reference (`…20261028T123109Z.json`) through `dense_identity`. T7 depends on this. Add a test that compares a standalone bm25 fixture against a 2.1 bm25 fixture. F4: fix at commit. In `test_opening.py` and `test_strategy_eval.py::test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder`, replace `13` with a count derived from the repository's eligible documents. F5: run `graphify update .` before the graph commit. Commit with the `Spec-Task: 008/T3` trailer and push, then commit the graph separately. Then start T4."
