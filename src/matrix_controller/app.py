"""Wires config, source, driver, and board into the polling loop."""

import asyncio

from matrix_controller.canvas import PixelBuffer
from matrix_controller.config import Settings
from matrix_controller.drivers import DisplayDriver, create_driver
from matrix_controller.fonts import BDFFont
from matrix_controller.profiles import resolve_profile
from matrix_controller.rendering.train_board import TrainBoard
from matrix_controller.sources import SourceError, TrainSource, create_source


async def run(
    settings: Settings,
    *,
    source: TrainSource | None = None,
    driver: DisplayDriver | None = None,
    max_frames: int | None = None,
) -> None:
    """Poll the source and push frames to the driver until cancelled."""
    source = source or create_source(settings)
    driver = driver or create_driver(
        settings.driver,
        resolve_profile(settings.hardware_profile),
        settings.matrix_overrides(),
    )
    board = TrainBoard(BDFFont.load())
    buffer = PixelBuffer()
    frames = 0
    try:
        while max_frames is None or frames < max_frames:
            try:
                trains = await source.fetch()
                board.render(buffer, trains)
            except SourceError as exc:
                print(f"source error: {exc}")
                board.render_message(buffer, "No train data")
            driver.show(buffer)
            frames += 1
            await asyncio.sleep(settings.polling_interval)
    finally:
        # Guard the closes independently: a raising source.close() must not
        # skip driver.close() (terminal cursor restore depends on it).
        try:
            await source.close()
        finally:
            driver.close()
