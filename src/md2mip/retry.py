"""Shared retry logic for litellm API calls."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import litellm

T = TypeVar("T")

MAX_RETRIES = 3
RETRY_BACKOFF = 10  # seconds


class LLMError(Exception):
    """Raised when the LLM call or response parsing fails."""


def litellm_retry(
    fn: Callable[[], T],
    *,
    model: str,
    max_retries: int = MAX_RETRIES,
    backoff: int = RETRY_BACKOFF,
) -> T:
    """Call fn() with retry on rate limits.

    Args:
        fn: Zero-arg callable that makes the litellm API call.
        model: Model string (for error messages).
        max_retries: Maximum number of attempts.
        backoff: Base backoff in seconds (multiplied by attempt number).

    Returns:
        The return value of fn().

    Raises:
        LLMError: On rate limit exhaustion or other API errors.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except litellm.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise LLMError(
                    f"LLM rate limited after {max_retries} retries ({model}): {e}"
                ) from e
        except Exception as e:
            raise LLMError(f"LLM API call failed ({model}): {e}") from e
    raise AssertionError("unreachable")
