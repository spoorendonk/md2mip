"""LLM call via litellm: markdown → IR JSON."""

from __future__ import annotations

import json
import re

import litellm

from md2mip.prompt import SYSTEM_PROMPT
from md2mip.retry import LLMError, litellm_retry

# Re-export for backward compatibility
__all__ = ["LLMError", "DEFAULT_MODEL", "parse_model"]

DEFAULT_MODEL = "claude-sonnet-4-20250514"


def parse_model(markdown: str, model: str = DEFAULT_MODEL) -> dict:
    """Send markdown to LLM and get back IR JSON dict.

    Args:
        markdown: The markdown model description.
        model: Any litellm model string (e.g., "claude-sonnet-4-20250514",
               "ollama/qwen3", "gpt-4o").

    Returns:
        Parsed IR as a dict.

    Raises:
        LLMError: If the API call fails or the response isn't valid JSON.
    """
    response = litellm_retry(
        lambda: litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": markdown},
            ],
            temperature=0,
            max_tokens=4096,
        ),
        model=model,
    )

    content = response.choices[0].message.content

    # Extract JSON from response (handle markdown fences if present)
    content = content.strip()
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
    if m:
        content = m.group(1)

    try:
        return json.loads(content)  # type: ignore[no-any-return]
    except json.JSONDecodeError as e:
        raise LLMError(f"LLM response is not valid JSON: {e}\nResponse:\n{content[:500]}") from e
