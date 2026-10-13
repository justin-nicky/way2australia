UV ?= python3 -m uv
UV_CACHE_DIR ?= $(CURDIR)/.uv-cache
UV_PYTHON_INSTALL_DIR ?= $(CURDIR)/.uv-python
UV_ENV = UV_CACHE_DIR=$(UV_CACHE_DIR) UV_PYTHON_INSTALL_DIR=$(UV_PYTHON_INSTALL_DIR)

.PHONY: setup test test-unit test-integration

setup:
	$(UV_ENV) $(UV) sync --all-packages --group dev

test:
	$(UV_ENV) $(UV) run pytest

test-unit:
	$(UV_ENV) $(UV) run pytest -m "not integration"

test-integration:
	$(UV_ENV) $(UV) run pytest -m integration; code=$$?; if [ $$code -eq 5 ]; then exit 0; else exit $$code; fi
