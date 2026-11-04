# Roadmap

## Phase 0 — Project bootstrap

Goal:
Create a shared, multi-agent, spec-driven development environment.

Includes:
- `AGENTS.md`
- Claude adapter
- project context files
- SDD workflow (Spec 003: task-gated agent workflow)
- stable command interface
- initial specs

Status:
In progress.

---

## Phase 1 — Production-oriented RAG

Target duration:
Approximately one focused week.

### 1. Project foundation
- Python workspace
- FastAPI skeleton
- repository boundaries
- local development tooling
- tests
- Qdrant local dependency

### 2. Document model + repository
- `KnowledgeDocument`
- metadata/versioning
- `DocumentRepository`
- `LocalDocumentRepository`
- manifest/schema validation

### 3. Ingestion baseline
- content hashing
- idempotent ingestion
- chunking
- embedding
- Qdrant upsert

### 4. Dense retrieval baseline
- BGE-M3
- dense top-k retrieval
- public access filter
- first measurable retrieval baseline

### 5. Evaluation framework
- versioned Evaluation Suite
- golden cases
- refusal cases
- security cases
- Recall@5
- MRR
- HitRate@5
- language/domain slices

### 6. Hybrid retrieval
- BM25
- RRF
- dense vs sparse vs hybrid comparisons

### 7. Chunking experiments
**Status (Spec 009):** **verified (2026-11-04, merged `5a6deb7` on `main`)**. Delivered: `recursive` v1 and `structure` v1 chunkers beside unchanged `heading` v1; BGE-M3-aligned token counting and a pre-embed truncation guard; `ChunkerIdentity` and settings 1.1 (dense and lexical); per-document lexical freshness; distinct-document `eval-retrieval` metrics and result 2.3; `eval-compare --cross-index`; security result 1.3 over three chunkers; default production index **`idx-v2`** (`recursive` 128 / 16 with title prefix — confounded arm, D071). Operator default: `make ingest` then `make index-lexical` for `idx-v2`.
- Still deferred (same spec carry-overs / later specs): FAQ-aware retrieval/indexing; optional semantic chunking; separating chunk size from title prefix in experiments; headed-document / `relevant_section_ids` evaluation coverage; `g026` en miss after promotion; per-scope lexical files (D050); Malayalam BM25 stemming (**Spec 010 / item 8**); Spec 008 serving items (**roadmap item 10** — grounded generation and first HTTP surface, not a retrieval-only route).

### 8. Multilingual retrieval
**Next spec (user direction 2026-11-04):** **Spec 010** — not started. See `CURRENT_STATE.md` Next step item 11 for the `spec-planner` brief (max 6–7 tasks).
- English
- Malayalam
- mixed queries
- language applicability handling (`lote_languages` at retrieval time)

### 9. Reranking + context building
- multilingual reranker
- deduplication
- context budgeting
- evidence ordering

### 10. Grounded generation + citations
- Bedrock Runtime
- versioned prompts
- answerability
- insufficient-evidence response
- backend-owned citation validation

### 11. Observability
- Langfuse traces
- stage latency
- model/tokens/cost metadata
- release/config IDs

### 12. Security
- authorization regression
- staff canary
- prompt injection tests
- poisoned retrieved content
- citation manipulation tests
- input/cost limits

### 13. Graceful degradation
- dense → BM25
- reranker failure → hybrid results
- Qdrant failure → SQLite FTS5
- model failure → evidence-only response where appropriate

Done early by Spec 008 (D056), ahead of item 7: retrieval degradation. `hybrid` serves BM25 from the local SQLite FTS5 file when Qdrant or the embedding model is unreachable (dense → BM25 and Qdrant failure → SQLite FTS5), and an explicit `bm25` needs neither Qdrant nor the `bge-m3` extra. Still open in this item: the reranker failure path (needs a reranker, item 9) and the model failure path (needs generation, item 10), plus the serving concerns Spec 008 deferred to the HTTP route: a circuit breaker, a startup policy for a missing or stale lexical file, and Qdrant 5xx eligibility (D062).

### 14. AWS deployment
- Docker
- Terraform
- EC2
- ECR
- CloudWatch
- IAM
- Bedrock

### 15. CI/CD + regression gates
- lint/type/test
- retrieval regression
- security regression
- citation validation
- deterministic gates

### 16. Recruiter demo
- user query UI
- RAG Lab
- engineering metrics
- experiment comparisons
- documented architecture/story

---

## Phase 2 — Knowledge Operations

### External document storage
- `S3DocumentRepository`
- immutable/versioned document bodies in S3
- metadata database

### Admin content management
- view active documents
- create/edit/upload document versions
- controlled draft workflow

### Knowledge Release Candidate
- create candidate from active release
- preserve previous active release during editing

### Change impact analysis
- structured document diff
- changed-section detection
- deterministic relationship lookup
- affected evaluation-case identification

### Evaluation Governance
Existing evaluation/golden cases can be:
- kept;
- modified;
- deprecated;
- replaced.

Nothing changes active evaluation truth without admin approval.

### LLM suggestions
LLM may suggest:
- obsolete cases;
- changed expected facts;
- new factual cases;
- edge cases;
- multilingual cases;
- refusal/security cases;
- uncovered knowledge sections.

Admin can:
- accept;
- edit + accept;
- reject;
- manually create another case.

Suggestions remain inactive until approved.

### Preview indexing
- re-chunk changed documents
- embed changed documents
- build/update candidate index

### Candidate evaluation
- run candidate Evaluation Suite
- compare against current active release
- hard-block security/authorization regressions where defined

### Publishing
- human approval
- atomic active-release switch
- rollback support

### Audit
Track:
- document versions;
- hashes/diffs;
- actors/timestamps/reasons;
- evaluation-case decisions;
- LLM suggestions;
- admin modifications;
- approvals;
- release outcomes.

### Basic analytics
Potentially:
- common topics;
- unsupported questions;
- language demand;
- knowledge gaps;
- latency/cost/fallback trends;
- release comparison.

---

## Future

Possible later capabilities:
- authenticated registered users;
- subscriber/private knowledge;
- staff/admin retrieval;
- additional CCL languages;
- user-specific history/progress where appropriate;
- broader analytics;
- agent capabilities only where they solve a real product problem.
