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


KNAPSACK_DATA = {
    "I": ["item1", "item2", "item3", "item4", "item5"],
    "v": [4, 2, 10, 1, 2],
    "w": [12, 1, 4, 1, 2],
    "W": 15,
}


def knapsack_fixture_with_data() -> dict:
    """Load knapsack fixture with inline data populated."""
    fixture = load_fixture("knapsack")
    fixture["data"] = {**KNAPSACK_DATA}
    return fixture
