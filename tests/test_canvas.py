import pytest

from matrix_controller.canvas import BLACK, WHITE, PixelBuffer
from matrix_controller.rendering.palette import ASCII_LEGEND, F_TRAIN_ORANGE, G_TRAIN_GREEN


def test_defaults_to_matrix_size() -> None:
    buf = PixelBuffer()
    assert (buf.width, buf.height) == (128, 32)
    assert buf.get_pixel(127, 31) == BLACK


def test_set_and_get_pixel() -> None:
    buf = PixelBuffer(4, 4)
    buf.set_pixel(1, 2, WHITE)
    assert buf.get_pixel(1, 2) == WHITE
    assert buf.get_pixel(0, 0) == BLACK


def test_out_of_bounds_write_is_ignored() -> None:
    buf = PixelBuffer(4, 4)
    buf.set_pixel(-1, 0, WHITE)
    buf.set_pixel(4, 0, WHITE)
    buf.set_pixel(0, 4, WHITE)  # must not raise


def test_out_of_bounds_read_raises() -> None:
    buf = PixelBuffer(4, 4)
    with pytest.raises(IndexError):
        buf.get_pixel(4, 0)


def test_clear_resets_all_pixels() -> None:
    buf = PixelBuffer(4, 4)
    buf.set_pixel(3, 3, WHITE)
    buf.clear()
    assert buf.get_pixel(3, 3) == BLACK


def test_to_ascii_uses_legend() -> None:
    buf = PixelBuffer(3, 2)
    buf.set_pixel(0, 0, F_TRAIN_ORANGE)
    buf.set_pixel(1, 0, G_TRAIN_GREEN)
    buf.set_pixel(2, 1, WHITE)
    buf.set_pixel(0, 1, (1, 2, 3))  # not in legend
    assert buf.to_ascii(ASCII_LEGEND) == "FG.\n?.#"
