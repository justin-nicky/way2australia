# 004 — Ingestion Baseline Tasks

Status: verified (2026-10-17, merged dde5b35)

Implement in order; each task depends on the ones before it. New ingestion code lives under `packages/rag/src/way2australia_rag/ingestion/` and its tests under `packages/rag/tests/ingestion/` (design "Package / file placement"). `make verify` must never need Docker, PyTorch or a model download.

## T1 — Hardening: loader date validation and policy-vs-config test

**State:** approved (2026-10-15)
**Requirements:** R2, R3

- [x] Add one strict `YYYY-MM-DD` date helper shared by the loader (`repositories/local.py` / `manifest.py`) and `repositories/validate.py`, so the two cannot diverge.
- [x] Make `LocalDocumentRepository` reject a bad value in `last_reviewed_at`, `effective_from`, `effective_to` and any other date field the metadata schema defines, with an error naming the document and field and containing no absolute path.
- [x] Add unit tests: a bad value in each date field fails loading; the error names document and field and has no absolute path; the seed corpus still loads with no change to `knowledge/`.
- [x] Add a deterministic test that loads `config/access_policy.yaml` and asserts `roles.guest.allowed_scopes == ["public"]`, that it equals the scopes in `GUEST_PUBLIC_POLICY`, and that every scope named in the file is an `AccessScope` member.
- [x] Do not edit `config/access_policy.yaml` or anything under `knowledge/`.

### Verification

- `make test-unit` (new date and policy tests pass)
- `make validate-knowledge`
- `make verify`

## T2 — Chunker interface, heading baseline and `section_id` rules

**State:** approved (2026-10-15)
**Requirements:** R4

- [x] Create the `ingestion` package (`__init__.py`, `errors.py` with the `IngestionError` hierarchy).
- [x] Implement `Chunk` (frozen) and the `Chunker` Protocol (`name`, `version`, `max_chunk_chars`, `chunk()`) in `chunking.py`.
- [x] Implement `HeadingChunker` (name `heading`, version `1`): ATX headings outside fenced code blocks; text before the first heading or a heading-less body is section `main`.
- [x] Implement slugging: NFKC, lower-case, Unicode-aware non-word runs to `-`, trimmed, empty slug falls back to `section`; leaf heading text only; duplicate slugs get `-2`, `-3`, … in document order.
- [x] Split sections longer than `max_chunk_chars` on paragraph then whitespace boundaries; every piece keeps the `section_id`, `position` is the piece index, each piece starts with its heading line.
- [x] Keep the chunker pure and deterministic; no Malayalam-specific code.
- [x] Unit tests on synthetic documents: no headings gives `main`/0; slugs stable under section reordering; duplicate headings unique; Malayalam and other non-Latin headings slug without special-casing; long section splits within the cap with same `section_id`; determinism; headings in code fences ignored.
- [x] Unit test on the seed corpus: 13 documents, one chunk each, `section_id` `main`, `position` 0 (documented as a baseline, not evidence that heading chunking works).
- [x] Do not add headings to any file under `knowledge/`.
- [x] Unit test: the NFC and NFD forms of the same Malayalam heading give the same slug.
- [x] Unit test: `section_id` comes from the full heading text even when the chunk text truncates the heading (heading longer than half the cap).

### Verification

- `make test-unit`
- `make verify`

## T3 — Embedder interface and deterministic fake

**State:** approved (2026-10-15)
**Requirements:** R5

- [x] Implement `EmbedderInfo` (frozen: model ID, revision, vector size, normalize, is_fake, settings) and the `Embedder` Protocol with separate `embed_documents()` and `embed_query()` in `embedding.py`.
- [x] Implement `FakeEmbedder` (model ID `fake-hash-embedder`, revision `1`, configurable vector size, default 64, `is_fake = True`): SHA-256-derived, expanded to the vector size, L2-normalized, dense-only.
- [x] Unit tests: same text gives same vector; declared size; normalization; query vs document methods; `is_fake`; no PyTorch import.

### Verification

- `make test-unit`
- `make verify`

## T4 — BGE-M3 adapter as an optional dependency

**State:** approved (2026-10-16)
**Requirements:** R6, R13

- [x] Add a `bge-m3` optional dependency group (`sentence-transformers`, which brings PyTorch) to `packages/rag/pyproject.toml`; update `uv.lock`; `make setup` must not install it.
- [x] Add `make setup-bge-m3` (same `uv sync` as `make setup` plus the `bge-m3` extra), with a Makefile comment that `make setup` removes the group again.
- [x] Resolve the current full commit SHA of `BAAI/bge-m3` from the model hub and record it for `config/ingestion.yaml` (created in T8) and in the task handoff; do not invent one.
- [x] Implement `BgeM3Embedder` in `bge_m3.py`: model ID `BAAI/bge-m3`, vector size 1024, dense-only, normalized; refuses a missing revision, `main` or `latest`; reports the pinned revision as its own; passes `revision=` to the loader.
- [x] Load the model lazily once per instance; `embed_documents` encodes in batches of the configured batch size.
- [x] Import `sentence-transformers` only inside the loader method with a targeted `# pyright: ignore[reportMissingImports]`; importing the package without the group works; selecting the adapter without it raises `OptionalDependencyError` naming `make setup-bge-m3`.
- [x] Unit tests (no model): revision refusal; `OptionalDependencyError` message when the group is absent (simulated); module import works without the group.
- [x] Opt-in smoke test: runs only when `W2A_RUN_BGE_M3_SMOKE=1` and the group is installed, embeds one English and one Malayalam sentence, checks size 1024 and normalization; otherwise reports "skipped" with the reason.

### Verification

- `make verify` (without the optional group installed; Pyright passes)
- `make test-unit` shows the smoke test as skipped
- Optional, by the user: `make setup-bge-m3` then `W2A_RUN_BGE_M3_SMOKE=1 make test-unit`, then `make setup` to return to the default environment

## T5 — Index settings, payload fields and point identity

**State:** approved (2026-10-16)
**Requirements:** R7, R8, R9

- [x] Implement `IndexSettings` (frozen, schema_version `1.0`, fields per design incl. `embedder_is_fake`, chunker name/version/`max_chunk_chars`, `hash_contract`) in `settings.py`, plus `build_index_settings(...)`.
- [x] Implement `compare(recorded, wanted)` returning differing fields, ignoring `hash_contract`, and the refusal text pointing to a new `index_version` label in `config/ingestion.yaml`.
- [x] Implement the collection-name derivation `<collection_base>-<index_version>` in one place.
- [x] Implement `PointPayload` (frozen) and `build_payload()` in `payload.py` with exactly the design's field table; define `IDENTITY_FIELDS`; exclude `persona_scope`, `last_reviewed_at` and eligibility-only fields.
- [x] Generate the `INGESTION_NAMESPACE` UUID once and implement `point_id(document_id, section_id, position)` (UUIDv5, unit-separator join) in `identity.py`, with a docstring documenting the constant.
- [x] Unit tests: `compare` ignores `hash_contract` and reports each other field; collection name derivation; payload field set equals the table; hash-coverage subset test against `CONTENT_HASH_METADATA_FIELDS` plus `chunk_text` and `content_hash`; `persona_scope` and `last_reviewed_at` absent; no Malayalam-specific `lote_languages` in code; `point_id` stable and distinct across section and position; namespace constant pinned by a test.

### Verification

- `make test-unit`
- `make verify`

## T6 — Qdrant writer: collection, settings, replace, delete

**State:** approved (2026-10-16)
**Requirements:** R7, R9, R13

- [x] Add `qdrant-client` (compatible with Qdrant `v1.19.2`) to `packages/rag/pyproject.toml` and `uv.lock`.
- [x] Implement `QdrantIndexStore` in `store.py` on the sync client: named `dense` vector; keyword payload indexes on `access_scope`, `tenant_id`, `document_id`, `content_language`, `lote_languages`.
- [x] Implement `ensure_collection(settings)` with the companion `<collection>-settings` collection (one fixed-ID point, 1-dimensional dummy vector, settings as payload) and the design's five-row startup table, raising `IndexSettingsMismatchError` with each differing field; never delete an existing collection.
- [x] Implement `read_state()` (payload-only scroll of identity fields and `content_hash`, returning `IndexedDocument` with version, hash and point-ID set), `replace_document()` (delete by `document_id` filter, then one upsert) and `delete_documents()`.
- [x] Unit tests on `QdrantClient(":memory:")`: each startup-table row; mismatch per field (model, revision, vector size, normalization, chunker version, size cap, fake vs real) refuses with no writes; `hash_contract` change does not refuse; replace shrinking 3 chunks to 2 leaves no orphan; delete; `read_state` round-trip.
- [x] Integration test (marker `integration`) against `http://localhost:6333`: the same settings-storage, replace and delete flows with a unique temporary collection base, removed afterwards; a fixture probes Qdrant and skips with a clear reason when unreachable.

### Verification

- `make test-unit`
- `docker compose up -d qdrant` then `make test-integration` (passes); without Docker, `make test-integration` reports the tests as skipped
- `make verify`

## T7 — Ingestion service: target state, change detection, run summary

**State:** approved (2026-10-16)
**Requirements:** R1, R10, R11, R13

- [x] Implement `IngestionService(repository, policy, chunker, embedder, store, batch_size)` in `service.py` (async), following design steps 1–7, depending only on Protocols, `DocumentRepository` and `QdrantIndexStore`.
- [x] Target state from `list_eligible_documents(repository, GUEST_PUBLIC_POLICY)` only; delete every indexed `document_id` not in the target.
- [x] Classify added / updated (hash, version or point-ID set differs) / unchanged; for each changed document embed first, then replace, in its own try/except; record failures and continue.
- [x] Implement `RunReport` (index version, collection, embedder model ID, `embedder_is_fake`, added/updated/unchanged/deleted `document_id` lists, failures) with no absolute paths or document text.
- [x] Unit tests on in-memory Qdrant, fake embedder and temporary repositories, with counting wrappers: first run adds all; second run zero added/updated/deleted, no embedding calls, no writes; changed body, changed metadata field and bumped `document_version` each update; review-date change does not update; 3-to-2 chunk shrink leaves no orphan; deprecated, retrieval-disabled and removed documents are deleted; security fixtures and non-public documents never reach the index; embedding failure keeps old points, reports and continues; missing points with matching hash/version are repaired.
- [x] Unit test: the seed corpus with the fake embedder indexes 13 documents, one chunk each, and a second run is idempotent.

### Verification

- `make test-unit`
- `make verify`

## T8 — CLI entry point, `make ingest`, configuration and baseline agreement

**State:** approved (2026-10-16)
**Requirements:** R11, R12

- [x] Add `config/ingestion.yaml` per the design, with the BGE-M3 revision SHA resolved in T4.
- [x] Implement `IngestionConfig` (file loader, validation, refuses missing/`main`/`latest` revision) and `RuntimeSettings` (Pydantic Settings: `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_BASE`) in `config.py`; add `pydantic-settings` to `packages/rag/pyproject.toml` and `uv.lock`.
- [x] Implement `cli.py` (`python -m way2australia_rag.ingestion.cli`) with `--repo-root`, `--config`, `--embedder {bge_m3,fake}`; print the summary (index, embedder, fake flag, counts, `document_id`s per category, `ERROR` lines); exit `0` / `1` / `2` as designed; no absolute paths, document text or API key in output.
- [x] Add `make ingest` to the `Makefile` (runs the CLI against the configured repository and Qdrant, passing extra options through `INGEST_ARGS`, e.g. `make ingest INGEST_ARGS="--embedder fake"`); the fake embedder is allowed and recorded as fake in the index.
- [x] Tests enforcing agreement with `experiments/configs/day1_baseline.yaml`: embedding model equal; corpus manifest path is the repository's manifest path; required access scope matches `GUEST_PUBLIC_POLICY`. Leave `day1_baseline.yaml` unchanged; the chunking divergence is recorded in T9.
- [x] CLI tests (in-memory Qdrant, fake embedder): exit codes `0`, `1`, `2` (mismatch, missing optional group, bad config); summary contains no absolute paths; config and settings loading.

### Verification

- `make test-unit`
- `make verify`
- `docker compose up -d qdrant`, then `make ingest INGEST_ARGS="--embedder fake"` twice (with `QDRANT_COLLECTION_BASE` set to a throwaway name): the second run reports `added: 0  updated: 0  deleted: 0`

## T9 — Documentation, decisions and handoff

**State:** approved (2026-10-17)
**Requirements:** R14, Definition of Done

- [x] Add `DECISIONS.md` entries (next free D-number) for: the `persona_scope` decision; the payload rule (non-identity fields hash-covered, identity compared directly, `last_reviewed_at` excluded); the optional BGE-M3 dependency and `make setup-bge-m3`; the one-version-per-`document_id` rule; the settings-mismatch refusal and rebuild-by-new-`index_version` rule (incl. companion settings collection and the `INGESTION_NAMESPACE` constant); the deliberate chunking divergence from `day1_baseline.yaml`.
- [x] Update `docs/project/TECH_STACK.md` with `qdrant-client`, `pydantic-settings` and the optional `bge-m3` group (`sentence-transformers`, pinned revision).
- [x] Update `docs/project/COMMANDS.md` with `make ingest` and `make setup-bge-m3`, including that `make setup` removes the optional group.
- [x] Update `docs/project/CURRENT_STATE.md` to implemented reality only.
- [x] Confirm no file under `knowledge/`, `evaluation/` or `config/` changed except the new `config/ingestion.yaml`.
- [x] Run spec-wide checks: `make verify`; `make test-integration` with Docker Qdrant; `make ingest` twice on the seed corpus (idempotent second run).
- [x] Keep next-spec work out (see Completion gate).
- [x] Hand off to `spec-orchestrator` for completion (`all tasks approved`, optional `spec-reviewer`, merge).

### Verification

- `make verify` passes without the optional BGE-M3 group installed.
- `make test-integration` passes with `docker compose up -d qdrant`.
- `make ingest` second run reports zero added, updated and deleted.
- `git diff --stat main -- knowledge evaluation config` shows only `config/ingestion.yaml`.
- `CURRENT_STATE.md`, `DECISIONS.md`, `TECH_STACK.md`, `COMMANDS.md` and this task list match implemented reality.

## Completion gate

Do not implement in this spec: retrieval or any query path, BM25 or sparse vectors, reranking, generation, evaluation runs or enforcement of `embedder_is_fake`, recursive/semantic/FAQ-aware chunking, the manifest hash-refresh script, version history, Langfuse tracing, HTTP routes, or any Phase 2 feature (Knowledge Release workflow, atomic publishing, rollback, S3).

## Pre-merge manual check (user-owned, not a gate)

Decided 2026-10-15: the Definition of Done idempotency check uses the fake embedder. Before merging `spec/004`, the user runs the opt-in BGE-M3 smoke test (`W2A_RUN_BGE_M3_SMOKE=1`) and one real BGE-M3 ingestion of the seed corpus into a throwaway collection, run twice (the second run must report 0 added, updated and deleted). The outcome is recorded as a one-off in `task-reviews.md` / `CURRENT_STATE.md`. T4 may be approved with the smoke test reported as skipped.
