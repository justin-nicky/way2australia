# Development Workflow

## Style

This project uses specification-driven development for non-trivial features.

Canonical flow:

```text
idea
  ↓
requirements
  ↓
human review
  ↓
design
  ↓
human review
  ↓
tasks
  ↓
implementation
  ↓
tests/evaluation
  ↓
spec verification
  ↓
commit
  ↓
CURRENT_STATE update
```

The specification is part of the implementation contract.

## Feature specs

Store specs under:

```text
.kiro/specs/<feature>/
  requirements.md
  design.md
  tasks.md
```

Recommended initial sequence:

1. project foundation;
2. document model + DocumentRepository;
3. local ingestion pipeline;
4. dense retrieval baseline;
5. evaluation framework;
6. BM25 + hybrid/RRF;
7. structure-aware chunking;
8. multilingual retrieval;
9. reranking + context builder;
10. grounded generation + citations;
11. observability;
12. security + authorization regression;
13. graceful degradation;
14. AWS/Terraform deployment;
15. CI/CD + evaluation gates;
16. recruiter demo/RAG Lab.

Create specs progressively.

## Requirements

Requirements describe **what must be true**, not implementation details.

Use explicit acceptance criteria.

## Design

Design describes:
- interfaces;
- components;
- data flow;
- error behavior;
- storage choices;
- security constraints;
- observability;
- testing strategy;
- alternatives/tradeoffs where relevant.

## Tasks

Tasks should be small enough that one coding agent can implement and verify them without broad interpretation.

Examples:
- create Pydantic model;
- implement Protocol;
- implement local adapter;
- add schema validation;
- add unit test;
- add integration test.

## Implementation rule

If implementation reveals a problem with approved requirements/design:

1. stop expanding implementation;
2. update the spec;
3. review the change;
4. continue only after the spec is correct.

Do not silently change architecture.

## Verification layers

### Fast local checks
- formatting/lint;
- type checking;
- unit tests;
- JSON/YAML/schema validation;
- knowledge metadata validation.

### Integration checks
- local Qdrant;
- repository/ingestion integration;
- retrieval behavior;
- authorization filters;
- citation validation.

### RAG evaluation
- Recall@5;
- MRR;
- HitRate@5;
- multilingual slices;
- refusal behavior;
- security regression;
- later generation metrics.

### CI
CI should strongly gate deterministic failures.

Stochastic/LLM-judge metrics should normally be warnings/reporting unless an active spec explicitly defines a stable gate.

## Multi-agent handoff

The repository is the handoff medium between Codex, Claude Code and Kiro.

Before ending substantial work:

1. update active spec tasks;
2. run relevant verification;
3. update `docs/project/CURRENT_STATE.md`;
4. update `docs/project/DECISIONS.md` for meaningful decisions;
5. leave future work as explicit spec tasks/TODOs, not hidden chat context.

Another coding agent should be able to continue from:
- Git state;
- `AGENTS.md`;
- current project docs;
- active spec.

## Git practices

Prefer small commits aligned with spec tasks.

Do not commit:
- secrets;
- `.env`;
- generated credentials;
- local vector indexes;
- model caches;
- large temporary artifacts unless intentionally versioned.

## Phase discipline

Phase 1 stays focused on the one-week production-oriented RAG project.

Do not pull Phase 2 Knowledge Operations into Phase 1 beyond:
- stable IDs;
- version fields;
- DocumentRepository abstraction;
- lightweight release identifiers;
- compatible telemetry fields.
