# md2mip Phase 1: Core Compiler

## Context

Build a CLI that compiles Markdown/LaTeX MIP models into standalone Python solver scripts. The LLM (Claude API) runs once at compile time to parse the math notation into a structured IR. A deterministic code generator then produces a self-contained `.py` file that uses HiGHS + numpy to solve the model. No LLM or md2mip needed at runtime.

## Project Structure

```
md2mip/
├── pyproject.toml
├── Makefile
├── src/md2mip/
│   ├── __init__.py
│   ├── cli.py          # Click CLI: compile, run
│   ├── compiler.py     # Orchestrator: markdown → IR → code
│   ├── llm.py          # LLM call via litellm: markdown → IR JSON
│   ├── prompt.py       # System prompt for the LLM
│   ├── ir.py           # IR dataclasses + validation
│   └── codegen.py      # IR → standalone Python script
├── tests/
│   ├── conftest.py
│   ├── test_ir.py
│   ├── test_codegen.py
│   ├── test_cli.py
│   └── test_generated.py  # Run generated scripts, check solutions
├── models/             # 6 test .md files (from plan-md2mip.md)
├── data/               # Matching YAML data files
└── fixtures/           # Captured IR JSONs for offline testing
```

## Key Design Decisions

1. **Single LLM call** — markdown → IR JSON only. Code generation from IR is deterministic (no second LLM call). Cheaper, faster, more debuggable.

2. **Programmatic codegen** (not templates) — `codegen.py` builds Python source with f-strings and helper functions. More testable than Jinja for the conditional logic involved.

3. **Dataclasses for IR** — keep deps minimal. `@dataclass` + manual `from_dict()` with clear errors. Pydantic later if needed.

4. **Expression strings in IR** — constraints use pseudo-Python like `"sum(x[i,j] for j in J) <= s[i]"`. The LLM prompt constrains the syntax; codegen parses these specific patterns. Parsed using Python's `ast` module (stdlib) — no extra deps needed since expressions are valid Python syntax.

5. **litellm for LLM abstraction** — single dependency handles Anthropic, Ollama, OpenAI, and 100+ other providers. Model specified as a string (`claude-sonnet-4-20250514`, `ollama/qwen3`, `ollama/llama3.3`, etc.). Default model: `claude-sonnet-4-20250514`. Recommended self-hosted: `ollama/qwen3` or `ollama/llama3.3`.

6. **Fixture-based testing** — capture good IR JSONs from the LLM once, then test codegen offline forever. Three tiers: unit (no deps), solver (needs HiGHS), integration (needs LLM, skip by default).

7. **JSON for IR, YAML for data** — IR is JSON (LLMs produce valid JSON reliably, JSON mode available). Data files are YAML or JSON (user's choice).

8. **Custom IR schema** — no existing standard covers algebraic models with sets/parameters/for-all at the JSON level. MathOptFormat (JuMP) is closest but instance-level only. Our IR is simple, tailored, and easy for LLMs to produce.

## Implementation Steps

### Step 1: Skeleton + IR schema
- `pyproject.toml` — deps: `litellm`, `click`; dev deps: `pytest`, `highspy`, `numpy`, `pyyaml`
- `Makefile` — `make` (pip install -e .[dev]), `make test` (pytest)
- `src/md2mip/ir.py` — dataclasses: `IR`, `SetDef`, `Parameter`, `Variable`, `Objective`, `Constraint`; `from_dict()` factory; `validate()`
- `fixtures/transportation.ir.json` — hand-write from the spec
- `tests/test_ir.py` — round-trip and validation tests

### Step 2: Code generator
- `src/md2mip/codegen.py` — `generate(ir: IR) -> str`
- Expression parser using Python `ast` module (stdlib). Walk the AST to classify names as variables vs parameters (the IR tells us which), extract coefficients, and emit numpy CSR construction code.
- Build iteratively: transportation first (matches spec example), then knapsack (binary), facility location (two var types + linking), lot sizing (lags), assignment, blending
- `tests/test_codegen.py` — fixture IR → generated code → syntax check + structural assertions
- `tests/test_generated.py` — exec generated code with data, assert optimal objective

### Step 3: LLM prompt + integration
- `src/md2mip/prompt.py` — system prompt with IR schema, worked example, notation rules, `"warnings"` field
- `src/md2mip/llm.py` — `parse_model(markdown, model) -> dict` via litellm. Supports any litellm model string. Provider auto-detected from model string. API keys via standard env vars (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) or no key needed for Ollama.
- `src/md2mip/compiler.py` — `compile_to_ir()`, `compile_to_python()`, `run_model()`
- Test against all 6 models, capture good IRs as fixtures

### Step 4: CLI
- `src/md2mip/cli.py` — Click group with `compile` (`-o`, `--ir-only`, `--model`) and `run` (`--data`, `--model`). `--model` accepts any litellm model string (default: `claude-sonnet-4-20250514`). Examples: `--model ollama/qwen3`, `--model gpt-4o`.
- `tests/test_cli.py` — CliRunner smoke tests

### Step 5: Test models + data + end-to-end validation
- Extract 6 models from plan-md2mip.md into `models/*.md`
- Write matching `data/*.yaml` files
- `tests/test_generated.py` — for each fixture IR: generate → exec → assert objective

## Hard Parts

- **Expression parsing in codegen** — use Python `ast` to parse IR expressions (they're valid Python). Walk the AST to decompose linear constraints into variable terms + coefficients + RHS. The IR already declares which names are variables vs parameters, so classification is straightforward. Emit `# TODO` for expressions that don't decompose cleanly.
- **Flat variable indexing** — multiple variable groups (x, y) share one index space. Track offsets carefully.
- **Lag references** — `I[t-1]` in lot sizing. IR must represent boundary conditions clearly (e.g., `I_init` parameter).
- **LLM prompt reliability** — iterative refinement against the 6 test models. Fixture-based testing insulates from variance.

## Verification

1. `make test` — all unit + solver tests pass
2. For each of the 6 models: `md2mip compile models/<model>.md -o /tmp/solver.py && python /tmp/solver.py data/<model>.yaml` produces correct optimal objective
3. Generated scripts run without md2mip installed (only need `highspy numpy pyyaml`)
4. `md2mip compile models/transportation.md --ir-only` outputs valid IR JSON
