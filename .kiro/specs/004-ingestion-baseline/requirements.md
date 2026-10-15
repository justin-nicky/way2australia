# 004 — Ingestion Baseline Requirements

Status: approved (2026-10-15)

## Goal

Turn eligible knowledge documents into a Qdrant dense index through a deterministic, idempotent, re-runnable batch pipeline: knowledge files in, dense index out.

The index is a derived artifact. Documents stay the source of truth; Qdrant records what was indexed, and no separate state store exists.

This spec is roadmap item 3 (ingestion baseline). It also closes the Spec 002 retrospective items F1, F3 and F4 and records the `persona_scope` decision (F2).

## Dependencies

- Spec 002 — document model and repository (merged): `LocalDocumentRepository`, `list_eligible_documents`, `GUEST_PUBLIC_POLICY`, `content-hash-v1`.
- Spec 001 — local Qdrant (`qdrant/qdrant:v1.19.2` in `docker-compose.yml`).
- Spec 002 retrospective: `.kiro/specs/002-document-model-and-repository/review.md` ("Notes for the next spec").

## Decisions resolved before drafting

- **Embedder:** an `Embedder` Protocol with a BGE-M3 adapter and a deterministic fake. The fake is used for unit tests and CI.
- **Chunking:** a heading/section baseline behind a `Chunker` Protocol. Recursive, semantic and FAQ-aware chunking belong to roadmap item 7.
- **`persona_scope`:** intentionally dropped. `access_scope` is the only authorization field. `persona_scope` stays in source files as informational metadata and is not loaded, not written to the payload and not hashed. The hash stays `content-hash-v1`. A later persona spec adds the field, its purpose and `content-hash-v2` together.
- **Versions (F4):** one version per `document_id` in the index. Version history stays Phase 2.
- **Hash-refresh script:** out of scope. Ingestion never edits knowledge, and rewriting `sha256`/`body_sha256` automatically would bypass the integrity check.
- **No separate state store:** each point's payload records what was indexed; ingestion reads it back from Qdrant.
- **No guard function:** the index records `embedder_is_fake`; the evaluation spec enforces it.
- **BGE-M3 is an optional dependency**, installed by a separate command, so `make setup`, `make verify` and CI stay fast with the fake embedder.

## R1 — Target state comes from eligible documents only

Ingestion shall compute its target state from `list_eligible_documents(repository, GUEST_PUBLIC_POLICY)` and never from `list_documents()`.

### Acceptance criteria

- The target state is exactly the set of eligible documents.
- After a run, every indexed `document_id` belongs to an eligible document, and every eligible document has points.
- Any point whose `document_id` is not among the eligible documents is deleted. This one rule covers deprecated, retrieval-disabled and removed documents.
- Security fixtures, synthetic documents and non-public documents never reach the index.
- Ingestion depends on `DocumentRepository`, never on physical file paths.

## R2 — Loader validates dates itself (retro F1)

`LocalDocumentRepository` shall reject any date field (`last_reviewed_at`, `effective_from`, `effective_to`, and any other date field in the metadata schema) that is not a valid `YYYY-MM-DD` date.

### Acceptance criteria

- The loader never accepts a document that `make validate-knowledge` rejects for date format.
- A bad value in any date field fails loading with an error naming the document and field, and no absolute path.
- The seed corpus still loads with no changes to `knowledge/`.

## R3 — Authorization policy agrees with configuration (retro F3)

A deterministic test shall assert that `GUEST_PUBLIC_POLICY` agrees with `config/access_policy.yaml`.

### Acceptance criteria

- The guest role maps to exactly `[public]` in both places.
- The access-scope enum values match the scopes named in the configuration.
- The test fails if either side changes alone.

## R4 — Chunker interface and heading baseline

Chunking shall sit behind a `Chunker` Protocol. The baseline splits on Markdown headings with a size cap.

### Acceptance criteria

- The chunker has a name and a version, both recorded in the index settings.
- `section_id` is derived from the slugged heading text, never from position, paragraph index or chunk index.
- A document with no headings is one section with the fixed `section_id` `main`.
- When the size cap splits a long section, every piece keeps the same `section_id`; only the chunk position differs.
- Chunking is deterministic: the same document yields the same chunks, IDs and positions.
- No Malayalam-specific behavior is hard-coded.
- The spec states that all 13 seed documents have no headings and run 83–248 words, so the baseline yields one chunk per document today. This is a baseline, not evidence that heading chunking works.
- No headings are added to files under `knowledge/` by this spec.

## R5 — Embedder interface and deterministic fake

Embedding shall sit behind an `Embedder` Protocol.

### Acceptance criteria

- The Protocol has separate `embed_documents()` and `embed_query()` methods.
- An embedder reports its model ID, revision, vector size, settings (including normalization) and whether it is fake.
- A deterministic fake embedder produces the same vectors for the same text, with the declared vector size.
- Output is dense-only.
- Unit tests and CI use the fake and need neither PyTorch nor a model download.

## R6 — BGE-M3 adapter as an optional dependency

A BGE-M3 adapter shall implement `Embedder`, with its heavy dependencies in an optional group.

### Acceptance criteria

- The adapter's dependencies (PyTorch and the model loader) are installable only through a separate documented command.
- `make setup`, `make verify` and CI never install or import them.
- The model revision is pinned in configuration and never "latest". The adapter reports that revision as its own.
- The model is loaded once per process, and batch size comes from configuration.
- `make verify` (Pyright included) passes without the optional group installed. The design keeps the adapter's unresolved imports from failing type checking, by lazy import with a targeted ignore or by excluding that module.
- Importing the package without the optional group installed works; selecting the adapter without it fails with an error naming the install command.
- A smoke test with the real model runs only when explicitly requested through an environment flag, and reports "skipped" otherwise.

## R7 — Index settings and mismatch refusal

The index shall record the settings it was built with, and ingestion shall refuse to mix incompatible vectors.

### Acceptance criteria

- Recorded settings: embedder model ID, revision, vector size, normalization, `embedder_is_fake`, chunker name and version, hash contract, index version label.
- Where the settings live is named in the design, with a fallback (a reserved settings point or per-point payload) if the pinned Qdrant version lacks collection metadata.
- If the embedder model, revision, vector size, normalization or chunker name/version differs from the recorded settings, ingestion refuses to write and names the mismatch.
- The refusal points to an explicit rebuild: a new collection named after a new index version label.
- The collection name has a single source: it is derived as `<base>-<index version label>` from the configuration, so the name and the recorded label cannot disagree.
- A change of hash contract (for example `content-hash-v2`) is not a refusal case: every document then appears changed and is re-indexed through ordinary change detection (R10).
- The settings-storage mechanism, including its fallback, works in both `qdrant-client` in-memory mode and Docker Qdrant.
- A collection with no recorded settings is created fresh; a non-empty collection with missing settings is refused.
- The vector field is a named `dense` vector, so sparse vectors can be added later.
- The evaluation spec, not this spec, enforces the use of `embedder_is_fake`.

## R8 — Payload fields and authorization data

Every point shall carry an explicit payload that supports retrieval-time authorization and language filtering.

### Acceptance criteria

- The design lists the payload fields explicitly. At least: `tenant_id`, `access_scope`, `owner_user_id`, `lote_languages`, `content_language`, `language_scope`, `document_id`, `document_version`, `section_id`, chunk position, chunk text, title, `knowledge_domain`, `source_authority`, `source_type`, `source_url` (needed for citations; covered by the hash), `content_hash`.
- Authorization and language fields are present even though only guest-eligible documents are indexed, so retrieval can filter as a second line of defence and later staff or subscriber scopes need no schema change.
- Every non-identity payload field is covered by `content_hash`. Identity fields (`document_id`, `document_version`, `section_id`, chunk position) are compared directly.
- `persona_scope` is not written to the payload.
- `last_reviewed_at` is not written to the payload, because the hash excludes it and a review-date change must not require a re-index.
- No `lote_languages` value is Malayalam-specific in code; global knowledge keeps `["*"]`.
- Language metadata and authorization metadata stay separate fields.

## R9 — Point identity and replacement

Point IDs shall be deterministic, and replacing a document shall leave no orphans.

### Acceptance criteria

- Each point ID is a UUIDv5 derived from `document_id`, `section_id` and chunk position, under a UUID namespace that is a documented constant.
- The same input yields the same IDs, so re-running is idempotent.
- Replacing a changed document deletes all of that document's points, then inserts the new ones, so a document that shrinks from 3 chunks to 2 leaves no orphaned chunk.
- The brief window between delete and insert is accepted for Phase 1 batch runs and is documented. Atomic switching belongs to the Phase 2 release workflow.

## R10 — Change detection

Ingestion shall compare the target state with what Qdrant records, and write only what changed.

### Acceptance criteria

- A document is re-indexed when its `content_hash` or its `document_version` differs from what the index records.
- An unchanged document is left untouched: no embedding call, no write.
- A second run on an unchanged corpus makes no writes and no embedding calls.
- State is read from Qdrant payloads; no separate state store, file or database is added.
- For a changed document, ingestion embeds the new chunks first, then deletes the document's points, then inserts the new ones. A document therefore never holds a mix of old and new chunks.
- If embedding fails, the document's previous points are kept. If deletion or insertion fails, the document may be left absent; the next run treats it as new and restores it.
- A failure on one document does not stop the others. The run reports each failure and exits non-zero.

## R11 — Run summary

Each run shall print a summary that makes idempotency visible.

### Acceptance criteria

- The summary reports documents added, updated, unchanged and deleted, plus the index version label and the embedder ID.
- It reports failures, and the exit code is non-zero if any occurred.
- The summary contains no absolute paths and no document text.
- Langfuse tracing is not added.

## R12 — Entry point and configuration

An ingestion command and a documented configuration shall exist.

### Acceptance criteria

- `make ingest` runs ingestion against the configured repository and Qdrant. It is not an HTTP route.
- The design names where each value lives:
  - Qdrant URL and collection base name (runtime settings, environment-driven);
  - embedder model ID, pinned revision and batch size, chunker size cap, index version label (versioned configuration file);
  - the collection name is derived from the base name and the index version label (R7), not set separately.
- The design reconciles these values with `experiments/configs/day1_baseline.yaml`. The embedding model must agree, and a test enforces it. The chunking strategy differs deliberately: that file is roadmap item 7's recursive experiment, so the design records the divergence and `day1_baseline.yaml` is left unchanged.
- No secrets are placed in code, configuration or prompts.
- Choosing the fake embedder for a real collection is allowed, and the index records it as fake.

## R13 — Test strategy

Tests shall stay fast by default and report honestly.

### Acceptance criteria

- `make verify` runs with the fake embedder and in-memory or mocked Qdrant, and needs neither PyTorch, a model download nor Docker.
- The settings-storage mechanism (R7) is tested in both in-memory mode and, as an integration test, against Docker Qdrant.
- Integration tests against the local Docker Qdrant carry the `integration` marker and report "skipped" when Qdrant is not reachable.
- The real-model smoke test runs only when explicitly requested and reports "skipped" otherwise.
- Deterministic checks cover: idempotency, replacement without orphans, deletion of non-eligible documents, no ineligible document reaching the index, settings-mismatch refusal, and stable section and point IDs.

## R14 — Decisions and documentation

Durable decisions shall be recorded in the repository.

### Acceptance criteria

- `DECISIONS.md` records: the `persona_scope` decision, the payload rule, the optional BGE-M3 dependency, the one-version-per-document rule and the mismatch-refusal rule.
- `TECH_STACK.md` records new dependencies (the Qdrant client and the optional BGE-M3 group).
- `COMMANDS.md` documents `make ingest` and the optional install command.
- `CURRENT_STATE.md` describes implemented reality only.

## Out of scope

- Retrieval, BM25 and sparse vectors, reranking, and generation.
- Evaluation runs and any enforcement of `embedder_is_fake`.
- Recursive, semantic and FAQ-aware chunking; `knowledge/structured/owner_approved_faq_pairs.jsonl`.
- Adding headings to `knowledge/` files (a human-approved content change).
- The manifest hash-refresh script.
- Version history and multiple versions per `document_id`.
- Knowledge Release workflow, atomic publishing, rollback, S3 and any Phase 2 feature.
- Langfuse tracing and analytics.
- Staff, subscriber or private-user indexing.

Known deferred gap: evaluation cases have empty `relevant_section_ids`, so only document-level retrieval metrics are possible at first.

## Definition of Done

- Every requirement above is satisfied and traced to a task and verification.
- `make verify` passes without installing the optional BGE-M3 group.
- Ingestion of the seed corpus into a local Qdrant is idempotent: a second run reports zero added, updated and deleted.
- No file under `knowledge/`, `evaluation/` or `config/` was changed, except a new ingestion configuration file if the design places one under `config/`.
- `CURRENT_STATE.md`, `DECISIONS.md`, `TECH_STACK.md` and `COMMANDS.md` match the implemented reality.
- Hand off to `spec-orchestrator` for completion.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T7 | `make test-unit`: eligible-only target, deletion of non-eligible, security fixtures never indexed |
| R2 | T1 | `make test-unit`: bad date in each field fails loading; `make validate-knowledge` |
| R3 | T1 | `make test-unit`: policy-vs-`config/access_policy.yaml` test |
| R4 | T2 | `make test-unit`: chunker and `section_id` tests, seed one-chunk baseline |
| R5 | T3 | `make test-unit`: fake embedder determinism/size/normalization |
| R6 | T4 | `make verify` without the group; smoke test skipped unless `W2A_RUN_BGE_M3_SMOKE=1` after `make setup-bge-m3` |
| R7 | T5, T6 | `make test-unit`: `compare`, name derivation, startup table and mismatch refusal (in-memory); `make test-integration` (Docker) |
| R8 | T5 | `make test-unit`: payload field set and hash-coverage subset test |
| R9 | T5, T6 | `make test-unit`: stable `point_id`, namespace pinned, 3-to-2 shrink leaves no orphan |
| R10 | T7 | `make test-unit`: idempotent second run with no embeds/writes, update triggers, failure isolation, repair |
| R11 | T7, T8 | `make test-unit`: `RunReport` and CLI summary/exit codes; `make ingest` twice |
| R12 | T8 | `make test-unit`: config/settings loading, `day1_baseline.yaml` agreement; `make ingest` |
| R13 | T4, T6, T7 | `make verify` (no Docker/PyTorch); `make test-integration` skips without Qdrant; smoke test opt-in |
| R14 | T9 | Review of `DECISIONS.md`, `TECH_STACK.md`, `COMMANDS.md`, `CURRENT_STATE.md`; `make verify` |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
