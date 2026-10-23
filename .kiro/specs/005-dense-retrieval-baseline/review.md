# 005 — Spec Review (retrospective)

Required end-of-spec retrospective (`agent-skills/spec-reviewer`, D031). Append-only; newest round at the bottom.

## Round 1 — 2026-10-23

- **Spec:** `005-dense-retrieval-baseline`
- **Diff reviewed:** `main...spec/005` (base `2f98ef9`, head `da27ada`; not merged). 48 files, +3787/−127. Working tree clean at the start.
- **Reviewer host / model:** Claude Code (subagent, fresh session, did not implement the spec) / `claude-opus-5-5`. Matches the `spec-reviewer` tier BEST = Opus in `agent-skills/MODEL_PREFERENCES.md`; no mismatch.
- **Outcome:** `PASS` (no BLOCKING or MAJOR finding; MINOR findings F3–F5 recorded under known issues in `CURRENT_STATE.md`; F1–F2 were documentation gaps reconciled in this round)
- **Usage:** 197K tokens · 42 tool uses · 7:02

### Verification run

Environment: optional `bge-m3` extra absent (`import sentence_transformers` → `ModuleNotFoundError`). Docker Qdrant was already running (user-started) with only `w2a-realcheck-idx-v1` and `w2a-realcheck-idx-v1-settings`; the container was not started or stopped, and those collections were only read. The real-model path was not run.

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | exit 0 | `ruff check` "All checks passed!"; `ruff format --check` "81 files already formatted"; pyright 0 errors; skills-check 5 mirrors match; validate-knowledge OK, 0 problems; pytest **446 passed, 1 skipped** (447 collected; the skip is the opt-in BGE-M3 smoke test; integration tests ran because Qdrant was reachable) |
| `make test-integration` | exit 0 | **19 passed**, 428 deselected |
| `make -n setup-bge-m3` | `UV_HTTP_TIMEOUT=300 ... uv sync --all-packages --group dev --extra bge-m3` | R10 |
| `QDRANT_COLLECTION_BASE=w2a-retro005-throwaway make ingest INGEST_ARGS="--embedder fake"` | exit 0 | added 13 |
| same base, `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake"` | exit 0 | header with `fake=true, device=unknown`; 5 hit lines `rank document_id section_id score title`; no bodies or paths |
| same base, `make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake --output <scratch>/baseline.json"` | exit 0 | 63 cases, excluded 0, N = 13, `random_hit_rate_formula` `min(1, 5/13)`, all four notes incl. "not a quality measurement"; JSON has every R8 field, `git_commit` `da27ada`, `git_dirty: false`, `device: null` (fake); no absolute path, no query or chunk text |
| same without `--allow-fake` | exit 2 | `RetrievalConfigurationError: the index was built with the fake embedder; ...`; no file written |
| Server-side authorization probe (scratch script, own throwaway collection) | as required | upserted 4 synthetic points whose chunk text is the query: `access_scope: staff`, `tenant_id: other`, `owner_user_id: u1`, and `owner_user_id` key absent. Unfiltered `query_points` returns exactly those 4 as nearest; `DenseRetriever.retrieve(top_k=50)` under guest access returns the 13 seed documents and none of the 4; `document_count` under the filter = 13. Confirms the filter (incl. `is_null` excluding a missing field) on the real Qdrant 1.19 server, not only local mode (see F3) |
| Read-only binding to the user's `w2a-realcheck-idx-v1` | binds | `DenseIndex.open(client, "w2a-realcheck", "idx-v1", info)` with `EmbedderInfo` built from `BGE_M3_MODEL_ID`, the pinned revision, `BGE_M3_VECTOR_SIZE`, `normalize=True`, `is_fake=False` (no model loaded) binds: BAAI/bge-m3 @ `5617a9f6…`, size 1024, fake=false. The fake embedder is refused with `IndexBindingError` naming `embedder_model_id`, `embedder_revision`, ... |
| Cleanup | done | deleted `w2a-retro005-throwaway-idx-v1` and `-settings` (my own); `GET /collections` lists only the two `w2a-realcheck-*` collections; scratch files removed; `experiments/results/` holds only `.gitkeep`; `git status` showed no change before the doc edits |
| `git diff --stat main...spec/005 -- evaluation/ knowledge/ config/ experiments/` | empty | protected-data check |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 access context, server-owned policy | `core/access.py` (`Role`, frozen `AccessContext`, blank tenant refused); `retrieval/access.py` `guest_access`, `resolve_access` (identical `GUEST_PUBLIC_POLICY`, other roles refused); `RuntimeSettings.tenant_id` (`W2A_TENANT_ID`, default, stripped, empty refused); `load_runtime_settings` used by ingestion and both retrieval CLIs | `core/tests/test_access.py`; `retrieval/test_access.py`; filter-identity test with hostile query texts in `test_retriever.py`; empty-tenant CLI tests (both CLIs, client factory never called) | SATISFIED |
| R2 filter during retrieval | `build_access_filter` (scope `MatchAny`, tenant `MatchValue`, `IsNull(owner_user_id)`), the only authorization filter in the code (grep: the other `models.Filter` is ingestion's delete-by-`document_id`); `DenseRetriever.retrieve` always passes it; `document_count` uses it | `test_access.py` (policy-derived filter), `test_retriever.py` (spy: filter on every query), `test_authorization_isolation.py` (in-memory); server-side probe this round | SATISFIED (Docker coverage gap: F3) |
| R3 fail-closed re-check | `check_hit` on every hit before any is returned; same `ResolvedAccess`; messages carry `document_id` and field names only | `test_access.py`, filter-dropping store raises in `test_authorization_isolation.py` | SATISFIED |
| R4 embedder bound to index | `DenseIndex.open`: collection, settings collection, settings record (malformed → field names only), `index_version`, five embedder fields, `dense` size; read-only (`collection_exists`, `get_collection`, `retrieve`, `query_points`, `scroll`); `read_index_settings` shared with ingestion | `test_index.py` (each refusal row, fake-vs-real both ways, non-vacuous no-writes spy, multi-page `document_count`, retrieval-side wording); realcheck binding probe this round | SATISFIED |
| R5 dense top-k | `retriever.py` (`top_k` int 1–50 default 5, bool refused, empty query refused, ranked by score, all hit fields, run metadata, `perf_counter` latency, no threshold, no language code); `models.py` | `test_retriever.py`; `test_retrieval_integration.py` (Docker) | SATISFIED |
| R6 developer query command | `retrieval/cli.py`; `make retrieve` (`QUERY`, `RETRIEVE_ARGS`); header incl. device; hit lines via `safe_text`; exit 0/2; no role/scope/tenant flag | `test_cli.py` (exit codes per table, missing extra before client, parser has no access options, no key/paths/bodies, control/bidi-safe hit and error lines); throwaway `make retrieve` this round | SATISFIED |
| R7 document-level metrics | `metrics.py` (dedupe, HitRate@k, Recall@k, MRR, `random_hit_rate` = `min(1, k/N)`, nearest-rank percentile); no chunk/point/section IDs | `test_metrics.py`; formula test with k >= N in `test_baseline.py` | SATISFIED |
| R8 baseline command and result | `goldens.py` (read-only, `golden_answerable` only, active/answerable/non-empty, paths inside repo, `access_context` ignored), `declared_release_id`, `baseline.py` (fake refused without flag, N under filter, warm-up excluded, device after warm-up, slices, p50/p95, notes, no overwrite, nothing written on error, partial file removed), `baseline_cli.py`, `make retrieval-baseline` | `test_goldens.py` (63 cases, hashes unchanged), `test_baseline.py`; throwaway runs this round | SATISFIED; the real BGE-M3 result is **PENDING** (user-owned, not a gate), recorded in `CURRENT_STATE.md` as R8/DoD allow |
| R9 index store hardening | `store.py` `_ensure_payload_indexes()` on creation and on the exists-empty-no-settings row before `_write_settings`; no payload/identity/settings/namespace/`index_version` change | `test_store.py` (spy incl. call order); `test_store_integration.py` (keyword `payload_schema`, `dense` size/Cosine, F4 re-creation, repeated index harmless) | SATISFIED |
| R10 quality gate and setup | `Makefile` `lint` runs `ruff format --check $(PYTHON_TARGETS)`; `UV_HTTP_TIMEOUT ?= 300`; `test_content_hash.py` formatted; two-way scope test | `make lint`; `make -n setup-bge-m3`; `test_date_and_policy.py` | SATISFIED |
| R11 test strategy | fake embedder + `:memory:` in unit tests; `integration` marker, unique bases, cleanup | `make verify` (no PyTorch, no model download); `make test-integration`; only the realcheck collections remained after the runs; `experiments/results/` clean | SATISFIED |
| R12 decisions and documentation | D033–D039 (T7), D040–D041 (this round); ARCHITECTURE retrieval section; COMMANDS retrieval section; CURRENT_STATE | doc review against code (below) | SATISFIED after this round's reconciliation (F1, F2) |
| Definition of Done | all items above; protected paths unchanged; real baseline recorded as pending | this round's runs | SATISFIED |

### Protected-data check

`git diff --stat main...spec/005 -- evaluation/ knowledge/ config/` → empty. `experiments/` (including `experiments/configs/day1_baseline.yaml`) is also unchanged, and no result file is committed. `test_goldens.py` asserts the `evaluation/` file hashes are unchanged after loading.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R12 / T7 (T7 review F1) | `TECH_STACK.md` listed the `pydantic-settings` variables without `W2A_TENANT_ID`, and `ARCHITECTURE.md`'s ingestion `config.py` row had the same gap. **Reconciled in this round** (docs only). TECH_STACK also now notes that the device is recorded (D038) and that the retrieval metrics are plain Python with DeepEval not yet a dependency. |
| F2 | MINOR | IMPLEMENTATION | R12 / T7 (T7 review F2) | `ARCHITECTURE.md` "## Current RAG query flow" described the target pipeline as current and put the "mandatory authorization filter" after RRF fusion, contradicting D035 and the code. **Reconciled in this round** at the user's instruction: renamed "Target RAG query flow", marked as not implemented, and corrected so the filter is applied inside each retriever (dense, BM25, SQLite FTS5 fallback) before fusion, never after RRF; the "Retrieval fallback" section and new D040 say the same. |
| F3 | MINOR | IMPLEMENTATION | R2, R11 / T4 | The isolation tests (`test_authorization_isolation.py`) run only on in-memory local-mode Qdrant, whose filter evaluation is a separate Python implementation from the server's. No committed Docker test proves the server excludes `staff` scope, another tenant, a non-null owner or a missing `owner_user_id` (`is_null` semantics). R2 asks only for an isolated test collection, so the requirement is met; this round confirmed the server behaviour manually (verification table). Recommended for the next spec that adds a query path (see Notes), not an RM task. |
| F4 | MINOR | IMPLEMENTATION | R5, R8 / T2, T6 | Unrecorded, immaterial interface-sketch deviations: `retrieval/__init__.py` has no public exports (design: "public exports"); `SuiteRef` holds `golden_dataset_path` instead of `datasets`; `run_baseline` also takes `index`, `embedder`, `excluded_case_count`, `repo_root`. Behaviour matches the requirements. Recorded in `design.md` "As-built notes"; no code change needed. |
| F5 | MINOR | SPEC_DEFECT | R1 / design error table | The design error table says a non-guest role is refused with "Qdrant contacted? no", but the design data flow (step 7 after step 6) and T5's startup order resolve access after the read-only `DenseIndex.open`; the code follows the data flow. Unreachable today (`guest_access` always builds `Role.GUEST`). Recorded in "As-built notes"; when a spec adds roles, resolve access before contacting Qdrant or fix the table (spec-planner, optional). |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/TECH_STACK.md` | Runtime configuration line adds `W2A_TENANT_ID`, `load_runtime_settings` and D034; embeddings line notes the device is recorded (D038); evaluation lists the plain-Python retrieval metrics (Spec 005) and marks DeepEval as not yet a dependency | F1 (user instruction 1); stale entries |
| `docs/project/ARCHITECTURE.md` | Ingestion `config.py` row adds `W2A_TENANT_ID` and the shared loader | F1 |
| `docs/project/ARCHITECTURE.md` | "Current RAG query flow" renamed "Target RAG query flow", marked not implemented; diagram shows `ResolvedAccess` and the authorization filter inside the dense and BM25 legs before RRF; text states it is applied inside each retriever (dense, BM25, FTS5 fallback) before fusion, never after RRF, reranking or generation | F2 (user instruction 2) |
| `docs/project/ARCHITECTURE.md` | "Retrieval fallback": fallbacks take the same `ResolvedAccess`, filter inside their own query and call `check_hit`; none implemented. Retrieval section decision range D033–D041 | F2, D040 |
| `docs/project/DECISIONS.md` | New D040 (authorization inside every retriever before fusion; extends D035, does not supersede it) | Durable rule from the user's T7 decision, needed by the hybrid spec |
| `docs/project/DECISIONS.md` | New D041 (payload-derived text printed only through `safe_text`; bidi/ANSI/controls stripped, ZWNJ/ZWJ kept) | Durable output-safety contract made in T6/T7 and recorded in no decision |
| `.kiro/specs/005-dense-retrieval-baseline/design.md` | Appended "## As-built notes": formula `min(1, 5/13)` vs the sketch `min(1, k/N) = 5/13`, CLI startup orders, error-table/data-flow mismatch, interface-sketch deviations, `invalid_fields`, shared loader, `safe_text`, partial-file cleanup; confirmation that `idx-v1` and the realcheck collection stay valid | Skill §3; user instruction 3; F4, F5 |
| `docs/project/CURRENT_STATE.md` | Date; current goal, Spec 005 summary, spec-status row and next steps now say retrospective round 1 `PASS` awaiting approval and merge; decisions D033–D041; the real BGE-M3 baseline stays **PENDING**; new "Spec 005 retrospective" known-issues list (F3–F5, plus T1 F2 and T7 F3 closed by user decision) | Skill §3/§4; user instruction 4 |

Checked and left unchanged: `COMMANDS.md` (`make retrieve`/`make retrieval-baseline` options, bounds, exit codes, output path, quoting caveat, `W2A_TENANT_ID`, `make lint` format check and `UV_HTTP_TIMEOUT` match the `Makefile` and CLIs); D033–D039 (each claim matches the code). `config/ingestion.yaml`'s header comment lists the environment variables without `W2A_TENANT_ID`; it describes what is not index-defining and is protected data, so it is left as is.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| `random_hit_rate_formula` recorded as `min(1, 5/13)` (concrete numbers), not the design sketch's `min(1, k/N) = 5/13` | Change log 2026-10-21; T6 review F2 and user decision 2026-10-21; T7; As-built notes |
| Retrieve CLI validates query and `--top-k` before config | T5 review round 1, accepted 2026-10-20 |
| Baseline CLI runs all file checks (suite, release, goldens, output) before the embedder and Qdrant | T6 review round 1, accepted 2026-10-21 |
| Device read after the warm-up; `Embedder.device` property on the Protocol; `CountingEmbedder` test double gained `device` | Change log 2026-10-20; T4 user decision |
| `AccessContext` strips and refuses blank `tenant_id` itself (beyond T2's `min_length=1`) | Change log 2026-10-20 (T4, from T2 review F4) |
| Shared `load_runtime_settings`; `IndexSettingsMismatchError.invalid_fields`; retrieval-side refusal advice; `document_count` missing-`document_id` → `IndexBindingError` | Change log 2026-10-20 (T5) |
| `safe_text` helper used by both CLIs incl. error lines, bidi stripping | Change log 2026-10-20, 2026-10-21 |
| Partial-file removal in `write_result`; generic loader message for location-less errors | Change log 2026-10-21 (T7) |
| `packages/rag/tests/retrieval/__init__.py` added (basename clash) | T2 review round 1 |
| `__init__` exports, `SuiteRef` field, `run_baseline` parameters | F4 |
| Error table vs data flow for non-guest roles | F5 |

### Cross-task consistency

- **Authorization is identical on every path.** Both CLIs build access only through `resolve_access(guest_access(load_runtime_settings(...)))`; `DenseRetriever.retrieve` takes a `ResolvedAccess` (never raw scopes), builds the filter with `build_access_filter` and re-checks every hit with `check_hit`; the baseline uses the same `ResolvedAccess` for N (`document_count`) and for every case, so N counts only visible documents. `build_access_filter`, `check_hit` and `resolve_access` in `retrieval/access.py` are the only authorization code (grep over `retrieval/`, `ingestion/` and `apps/`).
- **Nothing accepts role, scope or tenant from a query, flag or case.** Neither parser has such an option (tested); the tenant comes only from `W2A_TENANT_ID`; `GoldenCase.access_context` is loaded and never read; the filter-identity test pins hostile query texts.
- **Fail closed.** A re-check failure raises before any hit is returned; binding failures refuse before any query; a missing `owner_user_id` field is excluded by the filter (verified on the server this round) and would fail `PointPayload` validation in `check_hit` anyway; the baseline writes nothing on any error.
- **Spec 004 index unchanged.** `payload.py`, `settings.py`, `identity.py` and `INGESTION_NAMESPACE` are untouched in the diff; `IndexSettings` still validates the user's recorded `w2a-realcheck-idx-v1` settings, which bind read-only with the real BGE-M3 identity. The two ingestion changes (`_ensure_payload_indexes`, public `read_index_settings`) keep the ingestion message text and behaviour.
- **Errors and exits agree** across the retrieve CLI, the baseline CLI and the ingestion CLI (`RetrievalError`/`IngestionError` messages through `safe_text`, other exceptions as class name only, exit 2).
- **Task-review patterns:** all seven tasks passed task review in round 1 (implementer `claude-sonnet-5-5`, reviewer `claude-opus-5-5` each time). The recurring pattern was MINOR hardening deferred to a later task (T1 F1, T3 F1–F2, T4 F1, T5 F2, T6 F1–F5 all landed in T7 through one spec-planner amendment), which kept tasks approved but made T7 large. Recorded usage: implementers about 818K tokens, task reviewers about 829K tokens.

### Scope-drift review

No Spec 006 work (no `make eval-retrieval`, gates or section metrics; `goldens.py` is the declared stand-in), no BM25/sparse/RRF, reranking, language filtering, score thresholds, FastAPI route, Langfuse, fallback implementation, non-guest roles, device pinning, chunking change or new `index_version`. No Phase 2 feature. The Spec 004 items fixed (T6 F2, T6 F4, T1 F1, formatting, `UV_HTTP_TIMEOUT`) are exactly those R9/R10 list. Every spec edit after approval has a dated change-log line.

### Remediation required

None. No RM tasks added; `tasks.md` `Status:` unchanged. F5 is a SPEC_DEFECT for `spec-planner` only if the user wants the design table corrected; it is otherwise handled by the As-built note and the next roles spec.

### Notes for the next spec

- **Hybrid retrieval (Spec 007): authorization inside each leg, before fusion (D040, user instruction).** The BM25/sparse leg and any SQLite FTS5 fallback must take the same `ResolvedAccess`, apply the authorization filter inside their own query, and call `check_hit` on every hit before RRF. Never fetch unfiltered candidates and filter after RRF, reranking or generation. A non-Qdrant store (FTS5) needs a filter built from the same `ResolvedAccess` (no second scope list); write a test that a leg returning a forbidden hit makes the whole query fail closed.
- **Add a Docker authorization isolation test (F3)** when the next query path lands: forbidden synthetic points (`staff` scope, other tenant, non-null owner, missing `owner_user_id`) in a throwaway collection on the real server, nearest by construction, never returned by any leg. The in-memory tests do not exercise the server's filter engine.
- **Real BGE-M3 baseline is PENDING (user-owned, not a gate).** After merge: `make setup-bge-m3`, a real `make ingest`, `make retrieval-baseline`, `make setup`, then commit the `experiments/results/retrieval-baseline-*.json` and update `CURRENT_STATE.md`. The existing `w2a-realcheck-idx-v1` collection already binds, so `QDRANT_COLLECTION_BASE=w2a-realcheck make retrieval-baseline` is also possible without re-ingesting. The hybrid spec and Spec 006 need this number as their comparison point; a fake result is never a baseline.
- **Baseline caveats to carry forward:** top-5 over 13 documents is optimistic (random `min(1, 5/13)` = 0.3846; the fake plumbing run gave HitRate@5 0.3492, which is noise); `min(1, k/N)` understates the random rate for multi-relevant cases (design Alternatives); no pure-Malayalam golden case and empty `relevant_section_ids` remain evaluation-data gaps (C6).
- **Spec 006** reuses `metrics.py`, replaces `goldens.py`, and should keep the baseline JSON (`schema_version` 1.0) readable or bump the version.
- **Roles:** when a spec adds a role, resolve access before contacting Qdrant (F5), extend `resolve_access` only, and decide the `owner_user_id == user` condition for `user_private`.
- **Default output location:** `make retrieval-baseline` without `--output` writes into `experiments/results/`, which is not ignored by git; a fake run without `--output` leaves a file that could be committed by mistake. Consider refusing to default there with `--allow-fake`, or a git-ignore rule for throwaway names.
- **Still deferred:** shared `index/` package and moving `build_embedder` out of `ingestion/cli.py` (revisit with sparse vectors); device pinning (D038); Spec 004 T7 F1 (chunking outside the per-document try) and the other open Spec 004 nits.

### Final handoff

Outcome `PASS`. Nothing committed, pushed or merged. Uncommitted changes from this round: `.kiro/specs/005-dense-retrieval-baseline/review.md` (new), `design.md` (As-built notes appended), `docs/project/TECH_STACK.md`, `docs/project/ARCHITECTURE.md`, `docs/project/DECISIONS.md` (D040, D041), `docs/project/CURRENT_STATE.md`. No code, tests, `requirements.md`, `tasks.md`, `evaluation/`, `knowledge/` or `config/` edited. After the user approves this round, the orchestrator commits it with the `Spec-Review` trailer and merging `spec/005` into `main` can proceed.
