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

## D025 — `persona_scope` is not loaded, indexed or hashed (Spec 004)
`access_scope` is the only authorization field. `persona_scope` stays in source files and the manifest schema as informational metadata; it is not loaded into `KnowledgeDocument`, not written to the index payload and not in `content-hash-v1`. A later persona spec adds the field, its purpose and `content-hash-v2` together. Closes Spec 002 retrospective F2.

## D026 — Index payload rule and one version per document (Spec 004)
- The payload has 17 fields. Non-identity fields are covered by `content_hash` (so a change re-indexes the document); identity fields (`document_id`, `document_version`, `section_id`, `position`, chunk identity) are compared directly. `last_reviewed_at` is excluded from the hash and from the payload, so a review-date change never forces a re-index. Eligibility-only fields (`approval_status`, `lifecycle_status`, `retrieval_enabled`, `synthetic`, effective dates, `introduced_in_release`) are not in the payload: the eligibility policy decides what is indexed, not payload filtering. A test pins the payload field set and the hash-coverage subset.
- The index holds exactly one version per `document_id`. A new `document_version` or `content_hash` replaces all of that document's points (embed first, then delete-and-upsert, so an embedding failure leaves the old points). Version history stays Phase 2. Closes Spec 002 retrospective F4.
- Point IDs are UUIDv5 of `document_id`, `section_id` and `position` under `INGESTION_NAMESPACE` (`533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2`). This value is permanent: changing it changes every point ID. Stable section IDs: `slugify` applies NFKC and lower-casing, drops Unicode `Cf` characters (ZWJ, ZWNJ, zero-width space, BOM), treats `str.isalnum()` characters and `M*` marks as word characters (not regex `\w`, which splits Indic words) and turns other runs into `-`. A heading longer than half the chunk cap is truncated in the chunk text only, never in `section_id`.

## D027 — Optional BGE-M3 dependency (Spec 004)
`sentence-transformers` (which brings PyTorch) lives in the optional `bge-m3` group of `packages/rag`, with the model pinned to a full commit SHA in `config/ingestion.yaml`. `make verify`, CI and unit tests never need PyTorch, Docker or a model download; they use the deterministic fake embedder. `make setup-bge-m3` installs the group; `make setup` syncs without it and therefore removes it again. A missing group is detected when `BgeM3Embedder` is constructed (`importlib.util.find_spec`, no model load): `make ingest` exits 2 before any Qdrant write. `service.py` also re-raises `OptionalDependencyError` late, for a broken install that `find_spec` cannot see. Also new runtime dependencies in `packages/rag`: `qdrant-client` and `pydantic-settings`.

## D028 — Index settings mismatch refusal and rebuild by new `index_version` (Spec 004)
Index-defining settings (`index_version`, embedder model ID, revision, vector size, normalization and fake flag, chunker name, version and character cap, settings schema version; `hash_contract` is stored but not compared) are stored in a companion `<collection>-settings` collection. A run whose settings differ from the stored ones is refused with exit 2 and no writes, naming each differing field. The store never deletes or recreates a collection. To change settings, set a new `index_version` in `config/ingestion.yaml` (a new collection `<QDRANT_COLLECTION_BASE>-<index_version>`); the old collection is left for the operator to remove. A fake-embedder run records the collection as fake, so a real run is refused afterwards: always use a throwaway `QDRANT_COLLECTION_BASE` for fake runs, otherwise the default `way2australia-idx-v1` collection is marked fake and needs a new `index_version`. `embedder_is_fake` is recorded, not enforced, in this spec.

## D029 — Ingestion reads state from Qdrant, no separate state store (Spec 004)
Each point's payload records what was indexed. Ingestion reads it back, classifies each eligible document as added, updated or unchanged (content hash, document version and expected point-ID set), deletes `document_id`s that are no longer eligible, and continues past per-document failures (exit 1). Only documents passing the guest/public `EligibilityPolicy` reach the index. The run summary contains no absolute paths or body text. Exit codes: 0 success, 1 any document failure, 2 refusal or configuration error.

## D030 — Baseline chunking differs from `day1_baseline.yaml` on purpose (Spec 004)
`experiments/configs/day1_baseline.yaml` names recursive chunking (600 tokens, 60 overlap). The ingestion baseline uses heading/section chunking with a 2000-character cap, because token counting would couple the chunker to a tokenizer and the seed documents (13, 83 to 248 words, no headings) yield one chunk each either way. The embedding model, corpus manifest path and access scope are tested to agree with `day1_baseline.yaml`, which is left unchanged. Recursive, semantic and FAQ-aware chunking belong to the chunking roadmap item and need a new `index_version`.

## D031 — Required retrospective that reconciles documentation
Supersedes the "optional retrospective" part of D023.

- `spec-reviewer` runs for every spec after all tasks are approved. A spec is verified only after a retrospective round with outcome `PASS`, the user's approval and the merge.
- The retrospective reconciles documentation with the code as built: `DECISIONS.md`, `TECH_STACK.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md`, other touched docs, and `## As-built notes` in the spec's `design.md`. It edits docs only; code that contradicts the approved spec without a recorded amendment is a finding, not something to document.
- Its changes stay uncommitted until the user approves; the orchestrator commits them with `Spec-Review: <NNN>/retrospective`, then merges.
- Numbered D031 because `spec/004` already uses D025–D030.

## D032 — Spec 004 retrospective corrections to D026 and D027
Corrects wording in D026 and D027 to match the code; neither decision changes.

- D026 identity fields are exactly `document_id`, `document_version`, `section_id` and `chunk_position` (`payload.IDENTITY_FIELDS`). There is no separate "chunk identity" field; point IDs use the same `section_id` and position.
- D026 decides Spec 002 retrospective F4 (one version per `document_id`; the manifest loader already rejects a second record for a `document_id`). It does not fully close it: the `repositories/manifest.py` module docstring still says "one record per document version" and should be corrected in a later code change.
- D027's "optional `bge-m3` group" is a `[project.optional-dependencies]` extra of `packages/rag`, installed with `uv sync --extra bge-m3` (`make setup-bge-m3`). It is not a PEP 735 dependency group (`uv sync --group`).

## D033 — `AccessContext` and `Role` live in core; the guest resolver returns the identical policy object (Spec 005)
`packages/core/src/way2australia_core/access.py` defines `Role` (the roles in `config/access_policy.yaml`) and a frozen `AccessContext(role, tenant_id)`. It carries no scopes and no language fields: scopes are a server-code policy decision, and language never grants or denies access. `tenant_id` is stripped and a blank value is refused by the type itself. `resolve_access` (`retrieval/access.py`) is the only role-to-policy mapping; `guest` returns the same `GUEST_PUBLIC_POLICY` object that ingestion eligibility uses (a test pins the identity), and every other role raises `RetrievalConfigurationError` until a spec implements it.

## D034 — `W2A_TENANT_ID` is a server setting (Spec 005)
The tenant is `RuntimeSettings.tenant_id`, read from `W2A_TENANT_ID` (default `way2australia`). An empty or whitespace-only value is refused. The one shared loader `load_runtime_settings` (`ingestion/config.py`) turns a validation error into the caller's configuration error that names only environment variable names, never values, and gives a generic message if the error has no field location. Ingestion and both retrieval CLIs use it, so `make ingest` also records and refuses by this tenant. There is no CLI flag for role, scope or tenant, and no query or evaluation-case field can set them.

## D035 — One filter builder, a fail-closed re-check, and the same path for later fallbacks (Spec 005)
`build_access_filter(ResolvedAccess)` is the only place an authorization filter is built: `access_scope` in the policy's allowed scopes, `tenant_id` equal to the server tenant, and `owner_user_id` null (a point without that field is excluded). It runs inside the Qdrant query, before any text reaches a caller. `check_hit` re-validates every returned payload against the same `ResolvedAccess` and raises `RetrievalAuthorizationError` if a store drops the filter (fail closed, exit 2 in the CLIs). Later fallbacks (BM25, SQLite FTS5) must take the same `ResolvedAccess` and call `check_hit`; no second policy path may be added.

## D036 — Query-embedder binding is read-only and compares embedder fields only (Spec 005)
`DenseIndex.open` never writes. It requires the collection, its `-settings` record, a `dense` vector of the right size, `index_version` equality, and equality of the five embedder fields (model ID, revision, vector size, normalization, fake flag). Chunker fields and `hash_contract` are not compared: they describe how documents were split, not how a query is embedded. Refusals use retrieval-side advice (re-run ingestion into this index version, or point retrieval at the matching `index_version` and collection), never ingestion's "edit `config/ingestion.yaml`" wording. A fake embedder against a real index (or the reverse) is refused.

## D037 — Baseline result format (Spec 005)
`make retrieval-baseline` writes one JSON document (`schema_version` 1.0, `kind: retrieval_baseline`). Decisions:
- the release is declared, not verified: `--release` (default `seed-v1`) must match `knowledge/releases/<id>.json`, and the result records `declared_knowledge_release_id` with `release_snapshot_verified: false` beside the actual collection, `index_version` and full `IndexSettings`;
- a random-retrieval expectation is recorded as `random_hit_rate_formula` `min(1, k/N)` with the concrete numbers (for example `min(1, 5/13)`) and `random_hit_rate_at_k`, because top-5 over 13 documents is optimistic;
- one unmeasured warm-up query runs first; `warmup_ms` is recorded and excluded from p50/p95;
- query text, chunk text, absolute paths and secrets are never written; cases are identified by `case_id`/`case_version` and the ranked `document_id`s;
- a fake-embedder index is refused unless `--allow-fake`, and then the notes say "not a quality measurement";
- the golden's `access_context` is ignored: every case uses the one server-resolved guest access;
- a result file is never overwritten, nothing is written on error (a partial file from a failed write is removed), and tests never write under `experiments/results/`.

## D038 — The embedding device is recorded, not pinned, and not an index setting (Spec 005)
The retriever result and the baseline JSON record `embedder.device` read after the warm-up query (a real `BgeM3Embedder` reports `None` until the model loads). The device is not part of `IndexSettings` and is not compared at query time, and nothing pins it. Cross-machine reproducibility (for example `mps` versus `cpu`) is therefore left to later work. This follows Spec 004's open observation.

## D039 — `make lint` checks formatting (Spec 005)
`make lint` runs `ruff check` and `ruff format --check`, so `make verify` fails on format drift that `make format` would fix. `UV_HTTP_TIMEOUT ?= 300` is the default in the `Makefile` for `make setup-bge-m3` (override per run, for example `UV_HTTP_TIMEOUT=600`). Both close Spec 004 observations.
