.PHONY: all test test-llm lint fmt typecheck clean

-include .env
export

all: .venv

.venv: pyproject.toml
	python3 -m venv .venv
	.venv/bin/pip install -e '.[dev]'
	@touch .venv

test: .venv
	.venv/bin/pytest tests/ -x -q -m 'not llm'

test-llm: .venv
	.venv/bin/pytest tests/ -x -q -m llm

lint: .venv
	.venv/bin/ruff check src/ tests/

fmt: .venv
	.venv/bin/ruff format src/ tests/

typecheck: .venv
	.venv/bin/mypy src/
