# Versioning and releases

Phase 1 keeps the workflow lightweight but introduces stable identifiers now.

## Documents
- `document_id` remains stable across edits.
- `document_version` increments when approved content changes.
- Existing versions are not conceptually overwritten.
- `knowledge/releases/seed-v1.json` records the document versions used by the initial release.

## Evaluation cases
- `case_id` remains stable.
- `case_version` increments when an approved case changes.
- `status` supports future governance states such as `review_required`, `potentially_obsolete`, `deprecated`, `replaced`, and `suggested`.
- `evaluation/suites/public-eval-v1.json` defines the active case set.

## Derived artifacts
Chunks, embeddings and the Qdrant index are derived from document versions plus chunking/embedding configuration. They are not the source of truth.

## Phase 2
Mutable source documents move to S3 behind `S3DocumentRepository`; workflow metadata and relationships move to a metadata database. Knowledge Release Candidates will support document diffing, impacted-evaluation detection, LLM suggestions, human approval, preview indexing, audit trails, atomic publication and rollback.
