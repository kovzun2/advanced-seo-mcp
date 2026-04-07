# Contributing

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running tests

```bash
pytest -v
```

## Code style

We use `ruff` for linting and formatting, `mypy` for type checking.

```bash
ruff format src/ tests/
ruff check --fix src/ tests/
mypy src/
```

## Adding a new provider

1. Create a Pydantic model in `models/`
2. Create provider in `providers/` extending `BaseProvider`
3. Write tests in `tests/`
4. Register tool in `server.py`
5. Update README feature table
