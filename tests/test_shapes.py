from matrix_controller.canvas import BLACK, WHITE, PixelBuffer
from matrix_controller.rendering.shapes import (
    draw_circle,
    draw_diamond,
    draw_thick_f,
    draw_thick_g,
)


def lit_count(buf: PixelBuffer) -> int:
    return sum(buf.get_pixel(x, y) != BLACK for y in range(buf.height) for x in range(buf.width))


def test_circle_removes_cardinal_tips() -> None:
    buf = PixelBuffer(16, 16)
    draw_circle(buf, 8, 8, 6, WHITE)
    for tip in [(14, 8), (2, 8), (8, 14), (8, 2)]:
        assert buf.get_pixel(*tip) == BLACK
    assert buf.get_pixel(13, 8) == WHITE  # just inside the tip
    assert buf.get_pixel(8, 8) == WHITE


def test_circle_is_symmetric() -> None:
    # 17x17 buffer so the mirror of every pixel around center (8, 8) is in bounds.
    buf = PixelBuffer(17, 17)
    draw_circle(buf, 8, 8, 6, WHITE)
    for y in range(17):
        for x in range(17):
            assert buf.get_pixel(x, y) == buf.get_pixel(16 - x, y)  # mirror across x=8
            assert buf.get_pixel(x, y) == buf.get_pixel(x, 16 - y)  # mirror across y=8


def test_diamond_pixel_count() -> None:
    buf = PixelBuffer(16, 16)
    draw_diamond(buf, 8, 8, 5, WHITE)
    # |i| + |j| <= r lights 2r^2 + 2r + 1 pixels
    assert lit_count(buf) == 61
    assert buf.get_pixel(13, 8) == WHITE
    assert buf.get_pixel(14, 8) == BLACK


def test_thick_letters_draw_something_in_bbox() -> None:
    for draw in (draw_thick_f, draw_thick_g):
        buf = PixelBuffer(10, 12)
        draw(buf, 1, 1, WHITE)
        assert lit_count(buf) > 10
