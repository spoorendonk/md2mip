"""Generate data YAML templates from IR metadata."""

from __future__ import annotations

from md2mip.ir import IR


def generate_data_template(ir: IR) -> str:
    """Generate a YAML data file from IR.

    When ``ir.data`` is populated, writes a complete YAML with actual values.
    When ``ir.data`` is empty, writes a commented template showing the schema.
    """
    if ir.data:
        return _complete_yaml(ir)
    return _template_yaml(ir)


def _complete_yaml(ir: IR) -> str:
    """Generate a YAML file with actual values from ir.data."""
    lines = [f"# Data for {ir.name} model"]
    for sname, sdef in ir.sets.items():
        val = ir.data.get(sname, [])
        comment = f"  # {sdef.description}" if sdef.description else ""
        lines.append(f"{sname}: {_yaml_value(val)}{comment}")
    for pname, param in ir.parameters.items():
        val = ir.data.get(pname)
        if val is None:
            continue
        comment = _param_comment(pname, param, ir)
        lines.append(f"{pname}: {_yaml_value(val)}{comment}")
    return "\n".join(lines) + "\n"


def _template_yaml(ir: IR) -> str:
    """Generate a commented YAML template showing the schema."""
    lines = [f"# Data template for {ir.name} model"]
    lines.append(f"# Fill in values and pass as: python out/{ir.name}_solver.py data.yaml")
    for sname, sdef in ir.sets.items():
        desc = f"  # {sdef.description}" if sdef.description else ""
        lines.append(f"{sname}: []{desc}")
    for pname, param in ir.parameters.items():
        comment = _param_comment(pname, param, ir)
        if param.indices:
            lines.append(f"{pname}: []{comment}")
        elif param.default is not None:
            lines.append(f"{pname}: {param.default}{comment}")
        else:
            lines.append(f"{pname}: 0{comment}")
    return "\n".join(lines) + "\n"


def _param_comment(pname: str, param, ir: IR) -> str:
    """Build a comment string for a parameter."""
    parts = []
    if param.indices:
        index_desc = " x ".join(param.indices)
        parts.append(f"indexed by {index_desc}")
    elif not param.indices:
        parts.append("scalar")
    if param.description:
        parts.append(param.description)
    if parts:
        return "  # " + ": ".join(parts)
    return ""


def _yaml_value(val) -> str:
    """Format a Python value as inline YAML."""
    if isinstance(val, list):
        if val and isinstance(val[0], list):
            # Nested list: use YAML block style
            inner = "\n".join(f"  - {_yaml_value(row)}" for row in val)
            return "\n" + inner
        items = ", ".join(_yaml_scalar(v) for v in val)
        return f"[{items}]"
    return _yaml_scalar(val)


def _yaml_scalar(val) -> str:
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return str(val)
