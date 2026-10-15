# Prefer a standalone uv binary; fall back to the pip-installed module.
UV ?= $(shell command -v uv >/dev/null 2>&1 && echo uv || echo python3 -m uv)
UV_CACHE_DIR ?= $(CURDIR)/.uv-cache
UV_PYTHON_INSTALL_DIR ?= $(CURDIR)/.uv-python
UV_ENV = UV_CACHE_DIR=$(UV_CACHE_DIR) UV_PYTHON_INSTALL_DIR=$(UV_PYTHON_INSTALL_DIR)
PYTHON_TARGETS ?= apps packages tests scripts

.PHONY: setup format lint typecheck test test-unit test-integration verify skills-sync skills-check validate-knowledge

setup:
	$(UV_ENV) $(UV) sync --all-packages --group dev

format:
	$(UV_ENV) $(UV) run ruff format $(PYTHON_TARGETS)

lint:
	$(UV_ENV) $(UV) run ruff check $(PYTHON_TARGETS)

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

verify: lint typecheck skills-check validate-knowledge test
