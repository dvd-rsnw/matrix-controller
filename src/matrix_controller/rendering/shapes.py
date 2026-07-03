"""Pixel-art shapes: line bullets and the thick letters drawn inside them.

Everything here (circle, diamond, and the F/G letter art hand-tuned for a
13px bullet) is ported pixel-for-pixel from the original implementation to
preserve the board's look.
"""

from matrix_controller.canvas import Color, PixelBuffer


def draw_circle(buffer: PixelBuffer, cx: int, cy: int, radius: int, color: Color) -> None:
    """Filled circle with the four cardinal tip pixels removed for a rounder look."""
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if i * i + j * j <= radius * radius:
                if (abs(i) == radius and j == 0) or (abs(j) == radius and i == 0):
                    continue
                buffer.set_pixel(cx + i, cy + j, color)


def draw_diamond(buffer: PixelBuffer, cx: int, cy: int, radius: int, color: Color) -> None:
    """Filled diamond (the MTA express marker).

    Pass radius=5 for the board's express marker: the legacy renderer
    hardcoded that radius, so only 5 reproduces the original art.
    """
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if abs(i) + abs(j) <= radius:
                buffer.set_pixel(cx + i, cy + j, color)


def draw_thick_f(buffer: PixelBuffer, x: int, y: int, color: Color) -> None:
    """2px-thick 'F', 9px tall."""
    for i in range(9):  # vertical stroke
        buffer.set_pixel(x + 1, y + i, color)
        buffer.set_pixel(x + 2, y + i, color)
    for i in range(5):  # top bar
        buffer.set_pixel(x + 1 + i, y, color)
        buffer.set_pixel(x + 1 + i, y + 1, color)
    for i in range(4):  # middle bar
        buffer.set_pixel(x + 1 + i, y + 4, color)
        buffer.set_pixel(x + 1 + i, y + 5, color)


def draw_thick_g(buffer: PixelBuffer, x: int, y: int, color: Color) -> None:
    """2px-thick 'G', 9px tall, curved corners."""
    for i in range(1, 6):  # top row
        buffer.set_pixel(x + i, y, color)
    for i in range(0, 6):  # second row
        buffer.set_pixel(x + i, y + 1, color)
    for j in range(2, 4):  # left stroke only
        for i in range(0, 2):
            buffer.set_pixel(x + i, y + j, color)
    for j in range(4, 6):  # left stroke + inner bar
        for i in range(0, 2):
            buffer.set_pixel(x + i, y + j, color)
        for i in range(3, 6):
            buffer.set_pixel(x + i, y + j, color)
    for i in range(0, 2):  # seventh row
        buffer.set_pixel(x + i, y + 6, color)
    for i in range(4, 6):
        buffer.set_pixel(x + i, y + 6, color)
    for i in range(0, 6):  # eighth row
        buffer.set_pixel(x + i, y + 7, color)
    for i in range(1, 6):  # ninth row
        buffer.set_pixel(x + i, y + 8, color)
