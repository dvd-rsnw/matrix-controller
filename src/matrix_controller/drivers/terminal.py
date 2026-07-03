"""Pixel-accurate terminal simulator for the LED matrix.

Each character cell shows two vertically stacked pixels: '▀' with a 24-bit
foreground (top pixel) and background (bottom pixel) color.
"""

import sys
from typing import TextIO

from matrix_controller.canvas import PixelBuffer

_CLEAR = "\x1b[2J"
_HOME = "\x1b[H"
_HIDE_CURSOR = "\x1b[?25l"
_SHOW_CURSOR = "\x1b[?25h"
_RESET = "\x1b[0m"


class TerminalDriver:
    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream if stream is not None else sys.stdout
        self._started = False

    def show(self, buffer: PixelBuffer) -> None:
        if not self._started:
            self._stream.write(_CLEAR + _HIDE_CURSOR)
            self._started = True
        parts = [_HOME]
        for y in range(0, buffer.height, 2):
            for x in range(buffer.width):
                tr, tg, tb = buffer.get_pixel(x, y)
                br, bg, bb = buffer.get_pixel(x, y + 1) if y + 1 < buffer.height else (0, 0, 0)
                parts.append(f"\x1b[38;2;{tr};{tg};{tb}m\x1b[48;2;{br};{bg};{bb}m▀")
            parts.append(_RESET + "\n")
        self._stream.write("".join(parts))
        self._stream.flush()

    def close(self) -> None:
        if self._started:
            self._stream.write(_RESET + _SHOW_CURSOR + "\n")
            self._stream.flush()
