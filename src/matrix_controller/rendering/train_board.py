"""The two-row F/G arrival board layout.

Pixel measurements are hand-tuned for a 128x32 matrix and ported verbatim
from the original implementation to preserve the board's look.
"""

from collections.abc import Sequence

from matrix_controller.canvas import WHITE, PixelBuffer
from matrix_controller.fonts import BDFFont
from matrix_controller.models import TrainArrival
from matrix_controller.rendering import shapes, text
from matrix_controller.rendering.palette import F_TRAIN_ORANGE, G_TRAIN_GREEN

PADDING_X = 2
PADDING_Y = 2
ROW_HEIGHT = 10
CENTER_GAP = 6  # vertical gap between the two rows
CIRCLE_WIDTH = 13  # bullet diameter
FIRST_GAP = 3  # bullet -> line name
LINE_NAME_WIDTH = 72
SECOND_GAP = 5  # line name -> minutes block
MINUTES_WIDTH = 34
TEXT_BASELINE_OFFSET = 9  # text baseline, relative to a row's top edge

LINE_NAMES = {
    ("F", False): "6 Av Local",
    ("F", True): "6 Av - Culver Express",
    ("G", False): "Crosstown",
    ("G", True): "Crosstown",
}
MAX_NAME_CHARS = 14
MAX_STATUS_CHARS = 7


class TrainBoard:
    """Renders up to two arrivals, one per row."""

    def __init__(self, font: BDFFont) -> None:
        self._font = font

    def render(self, buffer: PixelBuffer, trains: Sequence[TrainArrival]) -> None:
        buffer.clear()
        for section, train in enumerate(trains[:2]):
            self._render_row(buffer, section, train)

    def render_message(self, buffer: PixelBuffer, message: str) -> None:
        """Full-board status line, used when no train data is available."""
        buffer.clear()
        baseline = buffer.height // 2 + 4
        text.draw_text(buffer, self._font, PADDING_X, baseline, message[:21], WHITE)

    def _render_row(self, buffer: PixelBuffer, section: int, train: TrainArrival) -> None:
        x = PADDING_X
        y = PADDING_Y if section == 0 else PADDING_Y + ROW_HEIGHT + CENTER_GAP

        bullet_color = F_TRAIN_ORANGE if train.line == "F" else G_TRAIN_GREEN
        circle_x = x + CIRCLE_WIDTH // 2
        circle_y = y + ROW_HEIGHT // 2
        if train.line == "F" and train.express:
            shapes.draw_diamond(buffer, circle_x, circle_y, 5, bullet_color)
        else:
            shapes.draw_circle(buffer, circle_x, circle_y, CIRCLE_WIDTH // 2, bullet_color)

        letter_x = x + (CIRCLE_WIDTH - 6) // 2
        letter_y = y + (ROW_HEIGHT - 8) // 2
        if train.line == "F":
            shapes.draw_thick_f(buffer, letter_x, letter_y, WHITE)
        elif train.line == "G":
            shapes.draw_thick_g(buffer, letter_x, letter_y, WHITE)

        baseline = y + TEXT_BASELINE_OFFSET
        line_name_x = x + CIRCLE_WIDTH + FIRST_GAP - 1
        name = LINE_NAMES.get((train.line, train.express), train.line)
        text.draw_text(buffer, self._font, line_name_x, baseline, name[:MAX_NAME_CHARS], WHITE)

        minutes_end_x = line_name_x + LINE_NAME_WIDTH + SECOND_GAP - 1 + MINUTES_WIDTH
        if " mins" in train.status:
            variable, _ = train.status.split(" mins", 1)
            text.draw_text_with_fixed_suffix(
                buffer, self._font, variable, " mins", minutes_end_x, baseline, WHITE
            )
        else:
            text.draw_text(
                buffer,
                self._font,
                minutes_end_x - MINUTES_WIDTH,
                baseline,
                train.status[:MAX_STATUS_CHARS],
                WHITE,
            )
