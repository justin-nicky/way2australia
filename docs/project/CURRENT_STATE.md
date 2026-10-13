# Current State

Last updated: 2026-10-13

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Approve and implement Spec 002 using the spec-driven skills (`spec-planner`, `spec-implementer`, `spec-reviewer`) and repository-based shared context so Codex, Claude Code and Kiro can be used interchangeably.

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
- spec-driven development skills (`spec-planner`, `spec-implementer`, `spec-reviewer`), with canonical source in `agent-skills/`, mirrored to `.claude/skills/`, `.agents/skills/` (Codex) and `.kiro/skills/` by `make skills-sync`, and checked by `make skills-check` (part of `make verify`);
- spec status lifecycle (`Status:` lines, `review.md`, remediation rounds) defined in `docs/project/WORKFLOW.md`;
- `Makefile` uses a standalone `uv` binary when available and falls back to `python3 -m uv`.

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
| 002 — document model and repository | **draft**: requirements, design and tasks are written, with traceability and per-task requirement IDs, and await human approval |

## Next step

1. Review Spec 002. If acceptable, set each of its three files to `Status: approved (YYYY-MM-DD)`, or ask `spec-planner` to revise it.
2. Run `spec-implementer` on `002-document-model-and-repository`.
3. Run `spec-reviewer` on it in a fresh session.

Spec 002 open points for the implementer to raise if they become material:
- The manifest already stores `sha256` (raw file) and `body_sha256` (stripped body). The new content-hash contract (T5) must state how it relates to them.
- The staff canary fixture lacks `document_version`, `lifecycle_status`, `introduced_in_release` and `retrieval_enabled`. Tests should state whether such fixtures are rejected as invalid or excluded as ineligible.
- `make validate-knowledge` (COMMANDS.md) overlaps R5/R6, but Spec 002 does not currently create it.

## Known issues / deferred

These are evaluation-data gaps. Changing them requires human-approved evaluation cases (C6).
- No golden case is tagged pure Malayalam (`query_language: ml`). The 9 `mixed` cases include 8 written mostly in Malayalam script.
- `relevant_section_ids` is empty in every evaluation case.

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
