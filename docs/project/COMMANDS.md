# Project Commands

This file defines the intended stable command surface for humans and coding agents.

The commands below are the target interface. The first foundation spec should create the supporting Makefile/scripts.

## Environment

```bash
make setup
```

## Quality

```bash
make format
make lint
make typecheck
make verify
```

`make verify` should run the fast deterministic verification set.

## Tests

```bash
make test
make test-unit
make test-integration
```

## Knowledge

```bash
make validate-knowledge
```

Expected:
- validate document metadata/frontmatter;
- validate IDs/version fields;
- validate manifests;
- ensure production corpus excludes test-only fixtures.

## Ingestion

```bash
make ingest
```

Expected:
- read through `DocumentRepository`;
- detect unchanged content;
- chunk changed documents;
- embed/upsert;
- record version metadata.

## Evaluation

```bash
make eval-retrieval
make eval-generation
make eval-security
```

Retrieval evaluation should support at least:
- Recall@5;
- MRR;
- HitRate@5;
- language/category slices.

## Experiments

```bash
make experiment CONFIG=experiments/configs/day1_baseline.yaml
```

Experiment results should record:
- Git commit;
- Knowledge Release ID;
- Evaluation Suite ID;
- chunker config/version;
- embedding model/version;
- retrieval strategy;
- reranker config;
- prompt version;
- metrics;
- stage latency;
- token/cost data where available.

## Docker

```bash
docker compose up -d
docker compose down
```

Expected local dependency: Qdrant.

## Infrastructure

Terraform remains explicit:

```bash
terraform fmt
terraform validate
terraform plan
terraform apply
```

Do not automate destructive infrastructure commands.

## Rule

Do not invent alternative project command surfaces unless this file is intentionally updated.
