# 001 — Project Foundation Design

## Design summary

Create a small Python monorepo-style foundation with a FastAPI application and reusable internal packages.

The first spec intentionally avoids RAG implementation details.

## Selected tooling

### Python

- Python 3.12
- `uv` for dependency/environment management
- FastAPI
- Pydantic
- Pydantic Settings
- pytest
- Ruff
- Pyright

### Local infrastructure

- Docker
- Docker Compose
- Qdrant

### Command surface

A root `Makefile` provides stable commands for humans and coding agents.

## Target structure after this spec

```text
way2australia-ai/
├── AGENTS.md
├── CLAUDE.md
├── Makefile
├── pyproject.toml
├── .python-version
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   └── way2australia_api/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── config.py
│   │   │       └── api/
│   │   │           ├── __init__.py
│   │   │           └── health.py
│   │   └── tests/
│   │       └── test_health.py
│   └── web/
│       └── .gitkeep
│
├── packages/
│   ├── core/
│   ├── rag/
│   └── observability/
│
├── knowledge/
├── evaluation/
├── sources/
├── config/
├── experiments/
├── analytics/
├── prompts/
├── tests/
├── docs/
└── infra/
```

Existing seed/context files should be merged into the appropriate directories rather than overwritten.

## FastAPI design

`main.py` owns application creation/wiring.

`api/health.py` owns the health route.

The health endpoint returns a minimal stable response such as:

```json
{
  "status": "ok"
}
```

It should not call Qdrant, Bedrock, or other RAG dependencies yet.

## Configuration design

Use a single Pydantic Settings object for application configuration.

Conceptual flow:

```text
environment / .env
        ↓
Settings
        ↓
application wiring
```

Avoid scattered `os.getenv()` calls.

Only a small number of foundation settings should exist initially.

## Python workspace

Use a root `pyproject.toml` and `uv`.

Application code may depend on reusable packages, but reusable packages must not depend on `apps/api`.

## Quality configuration

Ruff:
- formatting;
- linting.

Pyright:
- static type checking.

pytest:
- test execution.

Keep configuration primarily in `pyproject.toml` where supported.

## Make command design

Target interface:

```bash
make setup
make format
make lint
make typecheck
make test
make test-unit
make test-integration
make verify
```

`make verify` should run:
- lint;
- typecheck;
- tests.

## Docker Compose design

Define Qdrant only.

Requirements:
- explicit image version where practical;
- named/local volume;
- local port exposure;
- health check if supported cleanly.

Do not create Qdrant collections during this spec.

## Testing design

Initial automated tests:
1. application can be imported/created;
2. `/health` returns HTTP 200;
3. response structure is stable;
4. typed settings can be instantiated for a test environment.

Qdrant connectivity tests are postponed until a spec actually consumes Qdrant.

## Security/hygiene

`.gitignore` should cover at least:
- `.env`;
- `.venv`;
- Python cache;
- pytest/type-check caches;
- local Qdrant data;
- local model cache if later introduced.

`.env.example` contains variable names and safe placeholders only.

## Logging

Use standard Python logging or a very small wrapper.

Do not introduce Langfuse in this spec.

## Non-goals

No RAG behavior should be implemented as part of foundation setup.
