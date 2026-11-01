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

## T4 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: 136K tokens · 24 tool uses · 7:33
- Files changed:
  - new `retrieval/fallback.py` (`FallbackRetriever(primary | None, fallback, open_reason)`: one `except RetrievalUnavailableError`, same `access` and `top_k`, latency includes the failed attempt with `leg_latency_ms.dense_attempt`, no state);
  - `retrieval/models.py` (`requested_strategy`, `fallback_reason`); `bm25.py` and `retriever.py` set `requested_strategy`; `strategy.py` (`build_retriever` wraps `hybrid` in `FallbackRetriever`); `opening.py` (hybrid open-time fallback via `_open_fallback` and `open_standalone_lexical`; `dense` and `bm25` unchanged; a missing extra and every other error raised); `retrieval/cli.py` (fallback header line and stderr `WARNING`);
  - tests: new `tests/retrieval/test_fallback.py` (21 tests); `test_strategy.py` (hybrid is now a `FallbackRetriever`).
- Verification run: `make verify` -> pass (997 passed, 2 skipped; ruff, format, pyright clean); `make test-integration` (300 s alarm, Docker Qdrant) -> 22 passed, 23 s; `git diff --stat` on `fusion.py` and `hybrid.py` empty; `git status --porcelain -- evaluation knowledge config` empty. Manual, throwaway `QDRANT_COLLECTION_BASE=w2a-t008-f75e77fb` and a temporary lexical dir: default `make retrieve` hybrid returned 5 hits (`strategy=hybrid`); with `QDRANT_URL=http://127.0.0.1:1` it printed `strategy: bm25 (requested: hybrid; fallback: qdrant_unavailable)` plus the stderr WARNING, exit 0; with `--strategy dense` it printed `ERROR RetrievalUnavailableError: the vector store is unavailable (qdrant_unavailable).`, exit 2. Both throwaway collections and the lexical dir were deleted. `graphify update .` not run (orchestrator).
- Notes:
  - `HybridRetriever` is unchanged (task requires it), so `requested_strategy` for a non-degraded hybrid result is set by the `FallbackRetriever` wrapper; a bare `HybridRetriever` leaves it `None`.
  - Header: the extra `strategy: ... (requested: ...; fallback: ...)` line is printed only on fallback (first line). A normal result keeps the existing `hits: N (strategy=hybrid, ...)` line so existing output and tests are unchanged; the task's "prints `strategy: hybrid`" is met by that `strategy=hybrid` text.
  - `bind_to` in this code base is file-only (no Qdrant scroll), so the open-time fallback triggers from client creation and `DenseIndex.open`; `open_bound_lexical` sits in the same `try` so a future scroll would be covered.
  - The failed client is closed best effort before the fallback opens.
  - Stalled-fake test uses a client with a 1 s timeout plus `QdrantTimeouts(1, 1)` through `open_retrieval`; it serves BM25 with `qdrant_timeout` in under 4 s.

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`
- Usage: 156K tokens · 37 tool uses · 11:28
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright 0 errors; 997 passed, 2 skipped);
  - `make test-integration` (under a 300 s perl alarm; Docker Qdrant running) → pass (22 passed, 977 deselected, 24.6 s; no hang);
  - `.venv/bin/python -m pytest packages/rag/tests/retrieval/test_fallback.py --durations=5` → 21 passed; stalled-fake test 1.06 s;
  - `git diff --stat -- .../retrieval/fusion.py .../retrieval/hybrid.py packages/rag/src/way2australia_rag/ingestion` → empty;
  - `git status --porcelain -- evaluation knowledge config experiments` → empty;
  - manual, throwaway base `w2a-t008-891e5eba` with `W2A_LEXICAL_INDEX_DIR` in a scratch directory: `make ingest INGEST_ARGS="--embedder fake"` (added 13), `make index-lexical LEXICAL_ARGS="--embedder fake"` (13 chunks, digest `6045203bfeec`); `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake"` (default strategy) → `hits: 5 (strategy=hybrid, ...)` with leg ranks, exit 0; the same with `QDRANT_URL=http://127.0.0.1:1` → stderr `WARNING retrieval fell back to bm25: qdrant_unavailable`, first stdout line `strategy: bm25 (requested: hybrid; fallback: qdrant_unavailable)`, 5 BM25 hits, exit 0; with `--strategy dense` on the closed port → `ERROR RetrievalUnavailableError: the vector store is unavailable (qdrant_unavailable).`, exit 2, no URL. Both throwaway collections and the lexical directory deleted; only `w2a-realcheck-idx-v1` and its settings collection remain.
- Focus checks:
  - Authorization on the fallback path: `FallbackRetriever` passes the caller's `access` object and `top_k` unchanged to the fallback (`test_every_reason_falls_back_with_the_same_access_and_top_k` asserts identity with `is`); the fallback is the plain `BM25Retriever`, which keeps the SQL access clause and `check_hit` (unchanged). The open-time fallback opens the lexical file only through `open_standalone_lexical` (identity and freshness checks), never a wider store. No widening found.
  - Only `RetrievalUnavailableError` triggers a fallback: one `except` in `fallback.py`; in `opening.py` one `except RetrievalUnavailableError` that re-raises for `dense`; the embedder factory (missing extra) stays outside the `try`; `IndexBindingError` at open with Qdrant up still exits 2 on the default (hybrid) strategy (`test_cli.py::test_missing_collection_exits_2`). Configuration, model-ID, generic, authorization (either leg) and BM25 errors are raised (tests). Accepted.
  - Deviation, `strategy:` line only on fallback: R7 asks that the served strategy and the reason be printed when they differ; design R7 shows the header only for the fallback case. A normal run keeps the existing `hits: N (strategy=hybrid, ...)` line, so existing output and tests are unchanged and the T4 verification's "prints `strategy: hybrid`" is met in substance. Accepted (F4).
  - Deviation, `requested_strategy` set by the wrapper for normal hybrid results: required because `hybrid.py` must not change; every production `hybrid` comes from `build_retriever`, so it is always wrapped, and no source code reads the field except the CLI. Accepted (F4).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R11] `test_cli.py::test_unreachable_qdrant_prints_class_name_only` runs the default strategy (now `hybrid`) against `127.0.0.1:1`, so it now exercises the fallback and exits 2 only because the ambient lexical directory has no fake-identity file for `way2australia-idx-v1` (it prints `LexicalIndexBindingError ... does not exist`, checked by hand). A developer who once ran `make index-lexical LEXICAL_ARGS="--embedder fake"` without a collection base would see it exit 0 and fail → pass `--strategy dense` (and assert `RetrievalUnavailableError` and `qdrant_unavailable`), or point `W2A_LEXICAL_INDEX_DIR` at an empty `tmp_path`.
  - F2 [MINOR, IMPLEMENTATION, R2/R13] `test_stalled_qdrant_through_open_retrieval_serves_bm25_within_the_bound` asserts `< 1 + 3` s, above the tasks rule "1 s timeouts with a tolerance of at most 2 s" (it measures 1.06 s). The stall also fires at open time, so the per-query `query_timeout_s` path through `open_retrieval` (successful open, then a stalled search) is not exercised end to end; it is covered by T1's `DenseIndex.search` stall test plus the wrapper unit tests → tighten the bound to `1 + 2`; optionally note in the test docstring that this is the open-time stall.
  - F3 [MINOR, IMPLEMENTATION, R1/R6] the missing-revision and missing-model-ID cases are tested on the wrapper with stand-in exceptions (`RetrievalConfigurationError`, a plain `OSError`), not as `DenseRetriever` with an embedder raising the real cause chains inside `FallbackRetriever` (as the network case is). The composition holds (T1's `test_retriever.py` shows those chains are not mapped; the wrapper catches only `RetrievalUnavailableError`) → optionally add the two chains to `test_a_model_load_failure_with_a_network_cause_falls_back`'s pattern.
  - F4 [MINOR, IMPLEMENTATION, R7] the two accepted deviations above (header only on fallback; `requested_strategy` set by `FallbackRetriever`, `None` from a bare `HybridRetriever`) and the `fallback` parameter typed `Retriever` rather than `BM25Retriever` → record them in the design As-built notes (T8).
  - F5 [MINOR, IMPLEMENTATION, R13] `graphify update .` not run after the code change (cache files only) → the orchestrator runs it before the separate graph commit, as after T1–T3.
- Summary for user:
  - Changed: new `retrieval/fallback.py` (`FallbackRetriever`): on `RetrievalUnavailableError` from the hybrid primary it serves the same query through `BM25Retriever` with the same `access` and `top_k`, marks `requested_strategy`/`fallback_reason`, and records `dense_attempt` latency; no state between queries. `build_retriever` wraps `hybrid` in it. `open_retrieval` falls back at open time for `hybrid` only (standalone lexical open); `dense` still raises. `RetrievalResult` gains the two fields; `make retrieve` prints a `strategy: bm25 (requested: hybrid; fallback: <reason>)` first line plus a stderr `WARNING`, exit 0.
  - Verified by: `make verify` (997 passed, 2 skipped), `make test-integration` (22 passed), 21 new tests in `test_fallback.py` (closed port, stalled port, per-query failure, non-eligible errors, same access object, hits equal `bm25`), and a throwaway fake-embedder run: normal hybrid, closed-port fallback header, `--strategy dense` exit 2.
  - Worth your attention: the `strategy:` line appears only on fallback, a normal run keeps `hits: N (strategy=hybrid, ...)` (accepted, F4). Until T5, an `eval-retrieval` run with Qdrant down would write a 2.1 file that says `retrieval_strategy: hybrid` but holds BM25 results, so do not run real evaluations with Qdrant down before T5. One older CLI test now passes for a different reason and depends on the local lexical directory (F1); the stalled-port timing bound is 3 s instead of 2 s (F2).
  - Reading order:
    1. `packages/rag/src/way2australia_rag/retrieval/cli.py` → `main`, `format_result`, `_strategy_line`: the fallback header and stderr warning.
    2. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval` (the `try`/`except RetrievalUnavailableError`), `_open_fallback`, `_close_quietly`.
    3. `packages/rag/src/way2australia_rag/retrieval/fallback.py` → `FallbackRetriever.retrieve`: the single `except`, marking and latency.
    4. `packages/rag/src/way2australia_rag/retrieval/strategy.py` → `build_retriever`: `hybrid` wrapped.
    5. `packages/rag/src/way2australia_rag/retrieval/models.py` → `RetrievalResult.requested_strategy`, `fallback_reason`.
    6. `packages/rag/tests/retrieval/test_fallback.py`: wrapper unit tests, then closed-port, stalled-port and CLI tests.
    7. Supporting edits: `requested_strategy` in `bm25.py` and `retriever.py`; `test_strategy.py` (hybrid is a `FallbackRetriever`); `tasks.md` boxes.

### User decision
- 2026-10-31 — approved. Verbatim: "T4 approved. F1: fix at commit. Pin `test_unreachable_qdrant_prints_class_name_only` to `--strategy dense`. F2: fix at commit. Cap the stalled-port test's tolerance at 2 s, as the tasks rule says. The per-query path is covered by T1 and the wrapper tests; accepted. F3: accepted. T1's tests show those cause chains aren't mapped, so they fail closed. F4: T8 box (design As-built notes: header line only on fallback, `requested_strategy` set by `FallbackRetriever`, `fallback` typed `Retriever`). New T8 box (planner amendment): `open_retrieval` closes the Qdrant client on every open failure, not only on the fallback path, and `OpenedRetrieval.close()` closes the client too. Add a test. If T8 shouldn't carry code, record it in the next-spec notes for the HTTP route spec instead. Commit with the `Spec-Task: 008/T4` trailer and push, then commit the graph separately. Then start T5."

## T5 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: 190K tokens · 62 tool uses · 615:44 (wall clock includes a machine sleep or clock change; not a work time)
- Files changed:
  - `evaluation/retrieval_eval.py`: result 2.2 (`requested_strategy`, `served_strategies`, `retrieval_strategy`/`score_kind` null when mixed, `fallback_counts`, `warmup_fallback_reason`, `qdrant_timeouts`, `dense_identity`, per-case `served_strategy`/`fallback_reason`, `unanswerable.served_strategies`, `latency_ms.by_served_path` with `p50`/`p95` null when more than one path, `fusion` when any case was served by hybrid, `lexical_index` whenever opened, dense leg of a fallback case `null` in `leg_ranks`); new `qdrant_timeouts` parameter; `index_settings=None` refused for any served strategy other than `bm25` (checked after the warm-up and over all measured cases); `unanswerable_report` now takes the per-case results;
  - `evaluation/cli.py`: summary prints requested and served strategies, fallback counts and latency per path; passes `retrieval_config.qdrant` (not for `bm25`);
  - `evaluation/results.py`: reads 2.2 (2.0 and 2.1 unchanged); served strategy from `served_strategies`; mixed file refused with per-strategy counts; embedder pair from `dense_identity` when `index_settings` is null; lexical-object rule by served strategy;
  - `evaluation/compare.py`: latency lines labelled for fallback paths; requested-vs-served identity line;
  - tests: `test_retrieval_eval.py` (2.2 keys, fully-fallback, mixed, `index_settings=None` refusal and acceptance), `test_compare.py` (2.2 fixtures: standalone `bm25` vs 2.1 `bm25` accepted and gated, embedder revision difference refused, mixed refused, fallback latency label, committed Spec 007 BM25 reference vs a standalone 2.2 candidate), `test_strategy_eval.py` and `dense_equivalence` assertions (no-fallback 2.2 equals the 2.1 metrics, ranks and leg ranks; version strings 2.1 to 2.2); `tasks.md` boxes.
- Verification run: `make verify` -> pass (1011 passed, 2 skipped, with the Docker Qdrant integration tests; ruff, format, pyright clean); `make eval-compare BASE=...T123109Z.json CANDIDATE=...T123121Z.json` -> runs, PASS (hits 64 -> 68, MRR 0.7082 -> 0.9094), no refusal; `git status --porcelain -- evaluation knowledge config` empty; no dependency changes. No real BGE-M3 run and no real evaluation run. `graphify update .` not run (orchestrator).
- Notes:
  - Existing tests changed only in version strings and the added 2.2 keys (`served_strategy`, `fallback_reason`, `served_strategies`); ranks, scores and ordering assertions are unchanged.
  - `served_strategies` and `fallback_counts` span goldens and unanswerable cases (warm-up excluded); per-case `served_strategy` is on the golden rows only.
  - A mixed file is refused at read time (`read_result`), with the message `not comparable: <label> file '<name>' mixes served strategies (bm25: 3, hybrid: 78); re-run when the system is stable.`
  - The real fallback-only vs Spec 007 BM25 reference comparison needs the T7 user run; here it is covered by a fixture derived from the committed reference file.

### Review
- Model: claude-opus-5-5 (Opus 5.5); intended tier BEST (Claude Code `Opus`) matches
- Usage: 155K tokens · 30 tool uses · 20:51
- Verdict: PASS
- Commands: `make verify` → pass (ruff, format, pyright 0 errors, skills-check, validate-knowledge, validate-evaluation; 1011 passed, 2 skipped, Docker Qdrant reachable so the integration tests ran inside it); targeted `pytest -k "standalone or index_settings_none or 2_2 or mixed or fallback or dense_identity"` on `test_compare.py` and `test_retrieval_eval.py` → 13 passed (includes the standalone-`bm25`-vs-2.1-`bm25` test and the `index_settings=None` refusal test); `make eval-compare BASE=…20261028T123109Z.json CANDIDATE=…20261028T123121Z.json` → runs, PASS (hits 64 -> 68, MRR 0.7082 -> 0.9094), exit 0, no refusal; `make eval-retrieval` with a scratch copy of `config/ingestion.yaml` whose provider is `fake` (`--strategy hybrid` and `--strategy dense`, throwaway `QDRANT_COLLECTION_BASE=w2a-t008-revt5a1`, `--output experiments/results/tmp/…`) → refused exit 2 "the configured embedder is fake" before any Qdrant contact, as before; no file written, no collection created (only `w2a-realcheck-idx-v1` and its `-settings` remain); `git status --porcelain -- evaluation knowledge config` → empty. Scratch probe (outside the repo): a 2.2 file derived from the committed BM25 reference with `served_strategies: [bm25, hybrid]` and all golden rows `bm25` → refused (see F1). No real BGE-M3 run, no real evaluation.
- Checks: 2.2 keys match design R8 table (`requested_strategy`, `served_strategies`, `retrieval_strategy`/`score_kind` null when mixed, `fallback_counts`, `warmup_fallback_reason`, `qdrant_timeouts` null for `bm25`, `dense_identity`, `index_settings` null only when Qdrant never reached, per-case `served_strategy`/`fallback_reason`, `unanswerable.served_strategies` with distributions null when mixed, `latency_ms.by_served_path` with top-level p50/p95 null on more than one path, `fusion` when any case served by hybrid, `lexical_index` whenever opened, dense leg `null` in `leg_ranks` of a fallback case). `index_settings=None` is refused after the warm-up and again over all measured cases unless only `bm25` served. `read_result`: 1.0/2.0/2.1 paths unchanged (`dense_identity` read only for 2.2; `settings.get(key, identity.get(key))` falls back only when `index_settings` lacks the key); mixed 2.2 refused at read time (exit 2); lexical-object rule by served strategy; D054 identity refusals unchanged and fed from `dense_identity` for a standalone file. Existing tests change only in version strings and the added keys; no rank, score or ordering assertion changed. Code changed and `graphify update .` is left to the orchestrator (graph cache files present).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R9] The mixed-file refusal counts strategies over golden case rows only; unanswerable rows carry no `served_strategy`. When only unanswerable cases were served differently, the file is correctly refused but the message names one strategy, e.g. `mixes served strategies (bm25: 69)` (probe above), which contradicts "mixes". → Count over goldens and unanswerable cases (add `served_strategy`/`fallback_reason` to unanswerable rows, or append the `served_strategies` set to the message), with a test.
  - F2 [MINOR, IMPLEMENTATION, R8] Test names now describe the wrong version: `test_a_2_1_file_reads_with_strategy_and_lexical` reads a freshly written 2.2 file; also `test_dense_2_1_equals_the_pre_change_2_0_result`, `test_2_1_keys_for_each_strategy`, `test_eval_cli_writes_a_2_1_result_without_text`. 2.1 reading is still covered (`doc21` fixtures in `test_compare.py`, the committed Spec 007 BM25 file). → Rename to 2.2.
  - F3 [MINOR, IMPLEMENTATION, R9] `compare` prints the requested-vs-served identity line only when they differ; design R9 says identity lines show requested and served strategy. Behaviour is reasonable. → Either always print both, or record "only when they differ" in the design As-built notes (T8).
- Summary for user (PASS only):
  - Changed: `make eval-retrieval` writes result 2.2 (served strategy per case, fallback counts, Qdrant timeouts, `dense_identity`, latency per served path; single-strategy and p50/p95 fields `null` when mixed). `eval-compare` reads 2.2 by served strategy, refuses mixed files, takes the embedder pair from `dense_identity` when `index_settings` is `null`, and labels fallback latency. `index_settings=None` is refused unless every case was served by `bm25`.
  - Verified by: `make verify` (1011 passed, 2 skipped), the targeted 2.2 tests, the committed BM25-vs-hybrid compare (still PASS, exit 0), the fake-embedder refusal (exit 2, unchanged), protected paths clean.
  - Worth your attention: three MINOR findings (F1 mixed-refusal message counts goldens only; F2 stale `2_1` test names; F3 requested/served identity line printed only when they differ). The real standalone-vs-reference comparison is still the T7 user run; here it is covered by a fixture built from the committed reference.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval`, `format_summary`: passes `qdrant_timeouts`, prints requested/served, fallbacks, per-path latency.
    2. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation`: 2.2 keys, `_require_settings_if_dense_served`, `_latency_by_path`, `unanswerable_report`.
    3. `packages/rag/src/way2australia_rag/evaluation/results.py` → `_build_run`, `_served_strategy`: 2.2 reading, mixed refusal, embedder pair from `dense_identity`.
    4. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `_latency_note`, requested/served identity line.
    5. `packages/rag/tests/evaluation/test_retrieval_eval.py`: `Scripted` retriever, fully-fallback, mixed, `index_settings=None` tests.
    6. `packages/rag/tests/evaluation/test_compare.py`: `doc22` fixtures, standalone `bm25` vs 2.1 `bm25`, committed reference test.
    7. Supporting edits: `test_strategy_eval.py` (version strings, 2.2 no-fallback assertions), `tasks.md` boxes.

### User decision
- 2026-11-01 — approved. Verbatim: "T5 approved. F1: fix at commit. Include the `served_strategies` set in the mixed-file refusal message, so it's correct when only unanswerable cases differ. Add a test with mixed unanswerable cases only. F2: fix at commit. Rename the four tests from 2.1 to 2.2. F3: keep the code (print requested vs served only when they differ). T8 box: record it in the design As-built notes. Commit with the `Spec-Task: 008/T5` trailer and push, then commit the graph separately. Then start T6."

## T6 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Usage: not measured (subagent ended with an API error after finishing; the repository state was complete)
- Files changed:
  - `evaluation/security_eval.py`: five gated paths (`dense`, `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`) through `_retrievers`; harness-only `_UnavailableDense`; `run_security_evaluation(..., paths=PATHS)` replaces the `strategies` parameter; `SecurityReport.paths` (`strategies` is now derived from it); violations carry `path` and still `strategy`; a fallback path that does not serve BM25 with `qdrant_unavailable` is an `EvaluationHarnessError` (vacuous gate); security result `1.2` (`paths` added, `strategies` still written, `access.role` stays `guest`);
  - `evaluation/security_index.py`: `SecurityIndex` also carries the `chunker` and `seed_repository` that built the index (needed for the standalone-open check);
  - `evaluation/cli.py`: summary prints a `paths:` line and `VIOLATION path <path> case ...`;
  - tests: `test_security_eval.py` (every path gated per query at `top_k` 50, a forbidden hit injected into each path fails the gate and names the path, dropped lexical clause names the four lexical paths, a fallback that does not fall back is a harness error, `bm25` built with no dense index or embedder, standalone-open refusal, `_UnavailableDense` not referenced from `retrieval/`, result 1.2 keys, existing 1.1 assertions moved to 1.2); `test_security_integration.py` (parametrized over all five paths on Docker Qdrant, so `hybrid_fallback_query` runs against the live server).
- Verification run: `make verify` -> pass (1025 passed, 2 skipped, Docker Qdrant reachable; ruff, format, pyright clean); `make eval-security` -> PASS for all five paths on `public-eval-v2` (74 queries, 5 deferred; result under `experiments/results/tmp/`); `make test-integration` -> 24 passed (was 22; +2 paths); `git status --porcelain -- evaluation knowledge config` empty. Throwaway collections: Qdrant holds only `w2a-realcheck-idx-v1` and its `-settings`. `graphify update .` not run (left to the orchestrator as instructed).
- Notes:
  - Deviation from design R10 wording "freshness against the isolated security repository": the throwaway lexical file also holds the synthetic forbidden rows, which no repository document produces, so `verify_fresh` (full digest) would always refuse it. The `bm25` path instead runs the production `check_identity` on a separate handle (identity against the throwaway collection and the chunker that built it) plus a seed-freshness check: every chunk the seed repository and chunker produce must be in the file with the same version and hash. The retriever itself is built through `build_retriever(BM25, identity, None, None, lexical, config)`, the production standalone shape. For the T8 design As-built notes.
  - The gated `bm25` retriever still uses `index.lexical` (the handle bound by the production binding), so the existing clause-dropping double keeps working in tests.
  - `strategy` in a violation is the strategy the path exercises (`hybrid` for both fallback paths); `path` is the new key.
  - Existing gate behavior (sanity checks, zero-term skip) is unchanged and runs once per query.


### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`
- Usage: 146K tokens · 33 tool uses · 7:50
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright 0 errors, skills mirrors match, validate-knowledge and validate-evaluation OK; 1025 passed, 2 skipped; Docker Qdrant reachable, so the integration tests ran inside it too);
  - `make eval-security` → PASS (1099 ms, 74 queries: 5 security cases, 69 golden; 5 deferred). Result `experiments/results/tmp/security-evaluation-20261101T055245Z.json`: `schema_version` 1.2, `paths` = the five paths, `strategies` = `dense, bm25, hybrid`, `access.role` `guest`, `violations` empty, `bm25_no_term_queries` 0;
  - `perl -e 'alarm 300; exec @ARGV' make test-integration` → pass (24 passed, 1003 deselected; the security integration test is parametrized over the five paths);
  - `git status --porcelain -- evaluation knowledge config` → empty (allowed: none);
  - Qdrant collections after all runs: only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings` (no throwaway left; the reviewer created none outside the commands above).
- Checks against the focus points:
  - Fallback paths are not vacuous: `_gate` raises `EvaluationHarnessError` (exit 2) when a `hybrid_fallback_*` result is not `strategy` `bm25` with `fallback_reason` `qdrant_unavailable`, per query (`test_a_fallback_path_that_does_not_fall_back_is_a_harness_error`); `test_every_path_is_gated_for_every_query` runs all five paths on every query at `top_k` 50 through that check. The per-query dense and lexical unfiltered sanity checks are unchanged, so the forbidden rows are proven reachable for every path.
  - A forbidden hit injected into each path fails the gate and names exactly that path (parametrized over `PATHS`); a dropped SQL access clause names the four lexical paths. `RetrievalAuthorizationError` from `check_hit` is still recorded with `path`.
  - `_UnavailableDense` lives only in `security_eval.py`, built only by `_retrievers`; no CLI flag, environment variable or config key reaches it; the test scans `retrieval/` for the name.
  - `bm25` deviation (design R10): sound. `verify_fresh` compares the full digest and would always refuse the throwaway file, because it also holds the synthetic forbidden and canary rows. The substitute runs the production `check_identity` (dense identity, chunker, hash contract) plus "every seed chunk is in the file with the same version and hash", and the retriever is the production standalone shape (`build_retriever(BM25, identity, None, None, lexical, config)`, no dense index, no embedder). It cannot make the gate pass vacuously: authorization on that path is the SQL access clause plus `check_hit` over a file that holds the forbidden rows, and the lexical sanity check proves they match. See F1 and F2.
- Findings:
  - F1 [MINOR, SPEC_DEFECT, R10] design R10 says the `bm25` path is "built through the standalone path" with "freshness against the isolated security repository"; the code (a) checks a seed-chunk subset instead of `verify_fresh`, (b) checks on a separate handle and gates the retriever on `index.lexical` (the handle from the production `bind_to`), and (c) takes the identity from `IndexIdentity.from_dense` (source `qdrant`) instead of `IndexIdentity.expected` (`check_identity` does not compare `source`, so this is equivalent). → record all three in the design `## As-built notes` under T8's "every deviation found in T1–T7" box; no code change needed.
  - F2 [MINOR, IMPLEMENTATION, R10] the seed-freshness check is one-way: it refuses a missing or changed seed chunk but not an extra non-forbidden row in the file. Harmless today (the file is built moments earlier by the same harness) → optionally tighten to "file rows minus seed rows are all forbidden or canary documents" in a later touch.
  - F3 [MINOR, IMPLEMENTATION, R10] the plain `hybrid` path (now `FallbackRetriever(HybridRetriever, bm25, None)` from `build_retriever`) does not assert that it did not fall back, so a dense outage mid-run would let it serve BM25 silently. Mitigated: the per-query dense sanity check and the `dense` path (which raises) both reach Qdrant first in each query, and `make eval-security` uses an in-memory client → optionally assert `fallback_reason is None` on the `dense` and `hybrid` paths.
  - F4 [MINOR, IMPLEMENTATION, R10] the Docker test for `hybrid_fallback_query` builds and sanity-checks against live Qdrant, but by construction that path's dense leg (`_UnavailableDense`) never queries Qdrant; it gates the live-built lexical file through the fallback. That is what the task box asks; noted so nobody reads it as a live-Qdrant timeout test (that is R11's closed-port test).
  - Note (not a finding): `graphify update .` was not run by the implementer (left to the orchestrator, as in earlier tasks); only AST cache files under `graphify-out/` are untracked.
- Summary for user:
  - Changed: `make eval-security` now gates five paths: `dense`, standalone `bm25` (no dense index or embedder; identity and seed-chunk check on the throwaway file), `hybrid`, `hybrid_fallback_open` (BM25 with `qdrant_unavailable` at open) and `hybrid_fallback_query` (hybrid whose dense leg is the harness-only `_UnavailableDense`). Security result 1.2 adds `paths` (keeps `strategies`), every violation names its `path`, `access.role` stays `guest`; the CLI summary prints `paths:` and `VIOLATION path ...`. `SecurityIndex` now carries its chunker and seed repository.
  - Verified by: `make verify` (1025 passed, 2 skipped), `make eval-security` PASS on all five paths, `make test-integration` (24 passed), protected paths untouched.
  - Worth your attention: the `bm25` path does not run the full `verify_fresh` (the throwaway file holds synthetic forbidden rows, so the digest can never match); it checks identity plus "every seed chunk present", which the reviewer judges sound and not vacuous (F1, for a T8 As-built note). A fallback path that fails to fall back stops the run (exit 2) instead of passing. Four MINOR findings.
  - Reading order:
    1. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `run_security_evaluation`, `_retrievers` (the five paths), `_check_standalone_open`, `_UnavailableDense`, `_gate` (fallback vacuity check, `path` in violations), `security_document` (1.2).
    2. `packages/rag/src/way2australia_rag/evaluation/security_index.py` → `SecurityIndex.chunker`, `seed_repository`.
    3. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `format_security_summary`.
    4. `packages/rag/tests/evaluation/test_security_eval.py` → the "Spec 008 R10" tests at the end, then the 1.2 result test.
    5. `packages/rag/tests/evaluation/test_security_integration.py` → parametrized over `PATHS` on Docker Qdrant; `tasks.md` boxes.

### User decision
- 2026-11-01 — approved. Verbatim: "T6 approved. F1: T8 box (planner amendment). Record in the design's As-built notes all three R10 differences: the seed-chunk subset check instead of `verify_fresh`, the separate handle, and `from_dense` instead of `expected`. F2: accepted. The harness builds the file just before the check. F3: fix at commit. On the plain `hybrid` path, assert that no query fell back (`fallback_reason is None`). If one did, it's a harness error (exit 2), mirroring the fallback paths' check. Add a test. F4: accepted. Commit with the `Spec-Task: 008/T6` trailer and push, then commit the graph separately. Then stop at T7 and give me the commands for the real runs."

## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Files changed: `docs/project/CURRENT_STATE.md` (Last updated, Spec 008 row, Next step item 6); `.kiro/specs/008-retrieval-fallback/tasks.md` (T7 boxes, State). No code changes. The two result files are untracked and left for the user to commit: `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json` (closed port) and `...20261101T070736Z.json` (Qdrant up).
- No real run, model load or Qdrant change by the agent. The user ran the three commands.
- Field checks (read-only python over both files): run 1 `requested_strategy` hybrid, `served_strategies` `[bm25]`, all 69 cases `bm25` / `qdrant_unavailable`, `fallback_counts` `{qdrant_unavailable: 81}`, `index_settings` null, `dense_identity.source` `lexical_file`, `lexical_index` `lexical-v1` digest `6045203b...` 13 chunks, `git_commit` `1f72e62`, `git_dirty` false, `device` null, `by_served_path` only `bm25+fallback:qdrant_unavailable` p50 0.182, p95 0.235, n 69, metrics HitRate@5 0.9275, MRR 0.7082. Run 2 served `hybrid` x69, `fallback_counts` `{}`, `dense_identity.source` `qdrant`, `index_settings` present, `device` `mps:0`, same `lexical_index`, `git_commit` `1f72e62`, `git_dirty` false, `by_served_path` hybrid p50 86.183, p95 115.192, n 69, HitRate@5 0.9855, MRR 0.9094. `qdrant_timeouts` connect 2 s / query 3 s in both.
- `make eval-compare` re-run by the agent (read-only): run 1 vs `...T123109Z.json` PASS (hits 64 -> 64, MRR 0.7082 -> 0.7082); run 2 vs `...T123121Z.json` PASS (hits 68 -> 68, MRR 0.9094 -> 0.9094); no flips in either.
- Run 3 (user): standalone `--strategy bm25` on the closed port returned 5 hits in 2.6 ms; default strategy exit 2 with `OptionalDependencyError`, no fallback.
- Deviations: none. The `make setup-bge-m3` "again if needed" step was not needed; the extra stays removed.
- Verification run: `make verify` -> pass (1026 passed, 2 skipped; the `bge-m3` extra is not installed, the normal `make setup` state; ruff, format, pyright clean); `git status --porcelain -- evaluation knowledge config` empty. `graphify update .` not run (no code changed).

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`; implementer ran on a different model (Sonnet 5.5)
- Usage: 118K tokens · 22 tool uses · 4:07
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright 0 errors, 0 warnings; 1026 passed, 2 skipped; `bge-m3` extra not installed);
  - `make eval-compare BASE=…20261028T123109Z.json CANDIDATE=…20261101T070658Z.json` → exit 0, `eval-compare: PASS (hits 64 -> 64, MRR 0.7082 -> 0.7082)`, every slice +0.0000, no flip lines; prints `requested hybrid and was served by bm25`, latency marked `candidate includes failed dense attempt: qdrant_unavailable`, `git_commit` differs `6ed6e70 -> 1f72e62`;
  - `make eval-compare BASE=…20261028T123121Z.json CANDIDATE=…20261101T070736Z.json` → exit 0, `eval-compare: PASS (hits 68 -> 68, MRR 0.9094 -> 0.9094)`, every slice +0.0000, no flip lines; latency p50 80.3 -> 86.2 ms, p95 103.6 -> 115.2 ms (informational);
  - read-only `python3 -I` field checks over both result files (top-level fields, per-case `served_strategy`/`fallback_reason`, `unanswerable`, hit count) and over the Spec 007 hybrid reference latency;
  - `git status --porcelain -- evaluation knowledge config` → empty; `origin/spec/008` = `HEAD` = `1f72e62` (T1–T6 committed and pushed before the runs). No real evaluation, no model load, no Qdrant access by the reviewer; the tree after `make verify` is unchanged.
- Field checks (all claims in `CURRENT_STATE.md` item 6, the Spec 008 row and the T7 boxes):
  - Run 1 `…T070658Z.json`: schema 2.2, `requested_strategy` hybrid, `served_strategies` `["bm25"]`, `retrieval_strategy` bm25, 69/69 cases (`bm25`, `qdrant_unavailable`), `fallback_counts` `{qdrant_unavailable: 81}` (counted over measured goldens plus unanswerable, `retrieval_eval.py` L393: 69 + 12; the warm-up is the separate `warmup_fallback_reason` `qdrant_unavailable`), `index_settings` null, `dense_identity` source `lexical_file` (collection `w2a-realcheck-idx-v1`, `idx-v1`, BAAI/bge-m3 @ `5617a9f…`, not fake), `lexical_index` `lexical-v1` v1, digest `6045203b…`, 13 chunks, `device` null, `git_commit` `1f72e62…`, `git_dirty` false, `top_k` 5, 13 documents, `qdrant_timeouts` 2 s / 3 s, `by_served_path` only `bm25+fallback:qdrant_unavailable` p50 0.182 / p95 0.235 / n 69, warm-up 3.134 ms, `dense_attempt` leg 0.0, HitRate@5 0.9275, MRR 0.7082, 64 hits. All match.
  - Run 2 `…T070736Z.json`: `requested_strategy` hybrid, `served_strategies` `["hybrid"]`, 69/69 `hybrid` with no `fallback_reason`, `fallback_counts` `{}`, `warmup_fallback_reason` null, `dense_identity` source `qdrant`, `index_settings` present (BGE-M3, 1024, heading v1), `device` `mps:0`, same `lexical_index`, `git_commit` `1f72e62…`, `git_dirty` false, `by_served_path` hybrid p50 86.183 / p95 115.192 / n 69, legs dense p50 85.264, BM25 p50 0.659, warm-up 95.6 s, HitRate@5 0.9855, MRR 0.9094, 68 hits. Spec 007 hybrid reference latency 80.276 / 103.554. All match.
  - R12 criteria 1 and 2 are met from the files; criterion 3 (Run 3) rests on the user's report (no file exists by design); criterion 4 (files committed) completes when the user commits them at approval.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R12] `CURRENT_STATE.md` item 6 opens "fields checked by the agent from the files", but three statements come from the user's report and are not file-backed: the closed port `QDRANT_URL=http://127.0.0.1:1` (no URL is recorded in either result file), and all of Run 3 (5 hits in 2.6 ms; the default strategy exiting 2 with `OptionalDependencyError`). The Run 3 parenthetical "only a very common term matches" for hits 4 and 5 is an interpretation that nobody checked. The Run 3 behavior is consistent with design (`OptionalDependencyError` is never fallback-eligible, design table "`bge-m3` extra missing → exit 2 (never falls back)"). → at commit or in T8, mark the port and Run 3 as "reported by the user", and drop or qualify the "very common term" remark.
  - F2 [MINOR, IMPLEMENTATION, R12] the Agent box is checked while its last sub-bullet ("the user commits the two result files") is still pending (both files untracked). Expected by the workflow (the files are committed at approval), but R12's "result files are committed" holds only after that commit. → commit both files with the T7 commit.
- Summary for user:
  - Changed: docs only. `docs/project/CURRENT_STATE.md` records the three real runs (Spec 008 row, Next step item 6); `tasks.md` T7 boxes checked. Two new untracked result files for you to commit: `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json` (Qdrant unreachable: requested hybrid, all 69 served by `bm25` / `qdrant_unavailable`) and `…T070736Z.json` (Qdrant up: all served by `hybrid`, no fallback).
  - Verified by: field-by-field reads of both JSON files; both `make eval-compare` runs re-run by the reviewer (PASS 64 -> 64 / MRR 0.7082 and PASS 68 -> 68 / MRR 0.9094, no flips); `make verify` (1026 passed, 2 skipped); protected paths untouched; both files `git_dirty` false at `1f72e62`.
  - Worth your attention: the fallback reproduces the Spec 007 BM25 result exactly, and the up path reproduces hybrid exactly. Hybrid latency is about 6 ms (p50) and 12 ms (p95) higher than on 2026-10-28 (informational). The Run 3 lines and the closed port come from your report, not a file (F1). Two MINOR findings.
  - Reading order:
    1. `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json` → `requested_strategy`, `served_strategies`, `fallback_counts`, `dense_identity`, `latency_ms.by_served_path`.
    2. `experiments/results/retrieval-evaluation-idx-v1-20261101T070736Z.json` → the same fields on the up path.
    3. `docs/project/CURRENT_STATE.md` → Spec 008 row and Next step item 6.
    4. `.kiro/specs/008-retrieval-fallback/tasks.md` → T7 boxes.

### User decision
- 2026-11-01 — approved. Verbatim: "T7 approved. F1: fix at commit. In CURRENT_STATE item 6, mark the closed port (127.0.0.1:1) and all of Run 3 as user-reported. Drop the "only a very common term matches" remark, or qualify it as unverified. F2: include both result files in the T7 commit. Commit with the `Spec-Task: 008/T7` trailer and push, then commit the graph separately if it changed. Then start T8."

## T8 — round 1

### Implementation
- Model: claude-sonnet-5-5 (Sonnet 5.5); intended tier BEST_MINUS_ONE not compared against MODEL_PREFERENCES.md (subagent, no user to ask)
- Files changed (docs only, no code): `docs/project/DECISIONS.md` (D056–D062); `docs/project/ROADMAP.md` (item 13 note); `docs/project/ARCHITECTURE.md` ("Retrieval" module table and hybrid bullets, "Retrieval fallback" rewritten); `docs/project/COMMANDS.md` (strategies/fallback paragraph, `make retrieve`, `make eval-retrieval` 2.2, `make eval-security` 1.2, `make eval-compare`); `docs/project/TECH_STACK.md`; `docs/project/CURRENT_STATE.md` (Spec 008 implemented block, spec row, known issues, Next step item 7, Spec 007 carry-over closed); `.kiro/specs/008-retrieval-fallback/design.md` (As-built notes T3 to T7 and the hand-off); `tasks.md` (T8 boxes, State).
- Design As-built notes added: T3 (`bge_m3` import move, `index_settings` parameter), T4 F4 (a)–(c), T5 F3 and F1 (message form), T6 F1 (a)–(c) plus F2/F3/F4 and `security_index.py`, T7, and the carried items (`asyncio.run`, Qdrant client lifecycle, circuit breaker and others). The "Not changed" list was checked against `git diff --name-status main...HEAD`: it matches the code (the two ingestion moves are named); `evaluation/security_index.py` was not in the placement table and is noted under T6.
- Doc accuracy checks: the mixed-file refusal message and the five security paths were read from `results.py` and `security_eval.py`; the plain `hybrid` no-fallback assertion exists (`security_eval.py` L333); the client-close gap was read from `opening.py` (closed only on the fallback path through `_close_quietly`; `OpenedRetrieval.close()` closes only the lexical handle).
- T7 review F1 was already applied in `CURRENT_STATE.md` item 6 (port and Run 3 marked user-reported, remark dropped); not touched again.
- Verification run: `make verify` -> pass (1026 passed, 2 skipped; no `bge-m3` extra); `make test-integration` -> 24 passed (Docker Qdrant); `make eval-security` -> PASS on `dense`, `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`; `git diff --name-status main...HEAD -- evaluation knowledge config` lists only `config/retrieval.yaml`; `git status --porcelain -- evaluation knowledge config` empty.
- `graphify update .` not run: no code changed (docs only).
- Not verified: the doc statements about worst-case latency repeat the design's estimates and were not measured here.
- Usage: 163K tokens · 30 tool uses · 8:07

### Review
- Model: claude-opus-5-5 (Opus 5.5); matches the BEST tier (`Opus`) in `MODEL_PREFERENCES.md`; implementer ran on a different model (Sonnet 5.5)
- Verdict: PASS
- Commands:
  - `make verify` → pass, exit 0 (ruff check and format clean, pyright 0 errors; 1026 passed, 2 skipped; `bge-m3` extra not installed);
  - `make test-integration` → pass, exit 0 (24 passed, 1004 deselected; Docker Qdrant `way2australia-qdrant` running);
  - `make eval-security` → exit 0, `eval-security: PASS`, paths `dense, bm25, hybrid, hybrid_fallback_open, hybrid_fallback_query` (result `experiments/results/tmp/security-evaluation-20261101T120032Z.json`, git-ignored);
  - `git diff --name-status main...HEAD -- evaluation knowledge config` → only `M config/retrieval.yaml`; `git status --porcelain -- evaluation knowledge config` → empty; `git status --porcelain` after the runs → only the nine T8 doc files (no code, no `graphify-out/` change).
- Doc claims checked against the code: `classify_qdrant_error` (one-level unwrap through `ResponseHandlingException.source`, `TimeoutException` → timeout, `NetworkError` → unavailable) and `classify_model_error` (explicit `__cause__` only, 10 links, `OfflineModeIsEnabled` excluded) in `availability.py` (D057); `retrieval_client_factory` (`timeout=connect_timeout_s`, `check_compatibility=False`) and `RetrievalConfig.schema_version: Literal["1.1"]` (D059); `open_retrieval` order (embedder, then client, `DenseIndex.open`, `open_bound_lexical`; `RetrievalUnavailableError` on `hybrid` only → `_open_fallback`; client closed only on the fallback path, `OpenedRetrieval.close()` closes only the lexical handle) and `build_retriever` returning `FallbackRetriever(hybrid, bm25, None)` (ARCHITECTURE flow, D058, carried lifecycle item); `FallbackRetriever` single `except`, same `access`/`top_k`, `dense_attempt` leg; `make retrieve` `_strategy_line` printed only on fallback and the stderr `WARNING retrieval fell back to …` line (COMMANDS, T4 F4 (a)); `results._served_strategy`/`_mixed` message and `compare.py` "includes failed dense attempt" and "was served by" lines (D061, T5 notes); `security_eval._gate` vacuity checks for fallback paths and the plain `hybrid` no-fallback check (D061, T6 notes); 82-query / ~4 minute and 3× bound figures match design R6; ROADMAP item numbers 9 (reranking) and 10 (generation) correct; design "Not changed" list matches `git diff --name-status main...HEAD -- packages/rag/src` (only `ingestion/cli.py` and `ingestion/identity.py` in `ingestion/`, `lexical/cli.py` import only, no `fusion.py`/`hybrid.py`/`access.py`/`baseline*` change). D056–D062 present; all T4 F4, T5 F3 and T6 F1 As-built sub-items present; the `asyncio.run` and Qdrant client lifecycle items are in the design hand-off section, `CURRENT_STATE.md` Next step item 7 and known issues.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R14] `CURRENT_STATE.md` Next step item 6 still ends "The two result files are untracked; the user commits them.", but both files were committed in `3403261` (T7 commit; `git ls-files` lists them). → reword to "committed in `3403261`" at commit.
  - F2 [MINOR, IMPLEMENTATION, R14] `COMMANDS.md` quotes the mixed-file refusal as `golden cases bm25: 3, hybrid: 78`; the counts are over golden case rows, so on suite `public-eval-v2` (69 goldens) they sum to at most 69 (the sketch numbers come from the design R9 example, which counted all 81 queries). The message shape is correct. → use counts that fit the suite (for example `bm25: 3, hybrid: 66`) or mark them illustrative.
  - F3 [MINOR, IMPLEMENTATION, Definition of Done] the `graphify update .` box is checked, but the Implementation block says it was not run (docs only). Nothing is lost: `graphify update` is AST-only, no code changed and `graphify-out/` is unchanged. → either run it at commit or note "not needed (docs only)" on the box.
- Summary for user (PASS only):
  - Changed: docs only. `DECISIONS.md` D056–D062; `ROADMAP.md` item 13 note (retrieval degradation done early, reranker/generation paths still open); `ARCHITECTURE.md` retrieval module table and a rewritten "Retrieval fallback" section with the as-built open/query flow; `COMMANDS.md` (schema 1.1 timeouts, standalone `bm25`, fallback rules, result 2.2, security 1.2, `eval-compare` 2.2); `TECH_STACK.md`; `CURRENT_STATE.md` (Spec 008 block, hand-off item 7, known issues); `design.md` As-built notes T3–T7 plus the carried items.
  - Verified by: `make verify` (1026 passed, 2 skipped), `make test-integration` (24 passed), `make eval-security` (PASS on all five paths), branch protected-path check (only `config/retrieval.yaml`); every behavioral claim read against `availability.py`, `qdrant_client.py`, `strategy.py`, `opening.py`, `fallback.py`, `retrieval/cli.py`, `results.py`, `compare.py`, `security_eval.py`.
  - Worth your attention: three MINOR doc nits (stale "untracked" line in item 6, an impossible example count in COMMANDS, the graphify box). The HTTP-route carry-overs (circuit breaker, lexical startup policy, 5xx eligibility, async freshness, large-corpus freshness cost, Qdrant client close on every open failure) are now recorded for the retrospective.
  - Reading order (docs-only task, follow decisions → roadmap → architecture → commands → state → design):
    1. `docs/project/DECISIONS.md` → D056–D062 at the end.
    2. `docs/project/ROADMAP.md` → item 13 note.
    3. `docs/project/ARCHITECTURE.md` → "Retrieval" module table, then "Retrieval fallback" flow and bullets.
    4. `docs/project/COMMANDS.md` → strategies/fallback paragraph, `make retrieve`, `make eval-retrieval` 2.2, `make eval-security` 1.2, `make eval-compare`.
    5. `docs/project/TECH_STACK.md` → Qdrant client, lexical store and sparse retrieval lines.
    6. `docs/project/CURRENT_STATE.md` → Spec 008 implemented block, spec row, Next step item 7, Spec 008 known issues.
    7. `.kiro/specs/008-retrieval-fallback/design.md` → As-built notes T3–T7 and "Carried to later specs"; `tasks.md` T8 boxes.
- Usage: 164K tokens · 32 tool uses · 4:41

### User decision
- 2026-11-01 — approved. Verbatim: "T8 approved. F1: fix at commit. CURRENT_STATE item 6 should say both T7 result files were committed in `3403261`. F2: fix at commit. Use example counts that sum to 69 (for example `bm25: 3, hybrid: 66`). F3: note "not needed (docs only)" on the graphify box. The docs reach the graph through `/graphify . --update` after the merge. Commit with the `Spec-Task: 008/T8` trailer and push. Then start the required spec-reviewer retrospective, including the Spec 008 learning debrief."
