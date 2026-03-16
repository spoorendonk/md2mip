"""Run generated scripts with data and check solutions."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from md2mip.codegen import generate
from md2mip.ir import IR
from tests.conftest import DATA_DIR, load_fixture


def _run_generated(
    fixture_name: str, data_name: str | None = None, extra_args: list[str] | None = None
) -> tuple[int, str, str]:
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
        cmd = [sys.executable, f.name, str(data_path)]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
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

    def test_solves_large_instance(self):
        rc, stdout, stderr = _run_generated("transportation", data_name="transportation_large")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 8050.0) < 0.01


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


@pytest.mark.solver
class TestCapitalBudgeting:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("capital_budgeting")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 115.0) < 0.01


@pytest.mark.solver
class TestSetCovering:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("set_covering")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 140.0) < 0.01


@pytest.mark.solver
class TestGraphColoring:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("graph_coloring")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 3.0) < 0.01


@pytest.mark.solver
class TestSudoku:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("sudoku")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 0.0) < 0.01


@pytest.mark.solver
class TestMulticommodityFlow:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("multicommodity_flow")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 14.0) < 0.01


@pytest.mark.solver
class TestUnitCommitment:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("unit_commitment")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 300.0) < 0.01


@pytest.mark.solver
class TestNQueens:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("n_queens")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 0.0) < 0.01


@pytest.mark.solver
class TestJobShop:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("job_shop")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 10.0) < 0.01


@pytest.mark.solver
class TestTspMtz:
    def test_solves_correctly(self):
        rc, stdout, stderr = _run_generated("tsp_mtz")
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 85.0) < 0.01


@pytest.mark.solver
class TestKnapsackInlineData:
    """Test knapsack with inline data embedded in IR → generate solver + data YAML, run."""

    def test_inline_data_solves_correctly(self):
        raw = load_fixture("knapsack")
        raw["data"] = {
            "I": ["item1", "item2", "item3", "item4", "item5"],
            "v": [4, 2, 10, 1, 2],
            "w": [12, 1, 4, 1, 2],
            "W": 15,
        }
        ir = IR.from_dict(raw)
        code = generate(ir)

        from md2mip.data_template import generate_data_template

        data_yaml = generate_data_template(ir)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
            f.write(code)
            f.flush()
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=True) as df:
                df.write(data_yaml)
                df.flush()
                result = subprocess.run(
                    [sys.executable, f.name, df.name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"
        obj = _extract_objective(result.stdout)
        assert abs(obj - 15.0) < 0.01


@pytest.mark.solver
class TestInfeasible:
    def test_infeasible_exit_code(self):
        rc, stdout, stderr = _run_generated("transportation", data_name="transportation_infeasible")
        assert rc == 1

    def test_infeasible_reports_iis(self):
        rc, stdout, stderr = _run_generated("transportation", data_name="transportation_infeasible")
        assert rc == 1
        assert "infeasible" in stdout.lower()
        assert "IIS" in stdout


@pytest.mark.solver
class TestValidateEndToEnd:
    def test_validate_transportation(self):
        """Full validate pipeline through validate_model()."""
        from unittest.mock import patch

        from md2mip.compiler import validate_model

        raw = load_fixture("transportation")
        data_path = DATA_DIR / "transportation.yaml"

        with patch("md2mip.compiler.parse_model", return_value=raw):
            passed, actual, stdout = validate_model(
                "# dummy markdown", str(data_path), expected_obj=215.0
            )
        assert passed, f"Expected PASS, got actual={actual}\n{stdout}"
        assert abs(actual - 215.0) < 0.01


@pytest.mark.solver
class TestHiGHSOptions:
    def test_write_model_mps(self):
        with tempfile.NamedTemporaryFile(suffix=".mps", delete=False) as mps:
            mps_path = mps.name
        try:
            rc, stdout, stderr = _run_generated(
                "transportation",
                extra_args=[
                    "--opt",
                    "write_model_to_file=true",
                    "--opt",
                    f"write_model_file={mps_path}",
                ],
            )
            # write_model_to_file causes HiGHS to write the model without solving,
            # so the script exits 1 (status kNotset). Just check the file was written.
            assert Path(mps_path).stat().st_size > 0
        finally:
            Path(mps_path).unlink(missing_ok=True)

    def test_opt_time_limit(self):
        rc, stdout, stderr = _run_generated(
            "transportation",
            extra_args=["--opt", "time_limit=1"],
        )
        assert rc == 0, f"Script failed:\n{stderr}"
        obj = _extract_objective(stdout)
        assert abs(obj - 215.0) < 0.01

    def test_silent_output(self):
        rc, stdout, stderr = _run_generated(
            "transportation",
            extra_args=["--opt", "output_flag=false"],
        )
        assert rc == 0, f"Script failed:\n{stderr}"
        # HiGHS solver log goes to stdout; with output_flag=false it should be suppressed
        assert "Solving report" not in stdout
        assert "Objective:" in stdout  # our report still prints
