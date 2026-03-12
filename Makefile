.PHONY: all test test-llm lint fmt typecheck clean

-include .env
export

all:
	python3 -m venv .venv || true
	.venv/bin/pip install -e '.[dev]'

test:
	.venv/bin/pytest tests/ -x -q -m 'not llm'

test-llm:
	.venv/bin/pytest tests/ -x -q -m llm

lint:
	.venv/bin/ruff check src/ tests/

fmt:
	.venv/bin/ruff format src/ tests/

typecheck:
	.venv/bin/mypy src/
