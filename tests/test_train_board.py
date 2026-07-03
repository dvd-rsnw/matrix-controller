from matrix_controller.canvas import BLACK, WHITE, PixelBuffer
from matrix_controller.fonts import BDFFont
from matrix_controller.models import TrainArrival
from matrix_controller.rendering.palette import ASCII_LEGEND, F_TRAIN_ORANGE, G_TRAIN_GREEN
from matrix_controller.rendering.train_board import TrainBoard


def render(trains: list[TrainArrival]) -> PixelBuffer:
    buffer = PixelBuffer()
    TrainBoard(BDFFont.load()).render(buffer, trains)
    return buffer


def test_f_local_and_g(assert_matches_golden) -> None:
    buf = render(
        [
            TrainArrival(line="F", status="5 mins", express=False),
            TrainArrival(line="G", status="12 mins", express=False),
        ]
    )
    assert_matches_golden(buf.to_ascii(ASCII_LEGEND), "board_f_local_g")


def test_f_express_uses_diamond(assert_matches_golden) -> None:
    buf = render(
        [
            TrainArrival(line="F", status="3 mins", express=True),
            TrainArrival(line="G", status="Now", express=False),
        ]
    )
    assert_matches_golden(buf.to_ascii(ASCII_LEGEND), "board_f_express_g_now")


def test_single_train_leaves_second_row_empty() -> None:
    buf = render([TrainArrival(line="F", status="5 mins", express=False)])
    # bottom section (rows 18..27) must be fully dark
    for y in range(18, 28):
        for x in range(buf.width):
            assert buf.get_pixel(x, y) == BLACK


def test_bullets_use_line_colors() -> None:
    buf = render(
        [
            TrainArrival(line="F", status="5 mins", express=False),
            TrainArrival(line="G", status="7 mins", express=False),
        ]
    )
    # Sample left of the letter glyphs (which are white and start at x=6):
    # bullet centers are (8, 7) and (8, 23), so (4, y) is inside each circle.
    assert buf.get_pixel(4, 7) == F_TRAIN_ORANGE  # inside top bullet
    assert buf.get_pixel(4, 23) == G_TRAIN_GREEN  # inside bottom bullet


def test_render_message(assert_matches_golden) -> None:
    buffer = PixelBuffer()
    TrainBoard(BDFFont.load()).render_message(buffer, "API unavailable")
    assert_matches_golden(buffer.to_ascii(ASCII_LEGEND), "board_message")


def test_render_clears_stale_pixels() -> None:
    # The board runs in a long-lived loop reusing one buffer; render() owns clearing it.
    buffer = PixelBuffer()
    buffer.set_pixel(127, 31, WHITE)  # stale pixel in the always-dark footer
    TrainBoard(BDFFont.load()).render(
        buffer, [TrainArrival(line="F", status="5 mins", express=False)]
    )
    assert buffer.get_pixel(127, 31) == BLACK


def test_render_message_clears_stale_pixels() -> None:
    buffer = PixelBuffer()
    buffer.set_pixel(127, 31, WHITE)
    TrainBoard(BDFFont.load()).render_message(buffer, "API unavailable")
    assert buffer.get_pixel(127, 31) == BLACK


def test_g_express_keeps_circle_bullet() -> None:
    # Only the F train has an express diamond; a G express must stay a circle.
    buf = render([TrainArrival(line="G", status="5 mins", express=True)])
    # (12, 11) is (cx+4, cy+4) from the bullet center (8, 7): inside the radius-6
    # circle (32 <= 36) but outside a radius-5 diamond (|4|+|4| > 5).
    assert buf.get_pixel(12, 11) == G_TRAIN_GREEN


def test_third_train_is_ignored() -> None:
    two = [
        TrainArrival(line="F", status="5 mins", express=False),
        TrainArrival(line="G", status="12 mins", express=False),
    ]
    extra = TrainArrival(line="F", status="15 mins", express=False)
    # A third arrival would overdraw the second row; render() caps at two.
    assert render([*two, extra]).to_ascii(ASCII_LEGEND) == render(two).to_ascii(ASCII_LEGEND)


def test_render_message_shows_all_21_visible_chars() -> None:
    buffer = PixelBuffer()
    # Exactly 21 chars: char 20 ('!') occupies x=122..127, the last on-board column
    # block. Tightening the [:21] truncation would blank visible characters.
    TrainBoard(BDFFont.load()).render_message(buffer, "No upcoming arrivals!")
    assert any(
        buffer.get_pixel(x, y) != BLACK for x in range(122, 128) for y in range(buffer.height)
    )
