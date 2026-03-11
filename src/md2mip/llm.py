"""LLM call via litellm: markdown → IR JSON."""

from __future__ import annotations

import json
import re

import litellm

from md2mip.prompt import SYSTEM_PROMPT

DEFAULT_MODEL = "claude-sonnet-4-20250514"


class LLMError(Exception):
    """Raised when the LLM call or response parsing fails."""


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
    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": markdown},
            ],
            temperature=0,
            max_tokens=4096,
        )
    except Exception as e:
        raise LLMError(f"LLM API call failed ({model}): {e}") from e

    content = response.choices[0].message.content

    # Extract JSON from response (handle markdown fences if present)
    content = content.strip()
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
    if m:
        content = m.group(1)

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMError(
            f"LLM response is not valid JSON: {e}\nResponse:\n{content[:500]}"
        ) from e
