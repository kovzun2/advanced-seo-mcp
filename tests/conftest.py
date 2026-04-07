"""Shared pytest fixtures."""

import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def sample_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "onpage_sample.html").read_text()


@pytest.fixture
def sample_psi_response(fixtures_dir: Path) -> dict:
    import json
    return json.loads((fixtures_dir / "psi_sample.json").read_text())


@pytest.fixture
def sample_ahrefs_response(fixtures_dir: Path) -> dict:
    import json
    return json.loads((fixtures_dir / "ahrefs_backlinks.json").read_text())
