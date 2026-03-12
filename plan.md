# md2mip Plan

## Phase 1: Core Compiler ✅

All steps complete. 49 tests pass. Committed as `d66db81`.

- IR schema with dataclasses + validation (parameter/variable index checks, constraint operator checks)
- AST-based codegen: 6 models generate valid Python, solve to correct optima
- LLM integration via litellm with error handling (`LLMError`)
- Click CLI: `compile` (with `--ir-only`, `-o`, `--model`) and `run` (with `--data`)
- Fixture-based testing: unit, codegen syntax, solver correctness, CLI smoke

## Phase 2: End-to-End LLM Validation ✅

Committed as `01ffce7`. LLM integration tests for all 6 models.

- `@pytest.mark.llm` tests: compile to valid IR, solve to correct optima
- Rate-limit-aware test fixtures with pause between calls
- Lot sizing feasibility check (no exact optimum, upper bound only)

## Phase 3: OCR + Nasty Models ✅

Committed as `f391495`.

- `md2mip ocr <image> [-o model.md]` — extract math models from images via LLM vision
- 6 nasty/ambiguous model rewrites: sloppy notation, pure prose, table-only, misleading text, trivial edge case
- Rendered-math test images via matplotlib (proper sigmas, subscripts, inequalities)
- Codegen fix for bare variable references and zero-set models
- Compile default output to `out/<stem>_solver.py` with run instructions
- 59 offline tests pass

## Phase 4: Generated Script Enhancements ✅

- `--opt NAME=VALUE` repeatable flag for HiGHS option passthrough
- `_parse_highs_value()` helper converts string values to bool/int/float/str
- Removed `h.silent()` — users control output via `--opt output_flag=false`
- MPS export via `--opt write_model_to_file=true --opt write_model_file=out.mps`

Stretch goals:
- **Round-trip reporting**: format solution back into markdown tables matching input model structure
- **Model diff**: `md2mip diff v1.md v2.md` — compile both to IR, compare structurally, output human-readable diff
- **Parametric sweep**: `--sweep param=start:step:end` in generated scripts, outputs CSV
- **Infeasibility diagnosis**: extract IIS via HiGHS when solver returns infeasible
- **Abstract model library**: save compiled IRs as `.ir.json`, re-compile without LLM
- **Flowty integration**: detect network flow structure in IR → Flowty-based solver
- **Validation mode**: `md2mip validate model.md --data data.yaml --expect-objective 215`
