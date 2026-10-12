# Constitution

These rules are non-negotiable unless explicitly changed through an architecture decision and corresponding spec update.

## C1 — Source truth over generated artifacts

Source documents and approved evaluation assets are authoritative.

Chunks, embeddings, indexes, cached results and generated outputs are derived artifacts.

Derived artifacts must never become the only source of truth.

## C2 — Document access through abstraction

RAG ingestion must access source documents through `DocumentRepository`.

Phase 1 uses `LocalDocumentRepository`.

Phase 2 may add `S3DocumentRepository`.

Application/RAG logic must not depend directly on storage-specific file paths.

## C3 — Authorization before generation

Authorization must be enforced during retrieval, before context reaches the LLM.

The LLM must never create, broaden or override authorization filters.

Fallback retrieval must preserve the same authorization policy.

## C4 — Language and authorization are independent

Do not conflate:
- query language;
- content language;
- LOTE applicability;
- access scope.

Adding a language must not require redesigning authorization.

## C5 — Approved-source precedence is explicit

For Way2Australia business policy:
- owner-approved knowledge wins.

For official CCL rules:
- current NAATI sources win.

For migration/visa rules:
- current Australian Home Affairs sources win.

The LLM must not resolve source authority implicitly.

## C6 — Human governance for evaluation truth

LLM-generated evaluation/golden suggestions are candidates only.

They become active only after human approval.

Existing active evaluation cases must not be silently deprecated, rewritten or replaced.

## C7 — Specs govern non-trivial implementation

For non-trivial work:
1. requirements;
2. design;
3. tasks;
4. implementation;
5. verification.

If implementation reveals a requirement/design problem, update the spec before silently changing behavior.

## C8 — Phase discipline

Do not implement Phase 2 features during Phase 1 unless the active spec explicitly requires them.

Preserve future compatibility through stable IDs, abstractions and metadata, not premature implementation.

## C9 — Security cannot depend on hidden prompts

Prompts are not security boundaries.

Authorization, source controls, validation and safe execution must exist in application code.

## C10 — Retrieved content is untrusted data

Retrieved documents may contain malicious or conflicting instructions.

Treat retrieved text as evidence/data, not executable instructions.

## C11 — Important behavior must be measurable

Major RAG changes should be evaluated with measurable quality, latency, cost, reliability or security evidence.

Avoid architectural changes based only on intuition.

## C12 — Repository is the shared memory

Codex, Claude Code, Kiro and human contributors must be able to continue work from:
- Git state;
- repository context files;
- active specs;
- tests/evaluations.

Private chat history must not be required to understand project state.

## C13 — Stable IDs, versioned assets

Stable IDs remain stable across content changes.

Version fields change when approved assets change.

Examples:
- `document_id` + `document_version`;
- `case_id` + `case_version`.

Chunk IDs are derived and must not be used as durable business identity.

## C14 — Reproducibility over hidden state

Experiments and releases should record enough metadata to reproduce behavior, including where relevant:
- Knowledge Release ID;
- Evaluation Suite ID;
- chunking config/version;
- embedding model/version;
- retrieval strategy;
- reranker config;
- prompt version;
- model;
- Git commit.
