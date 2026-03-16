"""Tests for shared retry logic."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import litellm
import pytest

from md2mip.retry import LLMError, litellm_retry


class TestLitellmRetry:
    def test_success_on_first_try(self):
        result = litellm_retry(lambda: "ok", model="test")
        assert result == "ok"

    def test_retries_on_rate_limit(self):
        fn = MagicMock(
            side_effect=[
                litellm.RateLimitError(message="rate limited", model="test", llm_provider="test"),
                "ok",
            ]
        )
        with patch("md2mip.retry.time.sleep"):
            result = litellm_retry(fn, model="test")
        assert result == "ok"
        assert fn.call_count == 2

    def test_raises_after_max_retries(self):
        fn = MagicMock(
            side_effect=litellm.RateLimitError(
                message="rate limited", model="test", llm_provider="test"
            )
        )
        with patch("md2mip.retry.time.sleep"), pytest.raises(LLMError, match="rate limited"):
            litellm_retry(fn, model="test", max_retries=2)
        assert fn.call_count == 2

    def test_raises_immediately_on_other_error(self):
        fn = MagicMock(side_effect=RuntimeError("boom"))
        with pytest.raises(LLMError, match="boom"):
            litellm_retry(fn, model="test")
        assert fn.call_count == 1

    def test_backoff_timing(self):
        fn = MagicMock(
            side_effect=[
                litellm.RateLimitError(message="rate limited", model="test", llm_provider="test"),
                litellm.RateLimitError(message="rate limited", model="test", llm_provider="test"),
                "ok",
            ]
        )
        with patch("md2mip.retry.time.sleep") as mock_sleep:
            litellm_retry(fn, model="test", backoff=5)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(5)  # attempt 0: 5 * 1
        mock_sleep.assert_any_call(10)  # attempt 1: 5 * 2
