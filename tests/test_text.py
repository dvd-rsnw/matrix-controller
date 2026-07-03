from matrix_controller.canvas import WHITE, PixelBuffer
from matrix_controller.fonts import BDFFont
from matrix_controller.rendering.text import draw_text, draw_text_with_fixed_suffix


def column_is_lit(buf: PixelBuffer, x: int) -> bool:
    return any(buf.get_pixel(x, y) == WHITE for y in range(buf.height))


def test_draw_text_returns_advance() -> None:
    font = BDFFont.load()
    buf = PixelBuffer(64, 12)
    assert draw_text(buf, font, 2, 9, "5 mins", WHITE) == 2 + 36


def test_fixed_suffix_ends_at_end_x() -> None:
    font = BDFFont.load()
    buf = PixelBuffer(64, 12)
    draw_text_with_fixed_suffix(buf, font, "12", " mins", end_x=60, y=9, color=WHITE)
    # " mins" is 30px wide -> starts at x=30; "12" is 12px -> starts at x=18
    assert not column_is_lit(buf, 17)
    assert column_is_lit(buf, 19)  # '1' vertical stroke region
    assert not column_is_lit(buf, 60)  # nothing at or past end_x
