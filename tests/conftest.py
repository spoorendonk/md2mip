"""Shared fixtures for tests."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
DATA_DIR = Path(__file__).parent.parent / "data"


def load_fixture(name: str) -> dict:
    """Load a fixture IR JSON by name (without extension)."""
    path = FIXTURES_DIR / f"{name}.ir.json"
    return json.loads(path.read_text())
