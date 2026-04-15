# Contributing

## Setup

```bash
make setup
```

Manual alternative:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

## Running tests

```bash
make test
```

## Code style

We use `ruff` for linting and formatting, `mypy` for type checking.

```bash
make format
make lint
make typecheck
```

## Packaging smoke checks

```bash
make build
make smoke
```

## Adding a new provider

1. Create a Pydantic model in `models/`
2. Create provider in `providers/` extending `BaseProvider`
3. Write tests in `tests/`
4. Register tool in `server.py`
5. Update README feature table
6. Ensure the tool returns normalized `_meta` and structured `error` payloads
