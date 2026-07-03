"""Board colors and the ASCII legend used by golden-frame tests."""

from matrix_controller.canvas import WHITE, Color

F_TRAIN_ORANGE: Color = (238, 104, 0)
G_TRAIN_GREEN: Color = (121, 149, 52)

ASCII_LEGEND: dict[Color, str] = {
    F_TRAIN_ORANGE: "F",
    G_TRAIN_GREEN: "G",
    WHITE: "#",
}
