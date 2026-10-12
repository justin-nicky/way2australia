# 001 — Project Foundation Requirements

## Goal

Establish the minimum development and application foundation required for later RAG implementation.

This specification creates the repository/runtime skeleton only. It does **not** implement document ingestion, embeddings, retrieval, generation, evaluation, or deployment.

## R1 — Repository boundaries

The project shall expose clear boundaries for application code, reusable RAG code, shared domain code, tests, prompts, infrastructure, knowledge assets, and evaluation assets.

### Acceptance criteria

- `apps/api/` exists for the FastAPI application.
- `apps/web/` is reserved for the future Next.js frontend.
- `packages/rag/` exists for reusable RAG implementation.
- `packages/core/` exists for shared domain concepts.
- `packages/observability/` is reserved for shared tracing/logging helpers.
- knowledge/evaluation/config/prompt assets remain outside `packages/rag/`.
- the API route layer does not contain RAG implementation logic.

## R2 — Reproducible Python environment

The backend shall have a reproducible Python development environment.

### Acceptance criteria

- the supported Python version is explicitly defined;
- dependencies can be installed using one documented project command;
- runtime and development dependencies are identifiable;
- dependency state is reproducible on another development machine;
- project configuration is centralized rather than scattered across unrelated files.

## R3 — Minimal FastAPI application

The project shall expose a minimal working FastAPI application.

### Acceptance criteria

- the application can start locally;
- `GET /health` returns a successful response;
- the health endpoint does not depend on RAG services;
- API routing is separated from application startup/wiring;
- route handlers remain thin.

## R4 — Typed runtime configuration

Runtime configuration shall be accessed through a typed configuration layer.

### Acceptance criteria

- application modules do not repeatedly call `os.getenv()` directly;
- local environment variables can be loaded for development;
- required configuration fails clearly when invalid or missing;
- secrets are not committed;
- `.env.example` documents supported environment variable names without real secrets.

## R5 — Automated test foundation

The project shall provide a working automated test setup.

### Acceptance criteria

- unit tests can be executed with a stable project command;
- at least one API health test exists;
- failed tests return a non-zero status;
- the test layout supports later unit and integration test separation.

## R6 — Code-quality tooling

The project shall provide stable commands for formatting, linting, type checking, and verification.

### Acceptance criteria

The following commands exist:

- `make setup`
- `make format`
- `make lint`
- `make typecheck`
- `make test`
- `make verify`

`make verify` runs the agreed fast deterministic checks for this phase.

## R7 — Local Qdrant dependency

The project shall support starting Qdrant locally for future RAG work.

### Acceptance criteria

- Qdrant is defined through Docker Compose;
- the service can be started and stopped locally;
- persistent local data is stored outside committed source files;
- a health check is configured where practical;
- no ingestion or retrieval logic is required in this spec.

## R8 — Repository hygiene and secrets

The repository shall be safe to clone and use without exposing local secrets or generated state.

### Acceptance criteria

- `.gitignore` excludes `.env`, Python caches, virtual environments, local model/index data, editor noise, and other generated artifacts;
- `.env.example` contains placeholders only;
- no credentials are committed;
- generated local Qdrant data is ignored.

## R9 — Multi-agent handoff compatibility

The implementation shall preserve the repository as the canonical handoff medium between Codex, Claude Code, Kiro, and human contributors.

### Acceptance criteria

- root `AGENTS.md` remains the common agent entry point;
- `CLAUDE.md` remains a thin Claude adapter;
- stable project commands are documented in `docs/project/COMMANDS.md`;
- `docs/project/CURRENT_STATE.md` is updated after this spec is completed;
- the completed project can be continued without relying on private chat history.

## Out of scope

This specification does **not** implement:

- `KnowledgeDocument`;
- `DocumentRepository`;
- document ingestion;
- chunking;
- embeddings;
- Qdrant collections/indexing;
- BM25/FTS5;
- retrieval;
- reranking;
- Bedrock generation;
- RAG evaluation;
- Langfuse tracing;
- AWS deployment;
- Terraform resources;
- Next.js application functionality;
- Phase 2 Knowledge Operations.

## Definition of Done

This specification is complete only when:

- all approved tasks are complete;
- all acceptance criteria are satisfied;
- `make verify` passes;
- the FastAPI application starts;
- `/health` passes its automated test;
- Qdrant can be started through Docker Compose;
- no out-of-scope RAG functionality was added;
- `docs/project/CURRENT_STATE.md` reflects the completed foundation.

## Traceability

| Requirement | Primary tasks | Verification |
|---|---|---|
| R1 | T2 | repository structure review |
| R2 | T1 | `make setup` |
| R3 | T3 | API health test |
| R4 | T4 | configuration tests |
| R5 | T5 | `make test` |
| R6 | T6 | `make verify` |
| R7 | T7 | Docker/Qdrant health |
| R8 | T1, T7 | repository hygiene review |
| R9 | T8 | project docs/state review |
