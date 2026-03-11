"""Orchestrator: markdown → IR → Python code."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from md2mip.ir import IR
from md2mip.llm import parse_model, DEFAULT_MODEL
from md2mip.codegen import generate


def compile_to_ir(markdown: str, model: str = DEFAULT_MODEL) -> IR:
    """Compile markdown to IR via LLM."""
    raw = parse_model(markdown, model=model)
    ir = IR.from_dict(raw)
    ir.validate()
    return ir


def compile_to_python(markdown: str, model: str = DEFAULT_MODEL) -> str:
    """Compile markdown to standalone Python solver script."""
    ir = compile_to_ir(markdown, model=model)
    return generate(ir)


def compile_ir_to_python(ir: IR) -> str:
    """Compile an existing IR to Python (no LLM call)."""
    return generate(ir)


def run_model(markdown: str, data_path: str, model: str = DEFAULT_MODEL) -> subprocess.CompletedProcess:
    """Compile markdown and immediately run with data."""
    code = compile_to_python(markdown, model=model)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as f:
        f.write(code)
        f.flush()
        return subprocess.run(
            [sys.executable, f.name, data_path],
            capture_output=False,
        )
