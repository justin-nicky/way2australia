# Tech Stack

This file records the currently selected implementation stack and intentional non-selections.

## Backend

- Language: Python
- API framework: FastAPI
- Data validation/settings: Pydantic / Pydantic Settings
- Manifest schema validation: `jsonschema` (JSON Schema validation of the document manifest, `packages/rag`)
- Frontmatter parsing: `pyyaml` (YAML frontmatter of knowledge documents, `packages/rag`)
- HTTP client: httpx
- Testing: pytest
- Data analysis/evaluation support: Pandas where useful

## Frontend

- Next.js
- TypeScript

## RAG core

### Vector database
- Qdrant

### Lexical fallback
- SQLite FTS5

### Embeddings
- BGE-M3 initially

Reason:
- multilingual suitability;
- English/Malayalam support;
- local/open-source experimentation;
- low re-indexing cost during comparisons.

### Sparse retrieval
- BM25

### Fusion
- Reciprocal Rank Fusion (RRF)

### Reranking
- Local multilingual BGE reranker initially

### Generation
- Amazon Bedrock Runtime

Exact Bedrock model should be selected based on current:
- Mumbai region support;
- quality;
- latency;
- cost;
- structured-output needs.

## Evaluation

- pytest for deterministic tests
- custom retrieval metrics
- DeepEval where useful

Primary retrieval metrics:
- Recall@5
- MRR
- HitRate@5

Generation/e2e evaluation may include:
- correctness;
- faithfulness;
- answer relevance;
- citation correctness/coverage;
- refusal quality;
- failure rate.

LLM-as-judge metrics are not the sole source of truth.

## Observability

### RAG/application tracing
- Langfuse

### Infrastructure/application operations
- Amazon CloudWatch

## Containers

- Docker
- Docker Compose

## CI/CD

- GitHub Actions

## Infrastructure as Code

- Terraform

## AWS target

Initial region:
- Mumbai (`ap-south-1`)

Likely Phase 1 AWS services:
- EC2
- ECR
- EBS
- S3
- IAM
- CloudWatch
- SSM where useful
- Bedrock Runtime

## Phase 2 storage direction

### Source documents
- Amazon S3

### Metadata/workflow/audit
- relational metadata database
- exact engine intentionally not locked yet

### Derived retrieval index
- Qdrant

## Current intentionally avoided choices

Do not introduce these unless a later spec/decision explicitly changes direction:

- LangGraph
- Bedrock Knowledge Bases as the core RAG implementation
- Bedrock Agents / AgentCore for Phase 1
- Kubernetes / EKS
- multiple vector databases
- full agent orchestration
- fine-tuning
- complex microservices
- heavyweight framework abstractions that hide retrieval/evaluation behavior

## Tooling philosophy

Prefer plain, inspectable Python and small replaceable interfaces.

Use frameworks only where they improve productivity without obscuring the RAG mechanics being studied.
