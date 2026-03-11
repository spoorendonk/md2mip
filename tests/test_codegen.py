"""Tests for code generation."""

import ast as python_ast
import pytest

from md2mip.ir import IR
from md2mip.codegen import generate
from tests.conftest import load_fixture


class TestCodegenSyntax:
    """Generated code should be valid Python."""

    @pytest.mark.parametrize("name", [
        "transportation", "knapsack", "facility_location",
        "assignment", "blending", "lot_sizing",
    ])
    def test_generates_valid_python(self, name):
        raw = load_fixture(name)
        ir = IR.from_dict(raw)
        code = generate(ir)
        # Should parse as valid Python
        python_ast.parse(code)

    @pytest.mark.parametrize("name", [
        "transportation", "knapsack", "facility_location",
        "assignment", "blending", "lot_sizing",
    ])
    def test_has_required_functions(self, name):
        raw = load_fixture(name)
        ir = IR.from_dict(raw)
        code = generate(ir)
        assert "def load_data(" in code
        assert "def build_model(" in code
        assert "def solve_and_report(" in code
        assert 'if __name__ == "__main__"' in code

    @pytest.mark.parametrize("name", [
        "transportation", "knapsack", "facility_location",
        "assignment", "blending", "lot_sizing",
    ])
    def test_has_constraint_functions(self, name):
        raw = load_fixture(name)
        ir = IR.from_dict(raw)
        code = generate(ir)
        for cname in ir.constraints:
            assert f"def setup_{cname}_constraints(" in code


class TestCodegenStructure:
    def test_transportation_imports(self):
        raw = load_fixture("transportation")
        ir = IR.from_dict(raw)
        code = generate(ir)
        assert "import highspy" in code
        assert "import numpy as np" in code
        assert "import yaml" in code

    def test_transportation_no_md2mip_import(self):
        raw = load_fixture("transportation")
        ir = IR.from_dict(raw)
        code = generate(ir)
        assert "import md2mip" not in code
        assert "from md2mip" not in code

    def test_binary_variables_set_integrality(self):
        raw = load_fixture("knapsack")
        ir = IR.from_dict(raw)
        code = generate(ir)
        assert "kInteger" in code
