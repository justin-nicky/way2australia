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

## D020 — Local Qdrant image pin
Use the official `qdrant/qdrant:v1.19.2` Docker image for the Phase 1 local Qdrant dependency.

Local Qdrant data lives in a named Docker volume, keeping derived index state outside committed source files.

## D021 — Portable spec-driven agent skills
The SDD workflow is encoded as three Agent Skills: `spec-planner`, `spec-implementer` and `spec-reviewer`.

`agent-skills/` is the only editable source. `scripts/sync_agent_skills.py` generates the committed mirrors:
- `.claude/skills/` (Claude Code);
- `.agents/skills/` (Codex, documented repo-scope path; `.codex/skills/` is not used, to avoid duplicate listings);
- `.kiro/skills/` (Kiro).

Canonical frontmatter stays portable (`name`, `description`). Claude-only fields are injected into the Claude mirror:
- the implementer and reviewer are explicit-invocation only;
- the reviewer runs as a forked subagent with no implementer context.

Codex explicit-only invocation uses `agents/openai.yaml`. Model tiers are advisory; the model actually used is recorded in handoffs and reviews.

## D022 — Spec approval and review state live in the repository
Each spec file carries a `Status:` line. Approval is recorded there by date, never only in chat.

Independent review results are appended to `.kiro/specs/<spec>/review.md`. A failed review adds `RM<N>.<k>` remediation tasks to `tasks.md`.

Approved amendments are recorded in `## Change log` in `requirements.md`.

Implementation must not change `evaluation/`, `knowledge/` or `config/` unless an approved task requires it.

See `docs/project/WORKFLOW.md` → "Spec status".

## D023 — Task-gated agent workflow
Replace the whole-spec implement-then-review flow with a per-task loop: `spec-orchestrator` routes, `spec-implementer` does one task per run on branch `spec/<NNN>`, `task-reviewer` verifies it and summarizes it for the user, the user approves each task. `spec-reviewer` becomes an optional retrospective. Specified in Spec 003; lifecycle in `docs/project/WORKFLOW.md`.

Supersedes from D022:
- the `implemented — pending review`, `review failed — round N` and `verified (…, review round N)` statuses (retired);
- `review.md` as the required gate for "verified" (a spec is verified when every task is approved and the branch is merged);
- the forked, isolated-context reviewer (`context: fork`): independence now comes from a fresh session, because a fork inherits the caller's model.

Remains from D022:
- `Status:` lines and dated approvals live in the spec files;
- `## Change log` records approved amendments;
- implementation must not change `evaluation/`, `knowledge/` or `config/` unless an approved task requires it;
- `review.md` and `RM<N>.<k>` tasks, now only for the optional retrospective.

Model tiers stay advisory and apply when a session starts. Spec 003 itself was implemented under the old flow directly on `main` (bootstrap exception). The roadmap's ingestion spec is renumbered 004.

## D024 — Document repository, hashing and eligibility (Spec 002)
- `DocumentRepository` is a `Protocol` in `packages/rag`; `LocalDocumentRepository` reads the validated manifest and never exposes physical paths to callers.
- `content_hash` (`content-hash-v1`) is the only change-detection signal for ingestion. It covers the normalized body hash plus retrieval-affecting metadata; identity, review dates, release and path fields are excluded. Changing the recipe requires a new `HASH_CONTRACT` value. Manifest `sha256` (raw file) and `body_sha256` (body) are integrity checks the loader verifies.
- Production eligibility is one explicit `EligibilityPolicy`: approved AND active AND `retrieval_enabled` AND not synthetic AND `access_scope` in server-owned allowed scopes (Phase 1: `guest` -> `public`). Never inferred from directory; language metadata never widens access. Security fixtures are valid but ineligible and are tested through an isolated repository.
- The language rule lives only in `DocumentQuery.matches`.
- `make validate-knowledge` checks the seed corpus and runs inside `make verify`.
- New runtime dependencies in `packages/rag`: `jsonschema` (manifest JSON Schema validation, required by the design) and `pyyaml` (frontmatter parsing). Both are small, widely used and pinned in `uv.lock`.

## D031 — Required retrospective that reconciles documentation
Supersedes the "optional retrospective" part of D023.

- `spec-reviewer` runs for every spec after all tasks are approved. A spec is verified only after a retrospective round with outcome `PASS`, the user's approval and the merge.
- The retrospective reconciles documentation with the code as built: `DECISIONS.md`, `TECH_STACK.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md`, other touched docs, and `## As-built notes` in the spec's `design.md`. It edits docs only; code that contradicts the approved spec without a recorded amendment is a finding, not something to document.
- Its changes stay uncommitted until the user approves; the orchestrator commits them with `Spec-Review: <NNN>/retrospective`, then merges.
- Numbered D031 because `spec/004` already uses D025–D030.
