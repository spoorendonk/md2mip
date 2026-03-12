"""Click CLI: compile, run."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from md2mip.compiler import compile_to_ir, compile_to_python, run_model
from md2mip.llm import DEFAULT_MODEL
from md2mip.ocr import ocr_image


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
        Path(output).write_text(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


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
