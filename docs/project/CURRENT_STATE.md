# Current State

Last updated: 2026-10-15

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Implement Spec 004 (ingestion baseline, approved 2026-10-15) through `spec-orchestrator`. Specs 001–003 are complete. Repository-based shared context keeps Codex, Claude Code and Kiro interchangeable.

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
- task-gated spec-driven skills (`spec-orchestrator`, `spec-planner`, `spec-implementer`, `task-reviewer`, optional `spec-reviewer`), with canonical source in `agent-skills/`, mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/` by `make skills-sync`, and checked by `make skills-check` (part of `make verify`); exercised on real work by Spec 002 T3–T9 (Spec 003 dry run, recorded in its T9);
- task state lifecycle (`**State:**` lines, `task-reviews.md`, `spec/<NNN>` branches, `Spec-Task` trailers) and spec `Status:` values defined in `docs/project/WORKFLOW.md`, decision D023;
- `CLAUDE.md` imports only `AGENTS.md` and this file; other docs are read per role;
- `Makefile` uses a standalone `uv` binary when available and falls back to `python3 -m uv`;
- Spec 002 (merged to `main`): Pydantic document models and enums in `packages/core/documents`; `DocumentRepository` Protocol and `LocalDocumentRepository` with manifest JSON Schema validation, frontmatter parsing and `content-hash-v1` hashing; `EligibilityPolicy` for guest/public retrieval; `make validate-knowledge` (part of `make verify`); repository, hashing, eligibility, seed-corpus and isolated security-fixture tests.

Not yet implemented:
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
| 002 — document model and repository | **verified (2026-10-15, merged dca6cbd)**; branch `spec/002` (base `869c37f`; T1–T2 on `main`, approved without task review). T3 (the Spec 003 T9 dry run) approved 2026-10-14 after task review round 1 PASS: manifest loading and metadata validation in `packages/rag/.../repositories/manifest.py` and `frontmatter.py`, new deps `jsonschema` and `pyyaml`. T4 approved 2026-10-14 (LocalDocumentRepository; placeholder content_hash until T5); T5 approved 2026-10-14 (content-hash-v1 and manifest hash verification); T6 approved 2026-10-15 (eligibility policy); T7 approved 2026-10-15 (`make validate-knowledge`); T8 approved 2026-10-15 (isolated security repository, seed corpus tests); T9 approved 2026-10-15 (documentation and handoff); merged to `main` |
| 003 — task-gated agent workflow | **verified** (2026-10-15, bootstrap exception: implemented directly on `main`, base `9e95cfe`); dry run on Spec 002 recorded in its T9; T1–T8 closed by the user's instruction to close the spec, without per-task review records |
| 004 — ingestion baseline | **implementing** on branch `spec/004` (base `af659da`); T1 approved 2026-10-15 (shared strict date check, policy-vs-config test); T2 approved 2026-10-15 (heading chunker, `section_id` slug rule recorded in design); T3 next. User-owned pre-merge check (not a gate): one real BGE-M3 ingestion of the seed corpus into a throwaway collection, run twice, plus the opt-in smoke test |

## Next step

1. Run `/spec-orchestrator 004-ingestion-baseline` (creates `spec/004`, runs T1 first). The Spec 002 retrospective notes are already built into the spec.

Spec 002 decisions made before approval:
- `content_hash` (`content-hash-v1`) is the only change-detection signal; the manifest's `sha256` (raw file) and `body_sha256` (stripped body) are integrity checks the loader verifies.
- Security fixtures under `tests/fixtures/security/` now carry complete metadata (`document_version`, `lifecycle_status`, `introduced_in_release: security-fixtures`, `retrieval_enabled`) and are treated as valid but ineligible.
- T7 adds `make validate-knowledge`, which runs inside `make verify`.

## Known issues / deferred

These are evaluation-data gaps, deliberately deferred for now (decision 2026-10-13). Changing them requires human-approved evaluation cases (C6).
- No golden case is tagged pure Malayalam (`query_language: ml`). The 9 `mixed` cases include 8 written mostly in Malayalam script.
- `relevant_section_ids` is empty in every evaluation case.

Spec 002 retrospective (`.kiro/specs/002-document-model-and-repository/review.md`, round 1), MINOR, no remediation tasks:
- F1: `content_hash` is computed from the raw frontmatter mapping; the `YYYY-MM-DD` date check exists only in `validate-knowledge`, not in `LocalDocumentRepository`.
- F2 (spec defect, for `spec-planner`): `persona_scope` (schema and all seed docs) is silently dropped from `KnowledgeDocument` and not in `content-hash-v1`; the spec does not decide its treatment.
- F3: access scopes, source authorities and `GUEST_PUBLIC_POLICY` are hard-coded; nothing cross-checks `config/access_policy.yaml` / `source_precedence.yaml`.
- F4: the manifest allows one version per `document_id` (docstring says one record per version); version history and the "version increments on change" rule are unenforced.
- F5: `ARCHITECTURE.md` repository sketch uses `list_documents(status=...)`, not `DocumentQuery`.
- F6: loader and `validate-knowledge` validate documents on two separate paths (loader reports only the first Pydantic error, no date check).

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
