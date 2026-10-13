# 001 — Project Foundation Tasks

## T1 — Initialize Python project

- [x] Set Python version to 3.12.
- [x] Create root `pyproject.toml`.
- [x] Configure `uv`.
- [x] Add runtime dependencies required by this spec.
- [x] Add development dependencies.
- [x] Create `.python-version`.
- [x] Create `.gitignore`.
- [x] Create safe `.env.example`.

### Verification

```bash
make setup
```

## T2 — Create repository/package skeleton

- [x] Create `apps/api/`.
- [x] Reserve `apps/web/`.
- [x] Create `packages/core/`.
- [x] Create `packages/rag/`.
- [x] Create `packages/observability/`.
- [x] Add Python package/import configuration.
- [x] Preserve existing knowledge/evaluation/docs seed folders.

### Verification

- package imports succeed;
- reusable packages do not depend on `apps/api`.

## T3 — Implement FastAPI skeleton

- [x] Create application entry point.
- [x] Create health router.
- [-] Implement `GET /health`.
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
- [x] Create root `Makefile`.
- [x] Implement `make setup`.
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
