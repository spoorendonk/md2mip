# md2mip

Compile natural-language optimization models (Markdown) into standalone Python+HiGHS solver scripts.

```
markdown → (LLM) → IR → codegen → Python + HiGHS
```

## Quick example

```bash
# Compile a knapsack model
md2mip compile models/knapsack.md

# Run it with data
python out/knapsack_solver.py data/knapsack.yaml
```

```
Status: optimal
Objective: 16.0
Solution:
  x[item1] = 0.0
  x[item2] = 1.0
  x[item3] = 1.0
  x[item4] = 1.0
  x[item5] = 1.0
```

## Install

```bash
pip install -e '.[dev]'
# or
make
```

## Configuration

```bash
cp .env.template .env
# Set your ANTHROPIC_API_KEY in .env
```

## CLI

| Command    | Description                                |
|------------|--------------------------------------------|
| `compile`  | Markdown → standalone Python solver script |
| `run`      | Compile and immediately run with data      |
| `validate` | Compile, run, check expected objective     |
| `ocr`      | Extract a math model from an image (LLM vision) |

Run `md2mip --help` or `md2mip <command> --help` for details.

## Development

```bash
make test       # offline tests (no LLM)
make test-llm   # LLM integration tests
make lint       # ruff check
make fmt        # ruff format
make typecheck  # mypy
```

## License

MIT — see [LICENSE](LICENSE).
