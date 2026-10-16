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
- recursive baseline
- structure-aware chunking
- FAQ-aware retrieval/indexing
- optional semantic chunking
- token-based size cap using the embedding model's own tokenizer, instead of Spec 004's character cap (2,000 characters means different token counts per language; Malayalam uses more tokens per character than English)
- guard against silent truncation: count tokens before embedding and fail when a chunk exceeds the model's maximum sequence length (`sentence-transformers` truncates silently)
- parent-heading context in chunk text and duplicate-heading `section_id`s that do not depend on order (Spec 004 baseline limitations)

### 8. Multilingual retrieval
- English
- Malayalam
- mixed queries
- language applicability handling

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
