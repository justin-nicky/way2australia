# Current State

Last updated: 2026-10-14

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Finish Spec 003 (task-gated agent workflow: T1–T8 implemented, T9 dry run and T10 pending), then resume Spec 002 from T3 under the new flow. T3 is the Spec 003 dry run (T9). Repository-based shared context keeps Codex, Claude Code and Kiro interchangeable.

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
- task-gated spec-driven skills (`spec-orchestrator`, `spec-planner`, `spec-implementer`, `task-reviewer`, optional `spec-reviewer`), with canonical source in `agent-skills/`, mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/` by `make skills-sync`, and checked by `make skills-check` (part of `make verify`); not yet exercised on real work (dry run is Spec 003 T9);
- task state lifecycle (`**State:**` lines, `task-reviews.md`, `spec/<NNN>` branches, `Spec-Task` trailers) and spec `Status:` values defined in `docs/project/WORKFLOW.md`, decision D023;
- `CLAUDE.md` imports only `AGENTS.md` and this file; other docs are read per role;
- `Makefile` uses a standalone `uv` binary when available and falls back to `python3 -m uv`;
- on branch `spec/002` (not yet on `main`): knowledge manifest loading and validation (schema, duplicate identity, missing files, manifest/frontmatter mismatch) — Spec 002 T3.

Not yet implemented:
- Pydantic domain models;
- DocumentRepository;
- ingestion;
- embeddings;
- retrieval;
- generation;
- observability;
- CI/CD;
- Terraform deployment.

## Spec status

| Spec | Status |
|---|---|
| 001 — project foundation | implemented; completed before the review process existed (no `review.md`) |
| 002 — document model and repository | **implementing** on branch `spec/002` (base `869c37f`; T1–T2 on `main`, approved without task review). T3 (the Spec 003 T9 dry run) approved 2026-10-14 after task review round 1 PASS: manifest loading and metadata validation in `packages/rag/.../repositories/manifest.py` and `frontmatter.py`, new deps `jsonschema` and `pyyaml`. T4 approved 2026-10-14 (LocalDocumentRepository; placeholder content_hash until T5); T5 approved 2026-10-14 (content-hash-v1 and manifest hash verification); T6–T9 `not started` |
| 003 — task-gated agent workflow | **implementing** (bootstrap exception: directly on `main`, base `9e95cfe`): T1–T8 done, in task review; T9 dry run (needs the user) and T10 pending |

## Next step

1. Spec 003 T9 dry run done: Spec 002 T3 went implementer → task-reviewer → user approval on `spec/002`. Record any workflow defects it showed.
2. Fix any workflow defects found, then T10 and mark Spec 003 verified.
3. Continue Spec 002 T4–T9 with `spec-orchestrator`.

Spec 002 decisions made before approval:
- `content_hash` (`content-hash-v1`) is the only change-detection signal; the manifest's `sha256` (raw file) and `body_sha256` (stripped body) are integrity checks the loader verifies.
- Security fixtures under `tests/fixtures/security/` now carry complete metadata (`document_version`, `lifecycle_status`, `introduced_in_release: security-fixtures`, `retrieval_enabled`) and are treated as valid but ineligible.
- T7 adds `make validate-knowledge`, which runs inside `make verify`.

## Known issues / deferred

These are evaluation-data gaps, deliberately deferred for now (decision 2026-10-13). Changing them requires human-approved evaluation cases (C6).
- No golden case is tagged pure Malayalam (`query_language: ml`). The 9 `mixed` cases include 8 written mostly in Malayalam script.
- `relevant_section_ids` is empty in every evaluation case.

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
