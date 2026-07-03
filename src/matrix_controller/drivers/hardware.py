"""Display driver backed by hzeller/rpi-rgb-led-matrix. Only works on the Pi.

``rgbmatrix`` is imported lazily inside HardwareDriver so the rest of the
package imports fine on machines where the bindings can't be installed.
"""

from __future__ import annotations

import os
from typing import Any

from matrix_controller.canvas import PixelBuffer
from matrix_controller.profiles import HardwareProfile

# Fixed panel geometry for this project: two chained 64x32 panels.
ROWS = 32
COLS = 64
CHAIN_LENGTH = 2
HARDWARE_MAPPING = "adafruit-hat"


def matrix_options_kwargs(profile: HardwareProfile, overrides: dict[str, int]) -> dict[str, Any]:
    """RGBMatrixOptions attribute values for a profile plus env-var overrides.

    Pure data so it can be unit-tested without rgbmatrix installed.
    """
    values: dict[str, Any] = {
        "rows": ROWS,
        "cols": COLS,
        "chain_length": CHAIN_LENGTH,
        "parallel": 1,
        "hardware_mapping": HARDWARE_MAPPING,
        "disable_hardware_pulsing": True,
        "gpio_slowdown": profile.gpio_slowdown,
        "pwm_bits": profile.pwm_bits,
        "pwm_lsb_nanoseconds": profile.pwm_lsb_nanoseconds,
        "limit_refresh_rate_hz": profile.limit_refresh_rate_hz,
        "brightness": profile.brightness,
    }
    values.update(overrides)
    return values


class HardwareDriver:
    def __init__(self, profile: HardwareProfile, overrides: dict[str, int] | None = None) -> None:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        options = RGBMatrixOptions()
        for attr, value in matrix_options_kwargs(profile, overrides or {}).items():
            setattr(options, attr, value)
        self._matrix = RGBMatrix(options=options)
        self._offscreen = self._matrix.CreateFrameCanvas()
        _apply_process_tuning(profile)

    def show(self, buffer: PixelBuffer) -> None:
        # Writing every pixel fully replaces the previous frame; the swap is
        # vsync'd by the library, so there is no visible clear/flicker.
        for y in range(buffer.height):
            for x in range(buffer.width):
                r, g, b = buffer.get_pixel(x, y)
                self._offscreen.SetPixel(x, y, r, g, b)
        self._offscreen = self._matrix.SwapOnVSync(self._offscreen)

    def close(self) -> None:
        self._matrix.Clear()


def _apply_process_tuning(profile: HardwareProfile) -> None:
    """Pin off the library's spin core and raise priority. Best-effort."""
    if profile.cpu_affinity is not None:
        try:
            os.sched_setaffinity(0, set(profile.cpu_affinity))  # type: ignore[attr-defined]
        except (AttributeError, OSError) as exc:
            print(f"Could not set CPU affinity: {exc}")
    try:
        os.nice(-10)
    except OSError as exc:
        print(f"Could not raise process priority: {exc}")
