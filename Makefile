.PHONY: all test clean

all:
	python3 -m venv .venv || true
	.venv/bin/pip install -e '.[dev]'

test:
	.venv/bin/pytest tests/ -x -q
