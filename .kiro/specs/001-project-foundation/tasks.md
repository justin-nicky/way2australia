# 001 — Project Foundation Tasks

## T1 — Initialize Python project

- [ ] Set Python version to 3.12.
- [ ] Create root `pyproject.toml`.
- [ ] Configure `uv`.
- [ ] Add runtime dependencies required by this spec.
- [ ] Add development dependencies.
- [ ] Create `.python-version`.
- [ ] Create `.gitignore`.
- [ ] Create safe `.env.example`.

### Verification

```bash
make setup
```

## T2 — Create repository/package skeleton

- [ ] Create `apps/api/`.
- [ ] Reserve `apps/web/`.
- [ ] Create `packages/core/`.
- [ ] Create `packages/rag/`.
- [ ] Create `packages/observability/`.
- [ ] Add Python package/import configuration.
- [ ] Preserve existing knowledge/evaluation/docs seed folders.

### Verification

- package imports succeed;
- reusable packages do not depend on `apps/api`.

## T3 — Implement FastAPI skeleton

- [ ] Create application entry point.
- [ ] Create health router.
- [ ] Implement `GET /health`.
- [ ] Keep route logic independent of Qdrant/RAG services.

### Verification

- application starts;
- `/health` returns HTTP 200;
- automated test passes.

## T4 — Add typed configuration

- [ ] Create Pydantic Settings model.
- [ ] Wire settings into application startup/dependencies.
- [ ] Avoid scattered direct environment access.
- [ ] Add configuration tests.
- [ ] Keep settings limited to what this spec uses.

## T5 — Configure tests

- [ ] Configure pytest.
- [ ] Add API health test.
- [ ] Add basic application/config tests.
- [ ] Prepare unit/integration test layout.

### Verification

```bash
make test
```

## T6 — Configure quality tooling and stable commands

- [ ] Configure Ruff formatting.
- [ ] Configure Ruff linting.
- [ ] Configure Pyright.
- [ ] Create root `Makefile`.
- [ ] Implement `make setup`.
- [ ] Implement `make format`.
- [ ] Implement `make lint`.
- [ ] Implement `make typecheck`.
- [ ] Implement `make test`.
- [ ] Implement `make test-unit`.
- [ ] Implement `make test-integration`.
- [ ] Implement `make verify`.

### Verification

```bash
make verify
```

## T7 — Add local Qdrant service

- [ ] Add Qdrant to `docker-compose.yml`.
- [ ] Pin an appropriate image version.
- [ ] Configure local port.
- [ ] Configure persistent local volume.
- [ ] Add health check where practical.
- [ ] Ensure generated Qdrant data is ignored by Git.

### Verification

```bash
docker compose up -d
docker compose ps
docker compose down
```

## T8 — Final verification and handoff

- [ ] Run `make verify`.
- [ ] Confirm the API starts.
- [ ] Confirm `/health`.
- [ ] Confirm Qdrant starts locally.
- [ ] Confirm no secrets/generated local state are tracked.
- [ ] Confirm no out-of-scope RAG functionality was added.
- [ ] Update `docs/project/CURRENT_STATE.md`.
- [ ] Record durable implementation decisions in `docs/project/DECISIONS.md`.
- [ ] Mark tasks accurately.

## Completion gate

Do not start Spec 002 implementation until this spec's Definition of Done is satisfied or an explicit documented exception is approved.
