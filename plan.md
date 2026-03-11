# md2mip Plan

## Phase 1: Core Compiler ✅

All steps complete. 49 tests pass. Committed as `d66db81`.

- IR schema with dataclasses + validation (parameter/variable index checks, constraint operator checks)
- AST-based codegen: 6 models generate valid Python, solve to correct optima
- LLM integration via litellm with error handling (`LLMError`)
- Click CLI: `compile` (with `--ir-only`, `-o`, `--model`) and `run` (with `--data`)
- Fixture-based testing: unit, codegen syntax, solver correctness, CLI smoke

**Known data corrections from original plan:**
- Transportation optimal = 215 (not 110 — plan's expected value was wrong for the data)
- Facility location optimal = 185 (not 275 — opening only C is cheaper than A+C)
- Blending min_protein = 10% (not 20% — both ingredients < 20% made it infeasible)

## Phase 2: End-to-End LLM Validation (current)

Test that the full pipeline works: markdown → LLM → IR → codegen → solve.

### Steps

1. **LLM integration test**: run `md2mip compile` on each of the 6 model .md files,
   verify the LLM produces IR that passes validation and generates solvable code.
   Mark tests with `@pytest.mark.llm` (skip by default, run with `pytest -m llm`).

2. **Capture good IRs**: when LLM output is correct, save as fixtures to replace
   the hand-written ones. This makes fixture-based tests more realistic.

3. **Prompt refinement**: iterate on `prompt.py` if any model fails to parse correctly.
   The 6 models cover varied notation styles — this is the real stress test.

4. **CLI end-to-end**: `md2mip compile models/transportation.md --ir-only` should
   output valid IR JSON. `md2mip run models/knapsack.md --data data/knapsack.yaml`
   should print the optimal solution.

### Success criteria

- All 6 models: `md2mip compile models/<X>.md -o /tmp/solver.py && python /tmp/solver.py data/<X>.yaml` produces correct optimal
- `md2mip compile models/transportation.md --ir-only` outputs valid IR JSON
- Existing 49 tests still pass
- New LLM integration tests pass (when API key available)

## Phase 3: Extensions (future)

From plan-md2mip.md:
- `md2mip ocr <image.png> -o model.md` — OCR via Claude vision
- `md2mip compile --target mps` — MPS file output
- Multiple data scenarios / batch solve
- Solution report generation
