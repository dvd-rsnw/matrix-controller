"""In-memory RGB framebuffer that all rendering targets.

Renderers only ever call ``set_pixel``; display drivers read the finished
buffer. This keeps drawing code identical across hardware, terminal, and tests.
"""

from __future__ import annotations

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)

# Two chained 64x32 panels — a fixed property of this project's hardware.
MATRIX_WIDTH = 128
MATRIX_HEIGHT = 32


class PixelBuffer:
    """A ``width x height`` RGB pixel grid. Out-of-bounds writes are ignored."""

    def __init__(self, width: int = MATRIX_WIDTH, height: int = MATRIX_HEIGHT) -> None:
        self.width = width
        self.height = height
        self._pixels: list[Color] = [BLACK] * (width * height)

    def clear(self) -> None:
        self._pixels = [BLACK] * (self.width * self.height)

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self._pixels[y * self.width + x] = color

    def get_pixel(self, x: int, y: int) -> Color:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"pixel ({x}, {y}) outside {self.width}x{self.height} buffer")
        return self._pixels[y * self.width + x]

    def to_ascii(self, legend: dict[Color, str] | None = None) -> str:
        """Render as ASCII art: '.' for black, legend char or '?' for lit pixels."""
        legend = legend or {}
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                color = self.get_pixel(x, y)
                row.append("." if color == BLACK else legend.get(color, "?"))
            rows.append("".join(row))
        return "\n".join(rows)
