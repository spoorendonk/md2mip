"""Unit tests for OCR module (mocked, no API needed)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from md2mip.ocr import ocr_image


class TestOcr:
    def test_ocr_returns_markdown(self, tmp_path):
        """Mock litellm, verify return value."""
        img = tmp_path / "model.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "# Knapsack\n$$\\max \\sum v_i x_i$$"

        with patch("md2mip.ocr.litellm.completion", return_value=mock_response):
            result = ocr_image(str(img))

        assert "Knapsack" in result
        assert "\\max" in result

    def test_ocr_unsupported_format(self, tmp_path):
        """BMP should raise ValueError."""
        img = tmp_path / "model.bmp"
        img.write_bytes(b"BM" + b"\x00" * 100)

        with pytest.raises(ValueError, match="Unsupported image format"):
            ocr_image(str(img))

    def test_ocr_sends_correct_message_format(self, tmp_path):
        """Verify image_url in messages."""
        img = tmp_path / "model.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "# Model"

        with patch("md2mip.ocr.litellm.completion", return_value=mock_response) as mock_call:
            ocr_image(str(img))

        messages = mock_call.call_args[1]["messages"]

        # User message should contain image_url and text parts
        user_msg = messages[1]
        assert user_msg["role"] == "user"
        content = user_msg["content"]
        assert isinstance(content, list)
        types = {part["type"] for part in content}
        assert "image_url" in types
        assert "text" in types

        # Check base64 data URL
        img_part = [p for p in content if p["type"] == "image_url"][0]
        assert img_part["image_url"]["url"].startswith("data:image/png;base64,")

    def test_ocr_retries_on_rate_limit(self, tmp_path):
        """RateLimitError then success."""
        import litellm as _litellm

        img = tmp_path / "model.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "# Model after retry"

        side_effects = [
            _litellm.RateLimitError(
                message="rate limited",
                model="test",
                llm_provider="test",
            ),
            mock_response,
        ]

        with (
            patch("md2mip.ocr.litellm.completion", side_effect=side_effects),
            patch("md2mip.ocr.time.sleep"),
        ):
            result = ocr_image(str(img))

        assert "after retry" in result
