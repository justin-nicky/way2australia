# Project Commands

This file defines the intended stable command surface for humans and coding agents.

The commands below are the target interface. Implemented today: `setup`, `format`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `verify`, `skills-sync`, `skills-check`, `validate-knowledge`, `setup-bge-m3`, `ingest`, `retrieve`, `retrieval-baseline`. The other targets are created by the spec that needs them.

## Environment

```bash
make setup
make setup-bge-m3
```

`make setup` installs the dev environment without the optional `bge-m3` extra, and removes the extra if it was installed. `make setup-bge-m3` adds it (`uv sync ... --extra bge-m3`: `sentence-transformers`, which brings PyTorch) for real BGE-M3 embeddings. `make verify` never needs it. The download is large; on a slow connection uv may time out, so the `Makefile` defaults `UV_HTTP_TIMEOUT` to 300 seconds for this target; raise it per run if needed, for example `UV_HTTP_TIMEOUT=600 make setup-bge-m3`.

## Quality

```bash
make format
make lint
make typecheck
make verify
```

`make lint` runs `ruff check` and `ruff format --check`, so format drift fails `make verify`; `make format` fixes it.

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

## Retrieval

```bash
make retrieve QUERY="Is coaching compulsory?"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --top-k 3"
make retrieval-baseline
make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake --output /tmp/baseline.json"
```

`make retrieve` behavior:
- options (through `RETRIEVE_ARGS`): `--embedder {bge_m3,fake}`, `--top-k` (1 to 50, default 5), `--config`; `make retrieve` passes `--repo-root` itself. There is no option for role, scope or tenant: access is always guest/public for the tenant in `W2A_TENANT_ID`;
- prints a header (`index: <collection> (index_version ...; embedder <model> @ <revision>, fake=<bool>)`, `device=`), the hit count, and one line per hit: rank, `document_id`, `section_id`, score, title. It prints no document bodies, absolute paths or API keys; payload text is passed through `safe_text` (control characters, ANSI and bidi override characters removed);
- needs Qdrant with an index built by `make ingest` for the same `QDRANT_COLLECTION_BASE` and `index_version`; with `--embedder fake` use the throwaway base the fake ingest used;
- exit codes: `0` success (including zero hits), `2` refusal or configuration error (empty query, bad `--top-k`, empty `W2A_TENANT_ID`, missing `bge-m3` extra, missing or mismatched index, unreachable Qdrant, a hit that fails the access re-check). Retrieval and ingestion errors print `ERROR <ClassName>: <message>`; any other exception prints its class name only;
- quoting caveat: `QUERY` is expanded by the shell inside `"$(QUERY)"`, so a query containing `"`, `$` or a backtick needs care. To avoid it, run the module directly: `uv run python -m way2australia_rag.retrieval.cli --repo-root . "your query"` (or `python3 -m uv run python -m ...`), with the same options.

`make retrieval-baseline` behavior:
- options (through `BASELINE_ARGS`): `--embedder {bge_m3,fake}`, `--allow-fake`, `--top-k` (default 5), `--suite` (default `evaluation/suites/public-eval-v1.json`), `--release` (default `seed-v1`, must match `knowledge/releases/<id>.json`), `--output`, `--config`;
- runs the active, answerable golden cases that have `relevant_document_ids` (63 in `public-eval-v1`) through dense retrieval and prints overall HitRate@5 next to the random expectation `min(1, 5/N)`, Recall@5, MRR, p50/p95 latency (after an unmeasured warm-up), the result file name relative to the repository root, and notes;
- an index built with the fake embedder is refused (exit 2) unless `--allow-fake`; the result then carries the note "not a quality measurement". `--allow-fake` is for plumbing checks, never for a recorded baseline;
- the result is `experiments/results/retrieval-baseline-<index_version>-<UTC YYYYMMDDTHHMMSSZ>.json` unless `--output` is given. It is never overwritten and nothing is written on error. It holds no query text, chunk text, absolute paths or secrets. Tests and throwaway checks should use `--output` in a temporary directory. Do not commit a fake or throwaway result;
- the committed real BGE-M3 result is produced by the user after merge (`make setup-bge-m3`, a real `make ingest`, `make retrieval-baseline`, `make setup`);
- exit codes as `make retrieve`.

Environment (retrieval and ingestion): `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_BASE`, and `W2A_TENANT_ID` (default `way2australia`; empty or whitespace-only is refused with exit 2). The tenant is a server setting stored on every indexed point, so changing it changes which points `make retrieve` can see, and it also applies to `make ingest`.

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
