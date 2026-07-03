"""Text layout helpers on top of BDFFont."""

from matrix_controller.canvas import Color, PixelBuffer
from matrix_controller.fonts import BDFFont


def draw_text(buffer: PixelBuffer, font: BDFFont, x: int, y: int, text: str, color: Color) -> int:
    """Draw ``text`` at baseline ``(x, y)``; returns the end x."""
    return font.draw_text(buffer, x, y, text, color)


def draw_text_with_fixed_suffix(
    buffer: PixelBuffer,
    font: BDFFont,
    variable: str,
    suffix: str,
    end_x: int,
    y: int,
    color: Color,
) -> None:
    """Right-align ``suffix`` to end at ``end_x``, with ``variable`` just left of it.

    Keeps the ' mins' label anchored while the minute count grows/shrinks.
    """
    suffix_x = end_x - font.text_width(suffix)
    font.draw_text(buffer, suffix_x, y, suffix, color)
    font.draw_text(buffer, suffix_x - font.text_width(variable), y, variable, color)
