# md2mip

Compile natural-language optimization models (Markdown) into standalone Python+HiGHS solver scripts.

```
markdown → (LLM) → IR → codegen → Python + HiGHS
```

## Examples

### 1. Quick run — data in markdown (knapsack)

`models/knapsack.md` contains inline data (values, weights, capacity). One command:

```bash
md2mip run models/knapsack.md
```

The LLM extracts the data automatically. Output:

```
Status: optimal
Objective: 15.0
Solution:
  x[item1] = 0.0
  x[item2] = 1.0
  x[item3] = 1.0
  x[item4] = 1.0
  x[item5] = 1.0
```

### 2. Compile + run with different data (transportation)

```bash
# Compile — generates solver script AND data template
md2mip compile models/transportation.md

# Run with the generated default data
python out/transportation_solver.py out/transportation_data.yaml

# Run with a larger instance
python out/transportation_solver.py data/transportation_large.yaml
```

`compile` always writes two files:
- `out/<name>_solver.py` — standalone solver script
- `out/<name>_data.yaml` — complete data (if model has inline data) or template to fill in

### 3. OCR full pipeline

```bash
md2mip ocr photo.png -o model.md
md2mip compile model.md
python out/model_solver.py out/model_data.yaml
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
