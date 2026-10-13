# Current State

Last updated: 2026-10-13

## Current phase

Implementation bootstrap.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is partially implemented.

## Current goal

Start implementation using specification-driven development and repository-based shared context so Codex, Claude Code and Kiro can be used interchangeably.

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
- reusable package skeletons for `packages/core`, `packages/rag` and `packages/observability`;
- repository hygiene for local environment files, Python caches, local uv state and generated OS noise.

Not yet implemented:
- typed runtime configuration;
- automated API/config tests;
- full quality command surface;
- local Qdrant Docker Compose service;
- final Spec 001 verification/handoff;
- Pydantic domain models;
- DocumentRepository;
- ingestion;
- embeddings;
- retrieval;
- generation;
- observability;
- CI/CD;
- Terraform deployment.

## Recommended next specs

1. `.kiro/specs/001-project-foundation/`
2. `.kiro/specs/002-document-model-and-repository/`

The second should cover:
- `KnowledgeDocument`;
- metadata/version fields;
- `DocumentRepository` Protocol;
- `LocalDocumentRepository`;
- manifest loading;
- schema validation;
- document hashing;
- unit/integration tests.

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
