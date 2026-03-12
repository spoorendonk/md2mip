"""CLI smoke tests."""

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


class TestOcrCommand:
    def test_ocr_to_stdout(self, tmp_path):
        """Mock ocr_image, check stdout."""
        img_file = tmp_path / "model.png"
        img_file.write_bytes(b"\x89PNG" + b"\x00" * 100)

        with patch("md2mip.cli.ocr_image", return_value="# Extracted Model") as mock:
            runner = CliRunner()
            result = runner.invoke(cli, ["ocr", str(img_file)])
            assert result.exit_code == 0
            assert "Extracted Model" in result.output
            mock.assert_called_once()

    def test_ocr_to_file(self, tmp_path):
        """Mock ocr_image, check file written."""
        img_file = tmp_path / "model.png"
        img_file.write_bytes(b"\x89PNG" + b"\x00" * 100)
        out_file = tmp_path / "model.md"

        with patch("md2mip.cli.ocr_image", return_value="# Extracted Model"):
            runner = CliRunner()
            result = runner.invoke(cli, ["ocr", str(img_file), "-o", str(out_file)])
            assert result.exit_code == 0
            assert out_file.exists()
            assert "Extracted Model" in out_file.read_text()

    def test_ocr_passes_model_flag(self, tmp_path):
        """Verify --model forwarded."""
        img_file = tmp_path / "model.png"
        img_file.write_bytes(b"\x89PNG" + b"\x00" * 100)

        with patch("md2mip.cli.ocr_image", return_value="# Model") as mock:
            runner = CliRunner()
            result = runner.invoke(cli, [
                "ocr", str(img_file), "--model", "gpt-4o",
            ])
            assert result.exit_code == 0
            mock.assert_called_once_with(str(img_file), model="gpt-4o")


class TestRunCommand:
    def test_run_requires_data(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["run", "nonexistent.md"])
        assert result.exit_code != 0
