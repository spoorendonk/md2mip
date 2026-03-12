"""OCR: extract math models from images via LLM vision."""

from __future__ import annotations

import base64
import mimetypes
import time
from pathlib import Path

import litellm

from md2mip.llm import DEFAULT_MODEL, MAX_RETRIES, RETRY_BACKOFF, LLMError

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

OCR_SYSTEM_PROMPT = """\
You are a mathematical model extraction assistant.
Given an image of a mathematical optimization model, extract it into clean markdown.

Rules:
- Use LaTeX math notation: $...$ for inline math, $$...$$ for display math
- Use markdown headers, tables, and lists for structure
- Preserve all mathematical symbols exactly (summations, subscripts, sets, etc.)
- Use \\sum, \\forall, \\in, \\leq, \\geq for math operators
- Use x_i or x_{ij} for subscripted variables
- Use \\{0, 1\\} for binary domains
- Clearly separate sets, parameters, variables, objective, and constraints
- Output ONLY the markdown model, no commentary or explanations
"""


def ocr_image(image_path: str, model: str = DEFAULT_MODEL) -> str:
    """Extract a mathematical model from an image using LLM vision.

    Args:
        image_path: Path to the image file.
        model: Any litellm model string.

    Returns:
        Markdown text of the extracted model.

    Raises:
        ValueError: If the image format is not supported.
        LLMError: If the API call fails.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    mime = mimetypes.guess_type(str(path))[0] or f"image/{ext.lstrip('.')}"
    b64 = base64.b64encode(path.read_bytes()).decode()

    messages = [
        {"role": "system", "content": OCR_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
                {
                    "type": "text",
                    "text": "Extract the mathematical model from this image into clean markdown with LaTeX notation.",
                },
            ],
        },
    ]

    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=4096,
            )
            break
        except litellm.RateLimitError as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (attempt + 1))
                continue
            raise LLMError(
                f"LLM rate limited after {MAX_RETRIES} retries ({model}): {e}"
            ) from e
        except Exception as e:
            raise LLMError(f"LLM API call failed ({model}): {e}") from e
    else:
        raise LLMError(
            f"LLM rate limited after {MAX_RETRIES} retries ({model}): {last_err}"
        ) from last_err

    return response.choices[0].message.content.strip()
