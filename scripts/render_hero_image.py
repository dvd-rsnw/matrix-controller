#!/usr/bin/env python3
"""Render the demo board to docs/images/hero.png (the README screenshot).

Regenerate after any visual change: python3 scripts/render_hero_image.py
Requires the dev extras (Pillow).
"""

from pathlib import Path

from PIL import Image, ImageDraw

from matrix_controller.canvas import BLACK, PixelBuffer
from matrix_controller.fonts import BDFFont
from matrix_controller.models import TrainArrival
from matrix_controller.rendering.train_board import TrainBoard

SCALE = 8  # output pixels per LED
DOT = 7  # lit LED dot diameter (leaves a 1px grid gap)
BACKGROUND = (12, 12, 14)
OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "images" / "hero.png"

TRAINS = [
    TrainArrival(line="F", status="4 mins", express=False),
    TrainArrival(line="G", status="9 mins", express=False),
]


def main() -> None:
    buffer = PixelBuffer()
    TrainBoard(BDFFont.load()).render(buffer, TRAINS)

    image = Image.new("RGB", (buffer.width * SCALE, buffer.height * SCALE), BACKGROUND)
    draw = ImageDraw.Draw(image)
    for y in range(buffer.height):
        for x in range(buffer.width):
            color = buffer.get_pixel(x, y)
            if color == BLACK:
                continue
            px, py = x * SCALE, y * SCALE
            draw.ellipse([px, py, px + DOT, py + DOT], fill=color)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(f"wrote {OUTPUT} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
