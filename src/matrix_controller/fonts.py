"""Minimal BDF bitmap-font parser and rasterizer.

Draws the same pixels as rpi-rgb-led-matrix's ``graphics.DrawText`` so that
hardware, terminal, and test output are identical. Supports only the BDF
features used by the bundled public-domain X11 fixed fonts.

NOTE: resolves the fonts directory relative to the repository root, so the
package must be installed editable (``pip install -e .``) — see AGENTS.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from matrix_controller.canvas import Color, PixelBuffer

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
DEFAULT_FONT_PATH = ASSETS_DIR / "fonts" / "6x10.bdf"


@dataclass(frozen=True)
class Glyph:
    encoding: int
    dwidth: int  # horizontal advance
    bbx_w: int
    bbx_h: int
    bbx_xoff: int
    bbx_yoff: int
    rows: tuple[int, ...]  # bitmap rows, top to bottom; MSB = leftmost pixel


class BDFFont:
    def __init__(self, glyphs: dict[int, Glyph]) -> None:
        self._glyphs = glyphs

    @classmethod
    def load(cls, path: Path = DEFAULT_FONT_PATH) -> BDFFont:
        glyphs: dict[int, Glyph] = {}
        encoding, dwidth = -1, 0
        bbx = (0, 0, 0, 0)
        rows: list[int] = []
        in_bitmap = False
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if line.startswith("STARTCHAR"):
                encoding, dwidth, bbx, rows, in_bitmap = -1, 0, (0, 0, 0, 0), [], False
            elif line.startswith("ENCODING"):
                encoding = int(line.split()[1])
            elif line.startswith("DWIDTH"):
                dwidth = int(line.split()[1])
            elif line.startswith("BBX"):
                parts = line.split()
                bbx = (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))
            elif line == "BITMAP":
                in_bitmap = True
            elif line == "ENDCHAR":
                if encoding >= 0:
                    glyphs[encoding] = Glyph(encoding, dwidth, *bbx, tuple(rows))
                in_bitmap = False
            elif in_bitmap:
                rows.append(int(line, 16))
        return cls(glyphs)

    def char_width(self, char: str) -> int:
        glyph = self._glyphs.get(ord(char))
        return glyph.dwidth if glyph else 0

    def text_width(self, text: str) -> int:
        return sum(self.char_width(c) for c in text)

    def draw_text(self, buffer: PixelBuffer, x: int, y: int, text: str, color: Color) -> int:
        """Draw ``text`` with ``(x, y)`` as the baseline origin; returns the end x."""
        for char in text:
            glyph = self._glyphs.get(ord(char))
            if glyph is None:
                continue
            row_bits = ((glyph.bbx_w + 7) // 8) * 8
            for r, row in enumerate(glyph.rows):
                py = y - (glyph.bbx_yoff + glyph.bbx_h) + r
                for c in range(glyph.bbx_w):
                    if row >> (row_bits - 1 - c) & 1:
                        buffer.set_pixel(x + glyph.bbx_xoff + c, py, color)
            x += glyph.dwidth
        return x
