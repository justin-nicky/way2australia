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
