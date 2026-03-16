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

## Phase 9: Simple Models + Confidence Report

### 9a. Confidence report feature

Add a warnings/confidence summary printed during `md2mip compile`. The IR already has a `warnings: list[str]` field that the LLM can populate. Surface it:

- **`compiler.py`**: After `compile_to_ir()`, print any `ir.warnings` to stderr
- **`cli.py`**: In `compile` command, after compilation print a summary:
  - `"Parsed: {n} sets, {n} params, {n} vars, {n} constraints"`
  - If `ir.warnings`: print each warning prefixed with `"WARNING: "`
  - If no warnings: `"Confidence: high (no warnings)"`
- **`prompt.py`**: Strengthen the warnings instruction — tell the LLM to flag:
  - Ambiguous variable domains (continuous vs integer vs binary)
  - Missing bounds or unclear constraints
  - Contradictory text vs formulas
  - Assumptions made about notation

### 9b. New models (3 simple ones)

**1. Capital Budgeting** (`capital_budgeting`)
- 6 projects, 3 periods, select at most 3
- Cardinality: `sum(y[p] for p in P) <= max_projects`
- Implication: `y[3] <= y[1]` (project 3 requires project 1)
- Mutual exclusion: `y[4] + y[5] <= 1`
- Budget per period: `sum(cost[p,t] * y[p] for p in P) <= budget[t]`
- Nasty variant: Written as a business memo with vague language ("we can't afford more than three initiatives", "the database migration depends on the cloud move")

**2. Set Covering** (`set_covering`)
- 10 regions, 7 candidate facilities, sparse 0/1 coverage matrix
- Coverage: `sum(a[i,j] * y[j] for j in J) >= 1` for all i
- Minimize: `sum(cost[j] * y[j] for j in J)`
- Nasty variant: Presented as a table-only problem ("which fire stations cover which neighborhoods") with no math at all

**3. Graph Coloring** (`graph_coloring`)
- 6 vertices, 4 colors, ~8 edges
- Binary: `x[v,k]` (vertex v gets color k)
- Assignment: `sum(x[v,k] for k in K) == 1`
- Conflict: `x[u,k] + x[v,k] <= 1` for edges (u,v)
- Minimize colors: `sum(used[k] for k in K)` with `x[v,k] <= used[k]`
- Nasty variant: Described as a radio frequency assignment problem ("adjacent towers can't use the same channel")

### 9c. For each model
- `models/<name>.md` — clean markdown with LaTeX math
- `models/nasty_<name>.md` — ambiguous/sloppy variant
- `data/<name>.yaml` — small instance, hand-verified optimal
- `fixtures/<name>.ir.json` — hand-crafted expected IR
- Image generation: add to `tests/generate_test_images.py` (both plain + rendered)
- Tests: add to `test_ir.py`, `test_codegen.py`, `test_generated.py`, `test_llm_integration.py`

### Files to modify
- `src/md2mip/cli.py` — confidence report in compile command
- `src/md2mip/prompt.py` — strengthen warnings instructions
- `tests/generate_test_images.py` — add new models
- `tests/test_ir.py` — add to parametrize
- `tests/test_codegen.py` — add to parametrize
- `tests/test_generated.py` — add test classes
- `tests/test_llm_integration.py` — add to EXPECTED_OPTIMA + parametrize

### Verify
`make test && make lint && make typecheck`

---

## Phase 10: Multi-Period + Network Models

### New models (3)

**4. Unit Commitment** (`unit_commitment`)
- 3 generators, 6 time periods
- Vars: `p[g,t]` (power output), `u[g,t]` (on/off binary), `v[g,t]` (startup binary)
- Ramp-up: `p[g,t] - p[g,t-1] <= ramp_up[g]`
- Min/max output: `p_min[g] * u[g,t] <= p[g,t]`, `p[g,t] <= p_max[g] * u[g,t]`
- Startup logic: `v[g,t] >= u[g,t] - u[g,t-1]`
- Demand: `sum(p[g,t] for g in G) >= demand[t]`
- **New constructs:** ramp-rate difference constraints, startup coupling, param*binary bounding continuous
- Nasty variant: Power plant operator's notes with informal ramp descriptions ("Unit B can't increase more than 30MW per hour")

**5. Multi-Commodity Flow** (`multicommodity_flow`)
- 4 nodes, ~6 arcs, 2 commodities
- Vars: `flow[i,j,k]` — 3-index
- Flow conservation: `sum(flow[i,j,k] for j out) - sum(flow[j,i,k] for j in) == supply[i,k]`
- Shared capacity: `sum(flow[i,j,k] for k in K) <= capacity[i,j]`
- **New constructs:** 3-index variables, difference-of-sums, shared capacity
- Nasty variant: Drawn as a network diagram description ("pipes carry oil and gas, each pipe has a max throughput")

**6. Sudoku** (`sudoku`)
- 4x4 mini-sudoku (sets 1..4), ~6 given clues
- Vars: `x[i,j,k]` binary — 3-index
- One per cell: `sum(x[i,j,k] for k in K) == 1`
- Row/col/block uniqueness via == 1 constraints
- Objective: `minimize 0` (pure feasibility)
- **New constructs:** pure feasibility, 3-index binary, all-different
- Nasty variant: Just a partially-filled grid image, minimal text ("solve this puzzle")

### Codegen changes likely needed
- 3D array loading in `_load_data` for 3-index params
- `minimize 0` objective handling (constant objective)
- Ramp constraints: existing lag machinery from lot_sizing should handle `t-1` patterns
- `param * binary_var` products (e.g., `p_min[g] * u[g,t]`) in constraint expressions — may need `_parse_product` to handle param*var on constraint RHS

### For each model
Same deliverables as Phase 9: markdown, nasty variant, data, fixture, images, tests.

### Verify
`make test && make lint && make typecheck`

---

## Phase 11: Combinatorial + Scheduling Models

### New models (3)

**7. N-Queens** (`n_queens`)
- N=6 board
- Vars: `x[i,j]` binary (queen at row i, col j)
- One per row/col: `sum(x[i,j] for j in J) == 1`
- Diagonal conflicts: constraint pairs for same-diagonal cells
- Objective: feasibility (maximize `sum(x[i,j])` or dummy)
- **New constructs:** diagonal conflict constraints, data-driven pair exclusion
- Nasty variant: Described as "place 6 non-attacking rooks on a chess board where diagonals also matter"

**8. Job Shop Scheduling** (`job_shop`)
- 3 jobs, 3 machines, known optimal makespan
- Vars: `start[j,m]` continuous, `z[j1,j2,m]` binary ordering
- Precedence: `start[j,m2] >= start[j,m1] + duration[j,m1]`
- Disjunctive Big-M: `start[j1,m] + duration[j1,m] <= start[j2,m] + M*(1-z[j1,j2,m])`
- Makespan: `C_max >= start[j,last_m] + duration[j,last_m]`
- **New constructs:** Big-M disjunctive, makespan auxiliary variable, continuous scheduling vars
- Nasty variant: Factory floor manager's description ("Job A needs welding then painting then assembly, Job B needs...")

**9. TSP (MTZ)** (`tsp_mtz`)
- 5 cities, distance matrix
- Vars: `x[i,j]` binary (edge), `u[i]` continuous (visit order, 1..n)
- Degree: `sum(x[i,j] for j in J) == 1` and `sum(x[j,i] for j in J) == 1`
- MTZ: `u[i] - u[j] + n*x[i,j] <= n-1` for i,j >= 2
- **New constructs:** order variables with bounds, MTZ coupling binary+continuous
- Nasty variant: Delivery driver's problem ("visit these 5 addresses and return home, here are the drive times")

### Codegen changes likely needed
- Big-M expressions: `M*(1-z[i,j])` needs codegen to handle `1 - var` — the `_parse_product` / `_extract_linear_terms` would need to recognize this as `-M*z + M` (variable term + constant)
- Makespan via auxiliary: `C_max >= expr` is a standard >= constraint, should work
- MTZ constraint `u[i] - u[j] + n*x[i,j] <= n-1`: mixed continuous+binary terms — should work with existing term extraction

### For each model
Same deliverables as previous phases.

### Verify
`make test && make lint && make typecheck`
Full LLM integration: `make test-llm`

---

## Image Generation Strategy

For each new model, add to `tests/generate_test_images.py`:
- `rendered_<name>.png` — proper math rendering via matplotlib
- Also add to OCR LLM integration tests in `test_llm_integration.py`

For nasty variants, consider generating "photo-style" images (noisy, rotated) to test OCR robustness.

## Summary

| Phase | Models | Key new constructs |
|-------|--------|--------------------|
| 9 | capital_budgeting, set_covering, graph_coloring + confidence report | Cardinality, implication, mutual exclusion, conflict pairs, color-usage linking |
| 10 | unit_commitment, multicommodity_flow, sudoku | Ramp rates, 3-index vars, startup coupling, pure feasibility, all-different |
| 11 | n_queens, job_shop, tsp_mtz | Diagonal conflicts, Big-M disjunctive, MTZ subtour elimination, makespan |
