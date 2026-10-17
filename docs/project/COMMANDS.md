# Project Commands

This file defines the intended stable command surface for humans and coding agents.

The commands below are the target interface. Implemented today: `setup`, `format`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `verify`, `skills-sync`, `skills-check`, `validate-knowledge`, `setup-bge-m3`, `ingest`. The other targets are created by the spec that needs them.

## Environment

```bash
make setup
make setup-bge-m3
```

`make setup` installs the dev environment without the optional `bge-m3` extra, and removes the extra if it was installed. `make setup-bge-m3` adds it (`uv sync ... --extra bge-m3`: `sentence-transformers`, which brings PyTorch) for real BGE-M3 embeddings. `make verify` never needs it. The download is large; on a slow connection uv may time out, so raise the timeout, for example `UV_HTTP_TIMEOUT=600 make setup-bge-m3`.

## Quality

```bash
make format
make lint
make typecheck
make verify
```

`make verify` should run the fast deterministic verification set. It runs `make test`, which includes the `integration`-marked tests: they skip when Qdrant is unreachable, and when a local Qdrant is running they create and remove temporary collections against it.

## Tests

```bash
make test
make test-unit
make test-integration
```

## Agent skills

```bash
make skills-sync
make skills-check
```

- `skills-sync` regenerates `.claude/skills/`, `.agents/skills/` and `.kiro/skills/` from `agent-skills/`.
- `skills-check` fails if any mirror differs; it is part of `make verify`.

Run a role (each in a fresh session; the orchestrator is the usual entry point):

| Host | Commands |
|---|---|
| Claude Code | `/spec-orchestrator [NNN]`, `/spec-planner`, `/spec-implementer <NNN> [task]`, `/task-reviewer <NNN> <task>`, `/spec-reviewer <NNN>` |
| Codex | `$spec-orchestrator`, `$spec-planner`, `$spec-implementer <NNN> [task]`, `$task-reviewer <NNN> <task>`, `$spec-reviewer <NNN>` |
| Kiro | `/spec-orchestrator`, `/spec-planner`, `/spec-implementer`, `/task-reviewer`, `/spec-reviewer` |

Find an approved task's commit: `git log --grep='^Spec-Task: <NNN>/<task>$' spec/<NNN>`.

## Knowledge

```bash
make validate-knowledge
```

Expected:
- validate document metadata/frontmatter;
- validate IDs/version fields;
- validate manifests;
- ensure production corpus excludes test-only fixtures.

Behavior:
- lists every problem as `ERROR <document_id>: <field>: <reason>` and ends with a summary count;
- also reports manifest entries outside the approved production roots and markdown files under those roots that the manifest does not list;
- fails if a retrievable (active, retrieval-enabled) document in the public corpus is synthetic, not approved or not public;
- exits `0` when valid, `1` on any problem; runs inside `make verify`.

## Ingestion

```bash
make ingest
make ingest INGEST_ARGS="--embedder fake"
```

Behavior:
- options (through `INGEST_ARGS`): `--embedder {bge_m3,fake}` (default `embedder.provider` from the config), `--config` (default `<repo-root>/config/ingestion.yaml`); `make ingest` passes `--repo-root` itself;
- reads eligible documents through `DocumentRepository` (guest/public policy);
- chunks, embeds and upserts only added or changed documents, deletes documents that are no longer eligible;
- prints `index: <collection> (index_version <label>; embedder <model> @ <revision>, fake=<bool>)`, then `added: N  updated: N  unchanged: N  deleted: N`, the `document_id`s per category and `ERROR <document_id>: <reason>` lines; refusals go to stderr as `ERROR <ClassName>[: message]`;
- a second run on unchanged content reports `added: 0  updated: 0  unchanged: <all>  deleted: 0`;
- needs Qdrant (`docker compose up -d qdrant`); `QDRANT_URL`, `QDRANT_API_KEY` and `QDRANT_COLLECTION_BASE` come from the environment, index-defining settings from `config/ingestion.yaml`;
- real embeddings need `make setup-bge-m3`; without the extra the command exits 2 before contacting Qdrant;
- for `--embedder fake` always set a throwaway `QDRANT_COLLECTION_BASE`; a fake run on the default collection marks it fake and later real runs are refused until `index_version` changes;
- exit codes: `0` success, `1` any document failed, `2` refusal (settings mismatch, missing group, bad configuration, unreachable Qdrant).

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
