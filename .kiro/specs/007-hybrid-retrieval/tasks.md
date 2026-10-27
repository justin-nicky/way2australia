# 007 — Hybrid Retrieval Tasks

Status: implementing (branch spec/007, base 06b1af9)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-10-25). Design: `design.md` (approved 2026-10-25).

Rules for every task:
- **Protected paths.** `evaluation/`, `knowledge/` and `config/` change only where a task lists the path under "Allowed protected-path changes". Nothing under `knowledge/` changes in this spec. Every task checks `git status --porcelain -- evaluation knowledge config` and the reviewer compares the output with the task's list.
- **No live-count literals in new tests.** Counts of cases, documents or chunks come from the data being tested (manifest `case_count`, dataset line counts, repository listing), compared by consistency checks. Literal counts are allowed only in synthetic fixtures the test builds itself. Requirement-level numbers (91, 69, 12, 10) are checked against the manifest by consistency (`case_count == sum of dataset rows`, `v2 goldens == v1 goldens + promoted candidates`), not hard-coded.
- **`task-reviews.md`** is edited only by exact, targeted edits (append a round, change a named line); never rewritten or reformatted.
- **Dense behavior stays identical.** Existing dense tests may be updated only to add the new default model fields; dense ranks, scores, document IDs and ordering are never changed. `retrieval/metrics.py`, `retrieval/baseline.py`, `retrieval/baseline_cli.py` are not edited; the legacy snapshot test passes untouched (D046).
- `make verify` never needs Docker, PyTorch or a model download. Unit tests use `FakeEmbedder`, `QdrantClient(":memory:")` and SQLite files under `tmp_path`.
- Agents never write to, delete or re-ingest a `w2a-realcheck-*` collection and never run the real model. Docker runs use a throwaway base `w2a-t007-<8 hex>` (fake embedder) and delete it afterwards; Docker isolation tests use `w2a-sectest-<8 hex>`.
- Tests never write under `experiments/results/` (use `tmp_path`); throwaway CLI output goes to `experiments/results/tmp/`. Committed result files are never modified.
- After code changes run `graphify update .` (D048).
- **Review reading order.** Each task lists the order in which the task reviewer reads the change; the user reviews the reviewer's summary in that order.

## T1 — Evaluation Suite `public-eval-v2`

**State:** approved (2026-10-25)
**Requirements:** R1, R14

- [x] Create `evaluation/datasets/v2/golden_public.jsonl`, `unanswerable_public.jsonl`, `security_public.jsonl`: every v1 row copied in order with only `evaluation_suite_id` set to `public-eval-v2`, keeping v1 key order and JSON style (UTF-8, `ensure_ascii=False`, v1 separators). A scratch script may generate them; it is not committed.
- [x] Append `g064`–`g069` to the v2 golden file, mapped in order from `cand006_ml_001`–`cand006_ml_006` (`g065`, `g066` with the reworded queries in `proposed_case.query`), with the fields listed in R1 and the v1 golden key order.
- [x] Create `evaluation/suites/public-eval-v2.json` (`version: 2`, `status: active`, `introduced_in_release: seed-v1`, `case_count` equal to the v2 rows, `replaces` v1, notes).
- [x] Change only `status` to `replaced` in `evaluation/suites/public-eval-v1.json`.
- [x] Add `review.promoted_as: {"suite_id": "public-eval-v2", "case_id": ...}` to the six promoted rows of `evaluation/candidates/006-candidates.jsonl`; no other byte of the file changes except those insertions (rows stay `status: suggested`).
- [x] `evaluation/validate.py`: the `promoted_as` transcription check (design R1); problem lines carry field names only.
- [x] `evaluation/cli.py`: `DEFAULT_SUITE` → `evaluation/suites/public-eval-v2.json`. `retrieval/baseline_cli.py` is not touched.
- [x] `evaluation/retrieval_eval.py`: neutral g004/u001 note text (design R1).
- [x] Tests (`packages/rag/tests/evaluation/test_suite_v2.py` and updates):
  - v2 `case_count` equals its dataset rows; v2 goldens = v1 goldens + promoted candidates; v2 unanswerable and security row counts equal v1's;
  - every copied row equals its v1 row except `evaluation_suite_id`;
  - the mapping and field equality for `g064`–`g069` against the candidates file;
  - v1 dataset file hashes equal their committed versions (hash read from `git show HEAD:` or a pinned digest computed from the committed file in the test setup, not a literal count);
  - v1 manifest equals its committed JSON except `status`; candidates file equals its committed rows except `review.promoted_as`;
  - the transcription check fails on a `tmp_path` copy with a changed query, changed `relevant_document_ids`, a missing case and an unknown suite;
  - `eval-retrieval` and `eval-security` refuse the v1 suite (`replaced`) with exit 2;
  - existing tests that read the real suite follow the v2 default with consistency checks.

Allowed protected-path changes: new `evaluation/suites/public-eval-v2.json`; new `evaluation/datasets/v2/golden_public.jsonl`, `unanswerable_public.jsonl`, `security_public.jsonl`; `evaluation/suites/public-eval-v1.json` (`status` only); `evaluation/candidates/006-candidates.jsonl` (`review.promoted_as` only). Nothing in `knowledge/` or `config/`.

### Verification

- `make validate-evaluation` → `validate-evaluation: OK, 0 problems`.
- `make eval-security` → PASS on v2 (result under `experiments/results/tmp/`).
- `make verify`.
- `git diff --stat -- evaluation/datasets/golden_public.jsonl evaluation/datasets/unanswerable_public.jsonl evaluation/datasets/security_public.jsonl` → empty.
- `git diff -- evaluation/suites/public-eval-v1.json` shows only the `status` line.
- `git status --porcelain -- evaluation knowledge config` matches the allowed list.

Review reading order: `evaluation/suites/public-eval-v2.json` → `git diff evaluation/suites/public-eval-v1.json` → `git diff evaluation/candidates/006-candidates.jsonl` → the six new rows in `evaluation/datasets/v2/golden_public.jsonl` → `evaluation/validate.py` → `evaluation/cli.py`, `retrieval_eval.py` → tests.

## T2 — v2 dense baseline (user-owned gate)

**State:** approved (2026-10-25)
**Requirements:** R2

T1 must be approved, committed and pushed on `spec/007` first. No lexical or hybrid task starts before T2 is approved.

- [x] The orchestrator asks the user to run, from a clean `spec/007` checkout:
  1. `make setup-bge-m3` (on a slow connection `UV_HTTP_TIMEOUT=600 make setup-bge-m3`);
  2. `QDRANT_COLLECTION_BASE=w2a-realcheck make eval-retrieval` (default suite v2, `top_k` 5, read-only on `w2a-realcheck-idx-v1`);
  3. `make setup`;
  and to report the result file name.
- [x] The implementer checks the file (scratch script outside the repository, not committed): `kind: retrieval_evaluation`, `schema_version` 2.0, suite `public-eval-v2` version 2, `retrieval_strategy: dense`, golden case count equal to the v2 manifest's active goldens, unanswerable `n` equal to the v2 unanswerable rows, `embedder_is_fake: false`, collection `w2a-realcheck-idx-v1`, `index_version: idx-v1`, `top_k: 5`, `document_count` equal to the eligible corpus size, `git_dirty: false`, `git_commit` equal to the T1 commit.
- [x] Continuity check (same scratch script): the shared goldens (same `case_id`, `case_version`) against `experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json`: hits and MRR over the shared cases, plus every case whose `hit` or `reciprocal_rank` differs, by `case_id`. Expected: 60 hits, MRR 0.8783 over 63 shared cases; differences explained as device noise (D038) or flagged to the user.
- [x] `make eval-compare BASE=<T2 file> CANDIDATE=<T2 file>` passes (readability sanity check).
- [x] Update `CURRENT_STATE.md`: the T2 file as the Spec 007 reference (overall, `en`, `mixed`, `ml` metrics, misses by `case_id`, device, latency), the continuity result, the v1 2.0 file as a closed reference.
- [x] The result file is committed with the task (it is the only new file under `experiments/results/`).

Allowed protected-path changes: none. New file: `experiments/results/retrieval-evaluation-idx-v1-<UTC>.json` (user-produced).

### Verification

- The scratch checks above, with their output pasted into the implementer hand-off.
- `make eval-compare BASE=<T2> CANDIDATE=<T2>` exit 0.
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: the T2 result file (header fields, metrics, `ml`/`mixed` slices) → the continuity output → `CURRENT_STATE.md` diff.

## T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`

**State:** approved (2026-10-26)
**Requirements:** R3, R4, R5, R14

- [x] `lexical/__init__.py`, `lexical/tokenizer.py`: `TOKENIZER_NAME`, `TOKENIZER_VERSION`, `tokenize`, `query_terms` returning `QueryTerms(terms, truncated)` with `MAX_QUERY_TERMS = 64` (design R3).
- [x] `lexical/store.py`, `lexical/build.py`: schema, `lexical_settings` (including `dense_identity`), `source_chunk_digest`, `build_lexical_index` (temp file, `os.replace`, cleanup on failure), `production_entries`, `LexicalIndex.open` (read-only URI), `bind_to(dense)`, `search(...)`, `LexicalIndexBindingError` (subclass of `IndexBindingError`) with rebuild advice.
- [x] `retrieval/index.py`: read-only `DenseIndex.chunk_identities()` (scroll; payload include `document_id`, `document_version`, `content_hash`; no text). No other change to `DenseIndex`.
- [x] `ingestion/config.py`: `RuntimeSettings.lexical_index_dir` from `W2A_LEXICAL_INDEX_DIR` (default `<repo-root>/.local/lexical`); not index-defining.
- [x] `lexical/cli.py` and `Makefile` target `index-lexical` (`LEXICAL_ARGS`, passes `--repo-root`); `.gitignore` adds `/.local/lexical/`.
- [x] Tests (`packages/rag/tests/lexical/`):
  - tokenizer pins: real Malayalam words from `business_008_public_samples` and the queries of `g064`–`g069` (read from the v2 golden file by `case_id`, tokens pinned per word), `dialogue-ൽ`, English with punctuation and digits, NFD equals NFC, ZWJ/ZWNJ dropped, **legacy chillu sequence → consonant + virama, not equal to the atomic chillu letter**, no language-code literal in the module;
  - `query_terms`: de-duplication, first-seen order, a query with more than 64 distinct terms gives the first 64 and `truncated=True`;
  - build: entries, settings fields, digest stability and order independence, atomic replace (old file intact after an injected failure, no temp file left), the production builder reads only eligible documents (consistency with `list_eligible_documents`) and never `tests/fixtures/security/`;
  - open/bind refusals: missing file, malformed settings, unknown schema version or kind, other tokenizer version, other collection or `index_version`, `dense_identity` mismatch (embedder revision), chunker field mismatch, chunk-set mismatch with counts (in-memory Qdrant built through `IngestionService` with the fake embedder); open never writes (file mtime and bytes unchanged);
  - CLI: exit 0 with the summary line and no absolute path or chunk text; exit 2 on a bad config; no Qdrant client constructed.

Allowed protected-path changes: none (`.gitignore` and `Makefile` are not protected paths).

### Verification

- `make verify`.
- Manual: `QDRANT_COLLECTION_BASE=w2a-t007-<hex> W2A_LEXICAL_INDEX_DIR=<scratch dir> make index-lexical` → exit 0, summary line; running it twice gives the same digest; `git status --porcelain` shows no file under `.local/` (ignored).
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: `lexical/tokenizer.py` + tokenizer tests → `lexical/store.py` (schema, settings, open, bind) → `lexical/build.py` → `retrieval/index.py` diff → `lexical/cli.py`, `Makefile`, `.gitignore`, `ingestion/config.py` → remaining tests.

## T4 — BM25 retriever and SQL access clause

**State:** approved (2026-10-27)
**Requirements:** R6, R14

- [x] `retrieval/base.py`: `Retriever` Protocol, `Strategy` (`StrEnum`), `validate_request` shared with `DenseRetriever` (same messages; `DenseRetriever` calls it, behavior unchanged).
- [x] `retrieval/access.py`: `build_sql_access_clause(access)` (design R6), next to `build_access_filter`.
- [x] `retrieval/models.py`: the additive default fields (design "Interfaces / models"), including `query_terms_truncated`.
- [x] `retrieval/bm25.py`: `BM25Retriever` (quoted terms joined by `OR`, no `MATCH` for zero terms, `check_hit` on every row, `score_kind: "bm25"`, dense identity from the bound index, `query_terms_truncated`).
- [x] Tests (`packages/rag/tests/retrieval/test_bm25.py`, `test_access.py` additions):
  - ranking on a synthetic `tmp_path` corpus; deterministic tie-break by `point_id`;
  - authorization: staff scope, other tenant, owned and missing-owner rows (`owner_present = 0`) that contain the query terms are never returned; a store that drops the clause (test double) makes `check_hit` raise `RetrievalAuthorizationError`;
  - both builders cover the same three conditions for the same `ResolvedAccess`, and a different policy changes both;
  - injection: hostile queries (`NEAR`, `AND`, `NOT`, `*`, `access_scope:staff`, unbalanced quotes, parentheses, SQL fragments); a spy on `LexicalIndex.search` and `sqlite3` `set_trace_callback` show the SQL text is constant and the `MATCH` argument is exactly the quoted `lexical-v1` terms; the raw query never appears;
  - zero-term query: zero hits, `search` not called;
  - truncation: more than 64 distinct terms → exactly 64 quoted terms reach `MATCH`, `query_terms_truncated` true;
  - query and `top_k` validation messages equal the dense ones;
  - existing dense tests: only additions of the new default fields; ranks, scores, IDs and order unchanged.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `git diff -- packages/rag/tests/retrieval/test_retriever.py packages/rag/tests/retrieval/test_index.py` shows only new default-field expectations (if any).
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: `retrieval/access.py` diff → `retrieval/bm25.py` → injection and authorization tests → `retrieval/base.py`, `models.py` → remaining tests and dense test diffs.

## T5 — RRF fusion, hybrid retriever and `config/retrieval.yaml`

**State:** not started
**Requirements:** R7, R8, R14

- [ ] `retrieval/fusion.py`: pure `rrf_fuse` and `FusedHit` (design R7).
- [ ] `retrieval/hybrid.py`: `HybridRetriever` (sequential legs at `candidate_depth`, no catch, cut to `top_k`, re-rank, `score_kind: "rrf"`, `leg_ranks`, `leg_latency_ms`, `query_terms_truncated` from the BM25 leg).
- [ ] `config/retrieval.yaml` (design R8, `default_strategy: dense`) and `retrieval/strategy.py`: `RetrievalConfig` (Pydantic, `extra="forbid"`), `load_retrieval_config`, `build_retriever(strategy, ...)` as the only strategy-to-retriever mapping.
- [ ] Tests (`test_fusion.py`, `test_hybrid.py`, `test_strategy.py`):
  - hand-computed fused scores and orders for two small legs, ties broken by best rank then `point_id`, weights;
  - empty BM25 leg (pure-`ml` query with no matching terms, and a zero-term query): hybrid order equals the dense order;
  - fail closed: a stub leg whose store returns a forbidden payload makes the hybrid query raise and return nothing; any other leg exception propagates (no single-leg fallback);
  - authorization is never applied after fusion: `rrf_fuse` receives only `RetrievedChunk`s from legs (type-level and spy test);
  - config validation: unknown key, unknown strategy, `k < 1`, weights missing a leg or not positive, `candidate_depth` out of 1–50, `method` other than `rrf`; the committed `config/retrieval.yaml` loads.

Allowed protected-path changes: new `config/retrieval.yaml`.

### Verification

- `make verify`.
- `git status --porcelain -- evaluation knowledge config` → only `?? config/retrieval.yaml`.

Review reading order: `retrieval/fusion.py` + fusion tests → `retrieval/hybrid.py` + fail-closed and empty-leg tests → `config/retrieval.yaml` → `retrieval/strategy.py` → remaining tests.

## T6 — Strategy option in the CLIs and result format 2.1

**State:** not started
**Requirements:** R8, R9, R14

- [ ] Before any T6 code change: capture a fixture of the dense evaluation result produced by the unchanged runner (fake embedder, in-memory Qdrant, fixed clock, patched `git_state` and `perf_counter`) under `packages/rag/tests/evaluation/fixtures/`, for the equivalence test.
- [ ] `retrieval/cli.py`: `--strategy` (choices from `Strategy`, default from `config/retrieval.yaml`), lexical open and bind for `bm25`/`hybrid`, header `strategy=`, hybrid leg ranks, truncation note; access unchanged.
- [ ] `evaluation/cli.py` `retrieval`: `--strategy`, lexical open and bind after the dense binding; `retrieval_eval.py` takes a `Retriever` and writes result 2.1 (design R9: strategy, score kind, fusion, lexical identity, `leg_ranks`, `query_terms_truncated`, `truncated_query_count`, per-leg latency, `unanswerable.score_kind`).
- [ ] `evaluation/results.py`: supports 1.0, 2.0 and 2.1 (1.0/2.0 read as strategy `dense`, no lexical identity).
- [ ] Tests:
  - dense equivalence: the 2.1 dense result's per-case 2.0 fields and aggregates equal the captured fixture;
  - 2.1 keys for each strategy; no query or chunk text, absolute paths or secrets; never overwritten;
  - `leg_ranks` for relevant documents; truncation flag and count with a synthetic long query;
  - CLI exit codes: unknown strategy, missing lexical file, lexical mismatch, fake embedder still refused by `eval-retrieval`; `make retrieve --strategy hybrid --embedder fake` output format;
  - reading the committed 1.0 and 2.0 files and a 2.1 file.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- Manual (Docker, fake): `QDRANT_COLLECTION_BASE=w2a-t007-<hex> make ingest INGEST_ARGS="--embedder fake"`, the same base with `W2A_LEXICAL_INDEX_DIR=<scratch dir> make index-lexical`, then `make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --strategy hybrid"` and `--strategy bm25` → exit 0, strategy in the header, leg ranks; delete the throwaway collections afterwards.
- The real dense 2.1 equivalence (a real dense 2.1 run must pass `eval-compare` against the T2 baseline with no flips) is user-owned and is the **first step of T9**, because it needs T7's compare rules too. T6's deterministic equivalence test is the agent-side guard.
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: equivalence fixture and test → `evaluation/retrieval_eval.py` diff → `evaluation/results.py` → `evaluation/cli.py` diff → `retrieval/cli.py` diff → remaining tests.

## T7 — `eval-compare` identity rules

**State:** not started
**Requirements:** R10

- [ ] `evaluation/results.py`: `ComparableRun.info` gains `retrieval_strategy`, `embedder_model_id`, `embedder_revision`, `lexical`.
- [ ] `evaluation/compare.py`: the R10 table in the design (collection with the missing-collection rule, `index_version`, embedder, lexical identity, strategy identity line), new next-step text.
- [ ] Tests (`test_compare.py` additions):
  - the committed pair `retrieval-baseline-idx-v1-20261023T063534Z.json` (1.0) vs `retrieval-evaluation-idx-v1-20261024T193140Z.json` (2.0) passes (read from the repository, not modified);
  - dense vs hybrid (2.1) on the same identity passes with a `retrieval_strategy` identity line;
  - a collection difference is refused naming both collections;
  - a file with no collection (absent and `null`) is compared by `index_version` only, with the information line naming that file; an `index_version` difference is still refused;
  - embedder model or revision difference refused;
  - both lexical: digest or tokenizer difference refused; dense vs bm25 not refused (identity line);
  - existing refusals and the gate rule unchanged.

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make eval-compare BASE=experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` → exit 0.
- `make eval-compare BASE=<T2 file> CANDIDATE=experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` → exit 2, `not comparable:` (suite changed).
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: `evaluation/compare.py` diff → `evaluation/results.py` diff → tests.

## T8 — Security gate for BM25 and hybrid, Docker isolation test

**State:** not started
**Requirements:** R11, R12, R14

- [ ] `evaluation/security_index.py`: lexical file in the work directory with the same point IDs as the throwaway collection (seed, canary and probes, forbidden rows with the query's terms repeated 3 times, `missing_owner` without the key), opened and bound through the production `LexicalIndex`.
- [ ] `evaluation/security_eval.py`: per-leg unfiltered sanity checks (zero-term queries counted in `bm25_no_term_queries`), gate over `dense`, `bm25`, `hybrid` through `build_retriever` at `top_k` 50, violations with `strategy`, security result 1.1.
- [ ] `evaluation/cli.py` `security`: the lexical file lives and is removed with the existing `TemporaryDirectory`; summary names the strategies.
- [ ] Tests (`test_security_eval.py` additions):
  - the gate passes on v2 for all three strategies;
  - a lexical sanity-check failure (forbidden rows without the query terms) is a harness error (exit 2);
  - a BM25 store that drops the SQL clause produces violations (exit 1) naming `bm25` and `hybrid`;
  - the missing-owner row is excluded by `owner_present` (no `check_hit` violation in a correct run);
  - security result 1.1 keys, no text; the lexical file is gone after a run, including a failed one.
- [ ] `packages/rag/tests/evaluation/test_security_integration.py`: parametrized over the three strategies on Docker Qdrant (unique `w2a-sectest-<8 hex>`, lexical file in `tmp_path`, cleanup in `finally`, skip when Qdrant is unreachable).

Allowed protected-path changes: none.

### Verification

- `make verify`.
- `make eval-security` → PASS, three strategies listed.
- `make test-integration` (Docker Qdrant running) → all pass; `curl -s localhost:6333/collections` before and after shows no new `w2a-sectest-*` and the `w2a-realcheck-*` collections unchanged.
- `git status --porcelain -- evaluation knowledge config` → empty.

Review reading order: `evaluation/security_index.py` diff → `evaluation/security_eval.py` diff → sanity-check and violation tests → Docker test → `evaluation/cli.py` diff.

## T9 — Strategy comparison and default-strategy decision (user-owned gate)

**State:** not started
**Requirements:** R13

T1–T8 must be approved, committed and pushed on `spec/007` first.

- [ ] The orchestrator asks the user to run, from a clean `spec/007` checkout, with `QDRANT_COLLECTION_BASE=w2a-realcheck`:
  1. `make setup-bge-m3`;
  2. `make eval-retrieval EVAL_ARGS="--strategy dense"` then `make eval-compare BASE=<T2 file> CANDIDATE=<dense 2.1 file>`: must exit 0 with **no** `WARNING flipped` line. If not, stop here; the dense change goes back to T4/T6 through `changes requested`;
  3. `make index-lexical` (writes only the local git-ignored file; no Qdrant writes);
  4. `make eval-retrieval EVAL_ARGS="--strategy bm25"` and `make eval-retrieval EVAL_ARGS="--strategy hybrid"`;
  5. `make eval-compare BASE=<T2 file> CANDIDATE=<hybrid file>` and the same for the BM25 file (informational);
  6. `make setup`;
  and to report the file names and the compare output.
- [ ] The implementer checks each file like T2 (suite v2, not fake, `git_dirty: false`, same collection, `index_version`, embedder, `top_k`, document count, strategy as named, lexical identity present for `bm25`/`hybrid`).
- [ ] Apply the R13 rule from the per-case rows (scratch script): hybrid passes the gate; hybrid improves hits or MRR over T2; no `ml` or `mixed` case flips hit to miss. Only if all three hold, set `default_strategy: hybrid` in `config/retrieval.yaml`; otherwise leave `dense`.
- [ ] Record in `CURRENT_STATE.md`: overall, `en`, `mixed`, `ml` for dense (T2 and 2.1), BM25 and hybrid; every flip by `case_id`; `g004`, `g026`, `g061`; per-leg latency; truncated query count; the rule outcome. The decision text itself is written in T10.
- [ ] Commit the four result files with the task.
- [ ] If the default changes, tests that depend on the default read it from `config/retrieval.yaml` (no literal); `make verify` passes.

Allowed protected-path changes: `config/retrieval.yaml` (`default_strategy` line only, and only if the R13 rule holds). New files: the dense 2.1, BM25 and hybrid result files under `experiments/results/`.

### Verification

- The user's compare outputs (step 2 with no flips; step 5) pasted into the hand-off.
- The scratch rule check output.
- `make verify`.
- `git status --porcelain -- evaluation knowledge config` → empty, or only `M config/retrieval.yaml` with the one-line diff.

Review reading order: compare outputs (step 2, step 5) → the rule check (ml/mixed flips) → `git diff config/retrieval.yaml` (if any) → `CURRENT_STATE.md` diff → result file headers.

## T10 — Documentation, decisions and hand-off

**State:** not started
**Requirements:** R15, R14, Definition of Done

- [ ] `DECISIONS.md` from D049: v2 suite promotion and the closed v1 reference; SQLite FTS5 lexical store (vs Qdrant sparse), location, binding, `dense_identity` copy (self-describing file); `lexical-v1` tokenizer rule (ZWJ/ZWNJ dropped, legacy chillu distinct from atomic); RRF parameters, sequential legs, fail-closed fusion, empty-leg rule; result 2.1 and security 1.1; the `eval-compare` identity rules (missing-collection rule, lexical identity); corpus-wide BM25 statistics and future roles; the T9 default-strategy outcome with its numbers.
- [ ] `ARCHITECTURE.md` (retrieval section with the `lexical/` package and both legs; target flow marks dense, BM25 and RRF implemented), `COMMANDS.md` (`make index-lexical`, `W2A_LEXICAL_INDEX_DIR`, `--strategy`, new refusals, result 2.1, security coverage), `TECH_STACK.md` (FTS5 as BM25 store, no new dependency), `CURRENT_STATE.md` (implemented reality, spec status row, known issues).
- [ ] Known issues in `CURRENT_STATE.md`: legacy chillu sequences do not match atomic chillu in `lexical-v1` (roadmap 8; dense unaffected); `seed-v1` release still names suite v1 (Phase 2 releases); BM25 needs Qdrant and the `bge-m3` extra in this spec.
- [ ] T1 review F1 (user decision 2026-10-25): remove the unused `LEGACY_SUITE` constant from `packages/rag/tests/conftest.py`, or use it in `packages/rag/tests/retrieval/test_baseline.py` instead of the literal v1 suite path (implementer's choice; one test-only edit).
- [ ] T3 round 3 review F1 (user decision 2026-10-26): in `packages/rag/src/way2australia_rag/lexical/cli.py`, `check_target_allowed` allows only targets that `git check-ignore` reports as ignored (inside a git work tree), replacing the tracked-file check; the protected `knowledge/`, `evaluation/`, `config/` guard (by real on-disk location) stays. Add a test that an existing un-ignored folder such as `.local/other/` is refused (exit 2, nothing written).
- [ ] "Notes for the retrospective" (below) checked and extended with anything learned during implementation.
- [ ] Spec-wide checks and protected-path check against `main`.
- [ ] `graphify update .` after the last code change; doc changes refreshed per D048 if the user asks.

Allowed protected-path changes: none (docs only).

### Verification

- `make verify`, `make test-integration`, `make eval-security`.
- `git diff --name-status main...HEAD -- evaluation knowledge config` → exactly: `A evaluation/suites/public-eval-v2.json`, `A evaluation/datasets/v2/golden_public.jsonl`, `A evaluation/datasets/v2/unanswerable_public.jsonl`, `A evaluation/datasets/v2/security_public.jsonl`, `M evaluation/suites/public-eval-v1.json`, `M evaluation/candidates/006-candidates.jsonl`, `A config/retrieval.yaml`; nothing under `knowledge/`.
- Docs match the code (reviewer reads them against the files).

Review reading order: `DECISIONS.md` diff → `ARCHITECTURE.md` → `COMMANDS.md` → `TECH_STACK.md` → `CURRENT_STATE.md` → protected-path output.

## Out of this spec

Do not implement in this spec:
- Graceful degradation (roadmap 13): no fallback from dense to BM25 or from Qdrant to FTS5, no BM25 run without Qdrant.
- Qdrant sparse vectors, BGE-M3 sparse weights, SPLADE; server-side Qdrant fusion.
- Stemming, stopwords, transliteration, legacy-chillu mapping, language detection or filtering (roadmap 8).
- Reranking, context building, generation, Langfuse, an HTTP route, CI workflows.
- Chunking changes, a new dense `index_version`, re-ingestion, `relevant_section_ids`.
- The Phase 2 "compare shared cases" mode, new Knowledge Releases, approval workflows, edits to `knowledge/`.
- Evaluation changes beyond T1; activation of other candidates.
- Non-guest roles, device pinning, the open Spec 004 nits and Spec 006 retrospective F1 (unless a task touches the same code).

## Notes for the retrospective

Not a task. The `spec-reviewer` carries these into "Notes for the next spec" in `review.md`.

- BM25 must be able to run without Qdrant (and without the `bge-m3` extra) before it can serve as the FTS5 fallback (roadmap 13). The `dense_identity` copy in the lexical settings is the starting point; the binding to Qdrant then becomes optional for the fallback path only, with the same `ResolvedAccess` and `check_hit`.
- `lexical-v1` keeps legacy chillu sequences distinct from atomic chillu letters; revisit with multilingual retrieval (roadmap 8).
- BM25 statistics are corpus-wide per file; a roles spec needs per-scope files or an accepted statistics leak.
- The Phase 2 "compare shared cases" mode is still not built; v1 results are a closed reference.
