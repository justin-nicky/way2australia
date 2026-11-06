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

## Ingestion (Phase 1 baseline, Spec 004; chunking experiments Spec 009)

Batch pipeline in `packages/rag/src/way2australia_rag/ingestion/`, run by `make ingest` (`python -m way2australia_rag.ingestion.cli`). No HTTP route. Default production config (after Spec 009 T6): schema 1.1, `index_version` `idx-v2`, `recursive` v1 (128 tokens, 16 overlap, title prefix). Legacy heading index: `--config experiments/configs/chunking/heading-idx-v1.yaml`.

| Module | Role |
|---|---|
| `config.py`, `chunker_build.py` | `IngestionConfig` schema 1.0 (`heading` only) and 1.1 (discriminated `heading` / `structure` / `recursive` chunker union); `chunker_identity(config)` without loading a tokenizer; `build_chunker` after `build_tokenizer` |
| `tokenization.py`, `guard.py` | `ChunkTokenizer` (`BgeM3Tokenizer`, `FakeTokenizer`), `build_tokenizer`; `check_chunks` truncation guard (D065) |
| `chunking.py`, `structure.py`, `recursive.py` | `Chunker` Protocol with `ChunkerIdentity`; `HeadingChunker` (`heading` v1, unchanged output), `StructureChunker`, `RecursiveChunker` |
| `embedding.py`, `bge_m3.py` | `Embedder` Protocol, deterministic `FakeEmbedder`, `BgeM3Embedder` (optional `bge-m3` extra, dense only) |
| `settings.py`, `payload.py`, `identity.py` | `IndexSettings` 1.1 (chunker fields; 1.0 upgraded in memory), mismatch comparison, 17-field `PointPayload`, UUIDv5 `point_id` under `INGESTION_NAMESPACE` |
| `store.py` | `QdrantIndexStore`: collection `<QDRANT_COLLECTION_BASE>-<index_version>` with a named `dense` vector and keyword payload indexes; companion `<collection>-settings` collection holding the recorded settings |
| `service.py` | `IngestionService.run()` → `RunReport`; per-document try covers chunk, guard, embed (wrong vector count refused) |
| `cli.py` | wiring, `--config`, summary, exit codes 0/1/2 |

Data flow:

```text
config/ingestion.yaml (or --config) + environment
  ↓
build_embedder, build_tokenizer, build_chunker
  ↓
ensure_collection (create, or refuse if recorded settings differ)
  ↓
list_eligible_documents(DocumentRepository, GUEST_PUBLIC_POLICY)   ← target state
  ↓
read_state() from Qdrant payloads                                 ← current state
  ↓
delete indexed document_ids not in the target
  ↓
per document (try): chunk → guard → expected point IDs → classify
  ↓
changed documents: embed (batch) → replace_document
  ↓
run summary
```

- Authorization is applied when choosing what to index: only documents that pass `GUEST_PUBLIC_POLICY` are chunked or embedded. The payload also carries `access_scope`, `tenant_id` and `owner_user_id` for retrieval-time filtering, separate from the language fields.
- Qdrant records what was indexed; there is no other state store. The index holds one version per `document_id`.
- Changing an index-defining setting means a new `index_version`, which gives a new collection; the store never deletes a collection.
- Decisions: D025–D030, D032, D064–D071.

## Retrieval (Phase 1 dense baseline, Spec 005; hybrid added by Spec 007; fallback by Spec 008; reranking by Spec 011)

Library code in `packages/rag/src/way2australia_rag/retrieval/` plus `languages.py` at the package root and the shared access types in `packages/core`. No HTTP route yet. Developer CLIs run it: `make retrieve` (all strategies), `make index-lexical` and the legacy dense-only `make retrieval-baseline`.

| Module | Role |
|---|---|
| `core/access.py` | `Role`, frozen `AccessContext(role, tenant_id)` (blank tenant refused) |
| `access.py` | `guest_access`, `resolve_access` (the only role-to-policy mapping; guest returns `GUEST_PUBLIC_POLICY`), `ResolvedAccess`, `build_access_filter` (the only authorization filter builder), `check_hit` (fail-closed re-check) |
| `languages.py` (package root, not under `retrieval/`), `applicability.py` | `active_lote_codes`; `ResolvedLote`, `resolve_lote`, Qdrant/SQL applicability builders, `check_applicable` (`LanguageApplicabilityError`; orthogonal to access, D072) |
| `index.py` | `DenseIndex`: read-only binding to the collection and its `-settings` record; `search`, `document_count` |
| `retriever.py` | `DenseRetriever.retrieve(query, access, top_k, *, lote=None)` → `RetrievalResult` |
| `models.py`, `errors.py`, `text.py` | `RetrievedChunk`/`RetrievalResult`, error hierarchy, `safe_text` for printing payload text |
| `base.py`, `strategy.py` | `Strategy` (`dense`, `bm25`, `hybrid`), the `Retriever` Protocol (optional `lote` keyword), `RetrievalConfig` 1.3 (from `config/retrieval.yaml`, with `QdrantTimeouts`, `lexical.tokenizer` and `RerankConfig`, Spec 011) and `build_retriever`, the only place a strategy name becomes a retriever (`hybrid` is returned wrapped in `FallbackRetriever`; with a reranker, `FallbackRetriever(RerankingRetriever(HybridRetriever))`) |
| `bm25.py` | `BM25Retriever(identity, lexical)` over the lexical index; `build_sql_access_clause` (in `access.py`) is its authorization builder |
| `fusion.py`, `hybrid.py` | pure `rrf_fuse` and `HybridRetriever` (dense leg, then BM25 leg, at candidate depth); still fail closed |
| `errors.py`, `availability.py` | `RetrievalUnavailableError(reason)` and `FallbackReason`; `classify_qdrant_error` and `classify_model_error`, the one mapping per source (D057) |
| `qdrant_client.py` | `retrieval_client_factory`: the retrieval Qdrant client with the configured timeouts (D059) |
| `identity.py` | `IndexIdentity` (collection, `index_version`, embedder pair, fake flag, `source` `qdrant` or `lexical_file`) |
| `fallback.py` | `FallbackRetriever`: BM25 serves when the hybrid primary raises `RetrievalUnavailableError`, or when opening it did (D058) |
| `opening.py` | `open_retrieval(...) -> OpenedRetrieval` (the one wiring function for both CLIs: retriever, identity, `document_count`, `close`; with `rerank=True` it builds and loads the reranker once, D077; its `rerank` parameter defaults to off, so callers resolve the effective setting from `rerank.enabled`) and `open_standalone_lexical` (D060) |
| `reranking.py` | `RerankingRetriever` (Spec 011): top `rerank.depth` fused chunks, cross-encoder ordering, membership re-check, open/query skips (D076, D077) |
| `cli.py` | `make retrieve` (`--strategy`, `--rerank` / `--no-rerank` / `--reranker`) |
| `metrics.py`, `goldens.py`, `baseline.py`, `baseline_cli.py` | document-level metrics, read-only golden/suite/release loading, baseline runner and writer, `make retrieval-baseline` |

The lexical side lives in `packages/rag/src/way2australia_rag/lexical/` (Spec 007; settings 1.2 and freshness Spec 009): `tokenizer.py` (`TOKENIZERS`: `lexical-v1` unchanged output; `lexical-v2` adds Unicode-cited chillu sequence replacement before v1 steps; module-level `tokenize`/`query_terms` stay v1 aliases), `equivalents.py` (sequence table), `store.py` (SQLite FTS5 file: `chunks` with access columns, `lote_languages`, full payload, `chunk_terms` FTS5, settings 1.2 with `ChunkerIdentity`; 1.1 accepted without `--lote`; 1.0 refused), `build.py` (`production_entries`, atomic `build_lexical_index(..., tokenizer)`), `cli.py` (`make index-lexical`, `--tokenizer`, `--config`), and `freshness.py` (`verify_fresh` per D067). BM25 always queries with the tokenizer recorded in the file. Default tokenizer in `config/retrieval.yaml` is `lexical-v2` (D072). The file is a derived artifact, one per collection (or a second directory via `W2A_LEXICAL_INDEX_DIR`), bound to dense or to configuration plus the repository.

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
optional resolve_lote(CLI flag)         → ResolvedLote | None
  ↓
embed_query → Filter(must=[access, optional lote]) → query_points(dense, filter, limit=top_k)
  ↓
check_hit, then check_applicable when lote is set (authorization before applicability)
  ↓
RetrievalResult (hits sorted by score, document/section identity, header facts)
```

- Authorization: the filter is built from the server-resolved `ResolvedAccess` only (allowed `access_scope` values, server tenant, null `owner_user_id`) and is part of the Qdrant query, so unauthorized points never leave the store. The query text, the embedder and evaluation cases cannot change it. `check_hit` is a second line of defense. Future fallbacks must take the same `ResolvedAccess` and call `check_hit` (D035).
- Binding: the query embedder's model ID, revision, vector size, normalization and fake flag, plus `index_version`, must equal the recorded `IndexSettings`; chunker fields are not compared (D036).
- **Four language concepts (C4):** query language (evaluation slices only today), document `content_language`, CCL applicability (`lote_languages` / optional request `lote`), and authorization (`access_scope`, tenant, owner). Applicability filters run inside each leg when `lote` is set; omitted `lote` leaves behaviour unchanged. No query-language detection drives retrieval; script mix in results is reporting only.
- The baseline runner refuses a fake index without `--allow-fake`, uses one `ResolvedAccess` for every golden case (the case's `access_context` is ignored), computes document-level HitRate@k, Recall@k and MRR (overall, per `query_language`, per `category`), p50/p95 latency after an unmeasured warm-up, and the `min(1, k/N)` random expectation (D037).
- Decisions: D033–D041, D072 (applicability and tokenizers).

Hybrid retrieval (Spec 007, default strategy `hybrid` since D055):

```text
query → validate_request → ResolvedAccess (one, server-resolved); optional ResolvedLote
  dense leg:  embed_query → Qdrant filter (access + optional lote) → check_hit → check_applicable
  BM25 leg:   file tokenizer terms → FTS5 MATCH with SQL access AND lote clauses
              (WHERE before ORDER BY / LIMIT) → check_hit → check_applicable   (candidate_depth 50)
  → rrf_fuse (k 60, weights 1.0 / 1.0) → cut to top_k → RetrievalResult (score_kind rrf, leg ranks)
```

- Authorization is applied inside each leg's own query and re-checked per hit; fusion sees only authorized hits and fails closed (any leg error propagates; no single-leg fallback). An empty BM25 leg keeps the dense order.
- `dense` and `hybrid` build the embedder and open the dense index; `hybrid` also opens and binds the lexical file. `bm25` builds no embedder and no Qdrant client (Spec 008): it needs neither Qdrant nor the `bge-m3` extra, only the lexical file. See "Retrieval fallback" below.
- BM25 statistics (IDF, average document length) are computed over every row of a lexical file, including rows the access clause excludes. Today the production file holds only eligible public chunks (`production_entries` uses `GUEST_PUBLIC_POLICY`), so the statistics reveal nothing; only the security gate's temporary file holds forbidden rows. A future roles spec needs one lexical file per access scope, so that one scope's statistics never reflect another scope's text (D050).
- Decisions: D049–D055 (D056–D062 for the fallback below).

## Target RAG query flow

Target pipeline, partly implemented. Dense retrieval, BM25 retrieval, RRF fusion and the reranking stage exist (see "Retrieval" above and "Reranking" below); there is no FastAPI route, context builder or generation yet.

```text
User
  ↓
FastAPI
  ↓
validation / limits
  ↓
AccessContext(role=guest, server tenant) → resolve_access → ResolvedAccess
  ↓
optional CCL lote (registry-validated; separate from access)
  ↓
optional query transform
  ↓
dense retrieval                       sparse/BM25 retrieval
  (access + applicability filters       (same ResolvedAccess and optional lote
   inside the Qdrant query;              inside SQL; check_hit; check_applicable)
   check_hit; check_applicable)
  ↓                                      ↓
RRF fusion (only already-authorized hits)
  ↓
reranker (Spec 011, hybrid only: cross-encoder over the top rerank.depth fused chunks;
  membership re-check; on reranker outage the plain hybrid hits are served)
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

Authorization and optional language applicability are applied inside each retriever (dense, BM25 and the SQLite FTS5 fallback), as part of that retriever's own query, before fusion: every leg takes the same server-resolved `ResolvedAccess` and the same optional `ResolvedLote`, filters with them in the query, then re-checks each hit with `check_hit` and, when `lote` is set, `check_applicable` (D035, D040, D072). Neither filter is applied after RRF, after reranking or after generation.

## Reranking

Spec 011 (D075–D079). Reranking exists on `hybrid` only, inside the fallback:

```text
FallbackRetriever( RerankingRetriever( HybridRetriever(dense, bm25) ), bm25 )

query → access (+ optional lote) filters inside each leg → RRF fusion (top rerank.depth)
      → Reranker.score(query, chunk texts)       # BAAI/bge-reranker-v2-m3, pinned, raw logits
      → order by cross-encoder score (ties: fused rank) → cut to top_k
      → membership re-check: each hit equals exactly one leg-checked candidate, no duplicates;
        check_applicable when a lote is set
```

- Modules: `packages/rag/src/way2australia_rag/rerank/` (no exports in `__init__.py`): `base.py` (`Reranker` Protocol, `RerankerInfo`, `RerankScores`), `fake.py` (`FakeReranker`), `bge.py` (`BgeRerankerV2M3`, lazy `sentence-transformers` import), `errors.py` (`RerankSkipReason`, `RerankerUnavailableError`, `RerankerOutputError`, `classify_reranker_error`; reuses the private cause-chain helper of `retrieval/availability.py`), `build.py` (`build_reranker`); the stage itself is `retrieval/reranking.py`. The `rerank/` package knows nothing about access, `lote`, chunks or documents.
- Authorization and applicability stay inside the legs. The stage only reorders candidates it was given; it never fetches text or IDs, and the re-check runs on the reranked path and both skip paths.
- `RerankerUnavailableError` is separate from `RetrievalUnavailableError` and is caught only by the stage, so a reranker outage can never become a BM25 fallback. An eligible load failure at open is a sticky open-time skip for the run (`stage: open`); an eligible `score` failure skips that query (`stage: query`). Offline-and-not-cached weights are a configuration error (exit 2), not a skip. Malformed scores fail the query closed. There is no inference timeout (D077): the binding latency limit, circuit breaker, model lifecycle and device choice belong to roadmap item 10.
- A dense outage still reaches `FallbackRetriever`: BM25 serves without reranking.
- Default since Spec 011 T5: `rerank.enabled: true`, depth 20; `dense` and `bm25` need `--no-rerank`. Measured on the dev machine (`mps:0`): p95 about 1 s per query (D079).
- Context building (deduplication, budgeting, evidence ordering) is not implemented; it moved to roadmap item 10.

## Retrieval fallback

Spec 008 (D056–D062) implements the retrieval part of graceful degradation. Other paths below are planned.

Implemented, for `hybrid` only (the default or `--strategy hybrid`):

```text
open_retrieval(hybrid)
  embedder (missing bge-m3 extra → exit 2, never a fallback)
  → Qdrant client (retrieval_client_factory, timeouts 2 s / 3 s) → DenseIndex.open → LexicalIndex.bind_to
      ok                      → FallbackRetriever(HybridRetriever, BM25Retriever(identity from dense), no open reason)
      RetrievalUnavailableError → open_standalone_lexical (check_identity + verify_fresh, no Qdrant, no embedder)
                                  → FallbackRetriever(no primary, BM25Retriever(expected identity), reason)
  per query: primary.retrieve(..., lote) → on RetrievalUnavailableError only → BM25Retriever.retrieve(same query, same access, same top_k, same lote)
  → RetrievalResult(strategy = served, requested_strategy = hybrid, fallback_reason, leg_latency_ms.dense_attempt)
```

- Eligible failures (`RetrievalUnavailableError`, D057): Qdrant connect or network error (`qdrant_unavailable`), Qdrant timeout (`qdrant_timeout`), and an embedding model load or download failure whose explicit `__cause__` chain holds a network or timeout error (`model_unavailable`). Nothing else falls back: HTTP status errors including 5xx (D062), a missing collection, a settings mismatch, a missing or stale lexical file, a missing `bge-m3` extra, a model load failure without a network cause, authorization errors and SQLite errors all exit 2. `fusion.py` and `hybrid.py` are unchanged; the wrapper sits outside fusion.
- Explicit `dense` and `bm25` never fall back. `dense` with Qdrant down exits 2 with `RetrievalUnavailableError`. `bm25` is standalone.
- Policy (D058): per query, no state, no circuit breaker; worst case about `query_timeout_s` per query when Qdrant hangs, retried on every query. That retry applies only after a successful open: when the open itself fails, the opened retriever has no primary, and every query of that run is served by BM25 with the open-time reason (no per-query dense attempt, so `leg_latency_ms.dense_attempt` is about 0 ms) until the stack is opened again. The CLIs open once per run. A circuit breaker, a startup and reopen policy (including a missing or stale lexical file) and an async freshness check belong with the HTTP route spec.
- Freshness (D060): the standalone path proves the lexical file matches the repository and configuration, not the live Qdrant collection. It rereads every eligible document at each open; revisit for a large corpus.
- Marking and evaluation (D061): `make retrieve` prints `strategy: bm25 (requested: hybrid; fallback: <reason>)` and a stderr warning only on fallback; `make eval-retrieval` writes result 2.2 (served strategies, fallback counts, latency by served path), and `make eval-compare` compares by the served strategy and refuses a file that mixes strategies. `make eval-security` gates five paths, two of them fallback paths (security result 1.2).

Authorization: the fallback adds no authorization logic. `FallbackRetriever` passes the caller's `ResolvedAccess` object unchanged to `BM25Retriever`, which applies the SQL access clause inside its query and calls `check_hit` on every hit (D035, D040). The lexical file holds only eligible guest/public chunks (D050). `RetrievalAuthorizationError` is never caught by the wrapper, so an authorization failure cannot become a fallback.

Planned, not implemented:

- query rewrite failure → original query;
- reranker failure/timeout → hybrid/RRF output: implemented by Spec 011 (see "Reranking"); a binding per-request timeout is roadmap item 10 (D077);
- Langfuse unavailable → serving continues;
- model (generation) failure → evidence-only response where possible (roadmap 13; no generation yet);
- weak evidence → insufficient-evidence response.

Any later fallback must preserve authorization the same way: take the same `ResolvedAccess`, apply the authorization filter inside its own query and call `check_hit` on every hit.

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
| `retrieval_eval.py`, `slices.py`, `sections.py` | run active goldens (and unanswerable cases, top-1 score only) through the chosen retriever; retrieve to candidate depth, dedupe by document for MRR@k (Spec 009); slices by query language, category and source authority; section-level metrics |
| `results.py`, `compare.py`, `continuity.py`, `script_mix.py` | read results 1.0–2.5; quality gate; `--cross-index` (D069), `--cross-tokenizer` (D072) and `--cross-rerank` (D078); per-case continuity without refusing suite/lote/case-set (rerank identity refused, D078) |
| `security_corpus.py`, `security_index.py`, `security_eval.py` | throwaway corpus with forbidden and non-applicable rows; gate over eight paths (Spec 011 adds three rerank paths with a fake reranker), three chunkers, two `lote` modes (security 1.5, D078) |

Isolation and gates:
- Access: every query, quality or security, goes through `DenseRetriever` with the one `resolve_access(guest_access(settings))`; evaluation code builds no filter and reads no role, scope or tenant from a case (D033 to D035, D040).
- Quality runs refuse a fake embedder or fake index and read the index read-only (D036). Result files are never overwritten and hold IDs, scores and counts only (D043).
- The security gate runs on a throwaway `w2a-sectest-<8 hex>` collection with the fake embedder, normally in memory; ineligible content is written only there, never into a real index (D045). Failure is exit 1; a broken harness is exit 2, never a pass.
- Evaluation assets are never written by evaluation code (C6); candidates are `suggested`, never loaded as cases, and activated only by a human, versioned change.
- Ingestion eligibility is the only guard against synthetic or unapproved documents. Retrieval does not re-check it because the payload does not carry those fields, so `poisoned_public_document` (public scope, synthetic) is not an authorization case.
- Section-level keys are `"<document_id>#<section_id>"`. No active golden case has `relevant_section_ids` yet, so the section block reports zero measurable cases.
- The security result's `access.role` is hard-coded `guest`, correct in Phase 1; it must become the resolved role when other roles are added.
- Spec 007: `--strategy`, result 2.1; security 1.1. Spec 008: result 2.2; security 1.2. Spec 009: result 2.3; `--cross-index`; security 1.3. Spec 010: default suite `public-eval-v3`; `--lote`; result 2.4 with `by_script_mix`; `--cross-tokenizer`; `make eval-continuity`; security 1.4 with applicability. Spec 011: result 2.5 (rerank identity, served paths, skip and truncation counts); `--rerank` / `--no-rerank`; `--cross-rerank`; security 1.5 with eight paths. Decisions: D042–D047, D053–D054, D061–D072, D068–D070, D078.

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
