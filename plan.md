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

## Phase 5: Tooling — ruff + mypy ✅

Add linting, formatting, and type checking. Zero risk to existing logic.

### Steps

1. Add `ruff` and `mypy` to `[project.optional-dependencies] dev` in `pyproject.toml`
2. Add config to `pyproject.toml`:
   ```toml
   [tool.ruff]
   line-length = 100
   target-version = "py310"

   [tool.ruff.lint]
   select = ["E", "F", "W", "I", "UP", "B", "SIM"]

   [tool.mypy]
   python_version = "3.10"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = false
   ```
3. Add Makefile targets: `lint`, `fmt`, `typecheck`
4. Run `ruff format`, then `ruff check --fix` — fix auto-fixable issues
5. Run `mypy src/` — fix errors (add `# type: ignore` for litellm externals as needed)
6. `make test` — all 74 tests still pass

### Files
- `pyproject.toml` — deps + config
- `Makefile` — new targets

### Verify
`make lint && make typecheck && make test`

## Phase 6: Extract shared retry helper ✅

Deduplicate identical retry-with-backoff pattern from `llm.py` and `ocr.py`.

### Steps

1. Create `src/md2mip/retry.py` with:
   ```python
   def litellm_retry(fn: Callable[[], T], *, model: str,
                     max_retries: int = 3, backoff: int = 10) -> T:
   ```
   Catches `litellm.RateLimitError`, sleeps with linear backoff, raises `LLMError` on exhaustion or other exceptions.
2. Move `MAX_RETRIES`, `RETRY_BACKOFF` constants to `retry.py`
3. Refactor `llm.py:parse_model` — replace retry loop with `litellm_retry(lambda: litellm.completion(...))`
4. Refactor `ocr.py:ocr_image` — same pattern
5. Add `tests/test_retry.py` — mock RateLimitError, verify retry count and backoff
6. `make test && make lint && make typecheck`

### Files
- `src/md2mip/retry.py` (new)
- `src/md2mip/llm.py` — simplify
- `src/md2mip/ocr.py` — simplify
- `tests/test_retry.py` (new)

### Verify
Existing `test_ocr.py` retry test + new `test_retry.py` + all 74 tests pass

## Phase 7: Consolidate `_extract_linear_terms*` variants ✅

The three functions (`_extract_linear_terms`, `_extract_linear_terms_with_lags`,
`_extract_linear_terms_literal`) share ~80% logic. Merge into one. **Medium risk** — touches core codegen.

### Steps

1. Define a `LinearTerm` namedtuple:
   ```python
   class LinearTerm(NamedTuple):
       coeff: str
       var_name: str
       var_indices: list[str]
       iterators: list[tuple[str, str]]  # empty when N/A
       lag: int  # 0 when no lag
   ```
2. Create single `_extract_linear_terms(expr_str, ir, *, mode="normal")` where mode is `"normal"` | `"with_lags"` | `"literal"`:
   - `"normal"`: handles `sum()`, parses iterators, lag=0
   - `"with_lags"`: no `sum()`, parses lag from indices
   - `"literal"`: no `sum()`, no lag, iterators=[]
3. Update 4 call sites to use new function + destructure `LinearTerm`
4. Delete old `_extract_linear_terms_with_lags` and `_extract_linear_terms_literal`
5. `make test` — all tests must pass (especially `test_codegen.py` + `test_generated.py`)

### Files
- `src/md2mip/codegen.py` — consolidate + `LinearTerm`

### Verify
All 74 tests pass. `make lint && make typecheck`

## Phase 8: Minor fixes ✅

Small, isolated fixes. Low risk.

### Steps

1. **Temp file race** (`compiler.py:37,55`): Use `delete=False` + manual cleanup:
   ```python
   f = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
   try:
       f.write(code)
       f.close()
       return subprocess.run([sys.executable, f.name, data_path], ...)
   finally:
       Path(f.name).unlink(missing_ok=True)
   ```
2. **`_negate` fragility** (`codegen.py:855`): Use AST-based negation instead of string prefix matching. Parse coeff with `ast.parse`, wrap in `ast.UnaryOp(ast.USub())`, `ast.unparse`.
3. **Remove `_var_layout`** (`codegen.py:29-33`): Only called once, returns unused `offset_expr`. Inline as `for vname, var in ir.variables.items():` at the sole call site (line 121).
4. `make test && make lint && make typecheck`

### Files
- `src/md2mip/compiler.py` — tempfile fix
- `src/md2mip/codegen.py` — `_negate` fix + `_var_layout` removal

### Verify
All tests pass
