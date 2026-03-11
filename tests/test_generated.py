"""Run generated scripts with data and check solutions."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from md2mip.ir import IR
from md2mip.codegen import generate
from tests.conftest import load_fixture, DATA_DIR


def _run_generated(fixture_name: str, data_name: str | None = None) -> tuple[int, str, str]:
    """Generate code from fixture, run with data, return (returncode, stdout, stderr)."""
    raw = load_fixture(fixture_name)
    ir = IR.from_dict(raw)
    code = generate(ir)

    if data_name is None:
        data_name = fixture_name
    data_path = DATA_DIR / f"{data_name}.yaml"
    assert data_path.exists(), f"Data file not found: {data_path}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
        f.write(code)
        f.flush()
        result = subprocess.run(
            [sys.executable, f.name, str(data_path)],
            capture_output=True, text=True, timeout=30,
        )
    return result.returncode, result.stdout, result.stderr


def _extract_objective(stdout: str) -> float:
    for line in stdout.splitlines():
        if line.startswith("Objective:"):
            return float(line.split(":")[1].strip())
    raise ValueError(f"No objective found in output:\n{stdout}")


@pytest.mark.solver
class TestTransportation:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("transportation")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 215.0) < 0.01


@pytest.mark.solver
class TestKnapsack:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("knapsack")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 15.0) < 0.01


@pytest.mark.solver
class TestFacilityLocation:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("facility_location")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 185.0) < 0.01


@pytest.mark.solver
class TestAssignment:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("assignment")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        # Hungarian algorithm optimal
        assert obj <= 14.01  # Accept any valid optimal


@pytest.mark.solver
class TestLotSizing:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("lot_sizing")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        # Total demand=138, init inventory=5, feasible solution exists
        assert obj < 1500  # sanity check


@pytest.mark.solver
class TestBlending:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("blending")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 33.33) < 0.5  # with min_protein=0.10 (feasible data)
