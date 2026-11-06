# Current State

Last updated: 2026-11-06 (Spec 011 T1–T5 approved on `spec/011`; reranking promoted at depth 20; D073–D074)

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Specs **001–010** are **verified on `main`** (Spec 010 merged 2026-11-04, fast-forward to **`cae06c3`**). Default production index **`idx-v2`** / recursive 128+title (D071): run **`make ingest`**, then **`make index-lexical`** with default **`lexical-v2`** tokenizer (D072; settings 1.2; rebuild once if upgrading from 1.1 for `--lote`). Hybrid default retrieval needs the lexical file. Ignored stale `knowledge_release_id` / `evaluation_suite_id` keys remain on the promoted yaml until the next `index_version` (D071 carry-over). Verify-budget hook in-repo (**D073**); pytest-xdist **not** adopted for default verify (**D074**); follow-up **`pytest --durations=25`** still open. **Spec 011** (roadmap item 9, multilingual reranking; context building deferred to item 10) is **planned and approved** (requirements, design, tasks 2026-11-04) on branch **`spec/011`** (base `3b81508`); no task started. **Spec 011 progress (2026-11-05):** T1 (reranker contract, adapters, config; revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`), T2 (`RerankingRetriever`, skip policy, `--rerank`), T3 (result 2.5, compare, continuity) and T4 (security gate, eight paths, security 1.5) and T5 (user-run real evaluation, **reranking promoted at depth 20**: `rerank.enabled: true`, MRR 0.9228 → 0.9751, p95 +920.6 ms on `mps:0`) approved; R4 re-check amended to membership wording. **Next:** T6 (docs, decisions D075+, As-built notes, hand-off; amended 2026-11-06 with two required CLI tests and the promotion docs), then the required `spec-reviewer` retrospective. **No HTTP-route spec yet:** Spec 008 serving items belong with roadmap **item 10 (grounded generation)**. Repository-based shared context keeps Codex, Claude Code, Cursor and Kiro interchangeable (D063).

## Finalized high-level decisions

- Python/FastAPI backend.
- Next.js/TypeScript frontend.
- RAG under `packages/rag/`.
- Shared domain concepts under `packages/core/`.
- Public/guest retrieval only in Phase 1.
- English + Malayalam initially; future CCL languages through metadata/config.
- `DocumentRepository` abstraction from the beginning.
- `LocalDocumentRepository` in Phase 1.
- S3-backed repository planned for Phase 2.
- Qdrant primary retrieval.
- SQLite FTS5 fallback.
- BGE-M3 initial embeddings.
- BM25 + RRF hybrid retrieval (Spec 007, merged; default strategy `hybrid`, D055); `hybrid` degrades to BM25 when Qdrant or the embedding model is unreachable (Spec 008, merged).
- multilingual reranking planned.
- Amazon Bedrock Runtime for generation.
- Langfuse for RAG tracing.
- CloudWatch for operations.
- Terraform for AWS infrastructure.
- AWS Mumbai (`ap-south-1`) deployment target.
- GitHub Actions for CI/CD.
- Evaluation Suite includes goldens, unanswerable/refusal, multilingual, security and regression cases.
- Phase 2 Knowledge Release workflow/evaluation governance are designed but not implemented.
- Basic product analytics are Phase 2 only.

## Seed data status

Latest seed design includes:
- normalized public business knowledge;
- normalized official knowledge;
- Malayalam-specific official policy;
- structured owner-approved FAQ pairs;
- document manifest/inventory;
- document metadata schema;
- lightweight initial Knowledge Release;
- versioned evaluation datasets;
- Evaluation Suite manifest;
- evaluation schema;
- security fixtures;
- source-precedence/access/language configuration;
- Phase 2 analytics event schema.

## Current implementation status

Implemented:
- Python 3.12 workspace metadata using `uv`;
- reproducible dependency lockfile (`uv.lock`);
- root `make setup` command;
- FastAPI application package skeleton;
- minimal `GET /health` endpoint that starts locally and does not depend on RAG/Qdrant services;
- typed runtime settings for foundation API configuration;
- pytest foundation with health and configuration tests;
- `make test`, `make test-unit` and `make test-integration` commands;
- Ruff, Pyright and `make verify` quality command surface;
- local Qdrant Docker Compose service with persistent named volume;
- reusable package skeletons for `packages/core`, `packages/rag` and `packages/observability`;
- repository hygiene for local environment files, Python caches, local uv state and generated OS noise;
- final Spec 001 verification and handoff;
- task-gated spec-driven skills (`spec-orchestrator`, `spec-planner`, `spec-implementer`, `task-reviewer`, and the `spec-reviewer` retrospective, required since D031), with canonical source in `agent-skills/`, mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/` by `make skills-sync`, and checked by `make skills-check` (part of `make verify`); Cursor loads those same `.claude/skills/` and `.agents/skills/` mirrors (no extra `.cursor/skills/` target, D063); exercised on real work by Spec 002 T3–T9 (Spec 003 dry run, recorded in its T9);
- task state lifecycle (`**State:**` lines, `task-reviews.md`, `spec/<NNN>` branches, `Spec-Task` trailers) and spec `Status:` values defined in `docs/project/WORKFLOW.md`, decision D023;
- `CLAUDE.md` imports only `AGENTS.md` and this file; other docs are read per role;
- `Makefile` uses a standalone `uv` binary when available and falls back to `python3 -m uv`;
- Spec 002 (merged to `main`): Pydantic document models and enums in `packages/core/documents`; `DocumentRepository` Protocol and `LocalDocumentRepository` with manifest JSON Schema validation, frontmatter parsing and `content-hash-v1` hashing; `EligibilityPolicy` for guest/public retrieval; `make validate-knowledge` (part of `make verify`); repository, hashing, eligibility, seed-corpus and isolated security-fixture tests.

- Spec 004 (merged to `main`, `dde5b35`): ingestion baseline in `packages/rag/src/way2australia_rag/ingestion/`: `HeadingChunker` (`heading` v1, 2000-character cap, stable `section_id` slugs), `Embedder` Protocol with a deterministic fake and a BGE-M3 adapter (optional `bge-m3` extra, pinned model revision), `IndexSettings` and a 17-field `PointPayload`, UUIDv5 point IDs, `QdrantIndexStore` (companion `<collection>-settings` collection, refusal on settings mismatch), `IngestionService` (change detection by `content_hash`, document version and point-ID set; stale deletion; per-document failures), `config/ingestion.yaml`, CLI and `make ingest` (`INGEST_ARGS` pass-through, `--embedder fake`), `make setup-bge-m3`; unit tests (no Docker, no PyTorch) and Docker Qdrant integration tests;
- the seed corpus (13 public documents, one chunk each) ingests into Qdrant; with the fake embedder a second run reports 0 added, updated and deleted.

- Spec 005 (merged to `main`, `b33462e`): dense retrieval baseline.
  - `AccessContext` and `Role` in `packages/core` (blank tenant refused); `W2A_TENANT_ID` server setting (empty refused; shared `load_runtime_settings` used by ingestion and both retrieval CLIs).
  - `packages/rag/src/way2australia_rag/retrieval/`: read-only `DenseIndex` (binding to the index and its recorded settings, embedder fields compared), `build_access_filter` (scope, tenant, null owner) with the fail-closed `check_hit` re-check, `DenseRetriever`, `safe_text`.
  - `make retrieve QUERY=...`: guest/public dense search CLI.
  - `make retrieval-baseline`: document-level HitRate@k, Recall@k and MRR over the 63 `public-eval-v1` golden cases, p50/p95 latency after a warm-up, `min(1, k/N)` random expectation, JSON written to `experiments/results/` (never overwritten; a fake index needs `--allow-fake`).
  - `make lint` also runs `ruff format --check`; `UV_HTTP_TIMEOUT` defaults to 300 in the `Makefile`; payload indexes are re-created on the exists-empty-no-settings path.
  - Decisions D033 to D041 (D040 and D041 added by the retrospective). `make verify` without the `bge-m3` extra: 446 passed, 1 skipped; `make test-integration`: 19 passed against the running Qdrant (re-run by the retrospective, 2026-10-23).

- Spec 006 (merged to `main`, `ab28d89`): evaluation framework in `packages/rag/src/way2australia_rag/evaluation/`.
  - Governed read-only suite loader (`suite.py`, tolerant models) and two new schema files under `evaluation/schemas/`; `make validate-evaluation` (part of `make verify`) checks schemas, cross-checks, relevant-document existence and eligibility, and candidate rows.
  - `make eval-retrieval`: active goldens and unanswerable cases through `DenseRetriever`; result format 2.0 (`retrieval_evaluation`) with query-language, category and source-authority slices, `small_sample` flags, absent languages, section-level block, unanswerable top-1 score distribution (informational); refuses a fake embedder or index and a suite that is not `active`.
  - `make eval-security`: authorization hard gate on a throwaway in-memory `w2a-sectest-*` collection with the fake embedder (forbidden points nearest to every query, unfiltered sanity check, `top_k` 50); Docker isolation integration test.
  - `make eval-compare BASE=... CANDIDATE=...`: reads 1.0 and 2.0 results; gate: more than 1 fewer hit cases, or an MRR drop above `1/n`, fails; flips are warnings.
  - `make retrieval-baseline` is legacy and frozen (characterization test on a frozen fixture copy); the only `retrieval/` changes are the `goldens.py` wrapper and `RetrievalAuthorizationError.document_id`.
  - `evaluation/candidates/006-candidates.jsonl`: 7 `suggested` candidate rows (6 agent-drafted Malayalam golden rows, 1 change proposal for `g004`/`u001`); never loaded as cases.
  - Decisions D042 to D046, plus D047 (security result format, added by the retrospective). `referencing` is a direct `packages/rag` dependency.

- Spec 007 (merged to `main`, `3cf70eb`; T1–T10 approved, retrospective round 1 `PASS`): hybrid retrieval.
  - Suite `public-eval-v2` (91 cases; six approved Malayalam goldens `g064`–`g069`); v1 is `replaced`, its 2.0 result is a closed reference (D049).
  - `packages/rag/.../lexical/`: `lexical-v1` tokenizer, SQLite FTS5 store (`chunks` plus `chunk_terms`, settings with a `dense_identity` copy), atomic builder, `make index-lexical` (git-ignored target only; `W2A_LEXICAL_INDEX_DIR`, default `.local/lexical`) (D050, D051).
  - `retrieval/`: `Strategy` and `Retriever` Protocol (`base.py`), `BM25Retriever` with the SQL access clause (`build_sql_access_clause`), pure `rrf_fuse`, `HybridRetriever`, `config/retrieval.yaml` (`default_strategy: hybrid`, RRF `k` 60, equal weights, depth 50), `build_retriever` (D052).
  - `make retrieve` and `make eval-retrieval` take `--strategy`; result format 2.1; `eval-compare` identity refusals (collection, `index_version`, embedder pair, lexical identity, `lexical_index` object on bm25/hybrid files); `eval-security` gates `dense`, `bm25` and `hybrid` with a throwaway lexical file, security result 1.1 (D053, D054).
  - Default strategy `hybrid`, from the real runs of 2026-10-28 (Next step item 4): hybrid 68 of 69 goldens, MRR 0.9094 vs dense 66 and 0.8816 (D055). After Spec 009 T6 (2026-11-03), default index is **`idx-v2`** / recursive 128+title (hybrid MRR 0.9208 on realcheck arm vs 0.9094 baseline; see Next step item 9). Setup order for the default: `make ingest`, then `make index-lexical`; without the lexical file `make retrieve` and `make eval-retrieval` (no `--strategy`) exit 2, naming `make index-lexical` (tested).
  - `git_state` no longer counts untracked files under `experiments/results/` as dirty (T9 review decision).
  - `make verify` at T10: 864 passed, 1 skipped; `make test-integration`: 22 passed (Docker Qdrant); `make eval-security`: PASS for `dense`, `bm25` and `hybrid`. Re-run by the retrospective (2026-10-28) with the same counts.
  - The production lexical file holds only eligible guest/public chunks, so its corpus-wide BM25 statistics (IDF, average length) reveal nothing; a future roles spec needs one lexical file per access scope (D050).

- Spec 008 (merged to `main`, `1107b67`; T1–T8 approved, retrospective round 1 `PASS`): retrieval fallback.
  - `retrieval/errors.py`, `availability.py`: `RetrievalUnavailableError(reason)` (`qdrant_unavailable`, `qdrant_timeout`, `model_unavailable`) is the only fallback-eligible error; `classify_qdrant_error` unwraps one level through `ResponseHandlingException` only; `classify_model_error` needs a network or timeout error in the explicit `__cause__` chain; `__context__` is never followed; Qdrant HTTP status errors including 5xx are not eligible (D057, D062).
  - `config/retrieval.yaml` schema 1.1 (`qdrant.connect_timeout_s` 2, `query_timeout_s` 3); `retrieval_client_factory` (`check_compatibility=False`) (D059).
  - `bm25` needs neither Qdrant nor the `bge-m3` extra: `IndexIdentity`, `LexicalIndex.check_identity`, `lexical/freshness.py` (`verify_fresh`, digest recomputed from the repository), `open_standalone_lexical`, `BM25Retriever(identity, lexical)` (D060).
  - `FallbackRetriever` wraps `HybridRetriever` (hybrid only; per query after a successful open; an open-time outage makes BM25 serve the whole run; no circuit breaker; same `ResolvedAccess` object and `top_k`); `open_retrieval` is the one wiring function for `make retrieve` and `make eval-retrieval`; fusion and `HybridRetriever` unchanged (D058).
  - `make retrieve` prints `strategy: bm25 (requested: hybrid; fallback: <reason>)` and a stderr warning only on fallback; `make eval-retrieval` writes result 2.2 (served strategies, fallback counts, latency by served path, `dense_identity`, `index_settings` null when Qdrant was never reached); `make eval-compare` reads 2.2, compares by served strategy and refuses mixed files; `make eval-security` gates five paths (`dense`, standalone `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`), security result 1.2 (D061).
  - Real runs (T7): fallback-only run equals the Spec 007 BM25 reference (64 hits, MRR 0.7082), Qdrant-up run equals the Spec 007 hybrid reference (68 hits, MRR 0.9094); see Next step item 6.
  - Decisions D056 to D062. `make verify` at T8 (2026-11-01): 1026 passed, 2 skipped (no `bge-m3` extra); `make test-integration`: 24 passed (Docker Qdrant); `make eval-security`: PASS on all five paths; `git diff --name-status main...HEAD -- evaluation knowledge config` lists only `config/retrieval.yaml`. Re-run by the retrospective (2026-11-01) with the same counts; both T7 `eval-compare` runs re-run, same results.

- Spec 009 (**verified 2026-11-04, merged `5a6deb7`**): chunking experiments (T1–T7 approved 2026-11-03; required `spec-reviewer` retrospective round 1 `PASS`, approved 2026-11-04).
  - Tokenizer and truncation guard (`tokenization.py`, `guard.py`); `structure` v1 and `recursive` v1 chunkers; `ChunkerIdentity`; `IndexSettings` and lexical settings 1.1; per-document `verify_fresh`; distinct-document metrics and result 2.3; `eval-compare --cross-index`; security result 1.3 over three chunkers; experiment configs under `experiments/configs/chunking/`.
  - T6 promoted default index to **`idx-v2`** / `recursive` 128+title (D071); operator setup **`make ingest`** then **`make index-lexical`** on default `config/ingestion.yaml` (real lexical build needs BGE-M3 tokenizer files); `config/ingestion.yaml` matches `recursive-128.yaml` byte-for-byte for the arm hash.
  - Decisions D064–D071 (D063 is Cursor tooling on `main`). T7 documents and closes Spec 004 carry-overs (public `chunk_identity`, settings docstring, wrong-vector-count test).
  - Carry-overs live under **Known issues / deferred** (Spec 009 block) and `.kiro/specs/009-chunking-experiments/review.md` Notes for the next spec.

- Spec 010 (**verified 2026-11-04, merged `cae06c3`**; branch `spec/010`; T1–T6 approved; required `spec-reviewer` retrospective round 1 `PASS`, approved 2026-11-04):
  - Suite **`public-eval-v3`** (default for `make eval-retrieval` / `eval-security`); v2 `replaced`; v3 hybrid/bm25 refs `…20261104T105300Z.json` / `…20261104T105321Z.json`.
  - `languages.py` (package root), `retrieval/applicability.py`: optional `--lote` on every path including fallback; lexical settings **1.2**; default tokenizer **`lexical-v2`** (D072).
  - Result **2.4**; `eval-compare --cross-tokenizer`; `make eval-continuity`; security **1.4**.
  - Retrospective: `.kiro/specs/010-multilingual-retrieval/review.md` (Notes for the next spec → Spec 011 / verify-budget).

Not yet implemented:
- reranking; no HTTP retrieval route; retrieval degradation exists only for `hybrid` (Spec 008); the reranker and model-failure paths of roadmap 13 are not implemented (no reranker or generation yet);
- a recorded real BGE-M3 retrieval baseline, recorded in `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (commit `7418812`; BAAI/bge-m3 @ `5617a9f`, device `mps:0`, index `w2a-realcheck-idx-v1`): 63 cases, N=13; HitRate@5 0.952 vs random 0.385 (`min(1, 5/13)`), Recall@5 0.952, MRR 0.878; `en` (54) HitRate 0.963 / MRR 0.910, `mixed` (9) HitRate 0.889 / MRR 0.685; p50 61.5 ms, p95 216.5 ms (warm-up 105.9 s excluded); misses `g004`, `g026`, `g061`;
- the Phase 2 "compare shared cases" mode of `eval-compare` (today any difference in the case set is refused);
- generation;
- observability;
- CI/CD;
- Terraform deployment.

## Spec status

| Spec | Status |
|---|---|
| 001 — project foundation | implemented; completed before the review process existed (no `review.md`) |
| 002 — document model and repository | **verified (2026-10-15, merged dca6cbd)**; branch `spec/002` (base `869c37f`; T1–T2 on `main`, approved without task review). T3 (the Spec 003 T9 dry run) approved 2026-10-14 after task review round 1 PASS: manifest loading and metadata validation in `packages/rag/.../repositories/manifest.py` and `frontmatter.py`, new deps `jsonschema` and `pyyaml`. T4 approved 2026-10-14 (LocalDocumentRepository; placeholder content_hash until T5); T5 approved 2026-10-14 (content-hash-v1 and manifest hash verification); T6 approved 2026-10-15 (eligibility policy); T7 approved 2026-10-15 (`make validate-knowledge`); T8 approved 2026-10-15 (isolated security repository, seed corpus tests); T9 approved 2026-10-15 (documentation and handoff); merged to `main` |
| 003 — task-gated agent workflow | **verified** (2026-10-15, bootstrap exception: implemented directly on `main`, base `9e95cfe`); dry run on Spec 002 recorded in its T9; T1–T8 closed by the user's instruction to close the spec, without per-task review records |
| 004 — ingestion baseline | **verified (2026-10-17, merged dde5b35)**; merged at the user's request before the retrospective; required `spec-reviewer` retrospective round 1 `PASS`, approved by the user 2026-10-17; branch `spec/004` (base `af659da`); T1 approved 2026-10-15 (shared strict date check, policy-vs-config test); T2 approved 2026-10-15 (heading chunker, `section_id` slug rule recorded in design); T3 approved 2026-10-15 (`Embedder` Protocol and deterministic fake); T4 approved 2026-10-16 (BGE-M3 adapter, optional `bge-m3` extra, pinned revision; real-model smoke test skipped, user-owned); T5 approved 2026-10-16 (index settings, 17-field payload, UUIDv5 point identity); T6 approved 2026-10-16 (`QdrantIndexStore`, companion settings collection, Docker integration test); T7 approved 2026-10-16 (`IngestionService`, change detection, run report); T8 approved 2026-10-16 (`config/ingestion.yaml`, CLI, `make ingest`, day1_baseline agreement tests); T9 approved 2026-10-17 (docs, decisions and handoff). User-owned pre-merge check (not a gate): one real BGE-M3 ingestion of the seed corpus into a throwaway collection, run twice, plus the opt-in smoke test |
| 005 — dense retrieval baseline | **verified (2026-10-23, merged b33462e)**; required `spec-reviewer` retrospective round 1 `PASS`, approved by the user 2026-10-23; branch `spec/005` (base `2f98ef9`); T1 approved 2026-10-20 (payload-index re-creation, Docker index assertions, `ruff format --check` gate, two-way scope check); T2 approved 2026-10-20 (`AccessContext`/`Role`, `W2A_TENANT_ID`, guest resolver, single access filter, fail-closed `check_hit`); T3 approved 2026-10-20 (read-only `DenseIndex` binding, public `read_index_settings`); T4 approved 2026-10-20 (`DenseRetriever`, fail-closed re-check, isolation tests, `Embedder.device`); T5 approved 2026-10-20 (`make retrieve` CLI, shared settings loader, retrieval-side refusal advice); T6 approved 2026-10-21 (metrics, golden loader, `make retrieval-baseline`, `safe_text`); T7 approved 2026-10-23 (docs, decisions D033–D039, deferred review fixes). Retrospective round 1 `PASS` (docs reconciled: TECH_STACK, ARCHITECTURE target flow, D040–D041, design As-built notes); approved by the user and merged 2026-10-23. Real BGE-M3 baseline done by the user 2026-10-23 (`experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json`) |
| 006 — evaluation framework | **verified (2026-10-24, merged ab28d89)**; branch `spec/006` (base `a400bab`); required `spec-reviewer` retrospective round 1 `PASS`, approved by the user 2026-10-24; T1 approved 2026-10-23 (frozen-fixture legacy snapshot, read-only suite loader, `goldens.py` wrapper); T2 approved 2026-10-23 (evaluation schemas, `make validate-evaluation`); T3 approved 2026-10-24 (retrieval evaluation runner, result 2.0, `make eval-retrieval`); T4 approved 2026-10-24 (unanswerable score reporting); T5 approved 2026-10-24 (security corpus builder, `make eval-security` hard gate, Docker isolation test); T6 approved 2026-10-24 (`make eval-compare`, 1/n MRR gate, refusal messages); T7 approved 2026-10-24 (candidate cases file, agent-drafted Malayalam rows pending fluent-speaker review); T8 split into T8a (deferred code/test fixes) and T8b (docs, decisions, hand-off) by the 2026-10-24 amendment; T8a approved 2026-10-24 (deferred review fixes, live-count clean-up); T8b approved 2026-10-24 (docs, decisions D042 to D046, `.gitignore` `/MANIFEST`, two test fixes). Task-review findings: fixed in code or tests (T8a, T8b): T1 F4 (in T3/T5), T2 F1/F2/F3/F5, T3 F1, T4 F1, T5 F1/F4, T6 F1/F3/F5, T7 F1/F3, T8a F1/F2; recorded in docs only (design, `COMMANDS.md`, `ARCHITECTURE.md`, decisions): T1 F1/F2, T2 F4, T3 F2/F3, T5 F2/F3, T8b F1/F2 (reconciled by the retrospective); closed by user decision without a fix: T1 F3 (`.gitignore` negation acknowledged; later replaced by the T8b `/MANIFEST` anchor), T6 F2 (the 10-key cap is per list), T6 F4 (flip lines print `g002 v1`; recorded in the design As-built notes), T7 F2 (`NAATI CCL` in Latin script in `cand006_ml_001`, left for the fluent speaker), and the T7 owner-review item (the existing `requires_review: ["owner_review"]` accepted, test only). Awaiting human review, outside this spec: the 6 agent-drafted Malayalam candidates (fluent-speaker correction, then owner approval) and the `g004`/`u001` change proposal (owner decision). Post-merge check done by the user 2026-10-24: the real `make eval-retrieval` run (`experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json`) compared with the Spec 005 baseline by `make eval-compare` passed (hits 60 -> 60, MRR 0.8783 -> 0.8783, no flips); that file is the 2.0 baseline for suite `public-eval-v1` v1 |
| 007 — hybrid retrieval | **verified (2026-10-28, merged 3cf70eb)**; required `spec-reviewer` retrospective round 1 `PASS`, approved by the user 2026-10-28; branch `spec/007` (base `06b1af9`); approved 2026-10-25: requirements, design and tasks approved (10 tasks: T1 suite `public-eval-v2` (91 cases, six approved Malayalam candidates promoted), T2 user-owned real dense baseline on v2, T3–T8 lexical BM25 (SQLite FTS5) index, retriever, RRF hybrid, `--strategy`, result 2.1, `eval-compare` rules, security gate, T9 user-owned bm25/hybrid runs and default-strategy decision, T10 docs and hand-off); T1 approved 2026-10-25 (suite `public-eval-v2`, 91 cases, six Malayalam goldens g064–g069 promoted); T2 (v2 dense baseline) approved 2026-10-25: user-run result `experiments/results/retrieval-evaluation-idx-v1-20261025T134659Z.json` (see Next step); T3 approved 2026-10-26 (`lexical-v1` tokenizer, SQLite FTS5 lexical store, `make index-lexical`, `W2A_LEXICAL_INDEX_DIR`); T4 approved 2026-10-27 (`BM25Retriever`, SQL access clause, `retrieval/base.py`); T5 approved 2026-10-28 (RRF fusion, `HybridRetriever`, `config/retrieval.yaml`, default still `dense`); T6 approved 2026-10-28 (`--strategy`, result 2.1, dense equivalence fixture, per-leg document ranks); T7 approved 2026-10-28 (`eval-compare` identity refusals, R10); T8 approved 2026-10-28 (`eval-security` gate over dense, bm25 and hybrid, result 1.1); T9 approved 2026-10-28 (user-run dense 2.1, BM25 and hybrid results; the R13 rule holds, `default_strategy: hybrid` in `config/retrieval.yaml`, see Next step item 4); T10 approved 2026-10-28 (docs D049–D055, hardening boxes from the T1, T3, T4, T6–T9 reviews). Required `spec-reviewer` retrospective round 1 `PASS` (2026-10-28; three MINOR findings, docs reconciled, no RM tasks), approved by the user and merged 2026-10-28 |
| 008 — retrieval fallback | **verified (2026-11-01, merged 1107b67)**; required `spec-reviewer` retrospective round 1 `PASS` (five MINOR findings, docs reconciled, no RM tasks), approved by the user 2026-11-01 (branch spec/008, base f25b552); requirements, design and tasks approved 2026-10-29 (8 tasks: T1 failure classification and Qdrant timeouts, T2 standalone lexical open and freshness, T3 `bm25` without Qdrant or the extra, T4 `FallbackRetriever`, T5 result 2.2 and `eval-compare`, T6 security gate over fallback paths, T7 user-owned real runs, T8 docs and hand-off); T1–T6 approved (2026-10-31/11-01); T7 (user-owned real runs) approved 2026-11-01: Qdrant unreachable (`QDRANT_URL=http://127.0.0.1:1`) `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json`, Qdrant up `...20261101T070736Z.json` (see Next step item 6); T8 (docs D056–D062, ROADMAP note, As-built notes, hand-off) approved 2026-11-01; retrospective `.kiro/specs/008-retrieval-fallback/review.md` round 1 |
| 009 — chunking experiments | **verified (2026-11-04, merged `5a6deb7`)**; branch `spec/009` (base `d21dc41`); required `spec-reviewer` retrospective round 1 `PASS`, approved 2026-11-04; T1–T7 approved 2026-11-03; default **`idx-v2`**: **`make ingest`** then **`make index-lexical`**; D064–D071; deferred carry-overs in Known issues and 009 `review.md` Notes |
| 010 — multilingual retrieval | **verified (2026-11-04, merged `cae06c3`)**; branch `spec/010` (base `f0e809b`); T1–T6 approved 2026-11-04; required `spec-reviewer` retrospective round 1 `PASS`, approved 2026-11-04; D072; default suite v3 and `lexical-v2` |
| 011 — multilingual reranking | **in progress (T1–T5 approved 2026-11-05/06)**; branch `spec/011` (base `3b81508`); requirements, design (D-A sticky open-time skip, D-B no inference timeout, D-C `eval-continuity` refuses rerank identity differences) and tasks approved; 6 tasks (T1 reranker contract/adapters/config, T2 reranking stage and skip policy, T3 result 2.5 and compare, T4 security 1.5, T5 user-owned real runs and promotion, T6 docs and hand-off); T5 promoted depth 20 (`rerank.enabled: true` in `config/retrieval.yaml`, commit `5b24dc7`); T6 `not started` |

## Next step

**Spec 011 T5 done (2026-11-06; user-run, `w2a-realcheck-idx-v2`, suite `public-eval-v3`, `lote ml`, BGE-M3 @ `5617a9f`, reranker `BAAI/bge-reranker-v2-m3@953dc6f` on `mps:0`):**

- Files: rerank off `experiments/results/retrieval-evaluation-idx-v2-20261106T064835Z.json`; depth 20 `…20261106T072428Z.json`; depth 50 `…20261106T072853Z.json`; reference `…20261104T105300Z.json`. A Qdrant-down attempt (`…072053Z`, Docker stopped, BM25 fallback) was discarded and never committed.
- Continuity (off vs reference): `shared goldens: 87`, `continuity: no shared-case differences`, exit 0.
- `eval-compare --cross-rerank` vs reference, depth 20: `PASS (hits 86 -> 87, MRR 0.9228 -> 0.9751)`, flip `g026` miss→hit, p95 108.2 → 1028.7 ms (+920.6 ms). Depth 50: same quality (PASS, same hits and MRR), p95 2061.9 ms (+1953.7 ms), rerank leg about twice the depth-20 time.
- Promotion (R10): depth 20 passes (no `ml`/`mixed`/`en` hit→miss; p95 delta under 1000 ms) and is promoted: only `rerank.enabled` changed in `config/retrieval.yaml`. Two hits drop a rank (`g038`, `g062`, 1.0 → 0.5) and `g057` stays at 0.5. The unanswerable cross-encoder top-1 scores overlap the golden ones (three unanswerable cases above 0), so no fixed cut-off is safe.
- Operating change: with `rerank.enabled: true`, `--strategy dense|bm25` needs `--no-rerank`; default runs need the `reranker` extra and a cached model.

**Spec 011 next (2026-11-06):**

1. **T6** — fresh session: **`spec-orchestrator`** on `spec/011`. Then the required `spec-reviewer` retrospective, merge, and the user runs `/graphify . --update` on `main`.
2. After the merge and before Spec 012: bring the `chore/workflow-trim` plan to the user first (saved plan: command detection in the two scripts, graph once per spec, graphify query optional in briefs, graphify upgrade).

**Earlier (Spec 011 planning, 2026-11-04):**

1. Done 2026-11-05/06: Spec 011 T1–T5 (see above).
2. Optional: **`pytest --durations=25`** to rank slow tests before any future parallel verify work (D074 follow-up).
3. Remove user-level verify-budget hook copies after merge; committed hook is `.claude/settings.json` + `tools/hooks/verify_budget.py`.

1. Done 2026-10-24: the user ran the real `make eval-retrieval` on `w2a-realcheck-idx-v1` (`QDRANT_COLLECTION_BASE=w2a-realcheck`) and `make eval-compare` against the Spec 005 baseline: PASS, hits 60 -> 60, MRR 0.8783 -> 0.8783, no flips. The result `experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` (committed; BAAI/bge-m3 @ `5617a9f`, device `mps:0`, p50 79.7 ms, p95 97.8 ms) is the 2.0 baseline for suite `public-eval-v1` v1.
2. Done 2026-10-23: the user ran the real BGE-M3 baseline; result committed as `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json`. Use its numbers and the three misses (`g004`, `g026`, `g061`) as inputs to the next specs. Keep `make retrieval-baseline` results as new files; never overwrite this one.
3. Done 2026-10-25 (Spec 007 T2, in task review): the user ran the real `make eval-retrieval` on suite `public-eval-v2` v2; the result `experiments/results/retrieval-evaluation-idx-v1-20261025T134659Z.json` is the Spec 007 dense reference (BAAI/bge-m3 @ `5617a9f`, device `mps:0`, `w2a-realcheck-idx-v1`, `idx-v1`, `top_k` 5, 13 documents, strategy `dense`, `git_dirty` false). Known deviation, user-accepted: its `git_commit` is `b024f5d` (a docs-only spec amendment after the T1 commit `19cbbc3`; `git diff 19cbbc3 b024f5d` touches only `requirements.md` and `tasks.md`), not the T1 commit itself.
   - Overall (69 goldens): HitRate@5 0.9565, Recall@5 0.9565, MRR 0.8816 (random expectation 0.3846). `en` (54) 0.963 / MRR 0.9105; `mixed` (9) 0.8889 / MRR 0.6852; `ml` (6, small sample) 1.0 / MRR 0.9167.
   - Misses: `g004`, `g026`, `g061` (all other 66 goldens hit). Latency p50 78.5 ms, p95 120.0 ms (warm-up 16.2 s excluded). Unanswerable `n` 12 (top-1 scores informational).
   - Continuity against the v1 2.0 file: 63 shared goldens (same `case_id` and `case_version`), 60 hits and MRR 0.8783 on both sides; no case differs in hit, reciprocal rank or ranked document IDs (no device noise). The six new `ml` goldens `g064`-`g069` all hit.
   - `make eval-compare` of the file against itself: PASS (hits 66 -> 66, MRR 0.8816 -> 0.8816).
   - `experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` (suite `public-eval-v1` v1) is now a closed reference: v1 is `replaced` and cannot be re-run.
4. Spec 007 T9 (approved 2026-10-28; T1–T8 approved and pushed on `spec/007`). Done 2026-10-28: the user ran the real strategy comparison on suite `public-eval-v2` v2 (`w2a-realcheck-idx-v1`, `idx-v1`, BAAI/bge-m3 @ `5617a9f`, `mps:0`, `top_k` 5, 13 documents, `lexical-v1` digest `6045203b...`, 13 lexical chunks). Files: dense 2.1 `experiments/results/retrieval-evaluation-idx-v1-20261028T122835Z.json`, BM25 `...T123109Z.json`, hybrid `...T123121Z.json`; T2 reference `...20261025T134659Z.json`. Deviation for the user to accept: `git_dirty` is `true` in the BM25 and hybrid files (earlier result files were untracked at run time; code equals commit `6ed6e70`); dense 2.1 is clean.
   - Recorded deviation (user-accepted 2026-10-28, like the T2 `git_commit` one): the BM25 and hybrid result files have `git_dirty: true`. The only cause was the untracked dense result file from the same session in the working tree (`git_state` counts untracked files); all three files record `6ed6e70`. Default strategy is now `hybrid` (needs `make ingest`, then `make index-lexical`).
   - Dense 2.1 vs T2: `eval-compare` PASS, hits 66 -> 66, MRR 0.8816 -> 0.8816, no flip and no reciprocal-rank change (latency p50 78.5 -> 79.2 ms, p95 120.0 -> 157.3 ms, informational). Hybrid vs T2: PASS, hits 66 -> 68, MRR 0.8816 -> 0.9094. BM25 vs T2: FAIL (informational), hits 66 -> 64, MRR 0.8816 -> 0.7082.
   - Overall (HitRate@5 / Recall@5 / MRR, 69 goldens): dense T2 and 2.1 0.9565 / 0.9565 / 0.8816; BM25 0.9275 / 0.9130 / 0.7082; hybrid 0.9855 / 0.9855 / 0.9094.
   - `en` (54), HitRate / MRR: dense 0.9630 / 0.9105; BM25 0.9815 / 0.7562; hybrid 1.0000 / 0.9352. `mixed` (9, small sample): dense 0.8889 / 0.6852; BM25 0.8889 (Recall 0.7778) / 0.7222; hybrid 0.8889 / 0.8333. `ml` (6, small sample): dense 1.0 / 0.9167; BM25 0.5 / 0.2556; hybrid 1.0 / 0.7917.
   - Flips against T2 by `case_id`: dense 2.1 none. Hybrid: miss->hit `g004`, `g026`; no hit->miss. BM25: miss->hit `g004`, `g026`; hit->miss `g029` (en), `g067`, `g068`, `g069` (all `ml`).
   - `g004` (`business_001_overview_scope`): dense document rank 7 (miss), BM25 2, hybrid 3 (hit). `g026` (`business_006_mock_assessments`): dense 6, BM25 2, hybrid 3 (hit). `g061` (`official_002_candidate_rules_setup`): dense 6, BM25 9, hybrid miss; a miss in all three strategies.
   - Latency (ms): hybrid p50 80.3, p95 103.6 (legs: dense p50 79.5 / p95 102.5, BM25 p50 0.67 / p95 0.88); BM25 only p50 0.19, p95 0.27. Truncated queries: 0 (BM25 and hybrid).
   - R13 rule (scratch check over the per-case rows): hybrid passes the `eval-compare` gate; improves hits (66 -> 68) and MRR (0.8816 -> 0.9094); no `ml` or `mixed` case flips hit to miss. All three hold, so `default_strategy: hybrid` is set in `config/retrieval.yaml`; `dense` and `bm25` stay selectable with `--strategy`; tests that depend on the default read it from the config. The decision text is written in T10.
   - Hybrid ranks a relevant document lower than dense (T2) in four cases (reciprocal rank; dense leg rank / BM25 leg rank): `g006` en 1.0 -> 0.5 (1 / 3); `g029` en 1.0 -> 0.33 (1 / 9); `g064` ml 1.0 -> 0.5 (1 / 3); `g065` ml 0.5 -> 0.25 (2 / 5). BM25 term matches in the relevant document (chunk counts out of 13; "very common" is more than 6): `g006` `are` 12 and `the` 13 (very common) plus `materials` 6; `g029` `a` 13 (very common) plus `mock` 6; `g064` `naati` 5 and `ccl` 6 only; `g065` `naati` 5 only. In none of the four were the matches only very common terms; in `g064` and `g065` every Malayalam word has 0 chunk matches, so BM25 ranks on the Latin `NAATI` and `CCL`.
   - BM25 candidates per query (chunks matching the OR expression, at most 13, below candidate depth 50): `en` median 13 (min 5); `mixed` median 8 (min 3, max 11); `ml` median 3.5 (min 0, max 7).
5. Spec 007 is merged and verified (2026-10-28). Next: plan the next spec with `spec-planner`, passing the "Notes for the next spec" from `.kiro/specs/007-hybrid-retrieval/review.md` (BM25 without Qdrant or the `bge-m3` extra as the fallback, per-scope lexical files, Malayalam stemming, `g061`). The user should run `/graphify . --update` on `main`.
6. Spec 008 T7 (real runs, done 2026-11-01 by the user, result-file fields checked by the agent from the files; the closed port and all of Run 3 are reported by the user, not file-backed; both files `git_commit` `1f72e62`, `git_dirty` false, `top_k` 5, 69 goldens, 13 documents, `lexical-v1` digest `6045203b...`, 13 lexical chunks, `qdrant_timeouts` connect 2 s / query 3 s):
   - Run 1, Qdrant unreachable (`QDRANT_URL=http://127.0.0.1:1`, port reported by the user; no URL is recorded in the file): `experiments/results/retrieval-evaluation-idx-v1-20261101T070658Z.json`. `requested_strategy` hybrid, `served_strategies` `["bm25"]`, all 69 cases served by `bm25` with `fallback_reason` `qdrant_unavailable`, `fallback_counts` `{qdrant_unavailable: 81}` (69 goldens plus 12 unanswerable), `index_settings` null, `dense_identity.source` `lexical_file` (collection `w2a-realcheck-idx-v1`, `idx-v1`, BAAI/bge-m3 @ `5617a9f`), `device` null (the embedder was never loaded). Latency path `bm25+fallback:qdrant_unavailable` p50 0.182 ms, p95 0.235 ms, n 69 (warm-up 3.1 ms; `dense_attempt` is about 0 ms because the outage was detected once at open time and no query attempted the dense side, not because a refused connection is cheap). HitRate@5 0.9275, MRR 0.7082. `make eval-compare` against the Spec 007 BM25 reference `...20261028T123109Z.json`: PASS, hits 64 -> 64, MRR 0.7082 -> 0.7082, no flips (the output notes "requested hybrid and was served by bm25" and `git_commit` differs).
   - Run 2, Qdrant up: `experiments/results/retrieval-evaluation-idx-v1-20261101T070736Z.json`. Served `hybrid` for all 69 cases, `fallback_counts` `{}`, `warmup_fallback_reason` null, `dense_identity.source` `qdrant`, device `mps:0`, HitRate@5 0.9855, MRR 0.9094. Latency p50 86.2 ms, p95 115.2 ms (Spec 007 hybrid file: 80.3 / 103.6; informational; legs dense p50 85.3, BM25 p50 0.66; warm-up 95.6 s excluded). `make eval-compare` against `...20261028T123121Z.json`: PASS, hits 68 -> 68, MRR 0.9094 -> 0.9094, no flips. The agent re-ran both compares (read-only) and got the same results.
   - Run 3 (reported by the user; no file exists by design), no extra (after `make setup`): `make retrieve ... RETRIEVE_ARGS="--strategy bm25"` on the closed port returned 5 BM25 hits in 2.6 ms (hits 4 and 5 have score 0.0). The default strategy on the same port exited 2 with `OptionalDependencyError` (BGE-M3 needs the optional `bge-m3` dependency group) and did not fall back: a missing extra is a configuration error, not an outage. The extra was left removed (`make setup` state).
   - Deviations: none. Both result files were committed in `3403261`.
7. Spec 008 T8 hand-off (for the retrospective's "Notes for the next spec", HTTP route spec): a circuit breaker for repeated dense failures; a startup policy for a missing or stale lexical file; Qdrant 5xx eligibility (D062); the cost of the freshness check on a large corpus (D060); an async freshness check (`verify_fresh` uses `asyncio.run`, T2 review F3); and Qdrant client lifecycle (below). The user should run `/graphify . --update` on `main` after the merge.
8. Spec 008 is merged and verified (2026-11-01, `.kiro/specs/008-retrieval-fallback/review.md`). The user should run `/graphify . --update` on `main`. Next: plan the next spec with `spec-planner`, passing that round's "Notes for the next spec" (the HTTP route carry-overs).
9. Spec 009 T6 (done 2026-11-03 by the user on `w2a-realcheck`, promotion to default `way2australia-idx-v2`; agent wrap-up and commits on `spec/009`):
   - **Lexical rebuild (`idx-v1`, realcheck):** before/after `source_chunk_digest` `6045203bfeec8ee82a1191cf9993ba2621f3de17bc84b97248077833aef22760`, `chunk_count` **13** (unchanged; Qdrant untouched).
   - **Baseline 2.3 vs 2.2 reference:** `experiments/results/retrieval-evaluation-idx-v1-20261103T104346Z.json`; `make eval-compare` vs `...20261101T070736Z.json`: **PASS**, hits **68 → 68**, MRR **0.9094 → 0.9094**, no flips.
   - **Arm 2.3:** `experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json` (`w2a-realcheck-idx-v2`, hybrid, BGE-M3 @ `5617a9f`, `git_dirty` false). **`chunk_stats`:** 34 chunks, 13 documents, **`max_chunks_per_document` 4**, **`required_depth` 17** (≤ retrieval depth 50; matches T2 BGE-M3 counts).
   - **Cross-index compare** (baseline 2.3 → arm 2.3, `COMPARE_ARGS=--cross-index`):
     - `eval-compare: PASS (hits 68 -> 68, MRR 0.9094 -> 0.9208)`
     - Overall: HitRate@5 0.9855 → 0.9855; Recall@5 **0.9855 → 0.9783**; MRR 0.9094 → **0.9208** (+0.0114; gain below 1/69, largely from six **`ml`** cases MRR **0.7917 → 1.0000**). **`en`** (54): HitRate@5 / Recall@5 **1.0 → 0.9815**, MRR **0.9352 → 0.9321**; **`mixed`** MRR 0.8333 → 0.8000.
     - Cross-index lines: collection `w2a-realcheck-idx-v1` → `w2a-realcheck-idx-v2`; `index_version` idx-v1 → idx-v2; chunker heading 1 → recursive 1; ingestion_config `config/ingestion.yaml` → `experiments/configs/chunking/recursive-128.yaml`.
     - Flips: **`g061`** miss→hit (distinct rank **5**, reciprocal rank 0.2 on arm; baseline miss); **`g026`** hit→miss (**`en`**, mock).
   - **Promotion (R10 rule holds):** **`config/ingestion.yaml`** now matches **`recursive-128.yaml`** (schema 1.1, **`idx-v2`**, recursive 128/16/title). Default operator path: **`make ingest`**, then **`make index-lexical`**, then hybrid **`make retrieve`** / **`make eval-retrieval`** on **`way2australia-idx-v2`**. **`heading-idx-v1.yaml`** still selects **`idx-v1`** on realcheck (`QDRANT_COLLECTION_BASE=w2a-realcheck`); default Qdrant has no `way2australia-idx-v1` until ingested separately.
   - **Post-promotion binding check:** `experiments/results/retrieval-evaluation-idx-v2-20261103T105358Z.json` — same metrics as the arm file; recorded with **`git_dirty: true`** (config was uncommitted at run time; binding check only, not a reference baseline).
   - **Committed result files (T6):** `...idx-v1-20261103T104346Z.json`, `...idx-v2-20261103T104934Z.json`, `...idx-v2-20261103T105358Z.json`. Arm result belongs to **"128 tokens + title prefix"** together (confounded arm, design).
   - **T7 carry-over (document, do not fix in T6):** `config/ingestion.yaml` and `recursive-128.yaml` include ignored top-level `knowledge_release_id` / `evaluation_suite_id` (`public-eval-v1` stale); remove at next `index_version`.
10. Done 2026-11-04: Spec 009 retrospective round 1 `PASS` approved; `spec/009` merged into `main` (fast-forward to **`5a6deb7`**); verified docs **`6f49a33`**, graph **`461e070`** on `origin/main`.
11. **Spec 010 (user direction 2026-11-04; planned and approved 2026-11-04, see `.kiro/specs/010-multilingual-retrieval/`):** original brief: roadmap **item 8 — multilingual retrieval**. When the user requests planning, brief `spec-planner` with: **scope** — `lote_languages` applicability at retrieval time (separate from authorization; same filter on every path including fallback); Malayalam lexical normalization (legacy vs atomic chillu, D051) and a stemming or n-gram experiment for BM25; mixed-query handling; more `ml` and `mixed` evaluation cases (**user-owned task:** Justin writes or approves as fluent speaker); **measured gaps** from Spec 009 reference files (`…idx-v2-20261103T104934Z.json` and related): `mixed` MRR **0.80** (n=9); BM25-only loses **`g067`–`g069`**; slice samples too small (6 `ml`, 9 `mixed`); **009 Notes that apply** — Malayalam stemming, per-scope lexical files (D050) if access changes, hub-free verify discipline; **out of scope** — HTTP route, semantic chunking, FAQ indexing, size vs prefix experiment, reranking; **task budget** — at most **6–7** tasks.

## One-off: user-owned pre-merge check for Spec 004 (done 2026-10-17)

Not a gate. Run by the user before merging `spec/004` (see "Pre-merge manual check" in `.kiro/specs/004-ingestion-baseline/tasks.md`), reported by the user, not re-run by an agent:
- `make setup-bge-m3` (needed `UV_HTTP_TIMEOUT=600` on the user's connection);
- `W2A_RUN_BGE_M3_SMOKE=1 make test-unit`: 303 passed, 0 skipped (the smoke test ran);
- real ingestion into `w2a-realcheck-idx-v1` (BAAI/bge-m3 @ `5617a9f61b028005a4858fdac845db406aefb181`, fake=false): run 1 added 13; run 2 added 0, updated 0, unchanged 13, deleted 0 (model not loaded on run 2). Collection: 13 points, `dense` vector size 1024, Cosine;
- `make setup` restored the default environment.
Observations for later (no task opened): consider `UV_HTTP_TIMEOUT ?= 300` in the `setup-bge-m3` target; the model ran on `mps` (Apple GPU), so device pinning may matter for cross-machine reproducibility.

## Ingestion operating notes

- Default production index (after Spec 009 T6 promotion): **`idx-v2`**, **`recursive` v1** (128 tokens, 16 overlap, title prefix) in `config/ingestion.yaml`; collection **`way2australia-idx-v2`**. Legacy **`idx-v1`** / heading: `experiments/configs/chunking/heading-idx-v1.yaml` with `--config`.
- Use `QDRANT_COLLECTION_BASE` for every fake-embedder run. A fake run without it records the default collection for the configured `index_version` as fake, and a later real run is then refused until a new `index_version` is set in `config/ingestion.yaml`.
- After `make setup`, default runs (hybrid with reranking on, Spec 011 T5) need `make setup-bge-m3` plus a cached reranker (the first reranked run downloads the pinned model); `--strategy bm25` (and `dense`) now needs `--no-rerank`.
- `make setup` removes the optional `bge-m3` extra; use `make setup-bge-m3` before a real-embedding run (on a slow connection `UV_HTTP_TIMEOUT=600 make setup-bge-m3`). A missing extra is detected when the embedder is built (exit 2, before any Qdrant call).
- `make verify` runs the Docker integration tests too when a local Qdrant is reachable (they create and remove temporary collections); otherwise they skip.
- `INGESTION_NAMESPACE` (`533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2`) is permanent: changing it changes every point ID.
- Decisions: D025 to D030 and D032 in `DECISIONS.md`.

Spec 002 decisions made before approval:
- `content_hash` (`content-hash-v1`) is the only change-detection signal; the manifest's `sha256` (raw file) and `body_sha256` (stripped body) are integrity checks the loader verifies.
- Security fixtures under `tests/fixtures/security/` now carry complete metadata (`document_version`, `lifecycle_status`, `introduced_in_release: security-fixtures`, `retrieval_enabled`) and are treated as valid but ineligible.
- T7 adds `make validate-knowledge`, which runs inside `make verify`.

## Known issues / deferred

These are evaluation-data gaps, deliberately deferred for now (decision 2026-10-13). Changing them requires human-approved evaluation cases (C6).
- Pure Malayalam (`query_language: ml`) goldens: none in `public-eval-v1`. `public-eval-v2` (Spec 007 T1) has six, `g064`–`g069`, promoted from the six candidates the user (fluent speaker and owner) approved on 2026-10-25 (`ml_002` and `ml_003` with reworded queries); the candidate rows in `evaluation/candidates/006-candidates.jsonl` stay `status: suggested` with `review.promoted_as`. The 9 `mixed` cases include 8 written mostly in Malayalam script. The v2 dense baseline hits all six `ml` goldens.
- `relevant_section_ids` is empty in every evaluation case, so `eval-retrieval` reports zero section-measurable cases (deferred by Spec 009; headed documents and suite v3 are a later spec).

Spec 009 known issues and carry-overs (documented; no remediation tasks):
- Ignored top-level `knowledge_release_id` / `evaluation_suite_id` in `config/ingestion.yaml` and `experiments/configs/chunking/recursive-128.yaml` (`evaluation_suite_id` still names the replaced `public-eval-v1`). The ingestion loader ignores them. Remove at the next `index_version`; keep this promotion's byte copy so the arm's `ingestion_config` hash stays valid (D071).
- Size vs prefix confounding: the promoted arm is recursive 128 tokens *and* title prefix together (D071). Recorded metrics belong to that pair, not either treatment alone. A later spec may split them.
- `g026` (en, `business_006_mock_assessments`) flipped hit→miss on promotion. Overall HitRate@5 stayed 0.9855 (68/69); English HitRate@5 / Recall@5 1.0 → 0.9815, MRR 0.9352 → 0.9321. R10 allowed the flip (`en`, not `ml`/`mixed`). Revisit with reranking or a size-vs-prefix split.
- FAQ pairs: `knowledge/structured/owner_approved_faq_pairs.jsonl` is not indexed (own spec).
- Semantic chunking: out of scope (roadmap 7 remainder).
- Malayalam stemming: not implemented (declined in Spec 010; roadmap carry-over).
- Legacy chillu: **`lexical-v2`** default replaces legacy ZWJ sequences in BM25 (D072 amends D051); seed corpus and v3 queries have no legacy sequences, so T5 measured no gain.
- Spec 008 serving/API items remain open for **roadmap item 10 (grounded generation)**, not a retrieval-only HTTP spec (see Spec 008 known issues and 008 retrospective F4/F5): startup and reopen policy for a missing or stale lexical file **and** refusal when the file's recorded tokenizer disagrees with `config/retrieval.yaml` (Spec 010 T5 carry-over: `open_retrieval` does not check today; stale `lexical-v1` would serve silently after a v2 promotion); circuit breaker, Qdrant client lifecycle, async freshness (`verify_fresh` uses `asyncio.run`), freshness cost on a large corpus (D060/D067), fallback-stage observability, Qdrant 5xx eligibility (D062), API surface.
- Per-scope lexical files remain a roles-spec item (D050).
- In a shallow clone (base commit `06b1af9` absent) the Spec 007 T1 v1 byte-identity tests in `test_suite_v2.py` skip, and nothing flags it. Accepted while there is no CI; revisit in the CI spec.
- `g004` overlaps unanswerable `u001`: the owner decided `keep_both` on 2026-10-25 (g004 tests the "no guarantee" statement, u001 a safe redirect for a time-bound promise). g004 stays an active golden and remains a real retrieval miss for dense search.

Spec 008 known issues and carry-overs (documented by T8; no remediation tasks):
- Qdrant client lifecycle (T4 review): `open_retrieval` closes the Qdrant client on the fallback path but not on every open failure, and `OpenedRetrieval.close()` does not close the client. A long-running server would leak a connection pool per failed open; the CLIs exit after one run. **Roadmap item 10** (grounded generation / first HTTP surface) must close the client on every open failure and in `close()`, with a test.
- `verify_fresh` uses `asyncio.run`, so it cannot run inside a running event loop; **item 10** needs an async freshness check or a check at startup outside the loop (T2 review F3).
- The standalone freshness check rereads every eligible document at each open (milliseconds for 13 documents); revisit for a large corpus (D060).
- No circuit breaker: with Qdrant hanging, each hybrid query waits about `query_timeout_s` (3 s) before BM25 serves (D058). Qdrant 5xx and a Hugging Face hub 5xx are not fallback-eligible (D062).
- The security gate's standalone `bm25` path checks identity plus "every seed chunk present" instead of `verify_fresh`, and that check is one-way (an extra non-forbidden row is not refused); see the design As-built notes (T6).
- Only user-reported, not file-backed: the closed port of T7 Run 1 and all of Run 3.

Spec 008 retrospective (`.kiro/specs/008-retrieval-fallback/review.md`, round 1), MINOR, no remediation tasks:
- F1: an open-time outage makes BM25 serve the whole run (`FallbackRetriever(None, ...)`, as the design's open row says); D058, `ARCHITECTURE.md` and `COMMANDS.md` said every query retries the dense side. Reconciled in this round (D058 clarified, not changed).
- F2: result 2.2 and `eval-compare` do not distinguish an open-time from a per-query fallback (same `bm25+fallback:<reason>` path; `dense_attempt` about 0 ms after an open-time fallback, yet labelled "includes failed dense attempt"). Docs corrected; a `fallback_stage`-style field is left to **roadmap item 10** or observability (item 11).
- F3: post-approval amendments (task boxes added to T3, T5 and T8; the design "Not changed" list; two design R8 bullets) rest on verbatim user decisions in `task-reviews.md` but have no dated line in `requirements.md` `## Change log` (WORKFLOW.md). Resolved 2026-11-01 by the user's decision: `spec-planner` added eight dated lines to `requirements.md` `## Change log`, each citing its `task-reviews.md` decision.
- F4: `open_retrieval`'s `bm25` branch and `_open_fallback` duplicate the standalone open and lexical `document_count` wiring; fold into one helper when **roadmap item 10** reworks `open_retrieval` (together with the client lifecycle item).
- F5: no test drives the open-time fallback from a `bind_to` scroll failure (Qdrant fails after `DenseIndex.open`) through `open_retrieval`; covered by composition (`chunk_identities` maps transport errors, T1; the `except` spans `open_bound_lexical`, T4).

Spec 010 retrospective (`.kiro/specs/010-multilingual-retrieval/review.md`, round 1), MINOR, no remediation tasks:
- F1: `ARCHITECTURE.md` listed `languages.py` with `applicability.py` under the `retrieval/` intro; the file is at the package root. Reconciled in this round.
- F2: `COMMANDS.md` `make eval-security` said a query with no `lexical-v1` terms skips the lexical check. Reconciled to “no lexical terms”.
- F3: `COMMANDS.md` `make eval-continuity` implied lexical identity could be skipped via cross-mode compares; `continuity.py` always compares `lexical_index`. Reconciled (parenthetical dropped).
- F4: `COMMANDS.md` implemented-today list and “All four run one module” omitted `eval-continuity`. Reconciled.
- F5: `TECH_STACK.md` sparse retrieval still named only `lexical-v1`. Reconciled (default `lexical-v2`, D072).

Spec 010 known issues and carry-overs (documented by T6; no remediation tasks in this spec):
- **Query translation / transliteration** (including Latin-script Malayalam): the intended fix for **`g067`–`g069`** on BM25-only and on the hybrid **fallback** path when dense is unavailable; out of scope for Spec 010. BM25-only `ml` MRR **0.2396** (n=16) on v3 realcheck (`…20261104T105321Z.json`).
- **`g056` / `g057`:** hybrid fusion demotes a dense rank-1 relevant document to reciprocal rank 0.5 (BM25 rank 2); inputs for **roadmap item 9** reranking, not a Spec 010 bug.
- **No Malayalam knowledge content** was added (`knowledge/` unchanged); evaluation grew via v3 cases only.
- **Malayalam stemming** and **per-script fusion weighting** were declined (requirements out of scope).
- **Script mix** uses Unicode **name** prefixes, not Scripts.txt; romanized Malayalam counts as **`latin`** (reporting only).
- **`open_retrieval`** does not compare the lexical file's recorded tokenizer to `config/retrieval.yaml` (stale `lexical-v1` would serve silently); group with roadmap **item 10** startup policy (also missing/stale file).
- Spec **009** carry-overs below remain unchanged (ignored yaml keys, `g026`, FAQ, semantic chunking, per-scope lexical files, shallow-clone test skip, etc.).

Spec 007 known issues and carry-overs (documented by T10; no remediation tasks):
- Closed by Spec 010 (D072): `lexical-v2` maps legacy chillu sequences (consonant, virama, ZWJ) to the atomic chillu letter; `lexical-v1` remains available unchanged. Seed corpus and v3 queries have no legacy sequences, so T5 measured no gain.
- The `seed-v1` Knowledge Release still names suite `public-eval-v1` (replaced); releases are Phase 2 (D049).
- Closed by Spec 008: `bm25` needs neither Qdrant nor the `bge-m3` extra, and `hybrid` falls back to BM25 on a Qdrant or model outage.
- BM25 statistics (IDF, average length) are computed over every row of a lexical file, including rows the access clause excludes. Today only eligible guest/public chunks are indexed, so they reveal nothing; a future roles spec needs one lexical file per access scope (D050).
- Malayalam in BM25 matches only exact tokens (no stemming): `g067`–`g069` are lost by BM25 alone and `g064`/`g065` rank on the Latin `NAATI`/`CCL`; hybrid keeps every `ml` hit but with lower reciprocal ranks (MRR 0.9167 -> 0.7917 on a 6-case sample).
- The BM25 and hybrid result files of 2026-10-28 have `git_dirty: true` (user-accepted; cause: the untracked dense result of the same session); fixed going forward in `git_state`.
- `git_state` (shared with the legacy `make retrieval-baseline`) ignores every untracked file under `experiments/results/`, not only result JSON; a path git quotes reports dirty (fails safe). Accepted at T10 review (F3).

Spec 007 retrospective (`.kiro/specs/007-hybrid-retrieval/review.md`, round 1), MINOR, no remediation tasks:
- F1: the corpus-wide BM25 statistics note lacked "reveals nothing today" (T10 review F1); reconciled in this round in `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md` and this file.
- F2: resolved 2026-10-28: the `Read`/`Edit`/`Write(~/learning/**)` permissions added in the T6 commit (`cfcaeff`) were moved by the user to the git-ignored `.claude/settings.local.json` and removed from `.claude/settings.json`.
- F3: `design.md` "Not changed" lists `retrieval/baseline.py`, which T10 edited (`git_state`), and its interface sketch shows `query_terms` returning `list[str]` (it returns `QueryTerms`); both recorded in the design As-built notes in this round.

Spec 006 retrospective (`.kiro/specs/006-evaluation-framework/review.md`, round 1), MINOR, no remediation tasks:
- F1: the byte-identity check of `evaluation/` before and after a run is tested for the loader (`test_suite_loader.py`) and the validator (`test_validate.py`), not around the `eval-retrieval` and `eval-security` runners (the design's "each runner"). Both runners read evaluation data only through `load_suite`, and no evaluation code writes under `evaluation/`.
- Legacy `make retrieval-baseline --allow-fake` without `--output` still writes into `experiments/results/` (Spec 005 location, kept by R12/R13); only the new commands use the git-ignored `experiments/results/tmp/`. Do not commit a fake result.
- `make eval-security` is not a step of the `make verify` target; its gate runs inside `make verify` through `test_security_eval.py`.
- The security result's `access.role` is hard-coded `guest` (correct in Phase 1; change it when other roles are added).

Closed by Spec 005 (T1, T7): payload indexes are re-created on the exists-empty-no-settings path, with a call-order test (Spec 004 T6 F4); Docker integration assertions cover the payload indexes and the `dense` vector config (T6 F2); the policy-vs-config scope check is two-way (T1 F1); `ruff format --check` runs in `make lint` (formatting drift); `UV_HTTP_TIMEOUT` defaults to 300 for `make setup-bge-m3`; the BGE-M3 device is now recorded in retrieval results (D038).

Spec 005 retrospective (`.kiro/specs/005-dense-retrieval-baseline/review.md`, round 1), MINOR, no remediation tasks (F1 and F2 were documentation gaps, reconciled in that round):
- F3: closed by Spec 006 (T5): `packages/rag/tests/evaluation/test_security_integration.py` (`make test-integration`) proves on Docker Qdrant that staff-scope, other-tenant, owned and missing-owner points, each nearest by construction, are never returned.
- F4: interface sketches in `design.md` differ from the code (`retrieval/__init__.py` has no exports; `SuiteRef.golden_dataset_path`; extra `run_baseline` parameters); recorded in the design's As-built notes.
- F5: the design error table says a non-guest role is refused without Qdrant contact, but resolution runs after the read-only `DenseIndex.open` (as the design data flow and T5 say); unreachable today.
- Closed by user decision, no change: Spec 005 T1 F2 (repeated `create_payload_index` tested on the client directly), T7 F3 (no test of the exclusive-create race in `write_result`).

Spec 004 review findings still open (all MINOR, no remediation tasks; see `.kiro/specs/004-ingestion-baseline/task-reviews.md` and `review.md` round 1):
- T3 F1: `test_info_reports_fake_identity` uses `pytest.raises(Exception)` instead of `pydantic.ValidationError`.
- T5 F2: closed by Spec 009 T7 (settings docstring clarifies `max_length` vs truncation guard).
- T7 F1: closed by Spec 009 T1 (chunking inside the per-document try).
- T7 F2: `QdrantIndexStore` holds both `_index_version` and `index_version`.
- T7 F3: closed by Spec 009 T7 (`test_wrong_vector_count_is_a_per_document_failure`).
- T7 F5: `test_security_fixtures_never_reach_the_index` does not assert the fixtures loaded.
- T8 round 2 F1: the late `OptionalDependencyError` re-raise in `service.py` (broken installs) has no test.
- Retro F1: the `repositories/manifest.py` module docstring says "one record per document version"; the loader allows one record per `document_id` (D026, D032).
- The BGE-M3 device is recorded in retrieval results and the baseline JSON but not pinned and not an index setting (D038); the user's real run used `mps`.
- Default production index is `recursive` v1 (Spec 009 T6); `heading` v1 remains via `heading-idx-v1.yaml`. None of the 13 seed documents has headings, so heading behaviour is covered mainly by synthetic tests (D030).

Spec 002 retrospective (`.kiro/specs/002-document-model-and-repository/review.md`, round 1), MINOR, no remediation tasks (F1–F4 handled by Spec 004 as noted):
- F1: closed by Spec 004 T1: the strict `YYYY-MM-DD` check (`manifest.date_problems`) now runs in the loader and in `validate-knowledge`.
- F2: closed by D025 (`persona_scope` is informational: not loaded, indexed or hashed).
- F3: partly closed by Spec 004 T1 (`GUEST_PUBLIC_POLICY` and access scopes are tested against `config/access_policy.yaml`); source authorities are still not cross-checked against `source_precedence.yaml`.
- F4: decided by D026 (one version per `document_id`; version history is Phase 2); the `manifest.py` docstring is still stale and the "version increments on change" rule is unenforced.
- F5: `ARCHITECTURE.md` repository sketch uses `list_documents(status=...)`, not `DocumentQuery`.
- F6: loader and `validate-knowledge` validate documents on two separate paths (loader reports only the first Pydantic error, no date check).

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
