"""Tests for IR dataclasses."""

import pytest

from md2mip.ir import IR, Constraint, Objective, Parameter, SetDef, Variable
from tests.conftest import load_fixture


class TestIRFromDict:
    def test_transportation_round_trip(self):
        raw = load_fixture("transportation")
        ir = IR.from_dict(raw)
        assert ir.name == "transportation"
        assert set(ir.sets.keys()) == {"I", "J"}
        assert set(ir.parameters.keys()) == {"c", "s", "d"}
        assert set(ir.variables.keys()) == {"x"}
        assert ir.objective.sense == "minimize"
        assert len(ir.constraints) == 2

    def test_round_trip_json(self):
        raw = load_fixture("transportation")
        ir = IR.from_dict(raw)
        json_str = ir.to_json()
        ir2 = IR.from_json(json_str)
        assert ir2.name == ir.name
        assert set(ir2.sets.keys()) == set(ir.sets.keys())

    def test_knapsack(self):
        raw = load_fixture("knapsack")
        ir = IR.from_dict(raw)
        assert ir.name == "knapsack"
        assert ir.variables["x"].type == "binary"
        assert ir.objective.sense == "maximize"

    def test_facility_location(self):
        raw = load_fixture("facility_location")
        ir = IR.from_dict(raw)
        assert set(ir.variables.keys()) == {"x", "y"}
        assert ir.variables["y"].type == "binary"

    def test_lot_sizing(self):
        raw = load_fixture("lot_sizing")
        ir = IR.from_dict(raw)
        assert "T" in ir.sets
        assert ir.variables["z"].type == "binary"
        assert ir.parameters["I_init"].default == 5


class TestIRValidation:
    def test_valid_transportation(self):
        raw = load_fixture("transportation")
        ir = IR.from_dict(raw)
        ir.validate()  # Should not raise

    def test_empty_variables_raises(self):
        ir = IR(objective=Objective(sense="minimize", expression="x"))
        with pytest.raises(ValueError, match="no variables"):
            ir.validate()

    def test_invalid_sense_raises(self):
        ir = IR(
            variables={"x": Variable()},
            objective=Objective(sense="bogus", expression="x"),
        )
        with pytest.raises(ValueError, match="Invalid objective sense"):
            ir.validate()

    def test_empty_constraint_expression_raises(self):
        ir = IR(
            sets={"I": SetDef()},
            variables={"x": Variable(indices=["I"])},
            objective=Objective(sense="minimize", expression="sum(x[i] for i in I)"),
            constraints={"bad": Constraint(expression="")},
        )
        with pytest.raises(ValueError, match="expression is empty"):
            ir.validate()

    def test_unknown_set_in_for_all_raises(self):
        ir = IR(
            sets={"I": SetDef()},
            variables={"x": Variable(indices=["I"])},
            objective=Objective(sense="minimize", expression="sum(x[i] for i in I)"),
            constraints={"bad": Constraint(for_all=["j in Z"], expression="x[j] <= 1")},
        )
        with pytest.raises(ValueError, match="unknown set.*Z"):
            ir.validate()

    def test_unknown_set_in_variable_raises(self):
        ir = IR(
            sets={"I": SetDef()},
            variables={"x": Variable(indices=["Q"])},
            objective=Objective(sense="minimize", expression="x"),
        )
        with pytest.raises(ValueError, match="not a known set"):
            ir.validate()

    def test_unknown_set_in_parameter_raises(self):
        ir = IR(
            sets={"I": SetDef()},
            variables={"x": Variable(indices=["I"])},
            parameters={"c": Parameter(indices=["Z"])},
            objective=Objective(sense="minimize", expression="sum(x[i] for i in I) <= 1"),
            constraints={"c1": Constraint(expression="sum(x[i] for i in I) <= 1")},
        )
        with pytest.raises(ValueError, match="Parameter.*not a known set"):
            ir.validate()

    def test_constraint_missing_comparison_raises(self):
        ir = IR(
            sets={"I": SetDef()},
            variables={"x": Variable(indices=["I"])},
            objective=Objective(sense="minimize", expression="sum(x[i] for i in I)"),
            constraints={"bad": Constraint(expression="sum(x[i] for i in I)")},
        )
        with pytest.raises(ValueError, match="no comparison operator"):
            ir.validate()


class TestAllFixturesValid:
    @pytest.mark.parametrize(
        "name",
        [
            "transportation",
            "knapsack",
            "facility_location",
            "lot_sizing",
            "assignment",
            "blending",
            "capital_budgeting",
            "set_covering",
            "graph_coloring",
            "sudoku",
            "multicommodity_flow",
            "unit_commitment",
            "n_queens",
            "job_shop",
            "tsp_mtz",
        ],
    )
    def test_fixture_validates(self, name):
        raw = load_fixture(name)
        ir = IR.from_dict(raw)
        ir.validate()
