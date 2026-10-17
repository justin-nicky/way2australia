# Architecture

## Repository boundaries

Target repository shape:

```text
apps/
  api/
  web/

packages/
  rag/
  core/
  observability/

knowledge/
sources/
evaluation/
tests/
config/
experiments/
analytics/
prompts/
docs/
infra/
```

Future agent folders are intentionally not created in the current phase.

## Responsibility boundaries

### `apps/api`
FastAPI application layer:
- routes;
- request/response models;
- middleware;
- dependency wiring;
- application startup.

Routes should stay thin.

### `apps/web`
Next.js/TypeScript frontend:
- recruiter-facing assistant;
- RAG Lab;
- engineering views.

### `packages/rag`
Reusable RAG capability:
- document repositories;
- ingestion;
- chunking;
- embeddings;
- retrieval;
- sparse retrieval;
- fusion;
- reranking;
- query transformation;
- context construction;
- grounded generation;
- citation validation;
- reliability/fallbacks.

### `packages/core`
Shared application/domain concepts:
- document models;
- access context;
- language context;
- roles/scopes;
- common errors/config types.

### `packages/observability`
Shared tracing/logging/metrics helpers where useful.

## DocumentRepository

RAG ingestion must depend on an abstraction conceptually like:

```python
class DocumentRepository(Protocol):
    async def get_document(
        self,
        document_id: str,
        version: int | None = None,
    ) -> KnowledgeDocument:
        ...

    async def list_documents(
        self,
        status: str = "active",
    ) -> list[KnowledgeDocument]:
        ...
```

### Phase 1
`LocalDocumentRepository`
→ reads approved local seed knowledge.

### Phase 2
`S3DocumentRepository`
→ reads immutable/versioned source documents outside application code.

The RAG pipeline must not need redesign when storage changes.

## Knowledge model

Documents should retain stable metadata such as:
- `document_id`;
- `document_version`;
- `tenant_id`;
- `knowledge_domain`;
- `access_scope`;
- `language_scope`;
- `lote_languages`;
- `content_language`;
- `source_authority`;
- `approval_status`;
- `last_reviewed_at`;
- lifecycle status;
- release/version metadata.

Important rule:

**Authorization, language applicability, content language and query language are separate dimensions.**

## Source documents vs derived artifacts

Source documents are truth.

Derived artifacts:
- chunks;
- embeddings;
- sparse index entries;
- Qdrant points;
- preview indexes.

Derived artifacts must be reproducible from:
- source document version;
- chunker version/config;
- embedding model/version;
- retrieval/index configuration.

## Ingestion (Phase 1 baseline, Spec 004)

Batch pipeline in `packages/rag/src/way2australia_rag/ingestion/`, run by `make ingest` (`python -m way2australia_rag.ingestion.cli`). No HTTP route.

| Module | Role |
|---|---|
| `config.py` | `IngestionConfig` from `config/ingestion.yaml` (index-defining: `index_version`, embedder, pinned revision, chunker cap); `RuntimeSettings` from the environment (`QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_BASE`) |
| `chunking.py` | `Chunker` Protocol, `HeadingChunker` (`heading` v1, character cap), stable `section_id` slugs |
| `embedding.py`, `bge_m3.py` | `Embedder` Protocol, deterministic `FakeEmbedder`, `BgeM3Embedder` (optional `bge-m3` extra, dense only) |
| `settings.py`, `payload.py`, `identity.py` | `IndexSettings` and mismatch comparison, 17-field `PointPayload`, UUIDv5 `point_id` under `INGESTION_NAMESPACE` |
| `store.py` | `QdrantIndexStore`: collection `<QDRANT_COLLECTION_BASE>-<index_version>` with a named `dense` vector and keyword payload indexes; companion `<collection>-settings` collection holding the recorded settings |
| `service.py` | `IngestionService.run()` → `RunReport` |
| `cli.py` | wiring, summary, exit codes 0/1/2 |

Data flow:

```text
config/ingestion.yaml + environment
  ↓
ensure_collection (create, or refuse if recorded settings differ)
  ↓
list_eligible_documents(DocumentRepository, GUEST_PUBLIC_POLICY)   ← target state
  ↓
read_state() from Qdrant payloads                                 ← current state
  ↓
delete indexed document_ids not in the target
  ↓
per document: chunk → expected point IDs → added / updated / unchanged
  ↓
changed documents: embed first, then delete the document's points and upsert
  ↓
run summary
```

- Authorization is applied when choosing what to index: only documents that pass `GUEST_PUBLIC_POLICY` are chunked or embedded. The payload also carries `access_scope`, `tenant_id` and `owner_user_id` for retrieval-time filtering, separate from the language fields.
- Qdrant records what was indexed; there is no other state store. The index holds one version per `document_id`.
- Changing an index-defining setting means a new `index_version`, which gives a new collection; the store never deletes a collection.
- Decisions: D025–D030, D032.

## Current RAG query flow

```text
User
  ↓
FastAPI
  ↓
validation / limits
  ↓
AccessContext(role=guest)
  ↓
LanguageContext
  ↓
optional query transform
  ↓
dense retrieval + sparse/BM25
  ↓
RRF fusion
  ↓
mandatory authorization filter
  ↓
reranker
  ↓
context builder
  ↓
answerability / insufficient-evidence decision
  ↓
versioned prompt
  ↓
Amazon Bedrock
  ↓
citation validation
  ↓
response
```

Authorization must be enforced before retrieved content reaches generation.

## Retrieval fallback

Expected graceful-degradation paths:

- query rewrite failure → original query;
- dense embedding failure → BM25;
- reranker failure/timeout → hybrid/RRF output;
- Qdrant unavailable → SQLite FTS5 fallback;
- Langfuse unavailable → serving continues;
- model failure → evidence-only response where possible;
- weak evidence → insufficient-evidence response.

Fallback paths must preserve authorization.

## Primary stack

- Python
- FastAPI
- Pydantic
- Qdrant
- SQLite FTS5 fallback
- BGE-M3 embeddings initially
- BM25 + RRF hybrid retrieval
- multilingual reranker
- Amazon Bedrock generation
- Langfuse AI observability
- CloudWatch operations
- DeepEval + custom metrics
- pytest
- Docker / Docker Compose
- GitHub Actions
- Terraform
- AWS Mumbai (`ap-south-1`)

## Evaluation architecture

Evaluation Suite contains:
- factual/golden cases;
- retrieval cases;
- multilingual cases;
- unanswerable/refusal cases;
- security cases;
- regression/edge cases.

Evaluation cases should have stable IDs and versions.
Do not couple evaluations to chunk IDs.

## Knowledge Release

A Knowledge Release conceptually references:

```text
Knowledge Release
├── Document Snapshot
├── Evaluation Suite
├── RAG Config
└── Index Version
```

Phase 1 uses lightweight release identifiers for reproducibility.

## Phase 2 Knowledge Release workflow

```text
Active Release
   ↓
Admin starts change
   ↓
Knowledge Release Candidate
   ↓
new immutable document versions
   ↓
document diff
   ↓
deterministic impact analysis
   ↓
affected evaluation cases flagged
   ↓
LLM gap analysis / suggested cases
   ↓
admin review
   ├── keep
   ├── modify
   ├── deprecate
   ├── replace
   ├── accept suggestion
   ├── edit + accept
   ├── reject
   └── manually create case
   ↓
candidate Evaluation Suite
   ↓
rechunk changed documents
   ↓
candidate/preview index
   ↓
full evaluation
   ↓
admin approval
   ↓
atomic publish
   ↓
new Active Release
```

Nothing automatically changes active evaluations or production releases without human approval.

## Phase 2 storage

Target separation:

```text
S3
→ immutable/versioned source document bodies

Metadata database
→ document/version relationships
→ release state
→ evaluation suite state
→ review/approval/audit records

Qdrant
→ derived chunks/embeddings/index
```

Qdrant is not the document source of truth.

## Phase 2 audit

Document change records should eventually retain:
- document ID/version;
- previous version;
- hashes;
- changed sections;
- actor/time/reason;
- approval information.

Evaluation decisions should eventually retain:
- case ID/version;
- old/new status;
- action;
- reason;
- suggestion source;
- decision actor/time;
- original LLM suggestion;
- admin-edited version;
- final approved version.
