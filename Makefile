UV ?= python3 -m uv
UV_CACHE_DIR ?= $(CURDIR)/.uv-cache
UV_PYTHON_INSTALL_DIR ?= $(CURDIR)/.uv-python

.PHONY: setup

setup:
	UV_CACHE_DIR=$(UV_CACHE_DIR) UV_PYTHON_INSTALL_DIR=$(UV_PYTHON_INSTALL_DIR) $(UV) sync --all-packages --group dev
