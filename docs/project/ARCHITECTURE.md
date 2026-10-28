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
| `config.py` | `IngestionConfig` from `config/ingestion.yaml` (index-defining: `index_version`, embedder, pinned revision, chunker cap); `RuntimeSettings` from the environment (`QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_BASE`, `W2A_TENANT_ID` since Spec 005), built by the shared `load_runtime_settings` |
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

## Retrieval (Phase 1 dense baseline, Spec 005; hybrid added by Spec 007)

Library code in `packages/rag/src/way2australia_rag/retrieval/` plus the shared access types in `packages/core`. No HTTP route yet. Developer CLIs run it: `make retrieve` (all strategies), `make index-lexical` and the legacy dense-only `make retrieval-baseline`.

| Module | Role |
|---|---|
| `core/access.py` | `Role`, frozen `AccessContext(role, tenant_id)` (blank tenant refused) |
| `access.py` | `guest_access`, `resolve_access` (the only role-to-policy mapping; guest returns `GUEST_PUBLIC_POLICY`), `ResolvedAccess`, `build_access_filter` (the only filter builder), `check_hit` (fail-closed re-check) |
| `index.py` | `DenseIndex`: read-only binding to the collection and its `-settings` record; `search`, `document_count` |
| `retriever.py` | `DenseRetriever.retrieve(query, access, top_k)` → `RetrievalResult` |
| `models.py`, `errors.py`, `text.py` | `RetrievedChunk`/`RetrievalResult`, error hierarchy, `safe_text` for printing payload text |
| `base.py`, `strategy.py` | `Strategy` (`dense`, `bm25`, `hybrid`), the `Retriever` Protocol, `RetrievalConfig` (from `config/retrieval.yaml`) and `build_retriever`, the only place a strategy name becomes a retriever |
| `bm25.py` | `BM25Retriever` over the lexical index; `build_sql_access_clause` (in `access.py`) is its authorization builder |
| `fusion.py`, `hybrid.py` | pure `rrf_fuse` and `HybridRetriever` (dense leg, then BM25 leg, at candidate depth) |
| `cli.py` | `make retrieve` (`--strategy`) |
| `metrics.py`, `goldens.py`, `baseline.py`, `baseline_cli.py` | document-level metrics, read-only golden/suite/release loading, baseline runner and writer, `make retrieval-baseline` |

The lexical side lives in `packages/rag/src/way2australia_rag/lexical/` (Spec 007): `tokenizer.py` (`lexical-v1`), `store.py` (SQLite FTS5 file: `chunks` table with access columns and the full payload, `chunk_terms` FTS5 table, a settings row with the dense identity copy; read-only `LexicalIndex.open`, `bind_to(dense)`, `search`), `build.py` (`production_entries`, atomic `build_lexical_index`) and `cli.py` (`make index-lexical`, writes only a git-ignored file). The file is a derived artifact, one per collection, bound to the dense index by identity and chunk digest.

Query flow as built (dense strategy; `bm25` and `hybrid` described below):

```text
query text + environment (QDRANT_*, W2A_TENANT_ID) + config/ingestion.yaml
  ↓
load_runtime_settings            (empty tenant refused)
  ↓
build_embedder                   (missing bge-m3 extra exits 2 before any Qdrant call)
  ↓
Qdrant client → DenseIndex.open  (read-only; refuses a mismatched or missing index)
  ↓
resolve_access(guest_access(settings))  → ResolvedAccess(policy, tenant_id)
  ↓
embed_query → build_access_filter(access) → query_points(dense, filter, limit=top_k)
  ↓
check_hit on every returned payload (RetrievalAuthorizationError if it violates the policy)
  ↓
RetrievalResult (hits sorted by score, document/section identity, header facts)
```

- Authorization: the filter is built from the server-resolved `ResolvedAccess` only (allowed `access_scope` values, server tenant, null `owner_user_id`) and is part of the Qdrant query, so unauthorized points never leave the store. The query text, the embedder and evaluation cases cannot change it. `check_hit` is a second line of defense. Future fallbacks must take the same `ResolvedAccess` and call `check_hit` (D035).
- Binding: the query embedder's model ID, revision, vector size, normalization and fake flag, plus `index_version`, must equal the recorded `IndexSettings`; chunker fields are not compared (D036).
- Language fields (`content_language`, `lote_languages`) are returned with hits but there is no language filter, score threshold or reranking yet.
- The baseline runner refuses a fake index without `--allow-fake`, uses one `ResolvedAccess` for every golden case (the case's `access_context` is ignored), computes document-level HitRate@k, Recall@k and MRR (overall, per `query_language`, per `category`), p50/p95 latency after an unmeasured warm-up, and the `min(1, k/N)` random expectation (D037).
- Decisions: D033–D041.

Hybrid retrieval (Spec 007, default strategy `hybrid` since D055):

```text
query → validate_request → ResolvedAccess (one, server-resolved)
  dense leg:  embed_query → Qdrant filter → check_hit          (candidate_depth 50)
  BM25 leg:   lexical-v1 terms → FTS5 MATCH with the SQL access clause
              (WHERE before ORDER BY / LIMIT) → check_hit       (candidate_depth 50)
  → rrf_fuse (k 60, weights 1.0 / 1.0) → cut to top_k → RetrievalResult (score_kind rrf, leg ranks)
```

- Authorization is applied inside each leg's own query and re-checked per hit; fusion sees only authorized hits and fails closed (any leg error propagates; no single-leg fallback). An empty BM25 leg keeps the dense order.
- Every strategy builds the embedder and opens the dense index, and `bm25`/`hybrid` also open and bind the lexical file; `bm25` never embeds the query. BM25 therefore still needs Qdrant and the `bge-m3` extra; independence is the fallback spec's work (roadmap 13).
- BM25 statistics are corpus-wide per file (a roles spec needs per-scope files or an accepted leak).
- Decisions: D049–D055.

## Target RAG query flow

Target pipeline, partly implemented. Dense retrieval, BM25 retrieval and RRF fusion exist (see "Retrieval" above); there is no FastAPI route, reranker, context builder or generation yet.

```text
User
  ↓
FastAPI
  ↓
validation / limits
  ↓
AccessContext(role=guest, server tenant) → resolve_access → ResolvedAccess
  ↓
LanguageContext
  ↓
optional query transform
  ↓
dense retrieval                       sparse/BM25 retrieval
  (authorization filter inside          (same ResolvedAccess filter inside
   the Qdrant query; check_hit)          its query; check_hit)
  ↓                                      ↓
RRF fusion (only already-authorized hits)
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

Authorization is applied inside each retriever (dense, BM25 and the SQLite FTS5 fallback), as part of that retriever's own query, before fusion: every leg takes the same server-resolved `ResolvedAccess`, filters with it in the query and re-checks each hit with `check_hit` (D035, D040). It is never applied after RRF, after reranking or after generation, so unauthorized content never reaches fusion, the reranker, the context builder or the LLM.

## Retrieval fallback

Expected graceful-degradation paths:

- query rewrite failure → original query;
- dense embedding failure → BM25;
- reranker failure/timeout → hybrid/RRF output;
- Qdrant unavailable → SQLite FTS5 fallback;
- Langfuse unavailable → serving continues;
- model failure → evidence-only response where possible;
- weak evidence → insufficient-evidence response.

Fallback paths must preserve authorization: a fallback retriever takes the same `ResolvedAccess`, applies the authorization filter inside its own query and calls `check_hit` on every hit (D035, D040). None of these fallbacks is implemented yet: BM25 exists as a strategy but still needs Qdrant and the `bge-m3` extra, and there is no automatic switch between strategies.

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

## Evaluation (Phase 1 framework, Spec 006)

Library code in `packages/rag/src/way2australia_rag/evaluation/`, one CLI (`evaluation/cli.py`) behind `make validate-evaluation`, `eval-retrieval`, `eval-security` and `eval-compare`. It sits on top of `retrieval/` and imports it unchanged; the only edits there are the `goldens.py` compatibility wrapper and the `document_id` attribute on `RetrievalAuthorizationError`. Nothing in `retrieval/`, `ingestion/` or `repositories/` imports `evaluation/` except that wrapper.

| Module | Role |
|---|---|
| `models.py`, `suite.py` | tolerant typed cases and suite; `load_suite` reads manifest and datasets read-only, ignores `access_context`, refuses unknown dataset types and escaping paths |
| `schemas.py`, `validate.py` | local `referencing` registry for the three schemas; all checks behind `validate-evaluation` (schemas, cross-checks, relevant documents through the repository, candidates) |
| `retrieval_eval.py`, `slices.py`, `sections.py` | run active goldens (and unanswerable cases, top-1 score only) through `DenseRetriever`; slices by query language, category and source authority; section-level metrics |
| `results.py`, `compare.py` | read result files 1.0, 2.0 and 2.1 into a comparable form; the quality gate and the identity refusals (collection, `index_version`, embedder pair, lexical identity) |
| `security_corpus.py`, `security_index.py`, `security_eval.py` | isolated security repository, throwaway dense index and lexical file, authorization gate over `dense`, `bm25` and `hybrid` |

Isolation and gates:
- Access: every query, quality or security, goes through `DenseRetriever` with the one `resolve_access(guest_access(settings))`; evaluation code builds no filter and reads no role, scope or tenant from a case (D033 to D035, D040).
- Quality runs refuse a fake embedder or fake index and read the index read-only (D036). Result files are never overwritten and hold IDs, scores and counts only (D043).
- The security gate runs on a throwaway `w2a-sectest-<8 hex>` collection with the fake embedder, normally in memory; ineligible content is written only there, never into a real index (D045). Failure is exit 1; a broken harness is exit 2, never a pass.
- Evaluation assets are never written by evaluation code (C6); candidates are `suggested`, never loaded as cases, and activated only by a human, versioned change.
- Ingestion eligibility is the only guard against synthetic or unapproved documents. Retrieval does not re-check it because the payload does not carry those fields, so `poisoned_public_document` (public scope, synthetic) is not an authorization case.
- Section-level keys are `"<document_id>#<section_id>"`. No active golden case has `relevant_section_ids` yet, so the section block reports zero measurable cases.
- The security result's `access.role` is hard-coded `guest`, correct in Phase 1; it must become the resolved role when other roles are added.
- Spec 007: `eval-retrieval` takes `--strategy` and writes result 2.1; `eval-security` gates all three strategies on a throwaway lexical file as well (security result 1.1). Decisions: D042 to D047, D053, D054.

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
