# Architecture Decisions

This file records durable decisions so coding agents do not repeatedly revisit settled choices.

## D001 — Python-first backend
Use Python for RAG/backend implementation and Next.js/TypeScript for frontend.

## D002 — RAG as reusable internal package
RAG logic belongs under `packages/rag/`, separate from application code.

## D003 — Knowledge outside RAG package
Business/official knowledge, raw sources, evaluation datasets, prompts and experiment configs do not live inside `packages/rag/`.

## D004 — DocumentRepository abstraction
Ingestion obtains documents through `DocumentRepository`.

Phase 1: `LocalDocumentRepository`.
Phase 2: expected `S3DocumentRepository`.

## D005 — Documents are truth; chunks are derived
Documents and evaluation assets are versioned source entities. Chunks, embeddings and indexes are derived artifacts.

## D006 — Authorization during retrieval
Access filters are server-created and applied before context construction/generation.

## D007 — Public-only Phase 1
Implement only guest/public retrieval now while retaining metadata/interface support for future scopes.

## D008 — Language and authorization are independent
Language applicability, content language, query language and access scope remain separate concepts.

## D009 — Source precedence
- owner-approved source for Way2Australia business policy;
- NAATI for official CCL rules;
- Home Affairs for migration/visa rules.

## D010 — Qdrant primary, SQLite FTS5 fallback
Use Qdrant for primary retrieval and SQLite FTS5 as authorization-preserving lexical fallback.

## D011 — BGE-M3 initial embeddings
Start with BGE-M3 for multilingual, low-cost experimentation.

## D012 — Bedrock Runtime for generation
Use Amazon Bedrock Runtime through an internal generator abstraction.
Do not use Bedrock Knowledge Bases/Agents/AgentCore in Phase 1.

## D013 — Git/YAML prompt versioning
Prompts are versioned repository assets; Langfuse records operational versions/traces.

## D014 — Evaluation Suite model
Goldens are one evaluation-case category inside a broader Evaluation Suite.

## D015 — Human-governed LLM suggestions
Phase 2 LLM evaluation suggestions are candidates only.
Admin may accept, edit+accept, reject or manually create another case.

## D016 — Knowledge Release model
Use `Knowledge Release` for an immutable active release and `Knowledge Release Candidate` during Phase 2 changes.

A release references:
- Document Snapshot;
- Evaluation Suite;
- RAG Config;
- Index Version.

## D017 — Phase 2 storage direction
Plan for:
- S3 for immutable/versioned document bodies;
- metadata database for relationships/workflow/audit;
- Qdrant as derived retrieval index.

## D018 — Phase 2 analytics only
Define stable analytics event contracts in Phase 1; do not implement product analytics pipelines/dashboard yet.

## D019 — Local uv-managed Python for setup
Use `uv` for Python environment setup and dependency locking.

The root `make setup` command keeps uv cache and uv-managed Python installs in ignored repo-local directories so setup works in restricted coding-agent environments without writing hidden state under the user home directory.
