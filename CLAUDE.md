# md2mip

Markdown → MIP: compiles natural-language optimization models
into standalone solver CLIs (Python + HiGHS) via an LLM-generated IR.

## Quick Reference

```bash
make              # create venv, install deps (run first — all other targets depend on it)
make test         # offline tests (no LLM)
make test-llm     # LLM integration tests (needs API key)
make lint         # ruff check
make fmt          # ruff format
make typecheck    # mypy
```

## Architecture

```
markdown → (LLM) → IR (JSON) → codegen → solver CLI (Python + HiGHS)
image    → (OCR) → markdown → …
```

Key files:
- `src/md2mip/codegen.py` — IR → Python code generation (core)
- `src/md2mip/compiler.py` — orchestrator: markdown → IR → Python
- `src/md2mip/ir.py` — IR dataclasses (Variable, Constraint, Objective, etc.)
- `src/md2mip/llm.py` — LLM calls (litellm)
- `tests/conftest.py` — shared test helpers; `FIXTURES_DIR`, `DATA_DIR`, `load_fixture()`
- `fixtures/` — IR JSON fixtures for each model
- `data/` — YAML/JSON data files for each model

## Testing

- `@pytest.mark.llm` — tests requiring LLM API (skipped by default)
- `@pytest.mark.solver` — tests requiring HiGHS (run by default)
- Fixtures: `fixtures/<model>.ir.json` loaded via `load_fixture("<model>")`
- Data: `data/<model>.yaml` or `data/<model>.json`
- Models with full coverage: knapsack, transportation, blending, etc.

## Pre-commit gate

Always run before committing: `make fmt && make lint && make test && make typecheck`
Don't commit formatting separately — run `make fmt` first, then commit everything together.

## Codegen invariant

`codegen.py` generates Python code as strings. When refactoring codegen,
the generated solver output must remain functionally identical — verify
by running `make test` which exercises all model types (single constraint,
loop constraint, lag constraint, Big-M, etc.).

## Output contract

Generated solver stdout format is a machine-parseable contract:
```
Status: optimal|infeasible|<status>
Objective: <float>
Solution:
  var[label] = <float>
```
Do not change this format without updating tests and CLI docs.

## Self-review

Run `/review` on your own PRs before requesting merge.
Fix issues found before asking the user.

## Git

- Never commit directly to `main`. Always feature branches.
- Linear history only (squash-merge or rebase-merge).

## Workflow: Plan → Grind

Every task has two phases. Do not skip planning.

### Plan (default)

When given a task, **plan first**: investigate the code, propose an approach,
discuss with the user. Wait for approval before implementing (e.g. "grind", "go", "do it").

### Grind (on approval)

Execute autonomously. Build, test, fix, repeat until green.
Self-review, then fullgate: branch, PR, sync main, push.
Progress lives in files and git — not in your context window.

Only pause and ask a human when:
- A fix requires changing the public API or architecture
- You discover a bug in unrelated code you shouldn't touch
- You're stuck after multiple failed attempts

### Fullgate

Also runs standalone when user says **"fullgate"**:
branch → PR → sync (merge main **into** feature branch) → tests → docs →
push → review → build → test → push fixes → squash-merge → delete branch

### Claiming Work (GitHub)

- `gh issue edit <N> --add-label agent-wip` when starting on an issue or PR
- Check for `agent-wip` label before picking up work
- Remove label and close/merge when done

### Teams

For independent sub-tasks, launch a team. Each teammate works in its own
worktree. Lead integrates: merge, resolve conflicts, build/test the result.
