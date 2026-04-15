PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: setup install-dev test lint format typecheck build smoke clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e ".[dev]"
	$(BIN)/pre-commit install

install-dev:
	$(BIN)/python -m pip install -e ".[dev]"

test:
	PYTHONPATH=src $(BIN)/pytest --cov=advanced_seo_mcp --cov-report=term-missing --cov-report=xml --cov-fail-under=70 -v

lint:
	$(BIN)/ruff check src/ tests/

format:
	$(BIN)/ruff format src/ tests/

typecheck:
	PYTHONPATH=src $(BIN)/mypy src/ --ignore-missing-imports

build:
	$(BIN)/python -m build

smoke:
	PYTHONPATH=src $(BIN)/python -c "import advanced_seo_mcp"
	PYTHONPATH=src $(BIN)/python -c "from advanced_seo_mcp.server import mcp; print(mcp.name)"

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info coverage.xml
