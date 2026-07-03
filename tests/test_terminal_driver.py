import io

from matrix_controller.canvas import PixelBuffer
from matrix_controller.drivers.terminal import TerminalDriver


def make_driver() -> tuple[TerminalDriver, io.StringIO]:
    stream = io.StringIO()
    return TerminalDriver(stream=stream), stream


def test_show_writes_one_halfblock_per_two_rows() -> None:
    driver, stream = make_driver()
    buf = PixelBuffer(4, 4)
    buf.set_pixel(0, 0, (255, 0, 0))
    driver.show(buf)
    out = stream.getvalue()
    assert out.count("▀") == 4 * 2  # 4 wide, 4 tall -> 2 text rows
    assert "\x1b[38;2;255;0;0m" in out  # top pixel as 24-bit foreground
    assert "\x1b[48;2;0;0;0m" in out  # bottom pixel as background


def test_first_show_clears_and_hides_cursor_once() -> None:
    driver, stream = make_driver()
    buf = PixelBuffer(2, 2)
    driver.show(buf)
    driver.show(buf)
    out = stream.getvalue()
    assert out.count("\x1b[2J") == 1
    assert out.count("\x1b[?25l") == 1
    assert out.count("\x1b[H") == 2  # cursor homed every frame


def test_close_restores_cursor() -> None:
    driver, stream = make_driver()
    driver.show(PixelBuffer(2, 2))
    driver.close()
    assert "\x1b[?25h" in stream.getvalue()


def test_close_before_show_is_a_noop() -> None:
    driver, stream = make_driver()
    driver.close()
    assert stream.getvalue() == ""
