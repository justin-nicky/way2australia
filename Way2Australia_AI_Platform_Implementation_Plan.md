# Way2Australia AI Platform — Master Implementation Plan

**Plan date:** 13 October 2026  
**Current delivery focus:** Phase 1 — Production-oriented multilingual RAG  
**Next major phase:** Phase 2 — Knowledge Operations  
**Future direction:** Broader AI learning capabilities including multimodal dialogue/mock-test evaluation

---

## 1. Project Mission

Build a production-oriented AI platform for Way2Australia's NAATI CCL preparation product.

The first major capability is a multilingual Retrieval-Augmented Generation (RAG) assistant that answers questions from approved Way2Australia, NAATI, and Home Affairs knowledge with citations, measurable retrieval quality, observability, security controls, and graceful degradation.

The project is also intended to demonstrate practical AI engineering through:

- retrieval and chunking experiments;
- multilingual search;
- reranking;
- grounded generation;
- RAG evaluation;
- tracing and observability;
- security and prompt-injection resistance;
- reliability/fallback design;
- CI regression testing;
- cloud deployment and infrastructure-as-code;
- version-aware knowledge and evaluation governance.

The platform should remain extensible for future capabilities such as:

- multimodal mock-test evaluation;
- dialogue/audio assessment;
- interpretation feedback;
- learning analytics;
- additional CCL languages;
- authenticated/private learning experiences.

RAG is therefore treated as **one reusable AI capability inside the platform**, not the identity of the entire repository.

---

# 2. Phase 1 Scope

Phase 1 is intentionally focused and should remain achievable in approximately one concentrated week.

## 2.1 Implement now

- Public/guest users only.
- English and Malayalam query support.
- Architecture ready for more CCL languages.
- Approved Way2Australia public business knowledge.
- Approved public samples.
- Current NAATI official knowledge.
- Home Affairs information where relevant.
- Source-authority-aware retrieval.
- Dense retrieval baseline.
- BM25 lexical retrieval.
- Hybrid retrieval using Reciprocal Rank Fusion (RRF).
- Structure-aware / FAQ-aware retrieval experiments.
- Multilingual reranking.
- Grounded Bedrock generation.
- Backend-owned citation validation.
- Evaluation datasets and regression metrics.
- Langfuse tracing.
- Security regression testing.
- Graceful degradation.
- GitHub Actions CI/CD.
- AWS deployment.
- Terraform infrastructure.
- `DocumentRepository` abstraction from the beginning.
- Stable document/evaluation/release identifiers.

## 2.2 Prepare for, but do not implement yet

- S3-backed production knowledge repository.
- Admin document-management UI.
- Full document-edit workflow.
- Knowledge Release Candidate workflow.
- Evaluation governance UI.
- LLM-assisted evaluation-case suggestions.
- Metadata database.
- Atomic knowledge release publishing.
- Knowledge rollback UI/workflow.
- Product analytics dashboard.
- Staff/subscriber/private-user retrieval.
- Agent orchestration.
- Multimodal mock-test evaluation.

---

# 3. Core Engineering Principles

## 3.1 Documents are source-of-truth assets

The authoritative layer is:

```text
source documents
+ approved metadata
+ approved evaluation contracts
```

The following are derived artifacts:

```text
chunks
embeddings
Qdrant points
BM25/FTS entries
indexes
cached outputs
```

Derived artifacts must be reproducible from source versions and configuration.

---

## 3.2 RAG must not depend directly on filesystem storage

All source document access goes through:

```text
DocumentRepository
```

Phase 1:

```text
DocumentRepository
        ↓
LocalDocumentRepository
        ↓
knowledge/
```

Phase 2:

```text
DocumentRepository
        ↓
S3DocumentRepository
        ↓
Amazon S3 + metadata database
```

Changing document storage must not require rewriting chunking, embedding, retrieval, or generation logic.

---

## 3.3 Authorization is enforced before generation

Authorization is a retrieval constraint, not a prompt instruction.

The server creates the access filter.

The LLM must never:

- create access filters;
- broaden access filters;
- retrieve everything and filter afterward;
- decide whether private content is permitted.

All fallback retrieval paths must enforce the same access policy.

---

## 3.4 Language and authorization are separate

Keep these concepts independent:

- `query_language`
- `content_language`
- `language_scope`
- `lote_languages`
- `access_scope`

For example:

```yaml
content_language: "en"
language_scope: "global"
lote_languages: ["*"]
access_scope: "public"
```

versus:

```yaml
content_language: "en"
language_scope: "language_specific"
lote_languages: ["ml"]
access_scope: "public"
```

Adding Hindi, Tamil, Arabic, or another CCL language should not require changing authorization architecture.

---

## 3.5 Source authority is explicit

Way2Australia business policy:

```text
owner-approved knowledge
    >
current public website
    >
older snapshot/reference content
```

Official CCL rules:

```text
current NAATI source
```

Migration / visa / points:

```text
Australian Department of Home Affairs
```

The LLM should not be responsible for deciding source authority.

---

## 3.6 Human governance remains authoritative

LLM-generated suggestions may help administrators discover:

- stale evaluations;
- changed expected facts;
- missing coverage;
- new edge cases;
- multilingual cases;
- refusal cases;
- security cases.

But suggestions are candidates only.

They do not become approved evaluation truth without human action.

---

# 4. Final Repository Structure

```text
way2australia-ai/
│
├── AGENTS.md
├── CLAUDE.md
├── Makefile
├── pyproject.toml
├── uv.lock
├── docker-compose.yml
│
├── .kiro/
│   └── specs/
│       ├── 001-project-foundation/
│       │   ├── requirements.md
│       │   ├── design.md
│       │   └── tasks.md
│       │
│       ├── 002-document-model-and-repository/
│       │   ├── requirements.md
│       │   ├── design.md
│       │   └── tasks.md
│       │
│       └── ...
│
├── apps/
│   ├── api/
│   │   └── src/
│   │       └── way2australia_api/
│   │           ├── main.py
│   │           ├── config.py
│   │           └── api/
│   │
│   └── web/
│
├── packages/
│   ├── core/
│   │   └── src/way2australia_core/
│   │       ├── documents/
│   │       ├── auth/
│   │       ├── languages/
│   │       ├── config/
│   │       └── exceptions/
│   │
│   ├── rag/
│   │   └── src/way2australia_rag/
│   │       ├── repositories/
│   │       ├── ingestion/
│   │       ├── chunking/
│   │       ├── embeddings/
│   │       ├── retrieval/
│   │       ├── reranking/
│   │       ├── query_transform/
│   │       ├── context/
│   │       ├── generation/
│   │       ├── citations/
│   │       └── reliability/
│   │
│   └── observability/
│       └── src/way2australia_observability/
│
├── knowledge/
│   ├── public/
│   │   ├── business/
│   │   ├── official/
│   │   └── languages/
│   │       └── ml/
│   │
│   ├── structured/
│   │   └── owner_approved_faq_pairs.jsonl
│   │
│   ├── manifest/
│   │   ├── document_manifest.jsonl
│   │   └── document_inventory.csv
│   │
│   ├── schemas/
│   │   └── document_metadata.schema.json
│   │
│   └── releases/
│       └── seed-v1.json
│
├── sources/
│   └── raw/
│
├── evaluation/
│   ├── datasets/
│   │   ├── golden_public.jsonl
│   │   ├── unanswerable_public.jsonl
│   │   └── security_public.jsonl
│   │
│   ├── suites/
│   │   └── public-eval-v1.json
│   │
│   ├── schemas/
│   │   └── evaluation_case.schema.json
│   │
│   ├── retrieval/
│   ├── generation/
│   ├── security/
│   └── metrics/
│
├── tests/
│   └── fixtures/
│       └── security/
│           ├── staff_only_canary.md
│           └── poisoned_public_document.md
│
├── experiments/
│   ├── configs/
│   │   └── day1_baseline.yaml
│   └── results/
│
├── config/
│   ├── access_policy.yaml
│   ├── language_registry.json
│   └── source_precedence.yaml
│
├── analytics/
│   └── schemas/
│       └── rag_query_event.schema.json
│
├── prompts/
│
├── docs/
│   ├── project/
│   │   ├── MISSION.md
│   │   ├── CONSTITUTION.md
│   │   ├── TECH_STACK.md
│   │   ├── ROADMAP.md
│   │   ├── PRODUCT.md
│   │   ├── ARCHITECTURE.md
│   │   ├── WORKFLOW.md
│   │   ├── CONVENTIONS.md
│   │   ├── DECISIONS.md
│   │   ├── CURRENT_STATE.md
│   │   └── COMMANDS.md
│   │
│   └── knowledge/
│       ├── SCHEMA_AND_METADATA.md
│       ├── SOURCE_OF_TRUTH.md
│       ├── CONTENT_BOUNDARIES.md
│       ├── ADDING_A_NEW_LANGUAGE.md
│       ├── DAY1_USE.md
│       └── VERSIONING_AND_RELEASES.md
│
└── infra/
    └── terraform/
```

---

# 5. Responsibility Boundaries

## `apps/api`

Owns:

- HTTP routes;
- middleware;
- dependency wiring;
- request/response serialization;
- health endpoints;
- application startup.

The `/ask` route should remain thin.

It should not know:

- how files are loaded;
- how Qdrant works internally;
- how chunks are generated;
- how RRF works;
- how Bedrock is called.

---

## `apps/web`

Owns:

- public chat UI;
- recruiter/demo experience;
- RAG Lab;
- engineering metrics view.

Future:

- admin knowledge-management UI;
- mock-test evaluation UI;
- learning analytics UI.

---

## `packages/core`

Owns reusable domain contracts such as:

- `KnowledgeDocument`
- `AccessContext`
- `LanguageContext`
- roles/scopes
- document/version identifiers
- shared errors/config types

These are not inherently RAG-specific.

---

## `packages/rag`

Owns reusable RAG implementation:

- document repository adapters;
- ingestion;
- chunking;
- embedding;
- retrieval;
- BM25;
- fusion;
- reranking;
- context construction;
- answerability;
- generation;
- citations;
- fallback behavior.

---

## `packages/observability`

Owns shared:

- Langfuse wrappers;
- structured logging;
- metrics helpers;
- trace metadata helpers.

---

# 6. Knowledge and Seed Architecture

## 6.1 Normal production corpus

Only these should normally enter the public production RAG corpus:

```text
knowledge/public/business/
knowledge/public/official/
knowledge/public/languages/ml/
```

---

## 6.2 Structured FAQ asset

```text
knowledge/structured/owner_approved_faq_pairs.jsonl
```

contains the approved FAQ pairs as structured records.

Use it for:

- FAQ-aware retrieval experiments;
- evaluation candidate generation;
- content coverage review;
- later analytics/content operations.

It does not automatically replace normalized knowledge documents.

---

## 6.3 Raw sources

```text
sources/raw/
```

preserves:

- owner-supplied source material;
- website snapshots;
- provenance evidence.

Raw sources are not directly trusted as production retrieval content.

---

## 6.4 Manifest

```text
knowledge/manifest/document_manifest.jsonl
```

provides the machine-readable inventory.

```text
knowledge/manifest/document_inventory.csv
```

provides a human-reviewable inventory.

The manifest supports:

- stable IDs;
- paths;
- versions;
- hashes;
- approval state;
- ingestion reproducibility.

---

## 6.5 Release manifest

```text
knowledge/releases/seed-v1.json
```

is the lightweight Phase 1 Knowledge Release record.

It references:

- document versions;
- Evaluation Suite;
- RAG configuration;
- derived index state/version where applicable.

---

# 7. Document Model and Repository Abstraction

Conceptual interface:

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
        query: DocumentQuery | None = None,
    ) -> list[KnowledgeDocument]:
        ...
```

Phase 1 implementation:

```text
LocalDocumentRepository
```

Future implementation:

```text
S3DocumentRepository
```

The rest of the RAG pipeline depends on `DocumentRepository`, not on `Path`, S3 SDK calls, or repository-specific storage behavior.

---

# 8. Canonical Document Metadata

Example:

```yaml
schema_version: "1.0"

document_id: "business_006_mock_assessments"
document_version: 1

tenant_id: "way2australia"
title: "Mock assessments, scoring, feedback and review windows"
knowledge_domain: "mock_assessments"

access_scope: "public"
persona_scope:
  - "guest"
  - "future_authenticated_public_user"
owner_user_id: null

content_language: "en"
language_scope: "global"
lote_languages:
  - "*"

source_authority: "owner_approved"
source_type: "owner_approved_knowledge_base"
source_url: null

approval_status: "approved"
lifecycle_status: "active"

last_reviewed_at: "2026-10-09"
effective_from: "2026-10-09"
effective_to: null

introduced_in_release: "seed-v1"
retrieval_enabled: true
synthetic: false
```

Content hash is calculated deterministically from the normalized source representation.

---

# 9. Chunk Metadata

Chunks inherit security and provenance information from the document.

Typical payload:

```text
chunk_id
document_id
document_version
section_id
chunk_index

knowledge_release_id

tenant_id
access_scope
owner_user_id

content_language
language_scope
lote_languages

knowledge_domain
source_authority
approval_status

chunker_version
embedding_version
```

Important:

```text
chunk_id != permanent business identity
```

Goldens should reference stable document/section identities instead.

---

# 10. Small Documents and Chunking Strategy

The current normalized documents are intentionally small.

A document producing one chunk is valid.

Do not split content simply to increase chunk count.

The project should compare:

1. recursive chunking;
2. structure-aware chunking;
3. FAQ Q+A atomic units;
4. package/policy atomic units;
5. optional semantic chunking.

The objective is:

```text
better retrieval quality
```

not:

```text
more chunks
```

---

# 11. Authorization Model

## Phase 1

```text
role = guest
allowed_scope = public
```

Server-side access filters must be mandatory.

---

## Future model

| Persona | Conceptual allowed scopes | Additional condition |
|---|---|---|
| guest | public | none |
| staff | public + staff | authenticated staff |
| subscriber | public + subscriber | active entitlement |
| registered user | public + subscriber + user_private | owner match |
| admin | policy-defined | privileged auth policy |

For private-user knowledge:

```text
owner_user_id == authenticated_user.id
```

must also be enforced.

---

# 12. Multilingual Design

Build **one multilingual CCL RAG system**.

Current active LOTE:

```text
Malayalam = ml
```

Global knowledge:

```yaml
lote_languages: ["*"]
```

Malayalam-specific knowledge:

```yaml
lote_languages: ["ml"]
```

Evaluation must separately measure:

- English;
- Malayalam;
- mixed English/Malayalam.

BGE-M3 is the initial embedding model because of its multilingual suitability and low experimentation cost.

---

# 13. Phase 1 RAG Query Pipeline

```text
User
  ↓
FastAPI
  ↓
request validation
rate/token/input limits
  ↓
AccessContext
  ↓
LanguageContext
  ↓
optional query transformation
  ↓
┌───────────────────────┐
│ dense retrieval       │
│ sparse/BM25 retrieval │
└───────────┬───────────┘
            ↓
           RRF
            ↓
mandatory authorization filter
            ↓
language applicability handling
            ↓
reranker
            ↓
context builder
deduplication
token budget
            ↓
answerability / evidence sufficiency
       ┌────┴────┐
       ↓         ↓
 insufficient   sufficient
       ↓         ↓
 safe refusal   versioned prompt
                 ↓
             Bedrock Runtime
                 ↓
           structured output
                 ↓
          citation validation
                 ↓
             API response
```

---

# 14. Citation Strategy

The model does not invent URLs.

Context is passed using backend-controlled IDs such as:

```text
[SOURCE_1]
[SOURCE_2]
```

The model returns citation identifiers.

Backend code maps those identifiers to approved metadata:

```text
source ID
→ document
→ title
→ approved URL/source
```

The backend validates that every cited source was actually part of the retrieved context.

---

# 15. Retrieval Experiments

The system should evolve through controlled experiments instead of changing multiple variables simultaneously.

## Experiment A

```text
recursive chunking
+
BGE-M3 dense retrieval
```

Baseline.

---

## Experiment B

```text
recursive chunking
+
BM25
```

Lexical baseline.

---

## Experiment C

```text
recursive chunking
+
dense + BM25
+
RRF
```

Hybrid baseline.

---

## Experiment D

```text
structure-aware chunking
+
hybrid retrieval
```

Tests document structure preservation.

---

## Experiment E

```text
structure-aware
+
hybrid
+
local multilingual reranker
```

Tests reranking value.

---

## Experiment F

```text
structure-aware
+
hybrid
+
reranker
+
query transformation
```

Only keep query rewriting if it provides measurable benefit.

---

## FAQ-aware experiment

Because the owner has structured FAQ pairs, explicitly compare:

```text
normal document/chunk retrieval
vs
atomic question + answer indexing
```

This is a high-value experiment for the current corpus.

---

# 16. Evaluation Architecture

## 16.1 Evaluation Suite

Goldens are one class of evaluation asset.

```text
Evaluation Suite
├── factual/golden cases
├── retrieval cases
├── multilingual cases
├── unanswerable/refusal cases
├── security cases
└── regression/edge cases
```

Current Phase 1 suite:

```text
evaluation/suites/public-eval-v1.json
```

---

## 16.2 Stable evaluation identity

Example:

```json
{
  "case_id": "G-027",
  "case_version": 1,
  "status": "active",
  "evaluation_suite_id": "public-eval-v1",
  "introduced_in_release": "seed-v1",
  "relevant_document_ids": [
    "business_006_mock_assessments"
  ],
  "relevant_section_ids": [
    "mock.feedback_timeline"
  ]
}
```

Do not bind goldens to chunk IDs.

---

## 16.3 Retrieval metrics

Primary:

- Recall@5
- MRR
- Hit Rate@5

Secondary:

- Precision@5

---

## 16.4 Generation metrics

Measure where practical:

- correctness;
- faithfulness;
- answer relevance;
- citation correctness;
- citation coverage;
- groundedness.

LLM-as-judge metrics are not the sole quality authority.

---

## 16.5 Refusal metrics

Measure:

- refusal precision;
- refusal recall;
- false-refusal rate;
- unsupported-answer rate.

---

## 16.6 Performance metrics

Track:

- embedding latency;
- dense retrieval latency;
- sparse retrieval latency;
- fusion latency;
- rerank latency;
- generation latency;
- end-to-end p50/p95;
- token usage;
- estimated cost/query.

---

## 16.7 Evaluation slices

Always break down metrics where possible by:

- English;
- Malayalam;
- mixed;
- business knowledge;
- official knowledge;
- knowledge domain;
- answerable;
- unanswerable;
- security/adversarial.

---

# 17. Security Plan

## Threats

- direct prompt injection;
- indirect prompt injection;
- retrieval poisoning;
- authorization bypass;
- system-prompt extraction;
- citation manipulation;
- oversized-input denial of wallet;
- crawler SSRF;
- unsafe source ingestion;
- insecure logging;
- malicious retrieved instructions.

---

## Controls

- mandatory pre-retrieval access filtering;
- trusted provenance;
- approval state;
- source-authority metadata;
- retrieved text treated as untrusted evidence;
- system/context separation;
- no public side-effect tools;
- backend citation ownership;
- structured outputs;
- input/token/rate limits;
- timeouts;
- cost budgets;
- safe crawler allowlists/private-IP blocks;
- log redaction;
- secrets management;
- security regression fixtures.

---

## Security fixtures

### Staff-only canary

```text
SECURITY_CANARY_9F72
```

stored in a synthetic staff-scoped fixture.

A guest must never:

- retrieve it;
- receive it in context;
- output it;

including during fallback retrieval.

---

### Poisoned public document

Contains malicious instructions inside retrieval content.

The model should still treat them as data rather than higher-priority instructions.

---

# 18. Graceful Degradation

Expected fallback behavior:

```text
query rewrite fails
→ use original query

dense embedding/retrieval fails
→ BM25

reranker fails or times out
→ use hybrid/RRF ranking

Qdrant unavailable
→ SQLite FTS5

Langfuse unavailable
→ continue serving

Bedrock unavailable
→ evidence-only response where useful

evidence insufficient
→ safe refusal / unsupported response
```

Every fallback must preserve authorization filtering.

No secondary LLM provider failover is required in Phase 1.

---

# 19. Observability

## Langfuse

One trace per RAG query.

Recommended spans:

```text
validation
access.resolve
language.resolve
query.rewrite
embedding
dense.retrieve
sparse.retrieve
fusion
rerank
context.build
answerability
generation
citation.validate
output.validate
```

Recommended metadata:

- request ID;
- `knowledge_release_id`;
- Evaluation Suite ID where relevant;
- query language;
- detected LOTE;
- access scope;
- knowledge domain;
- source authority;
- experiment ID;
- prompt version;
- fallback state;
- model/config versions;
- scores;
- latency;
- tokens/cost.

Avoid indiscriminately logging raw private/sensitive context.

---

## CloudWatch

Track application/infrastructure health:

- CPU;
- memory;
- disk;
- request count;
- 5xx;
- restart count;
- health failures.

---

# 20. Phase 1 Analytics Contract

Phase 1 does **not** build a product analytics pipeline.

It only defines/emits a stable event shape.

Example:

```json
{
  "request_id": "...",
  "knowledge_release_id": "seed-v1",
  "role": "guest",
  "query_language": "mixed",
  "detected_lote": "ml",
  "knowledge_domain": "mock_assessments",
  "retrieval_strategy": "hybrid_rerank",
  "retrieved_document_ids": [
    "business_006_mock_assessments"
  ],
  "answer_status": "answered",
  "fallback_used": false,
  "latency_ms": 740,
  "prompt_version": "answer-v2"
}
```

Phase 2 analytics can then answer:

- what users ask most;
- unsupported topics;
- language demand;
- knowledge gaps;
- refusal rate;
- fallback rate;
- release-level quality changes.

---

# 21. Technology Stack

## Backend

- Python 3.12
- FastAPI
- Pydantic
- Pydantic Settings
- httpx
- pytest
- Ruff
- Pyright
- `uv`

## Frontend

- Next.js
- TypeScript

## RAG

- Qdrant
- SQLite FTS5 fallback
- BGE-M3 embeddings
- BM25
- RRF
- local multilingual BGE reranker
- Amazon Bedrock Runtime

## Evaluation

- deterministic custom metrics
- pytest
- DeepEval where useful

## Observability

- Langfuse
- CloudWatch

## Deployment

- Docker
- Docker Compose
- GitHub Actions
- Terraform
- AWS Mumbai (`ap-south-1`)

## Intentionally not part of Phase 1

- LangGraph
- Bedrock Knowledge Bases
- Bedrock Agents
- AgentCore
- EKS
- second vector database
- fine-tuning
- large microservice architecture

---

# 22. AWS Deployment Architecture

Phase 1:

```text
Next.js / Vercel
        ↓
FastAPI
AWS Mumbai (ap-south-1)
        ↓
┌────────────────────┐
│ Qdrant + EBS       │
│ SQLite FTS5        │
│ Bedrock Runtime    │
│ Langfuse client    │
└────────────────────┘
```

Supporting AWS:

- EC2
- ECR
- EBS
- S3 for experiment/evaluation artifacts
- CloudWatch
- IAM
- SSM where appropriate

Phase 2 adds deliberate knowledge storage:

- versioned S3 knowledge bucket;
- metadata database;
- knowledge-management service/workflow infrastructure.

---

# 23. Terraform Scope

Phase 1 Terraform may manage:

- AWS provider/region;
- EC2;
- security groups;
- ECR;
- EBS;
- IAM roles/policies;
- S3 artifact bucket;
- CloudWatch;
- SSM references where appropriate.

Terraform should **not** manage:

- knowledge chunks;
- Qdrant collection content;
- prompts;
- goldens;
- runtime RAG data.

Phase 2 may extend Terraform for:

- versioned S3 knowledge storage;
- metadata DB;
- related IAM/lifecycle policies.

---

# 24. CI/CD

Target flow:

```text
git push
   ↓
Ruff / formatting checks
   ↓
Pyright
   ↓
pytest
   ↓
knowledge/schema validation
   ↓
retrieval regression
   ↓
citation validation
   ↓
authorization/security regression
   ↓
selected generation evaluation
   ↓
Docker build
   ↓
ECR
   ↓
EC2 deploy
   ↓
health check
```

Deterministic failures should be hard CI gates.

Probabilistic judge metrics should generally be reported/warned on unless a later spec defines a stable threshold.

---

# 25. Spec-Driven Development Workflow

The repository is the shared memory for Codex, Claude Code, Kiro, and humans.

Fast orientation:

```text
MISSION.md
↓
CONSTITUTION.md
↓
TECH_STACK.md
↓
ROADMAP.md
↓
CURRENT_STATE.md
↓
active spec
```

Each non-trivial capability uses:

```text
requirements.md
      ↓
design.md
      ↓
tasks.md
      ↓
implementation
      ↓
verification
      ↓
CURRENT_STATE update
```

If implementation reveals that requirements/design are wrong:

```text
update spec first
→ review
→ continue implementation
```

Do not silently change architecture.

---

# 26. Initial Spec Sequence

## Spec 001 — Project Foundation

Covers:

- Python/uv workspace;
- FastAPI skeleton;
- typed configuration;
- pytest;
- Ruff;
- Pyright;
- Makefile;
- Docker Compose;
- local Qdrant;
- health endpoint;
- multi-agent handoff baseline.

---

## Spec 002 — Document Model + DocumentRepository

Covers:

- `KnowledgeDocument`;
- stable IDs/version semantics;
- `DocumentRepository`;
- `LocalDocumentRepository`;
- manifest loading;
- metadata/schema validation;
- deterministic hashing;
- public production eligibility;
- tests;
- S3 portability.

---

## Recommended following specs

```text
003 — Ingestion Pipeline
004 — Dense Retrieval Baseline
005 — Evaluation Framework
006 — BM25 + Hybrid/RRF
007 — Structure-aware / FAQ-aware Chunking
008 — Multilingual Retrieval
009 — Reranking + Context Builder
010 — Grounded Generation + Citations
011 — Observability
012 — Security + Authorization Regression
013 — Graceful Degradation
014 — AWS + Terraform
015 — CI/CD + Evaluation Gates
016 — Recruiter Demo / RAG Lab
```

Specs should be created progressively rather than all implemented at once.

---

# 27. Seven-Day Phase 1 Execution Plan

## Day 1 — Foundation + document contracts + dense baseline

Implement:

- repository/application structure;
- project tooling;
- `KnowledgeDocument`;
- `DocumentRepository`;
- `LocalDocumentRepository`;
- manifest validation;
- recursive baseline chunking;
- BGE-M3;
- Qdrant dense index;
- guest/public filter;
- retrieval-only evaluation;
- `knowledge_release_id = seed-v1`.

End-of-day evidence:

- local API foundation works;
- approved documents load through repository abstraction;
- dense retrieval works;
- first Recall@5/MRR/Hit Rate baseline exists.

---

## Day 2 — Ingestion quality + lexical/hybrid + structure-aware

Implement:

- SHA-256 content hash;
- idempotent ingestion;
- BM25;
- RRF;
- SQLite FTS5 fallback;
- source/approval validation;
- structure-aware chunking;
- FAQ/package atomic-unit experiment.

Run:

- dense;
- BM25;
- hybrid;
- structure-aware hybrid.

End-of-day evidence:

- measurable retrieval comparison.

---

## Day 3 — Multilingual + reranking

Implement/evaluate:

- English queries;
- Malayalam queries;
- mixed queries;
- multilingual applicability;
- local multilingual reranker;
- context deduplication;
- token budgeting;
- FAQ-aware experiment.

End-of-day evidence:

- cross-language retrieval metrics;
- reranking comparison.

---

## Day 4 — Generation + citations + observability + first deployment

Implement:

- Bedrock generator abstraction;
- versioned prompts;
- answerability;
- unsupported/refusal behavior;
- backend citation validation;
- Langfuse tracing;
- Terraform foundation;
- first AWS Mumbai deployment.

End-of-day evidence:

- traceable deployed grounded RAG.

---

## Day 5 — Query transformation + full eval runner + CI/CD

Implement:

- optional query rewrite;
- DeepEval/custom generation metrics;
- experiment runner;
- GitHub Actions;
- CloudWatch;
- analytics event shape;
- version-aware evaluation metadata.

End-of-day evidence:

- reproducible regression pipeline.

---

## Day 6 — Security + failure injection

Implement/test:

- canary authorization test;
- poisoned-document test;
- prompt-injection regressions;
- citation manipulation;
- input limits;
- timeout/cost limits;
- log redaction;
- Qdrant failure;
- reranker failure;
- Bedrock failure;
- fallback authorization.

End-of-day evidence:

- security/reliability matrix.

---

## Day 7 — Final benchmark + portfolio experience

Run finalist architectures.

Select final configuration using:

- quality;
- latency;
- reliability;
- cost;
- multilingual behavior.

Build/finish:

- recruiter-facing chat;
- RAG Lab;
- engineering metrics view;
- README;
- architecture diagrams;
- final deployed regression;
- Phase 2 roadmap documentation.

No new core RAG concept should be introduced on Day 7.

---

# 28. Phase 1 Definition of Done

Phase 1 is complete when the system can demonstrate all of the following.

## Product behavior

- normal English question answered with grounded citations;
- Malayalam/mixed query retrieves correct evidence;
- unsupported question safely refuses/redirects;
- private/staff content never reaches a guest.

## Retrieval evidence

Comparison of at least:

- vector;
- BM25;
- hybrid;
- hybrid + reranking.

Include:

- Recall@5;
- MRR;
- Hit Rate@5;
- latency;
- cost where relevant.

## Observability

- Langfuse traces;
- release/config metadata;
- stage latency visibility;
- CloudWatch health.

## Security

- staff-canary regression passes;
- poisoned-document regression passes;
- fallback authorization passes.

## Reliability

Demonstrate expected behavior when:

- Qdrant fails;
- reranker fails;
- Bedrock fails.

## Engineering

- CI catches deterministic regressions;
- Terraform can recreate the required AWS foundation;
- source documents are read only through `DocumentRepository`;
- document/evaluation/release IDs are recorded.

---

# 29. Phase 2 — Knowledge Operations

Phase 2 makes content updates safe, reviewable, auditable, and reversible.

---

## 29.1 Storage model

```text
Admin UI
   ↓
Content Management API
   ↓
┌─────────────────────────────┐
│ Metadata DB                 │
│ document/version/workflow   │
│ evaluation relationships    │
│ release/audit records       │
└─────────────────────────────┘
   +
┌─────────────────────────────┐
│ Amazon S3                   │
│ immutable document versions │
└─────────────────────────────┘
```

Qdrant remains the derived search index.

---

## 29.2 S3 concept

Illustrative layout:

```text
s3://way2australia-knowledge/
  documents/
    business_006_mock_assessments/
      v1/document.md
      v2/document.md
      v3/document.md

    official_001_ccl_scoring/
      v1/document.md
```

The exact object layout can be finalized in the Phase 2 storage spec.

---

# 30. Knowledge Release Model

A Knowledge Release references independently versioned assets:

```text
Knowledge Release 12
├── Document Snapshot 18
├── Evaluation Suite 8
├── RAG Config 6
└── Index Version 18
```

Do not create one giant duplicated “config object.”

Each asset remains independently versioned.

---

# 31. Controlled Document-Change Workflow

```text
ACTIVE KNOWLEDGE RELEASE
          ↓
Admin starts change
          ↓
Knowledge Release Candidate
          ↓
Upload/edit document(s)
          ↓
new immutable document version(s)
          ↓
structured diff
          ↓
changed-section detection
          ↓
┌─────────────────────────────┐
│ deterministic impact lookup │
└─────────────────────────────┘
          ↓
existing evaluations flagged
          +
coverage-gap analysis
          ↓
LLM suggestions
          ↓
ADMIN REVIEW
   ├── keep existing case
   ├── modify case
   ├── deprecate case
   ├── replace case
   ├── accept suggestion
   ├── edit + accept
   ├── reject suggestion
   └── manually create case
          ↓
Candidate Evaluation Suite
          ↓
re-chunk/re-embed changed docs
          ↓
Candidate / Preview Index
          ↓
full candidate evaluation
          ↓
current vs candidate comparison
          ↓
Admin approval
          ↓
ATOMIC PUBLISH
          ↓
NEW ACTIVE RELEASE
```

Production keeps serving the previous active release until publish succeeds.

---

# 32. Evaluation Governance

Possible states:

```text
ACTIVE
REVIEW_REQUIRED
POTENTIALLY_OBSOLETE
DEPRECATED
REPLACED
SUGGESTED
```

No active case is automatically modified/deprecated.

---

## Existing impacted case

Example:

```text
G-027

Current expected fact:
3 working days

Candidate document:
2 working days

Status:
REVIEW_REQUIRED
```

Admin options:

- keep;
- modify;
- deprecate;
- replace.

---

## LLM-generated candidate

Example:

```text
Reason:
A new cancellation exception was added but no active evaluation covers it.

Suggested query:
...

Suggested expected facts:
...

Suggested category:
policy-edge-case
```

Admin options:

- accept;
- edit + accept;
- reject;
- create a different manual case.

Until approved:

```text
status = SUGGESTED
```

It must not participate in release gating.

---

# 33. Evaluation Impact Detection

Use deterministic relationships first.

Relationships may include:

- `document_id`;
- `section_id`;
- expected facts;
- source references.

Example:

```text
business_006@v4
        ↓
mock.feedback_timeline changed
        ↓
G-027
G-058
        ↓
REVIEW_REQUIRED
```

The LLM can explain semantic impact and identify likely gaps.

It should not be the only mechanism for discovering affected cases.

---

# 34. Phase 2 Audit Trail

## Document changes

Persist:

- document ID;
- old/new version;
- old/new hash;
- changed sections;
- changed by;
- changed at;
- change reason;
- approval status;
- approved by/at.

---

## Evaluation decisions

Persist:

- case ID;
- old/new version;
- action;
- reason;
- suggested by;
- decided by;
- decided at.

Actions may include:

```text
KEEP
MODIFY
DEPRECATE
REPLACE
ACCEPT_SUGGESTION
REJECT_SUGGESTION
MANUAL_CREATE
```

---

## LLM suggestion audit

Persist:

- original suggestion;
- model/version;
- prompt version;
- admin-edited version;
- accepted/rejected state;
- final approved case if applicable.

---

## Release audit

Persist:

- release ID;
- parent release ID;
- exact document snapshot;
- Evaluation Suite version;
- RAG config;
- index version;
- evaluation results;
- approver;
- publish time.

---

# 35. Atomic Publish and Rollback

Conceptually:

```text
active_release_id = release_11
```

After approval:

```text
active_release_id = release_12
```

Rollback:

```text
active_release_id = release_11
```

This prevents partially updated production knowledge.

Important production releases may retain index snapshots to make rollback fast.

---

# 36. Phase 2 Analytics

Because Phase 1 emits stable release/query metadata, Phase 2 can measure:

- common user questions;
- unsupported topics;
- knowledge gaps;
- language demand;
- retrieval success/failure;
- refusal behavior;
- fallback rate;
- latency/cost changes;
- quality changes by `knowledge_release_id`.

Example comparison:

```text
Release 16
vs
Release 17

Recall@5
Refusal rate
p95 latency
fallback rate
user topic distribution
```

---

# 37. Future AI Capabilities Beyond Knowledge Operations

The repository should remain broad enough for Way2Australia to add AI capabilities beyond RAG.

Potential future areas:

## Multimodal mock-test evaluation

Possible pipeline:

```text
audio/dialogue submission
        ↓
speech/audio preprocessing
        ↓
transcription / segmentation
        ↓
source vs interpreted response alignment
        ↓
multimodal evaluation
        ↓
structured feedback
        ↓
human/learner-facing report
```

This should be designed as a separate AI capability rather than forced into `packages/rag`.

Possible future package boundary:

```text
packages/
├── rag/
├── dialogue_evaluation/
└── ...
```

The actual architecture should be specified when this phase begins.

---

# 38. Recruiter / Portfolio Story

The project should tell a clear engineering story:

```text
baseline
  ↓
measure failure
  ↓
form hypothesis
  ↓
run controlled experiment
  ↓
measure quality/latency/cost
  ↓
select architecture
  ↓
add regression protection
  ↓
deploy
  ↓
trace real behavior
  ↓
identify next failure
```

The value of the project is not that it “has a chatbot.”

The value is that it demonstrates:

- production RAG architecture;
- multilingual retrieval;
- measurable experimentation;
- evaluation discipline;
- source governance;
- security;
- reliability;
- observability;
- CI/CD;
- cloud deployment;
- future-safe knowledge operations.

---

# 39. Current Implementation Starting Point

The project should currently proceed in this order:

```text
Spec 001
Project Foundation
      ↓
Spec 002
Document Model + DocumentRepository
      ↓
Spec 003
Ingestion
      ↓
Spec 004
Dense Retrieval Baseline
      ↓
Spec 005
Evaluation
      ↓
subsequent RAG specs
```

Do not ask a coding agent to build the whole seven-day system from one prompt.

Each spec should remain:

> one coherent architectural capability that can be implemented, tested, reviewed, and understood independently.

---

# 40. Final Architecture Principle

Phase 1 should stay deliberately simple enough to finish and understand.

At the same time, it should establish the boundaries that matter later:

```text
stable document identity
+
versioned evaluation identity
+
DocumentRepository
+
Knowledge Release ID
+
authorization-aware retrieval
+
language-neutral metadata
+
measurable experiments
```

That allows Phase 2 to add:

```text
S3 storage
admin editing
release candidates
evaluation governance
LLM suggestions
audit trails
atomic publishing
rollback
analytics
```

without rewriting the RAG engine.

And it allows future AI capabilities such as multimodal dialogue evaluation to be added beside RAG rather than entangled inside it.

---

## Canonical Summary

### Phase 1

Build and deploy a measurable, multilingual, secure, observable, production-oriented RAG capability.

### Phase 2

Build the Knowledge Operations layer that safely governs document and evaluation changes.

### Future

Expand Way2Australia AI into a broader preparation platform with multimodal assessment and other learning capabilities.

