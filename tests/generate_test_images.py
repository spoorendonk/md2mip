#!/usr/bin/env python3
"""Generate test image fixtures from markdown model files.

Produces two styles:
  - "plain" images: raw markdown text rendered as monospace (Pillow)
  - "rendered" images: headers, formatted math, bullets, tables (matplotlib)

Run once to regenerate: python tests/generate_test_images.py
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

TESTS_DIR = Path(__file__).parent
IMAGES_DIR = TESTS_DIR / "images"
MODELS_DIR = TESTS_DIR.parent / "models"


# ---------------------------------------------------------------------------
# Plain text images (Pillow) — raw markdown as monospace
# ---------------------------------------------------------------------------


def render_text_to_image(
    text: str,
    output_path: Path,
    font_size: int = 16,
    noise: bool = False,
    rotation: float = 0.0,
) -> None:
    """Render text onto a white background PNG."""
    mono_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    font = None
    for p in mono_paths:
        try:
            font = ImageFont.truetype(p, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default(size=font_size)

    lines = text.split("\n")
    line_height = font_size + 4
    width = max(len(line) for line in lines) * (font_size * 2 // 3) + 40
    height = len(lines) * line_height + 40

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text, fill="black", font=font)

    if noise:
        pixels = img.load()
        for _ in range(width * height // 50):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            pixels[x, y] = (
                random.randint(0, 80),
                random.randint(0, 80),
                random.randint(0, 80),
            )

    if rotation:
        img = img.rotate(rotation, expand=True, fillcolor="white")

    img.save(output_path)
    print(f"  Generated (plain): {output_path.name}")


# ---------------------------------------------------------------------------
# Rendered math images (matplotlib) — proper math notation
# ---------------------------------------------------------------------------


def _parse_markdown_blocks(md: str) -> list[dict]:
    """Parse markdown into a sequence of typed blocks for rendering.

    Block types: header, text, display_math, bullet, table_row, blank.
    Text and bullets may contain inline math ($...$).
    """
    blocks: list[dict] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            blocks.append({"type": "blank"})
        elif stripped.startswith("# "):
            blocks.append({"type": "header", "level": 1, "text": stripped[2:]})
        elif stripped.startswith("## "):
            blocks.append({"type": "header", "level": 2, "text": stripped[3:]})
        elif stripped.startswith("### "):
            blocks.append({"type": "header", "level": 3, "text": stripped[4:]})
        elif stripped.startswith("$$"):
            # Display math — may be single-line $$...$$ or multi-line
            math = stripped[2:]
            if math.endswith("$$") and len(math) > 2:
                math = math[:-2]
            else:
                # Collect until closing $$
                i += 1
                parts = [math] if math else []
                while i < len(lines):
                    if lines[i].strip().endswith("$$"):
                        tail = lines[i].strip()
                        if tail != "$$":
                            parts.append(tail[:-2])
                        break
                    parts.append(lines[i].strip())
                    i += 1
                math = " ".join(parts)
            blocks.append({"type": "display_math", "math": math.strip()})
        elif stripped.startswith("|"):
            blocks.append({"type": "table_row", "text": stripped})
        elif stripped.startswith("- "):
            blocks.append({"type": "bullet", "text": stripped[2:]})
        else:
            blocks.append({"type": "text", "text": stripped})

        i += 1
    return blocks


def _render_inline(ax, x: float, y: float, text: str, fontsize: float, transform) -> None:
    """Render text that may contain inline $...$ math."""
    # Split on $...$ but not $$
    parts = re.split(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", text)
    # parts alternates: [text, math, text, math, ...]
    segments = []
    for j, part in enumerate(parts):
        if j % 2 == 0:
            if part:
                segments.append(part)
        else:
            segments.append(f"${part}$")

    joined = "".join(segments)
    ax.text(
        x,
        y,
        joined,
        fontsize=fontsize,
        transform=transform,
        verticalalignment="top",
        family="serif",
    )


def render_markdown_to_image(
    md: str,
    output_path: Path,
    width_inches: float = 9,
    dpi: int = 150,
) -> None:
    """Render markdown with proper math notation using matplotlib."""
    blocks = _parse_markdown_blocks(md)

    # Estimate height needed
    n_content = sum(1 for b in blocks if b["type"] != "blank")
    n_blank = sum(1 for b in blocks if b["type"] == "blank")
    height_inches = max(3, (n_content * 0.4 + n_blank * 0.15 + 0.8))

    fig, ax = plt.subplots(figsize=(width_inches, height_inches))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    y = 0.97  # start near top, in axes coords
    step_text = 0.4 / height_inches  # normalized step per text line
    step_blank = 0.15 / height_inches
    margin = 0.04

    font_sizes = {1: 18, 2: 15, 3: 13}

    # Skip separator table rows (|---|---|...)
    sep_re = re.compile(r"^\|[\s\-:|]+\|$")

    for block in blocks:
        btype = block["type"]

        if btype == "blank":
            y -= step_blank
        elif btype == "header":
            level = block["level"]
            fs = font_sizes.get(level, 12)
            ax.text(
                margin,
                y,
                block["text"],
                fontsize=fs,
                fontweight="bold",
                transform=ax.transAxes,
                verticalalignment="top",
                family="serif",
            )
            y -= step_text * 1.3
        elif btype == "display_math":
            math_str = f"${block['math']}$"
            ax.text(
                0.5,
                y,
                math_str,
                fontsize=14,
                ha="center",
                transform=ax.transAxes,
                verticalalignment="top",
                family="serif",
            )
            y -= step_text * 1.8
        elif btype == "bullet":
            _render_inline(
                ax,
                margin + 0.02,
                y,
                f"\u2022  {block['text']}",
                fontsize=11,
                transform=ax.transAxes,
            )
            y -= step_text
        elif btype == "table_row":
            text = block["text"]
            if sep_re.match(text):
                continue  # skip separator rows
            _render_inline(ax, margin, y, text, fontsize=10, transform=ax.transAxes)
            y -= step_text * 0.9
        elif btype == "text":
            _render_inline(ax, margin, y, block["text"], fontsize=11, transform=ax.transAxes)
            y -= step_text

    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white", pad_inches=0.2)
    plt.close(fig)
    print(f"  Generated (rendered): {output_path.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    IMAGES_DIR.mkdir(exist_ok=True)

    knapsack_md = (MODELS_DIR / "knapsack.md").read_text()
    transport_md = (MODELS_DIR / "transportation.md").read_text()
    capital_budgeting_md = (MODELS_DIR / "capital_budgeting.md").read_text()
    set_covering_md = (MODELS_DIR / "set_covering.md").read_text()
    graph_coloring_md = (MODELS_DIR / "graph_coloring.md").read_text()

    # Plain text images (raw markdown as monospace)
    render_text_to_image(knapsack_md, IMAGES_DIR / "clean_knapsack.png")
    render_text_to_image(transport_md, IMAGES_DIR / "clean_transport.png")
    render_text_to_image(
        transport_md,
        IMAGES_DIR / "noisy_transport.png",
        noise=True,
        rotation=1.5,
    )

    # Rendered math images (proper notation via matplotlib)
    render_markdown_to_image(knapsack_md, IMAGES_DIR / "rendered_knapsack.png")
    render_markdown_to_image(transport_md, IMAGES_DIR / "rendered_transport.png")
    render_markdown_to_image(capital_budgeting_md, IMAGES_DIR / "rendered_capital_budgeting.png")
    render_markdown_to_image(set_covering_md, IMAGES_DIR / "rendered_set_covering.png")
    render_markdown_to_image(graph_coloring_md, IMAGES_DIR / "rendered_graph_coloring.png")

    print("Done.")


if __name__ == "__main__":
    main()
