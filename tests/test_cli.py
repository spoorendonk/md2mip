"""CLI smoke tests."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from md2mip.cli import cli
from tests.conftest import load_fixture


class TestCompileCommand:
    def test_compile_ir_only(self, tmp_path):
        """Test --ir-only flag with mocked LLM."""
        fixture = load_fixture("transportation")
        model_file = tmp_path / "model.md"
        model_file.write_text("# Test model")

        with patch("md2mip.compiler.parse_model", return_value=fixture):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "compile", str(model_file), "--ir-only",
            ])
            assert result.exit_code == 0
            assert '"transportation"' in result.output

    def test_compile_to_file(self, tmp_path):
        """Test -o flag."""
        fixture = load_fixture("transportation")
        model_file = tmp_path / "model.md"
        model_file.write_text("# Test model")
        out_file = tmp_path / "solver.py"

        with patch("md2mip.compiler.parse_model", return_value=fixture):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "compile", str(model_file), "-o", str(out_file),
            ])
            assert result.exit_code == 0
            assert out_file.exists()
            content = out_file.read_text()
            assert "import highspy" in content


    def test_compile_passes_model_flag(self, tmp_path):
        """Test --model flag is forwarded to LLM."""
        fixture = load_fixture("transportation")
        model_file = tmp_path / "model.md"
        model_file.write_text("# Test model")

        with patch("md2mip.compiler.parse_model", return_value=fixture) as mock:
            runner = CliRunner()
            result = runner.invoke(cli, [
                "compile", str(model_file), "--ir-only",
                "--model", "ollama/qwen3",
            ])
            assert result.exit_code == 0
            mock.assert_called_once()
            assert mock.call_args[1]["model"] == "ollama/qwen3"

    def test_compile_llm_error(self, tmp_path):
        """Test graceful error when LLM fails."""
        from md2mip.llm import LLMError
        model_file = tmp_path / "model.md"
        model_file.write_text("# Test model")

        with patch("md2mip.compiler.parse_model", side_effect=LLMError("API down")):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "compile", str(model_file), "--ir-only",
            ])
            assert result.exit_code != 0


class TestRunCommand:
    def test_run_requires_data(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "nonexistent.md"])
        assert result.exit_code != 0
