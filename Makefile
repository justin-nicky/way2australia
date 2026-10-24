# Prefer a standalone uv binary; fall back to the pip-installed module.
UV ?= $(shell command -v uv >/dev/null 2>&1 && echo uv || echo python3 -m uv)
UV_CACHE_DIR ?= $(CURDIR)/.uv-cache
UV_PYTHON_INSTALL_DIR ?= $(CURDIR)/.uv-python
UV_ENV = UV_CACHE_DIR=$(UV_CACHE_DIR) UV_PYTHON_INSTALL_DIR=$(UV_PYTHON_INSTALL_DIR)
PYTHON_TARGETS ?= apps packages tests scripts
UV_HTTP_TIMEOUT ?= 300

.PHONY: setup setup-bge-m3 format lint typecheck test test-unit test-integration verify skills-sync skills-check validate-knowledge validate-evaluation ingest retrieve retrieval-baseline eval-retrieval eval-security

setup:
	$(UV_ENV) $(UV) sync --all-packages --group dev

# Adds the optional bge-m3 group (sentence-transformers, which brings PyTorch).
# `make setup` syncs without the group and therefore removes it again.
setup-bge-m3:
	UV_HTTP_TIMEOUT=$(UV_HTTP_TIMEOUT) $(UV_ENV) $(UV) sync --all-packages --group dev --extra bge-m3

format:
	$(UV_ENV) $(UV) run ruff format $(PYTHON_TARGETS)

lint:
	$(UV_ENV) $(UV) run ruff check $(PYTHON_TARGETS)
	$(UV_ENV) $(UV) run ruff format --check $(PYTHON_TARGETS)

typecheck:
	$(UV_ENV) $(UV) run pyright $(PYTHON_TARGETS)

test:
	$(UV_ENV) $(UV) run pytest

test-unit:
	$(UV_ENV) $(UV) run pytest -m "not integration"

test-integration:
	$(UV_ENV) $(UV) run pytest -m integration; code=$$?; if [ $$code -eq 5 ]; then exit 0; else exit $$code; fi

skills-sync:
	$(UV_ENV) $(UV) run python scripts/sync_agent_skills.py

skills-check:
	$(UV_ENV) $(UV) run python scripts/sync_agent_skills.py --check

validate-knowledge:
	$(UV_ENV) $(UV) run python -m way2australia_rag.repositories.validate --repo-root $(CURDIR)

validate-evaluation:
	$(UV_ENV) $(UV) run python -m way2australia_rag.evaluation.cli validate --repo-root $(CURDIR)

verify: lint typecheck skills-check validate-knowledge validate-evaluation test

# Index approved public knowledge into Qdrant. Extra options go in INGEST_ARGS,
# e.g. make ingest INGEST_ARGS="--embedder fake".
ingest:
	@$(UV_ENV) $(UV) run python -m way2australia_rag.ingestion.cli --repo-root $(CURDIR) $(INGEST_ARGS)

# Dense retrieval over the guest/public index. Extra options go in RETRIEVE_ARGS,
# e.g. make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake".
retrieve:
	@$(UV_ENV) $(UV) run python -m way2australia_rag.retrieval.cli --repo-root $(CURDIR) $(RETRIEVE_ARGS) "$(QUERY)"

# Run the golden cases through dense retrieval and write a JSON result. Extra
# options go in BASELINE_ARGS, e.g. make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake".
retrieval-baseline:
	@$(UV_ENV) $(UV) run python -m way2australia_rag.retrieval.baseline_cli --repo-root $(CURDIR) $(BASELINE_ARGS)

# Quality evaluation over the active suite (needs a real BGE-M3 index; refuses fake).
# Extra options go in EVAL_ARGS, e.g. make eval-retrieval EVAL_ARGS="--top-k 3".
eval-retrieval:
	@$(UV_ENV) $(UV) run python -m way2australia_rag.evaluation.cli retrieval --repo-root $(CURDIR) $(EVAL_ARGS)

# Authorization hard gate on a throwaway in-memory index (fake embedder, no Docker,
# no model). Result JSON goes to experiments/results/tmp/ (git-ignored).
# Extra options go in EVAL_ARGS, e.g. make eval-security EVAL_ARGS="--output /tmp/x.json".
eval-security:
	@$(UV_ENV) $(UV) run python -m way2australia_rag.evaluation.cli security --repo-root $(CURDIR) $(EVAL_ARGS)
