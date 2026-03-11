"""End-to-end LLM integration tests.

These tests call the real LLM API and require an API key.
Skip by default: run with `pytest -m llm`.
"""

import logging
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from md2mip.compiler import compile_to_ir, compile_to_python

# Silence litellm's verbose logging
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("litellm").setLevel(logging.WARNING)

MODELS_DIR = Path(__file__).parent.parent / "models"
DATA_DIR = Path(__file__).parent.parent / "data"

# Expected optimal values for each model (verified by hand and fixture tests)
EXPECTED_OPTIMA = {
    "transportation": 215.0,
    "knapsack": 15.0,
    "facility_location": 185.0,
    "assignment": 13.0,
    "blending": 33.33,
}

# Lot sizing doesn't have a single known optimum, just a feasibility bound
LOT_SIZING_UPPER_BOUND = 1500.0


def _try_llm():
    """Check if any LLM provider is available."""
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    if os.environ.get("OPENAI_API_KEY"):
        return True
    # Check Ollama
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1)
        return True
    except Exception:
        return False


@pytest.fixture(autouse=True)
def _rate_limit_pause():
    """Pause between LLM tests to avoid 429s."""
    yield
    time.sleep(5)


requires_llm = pytest.mark.skipif(
    not _try_llm(),
    reason="No LLM provider available (set ANTHROPIC_API_KEY, OPENAI_API_KEY, or run Ollama)",
)


@pytest.mark.llm
@requires_llm
class TestLLMCompileToIR:
    """Test that the LLM produces valid IR from each markdown model."""

    @pytest.mark.parametrize("model_name", [
        "transportation", "knapsack", "facility_location",
        "lot_sizing", "assignment", "blending",
    ])
    def test_compile_produces_valid_ir(self, model_name):
        markdown = (MODELS_DIR / f"{model_name}.md").read_text()
        ir = compile_to_ir(markdown)
        ir.validate()
        assert ir.variables, f"No variables extracted for {model_name}"
        assert ir.constraints, f"No constraints extracted for {model_name}"


@pytest.mark.llm
@requires_llm
class TestLLMEndToEnd:
    """Test full pipeline: markdown → LLM → IR → codegen → solve."""

    @pytest.mark.parametrize("model_name", [
        "transportation", "knapsack", "facility_location",
        "assignment", "blending",
    ])
    def test_solve_correct_optimal(self, model_name):
        markdown = (MODELS_DIR / f"{model_name}.md").read_text()
        code = compile_to_python(markdown)

        data_path = DATA_DIR / f"{model_name}.yaml"
        assert data_path.exists()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                [sys.executable, f.name, str(data_path)],
                capture_output=True, text=True, timeout=60,
            )

        assert result.returncode == 0, f"Solver failed:\n{result.stderr}"

        # Extract objective
        obj = None
        for line in result.stdout.splitlines():
            if line.startswith("Objective:"):
                obj = float(line.split(":")[1].strip())
        assert obj is not None, f"No objective in output:\n{result.stdout}"

        expected = EXPECTED_OPTIMA[model_name]
        assert abs(obj - expected) < 1.0, (
            f"{model_name}: expected ~{expected}, got {obj}"
        )

    def test_lot_sizing_feasible(self):
        markdown = (MODELS_DIR / "lot_sizing.md").read_text()
        code = compile_to_python(markdown)
        data_path = DATA_DIR / "lot_sizing.yaml"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                [sys.executable, f.name, str(data_path)],
                capture_output=True, text=True, timeout=60,
            )

        assert result.returncode == 0, f"Solver failed:\n{result.stderr}"
        for line in result.stdout.splitlines():
            if line.startswith("Objective:"):
                obj = float(line.split(":")[1].strip())
                assert obj < LOT_SIZING_UPPER_BOUND
                return
        pytest.fail(f"No objective in output:\n{result.stdout}")
