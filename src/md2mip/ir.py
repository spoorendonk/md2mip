"""IR dataclasses for MIP model representation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SetDef:
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> SetDef:
        return cls(description=d.get("description", ""))


@dataclass
class Parameter:
    indices: list[str] = field(default_factory=list)
    description: str = ""
    default: Any = None

    @classmethod
    def from_dict(cls, d: dict) -> Parameter:
        return cls(
            indices=d.get("indices", []),
            description=d.get("description", ""),
            default=d.get("default"),
        )


@dataclass
class Variable:
    indices: list[str] = field(default_factory=list)
    type: str = "continuous"
    lower_bound: float | None = 0
    upper_bound: float | None = None
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Variable:
        return cls(
            indices=d.get("indices", []),
            type=d.get("type", "continuous"),
            lower_bound=d.get("lower_bound", 0),
            upper_bound=d.get("upper_bound"),
            description=d.get("description", ""),
        )


@dataclass
class Objective:
    sense: str = "minimize"
    expression: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Objective:
        return cls(
            sense=d.get("sense", "minimize"),
            expression=d.get("expression", ""),
        )

    def validate(self):
        if self.sense not in ("minimize", "maximize"):
            raise ValueError(f"Invalid objective sense: {self.sense!r}")
        if not self.expression:
            raise ValueError("Objective expression is empty")


@dataclass
class Constraint:
    for_all: list[str] = field(default_factory=list)
    expression: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Constraint:
        return cls(
            for_all=d.get("for_all", []),
            expression=d.get("expression", ""),
        )

    def validate(self):
        if not self.expression:
            raise ValueError("Constraint expression is empty")


@dataclass
class IR:
    name: str = ""
    sets: dict[str, SetDef] = field(default_factory=dict)
    parameters: dict[str, Parameter] = field(default_factory=dict)
    variables: dict[str, Variable] = field(default_factory=dict)
    objective: Objective = field(default_factory=Objective)
    constraints: dict[str, Constraint] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> IR:
        return cls(
            name=d.get("name", ""),
            sets={k: SetDef.from_dict(v) for k, v in d.get("sets", {}).items()},
            parameters={k: Parameter.from_dict(v) for k, v in d.get("parameters", {}).items()},
            variables={k: Variable.from_dict(v) for k, v in d.get("variables", {}).items()},
            objective=Objective.from_dict(d.get("objective", {})),
            constraints={k: Constraint.from_dict(v) for k, v in d.get("constraints", {}).items()},
            warnings=d.get("warnings", []),
            data=d.get("data", {}),
        )

    @classmethod
    def from_json(cls, s: str) -> IR:
        return cls.from_dict(json.loads(s))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def validate(self):
        """Validate the IR for consistency."""
        if not self.variables:
            raise ValueError("IR has no variables")
        self.objective.validate()
        for name, c in self.constraints.items():
            try:
                c.validate()
            except ValueError as e:
                raise ValueError(f"Constraint {name!r}: {e}") from e
        # Check that for_all references known sets
        known_sets = set(self.sets)
        for cname, c in self.constraints.items():
            for fa in c.for_all:
                # "i in I" -> check I is a known set
                parts = fa.split(" in ")
                if len(parts) == 2:
                    set_name = parts[1].strip()
                    if set_name not in known_sets:
                        raise ValueError(
                            f"Constraint {cname!r}: for_all references unknown set {set_name!r}"
                        )
        # Check parameter indices reference known sets
        for pname, p in self.parameters.items():
            for idx in p.indices:
                if idx not in known_sets:
                    raise ValueError(f"Parameter {pname!r}: index {idx!r} is not a known set")
        # Check variable indices reference known sets
        for vname, v in self.variables.items():
            for idx in v.indices:
                if idx not in known_sets:
                    raise ValueError(f"Variable {vname!r}: index {idx!r} is not a known set")
        # Check constraint expressions contain a comparison operator
        for cname, c in self.constraints.items():
            expr = c.expression
            if not any(op in expr for op in ("<=", ">=", "==")):
                raise ValueError(
                    f"Constraint {cname!r}: expression has no comparison operator (<=, >=, ==)"
                )
