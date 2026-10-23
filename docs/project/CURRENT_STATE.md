# Current State

Last updated: 2026-10-23

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Implement Spec 006 (evaluation framework, approved 2026-10-23; 8 tasks) through `spec-orchestrator`. Specs 001–005 are complete. Repository-based shared context keeps Codex, Claude Code and Kiro interchangeable.

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
- BM25 + RRF hybrid retrieval planned.
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
- task-gated spec-driven skills (`spec-orchestrator`, `spec-planner`, `spec-implementer`, `task-reviewer`, and the `spec-reviewer` retrospective, required since D031), with canonical source in `agent-skills/`, mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/` by `make skills-sync`, and checked by `make skills-check` (part of `make verify`); exercised on real work by Spec 002 T3–T9 (Spec 003 dry run, recorded in its T9);
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

Not yet implemented:
- BM25, hybrid retrieval (RRF) and reranking; no HTTP retrieval route;
- a recorded real BGE-M3 retrieval baseline, recorded in `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (commit `7418812`; BAAI/bge-m3 @ `5617a9f`, device `mps:0`, index `w2a-realcheck-idx-v1`): 63 cases, N=13; HitRate@5 0.952 vs random 0.385 (`min(1, 5/13)`), Recall@5 0.952, MRR 0.878; `en` (54) HitRate 0.963 / MRR 0.910, `mixed` (9) HitRate 0.889 / MRR 0.685; p50 61.5 ms, p95 216.5 ms (warm-up 105.9 s excluded); misses `g004`, `g026`, `g061`;
- evaluation runs;
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
| 006 — evaluation framework | **implementing** on branch `spec/006` (base `a400bab`); 8 tasks, T1 next. User-owned post-merge step (not a gate): a real `make eval-retrieval` run reproducing the Spec 005 baseline (0.952 / 0.878) via `make eval-compare` |

## Next step

1. Run `/spec-orchestrator 006-evaluation-framework` (creates `spec/006`, runs T1 first). The Spec 005 retrospective notes are built into the spec.
2. Done 2026-10-23: the user ran the real BGE-M3 baseline; result committed as `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json`. Use its numbers and the three misses (`g004`, `g026`, `g061`) as inputs to the next specs. Keep `make retrieval-baseline` results as new files; never overwrite this one.
3. Plan the next roadmap spec (evaluation runs, hybrid retrieval) separately with `spec-planner`, starting from the "Notes for the next spec" in `.kiro/specs/005-dense-retrieval-baseline/review.md` (round 1).

## One-off: user-owned pre-merge check for Spec 004 (done 2026-10-17)

Not a gate. Run by the user before merging `spec/004` (see "Pre-merge manual check" in `.kiro/specs/004-ingestion-baseline/tasks.md`), reported by the user, not re-run by an agent:
- `make setup-bge-m3` (needed `UV_HTTP_TIMEOUT=600` on the user's connection);
- `W2A_RUN_BGE_M3_SMOKE=1 make test-unit`: 303 passed, 0 skipped (the smoke test ran);
- real ingestion into `w2a-realcheck-idx-v1` (BAAI/bge-m3 @ `5617a9f61b028005a4858fdac845db406aefb181`, fake=false): run 1 added 13; run 2 added 0, updated 0, unchanged 13, deleted 0 (model not loaded on run 2). Collection: 13 points, `dense` vector size 1024, Cosine;
- `make setup` restored the default environment.
Observations for later (no task opened): consider `UV_HTTP_TIMEOUT ?= 300` in the `setup-bge-m3` target; the model ran on `mps` (Apple GPU), so device pinning may matter for cross-machine reproducibility.

## Ingestion operating notes

- Use `QDRANT_COLLECTION_BASE` for every fake-embedder run. A fake run without it records the default `way2australia-idx-v1` collection as fake, and a later real run is then refused until a new `index_version` is set in `config/ingestion.yaml`.
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
- No golden case is tagged pure Malayalam (`query_language: ml`). The 9 `mixed` cases include 8 written mostly in Malayalam script.
- `relevant_section_ids` is empty in every evaluation case.

Closed by Spec 005 (T1, T7): payload indexes are re-created on the exists-empty-no-settings path, with a call-order test (Spec 004 T6 F4); Docker integration assertions cover the payload indexes and the `dense` vector config (T6 F2); the policy-vs-config scope check is two-way (T1 F1); `ruff format --check` runs in `make lint` (formatting drift); `UV_HTTP_TIMEOUT` defaults to 300 for `make setup-bge-m3`; the BGE-M3 device is now recorded in retrieval results (D038).

Spec 005 retrospective (`.kiro/specs/005-dense-retrieval-baseline/review.md`, round 1), MINOR, no remediation tasks (F1 and F2 were documentation gaps, reconciled in that round):
- F3: the authorization isolation tests (`test_authorization_isolation.py`) run only on in-memory local-mode Qdrant; no committed Docker test proves the server applies the filter (the retrospective checked it manually on Docker: staff scope, other tenant, non-null owner and a missing `owner_user_id` were each nearest unfiltered and never returned).
- F4: interface sketches in `design.md` differ from the code (`retrieval/__init__.py` has no exports; `SuiteRef.golden_dataset_path`; extra `run_baseline` parameters); recorded in the design's As-built notes.
- F5: the design error table says a non-guest role is refused without Qdrant contact, but resolution runs after the read-only `DenseIndex.open` (as the design data flow and T5 say); unreachable today.
- Closed by user decision, no change: Spec 005 T1 F2 (repeated `create_payload_index` tested on the client directly), T7 F3 (no test of the exclusive-create race in `write_result`).

Spec 004 review findings still open (all MINOR, no remediation tasks; see `.kiro/specs/004-ingestion-baseline/task-reviews.md` and `review.md` round 1):
- T3 F1: `test_info_reports_fake_identity` uses `pytest.raises(Exception)` instead of `pydantic.ValidationError`.
- T5 F2: the `settings.py` docstring says `max_length` never changes vectors; revisit if `max_length` becomes configurable.
- T7 F1: chunking and point-ID computation run outside the per-document try/except, so an unexpected chunker exception would abort the run.
- T7 F2: `QdrantIndexStore` holds both `_index_version` and `index_version`.
- T7 F3: no test for the "embedder returned a wrong number of vectors" guard.
- T7 F5: `test_security_fixtures_never_reach_the_index` does not assert the fixtures loaded.
- T8 round 2 F1: the late `OptionalDependencyError` re-raise in `service.py` (broken installs) has no test.
- Retro F1: the `repositories/manifest.py` module docstring says "one record per document version"; the loader allows one record per `document_id` (D026, D032).
- The BGE-M3 device is recorded in retrieval results and the baseline JSON but not pinned and not an index setting (D038); the user's real run used `mps`.
- The index is derived from `heading` chunking; none of the 13 seed documents has headings, so heading behavior is covered only by synthetic tests, and the chunking strategy differs from `experiments/configs/day1_baseline.yaml` (recursive, 600 tokens) on purpose (D030).

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
