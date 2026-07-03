from matrix_controller.canvas import BLACK, WHITE, PixelBuffer
from matrix_controller.fonts import DEFAULT_FONT_PATH, BDFFont


def test_default_font_path_exists() -> None:
    assert DEFAULT_FONT_PATH.is_file()


def test_char_and_text_width_monospace() -> None:
    font = BDFFont.load()
    assert font.char_width("A") == 6
    assert font.text_width("5 mins") == 36


def test_draw_text_renders_glyph_A_pixels() -> None:
    # Glyph 'A': BBX 6 10 0 -2, bitmap rows (top to bottom):
    # 00 20 50 88 88 F8 88 88 00 00
    # Matches rgbmatrix's Font::DrawGlyph: y_pos = y - bbx_h - bbx_yoff,
    # then row r is drawn at y_pos + r, i.e. py = y - (bbx_yoff + bbx_h) + r.
    # With y=9, bbx_yoff=-2, bbx_h=10: py = y - 8 + r.
    font = BDFFont.load()
    buf = PixelBuffer(8, 12)
    end_x = font.draw_text(buf, 0, 9, "A", WHITE)
    assert end_x == 6
    # bitmap row 0x20 (r=1) -> single pixel at column 2, screen row 9-8+1 = 2
    assert buf.get_pixel(2, 2) == WHITE
    assert buf.get_pixel(1, 2) == BLACK
    # bitmap row 0xF8 (r=5) -> columns 0..4 at screen row 9-8+5 = 6
    for x in range(5):
        assert buf.get_pixel(x, 6) == WHITE
    assert buf.get_pixel(5, 6) == BLACK


def test_draw_text_advances_pen_between_glyphs() -> None:
    # A mutant that redraws every glyph at the starting x (while still
    # returning the correct total advance) must fail this: the second
    # glyph's ink has to land 6px (one DWIDTH) to the right of the first's.
    font = BDFFont.load()
    buf = PixelBuffer(14, 12)
    end_x = font.draw_text(buf, 0, 9, "AA", WHITE)
    assert end_x == 12
    # bitmap row 0x20 (r=1) -> column 2 for the first 'A', column 8 for the second.
    assert buf.get_pixel(2, 2) == WHITE
    assert buf.get_pixel(8, 2) == WHITE
    # Nothing lit in between at that row.
    for x in (3, 4, 5, 6, 7):
        assert buf.get_pixel(x, 2) == BLACK


def test_draw_text_renders_descender_at_and_below_baseline() -> None:
    # Glyph 'g' (encoding 103): BBX 6 10 0 -2, bitmap rows (top to bottom):
    # 00 00 00 78 88 88 78 08 88 70
    # Using the corrected formula py = y - 8 + r with baseline y=9:
    #   r=8 (row 0x88 = 100010) -> py = 9 (at the baseline): columns 0 and 4 lit.
    #   r=9 (row 0x70 = 011100) -> py = 10 (below the baseline): columns 1,2,3 lit.
    # A mutant that clips ink at/below the baseline would drop both rows.
    font = BDFFont.load()
    buf = PixelBuffer(8, 12)
    font.draw_text(buf, 0, 9, "g", WHITE)
    assert buf.get_pixel(0, 9) == WHITE
    assert buf.get_pixel(4, 9) == WHITE
    for x in (1, 2, 3, 5):
        assert buf.get_pixel(x, 9) == BLACK
    for x in (1, 2, 3):
        assert buf.get_pixel(x, 10) == WHITE
    for x in (0, 4, 5):
        assert buf.get_pixel(x, 10) == BLACK


def test_final_glyph_in_font_file_is_parsed() -> None:
    # The font file's last glyph is uniFFFD (ENCODING 65533, U+FFFD).
    # A parser that only flushes a glyph upon seeing the *next* STARTCHAR
    # would silently drop this one.
    font = BDFFont.load()
    assert font.char_width("�") == 6


def test_unknown_char_is_skipped() -> None:
    font = BDFFont.load()
    buf = PixelBuffer(8, 12)
    # U+FFFF is not in the font; width 0, nothing drawn, and the pen must
    # not advance for a glyph the font lacks.
    assert font.char_width("￿") == 0
    assert font.draw_text(buf, 0, 9, "￿", WHITE) == 0
    assert buf.to_ascii() == "\n".join(["." * 8] * 12)
