"""Click CLI: compile, run."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from md2mip.compiler import compile_to_ir, compile_to_python, run_model, validate_model
from md2mip.llm import DEFAULT_MODEL
from md2mip.ocr import ocr_image

OUT_DIR = Path("out")


@click.group()
def cli():
    """md2mip — compile Markdown/LaTeX MIP models into standalone Python solver scripts."""


@cli.command()
@click.argument("model_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file path")
@click.option("--ir-only", is_flag=True, help="Output IR JSON instead of Python")
@click.option("--model", default=DEFAULT_MODEL, help=f"LLM model string (default: {DEFAULT_MODEL})")
def compile(model_path: str, output: str | None, ir_only: bool, model: str):
    """Compile a markdown model to a standalone Python solver script."""
    markdown = Path(model_path).read_text()

    if ir_only:
        ir = compile_to_ir(markdown, model=model)
        result = ir.to_json()
    else:
        result = compile_to_python(markdown, model=model)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result)
        click.echo(f"Written to {output}")
    elif ir_only:
        click.echo(result)
    else:
        stem = Path(model_path).stem
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUT_DIR / f"{stem}_solver.py"
        out_path.write_text(result)
        click.echo(f"Written to {out_path}")
        click.echo(f"Run:    python {out_path} <data.yaml>")


@cli.command()
@click.argument("model_path", type=click.Path(exists=True))
@click.option("--data", required=True, type=click.Path(exists=True), help="Data file (YAML or JSON)")
@click.option("--model", default=DEFAULT_MODEL, help=f"LLM model string (default: {DEFAULT_MODEL})")
def run(model_path: str, data: str, model: str):
    """Compile and immediately run a model with data."""
    markdown = Path(model_path).read_text()
    result = run_model(markdown, data, model=model)
    sys.exit(result.returncode)


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file path")
@click.option("--model", default=DEFAULT_MODEL, help=f"LLM model string (default: {DEFAULT_MODEL})")
def ocr(image_path: str, output: str | None, model: str):
    """Extract a math model from an image using LLM vision."""
    result = ocr_image(image_path, model=model)

    if output:
        Path(output).write_text(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@cli.command()
@click.argument("model_path", type=click.Path(exists=True))
@click.option("--data", required=True, type=click.Path(exists=True), help="Data file (YAML or JSON)")
@click.option("--expect-objective", required=True, type=float, help="Expected objective value")
@click.option("--tol", default=0.01, type=float, help="Absolute tolerance (default: 0.01)")
@click.option("--model", default=DEFAULT_MODEL, help=f"LLM model string (default: {DEFAULT_MODEL})")
def validate(model_path: str, data: str, expect_objective: float, tol: float, model: str):
    """Validate a model: compile, run, check objective value."""
    markdown = Path(model_path).read_text()
    passed, actual, stdout = validate_model(markdown, data, expect_objective, tol=tol, model=model)
    if passed:
        click.echo(f"PASS (expected={expect_objective}, actual={actual:.4f}, tol={tol})")
    else:
        actual_str = f"{actual:.4f}" if actual is not None else "N/A"
        click.echo(f"FAIL (expected={expect_objective}, actual={actual_str}, tol={tol})")
        sys.exit(1)
