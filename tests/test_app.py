from matrix_controller import app
from matrix_controller.canvas import BLACK, PixelBuffer
from matrix_controller.config import Settings
from matrix_controller.models import TrainArrival
from matrix_controller.sources import SourceError


class StubSource:
    def __init__(self, results: list[object]) -> None:
        self._results = list(results)
        self.closed = False

    async def fetch(self) -> list[TrainArrival]:
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result  # type: ignore[return-value]

    async def close(self) -> None:
        self.closed = True


class StubDriver:
    def __init__(self) -> None:
        self.frames: list[PixelBuffer] = []
        self.closed = False

    def show(self, buffer: PixelBuffer) -> None:
        snapshot = PixelBuffer(buffer.width, buffer.height)
        for y in range(buffer.height):
            for x in range(buffer.width):
                snapshot.set_pixel(x, y, buffer.get_pixel(x, y))
        self.frames.append(snapshot)

    def close(self) -> None:
        self.closed = True


def lit(buffer: PixelBuffer) -> bool:
    return any(
        buffer.get_pixel(x, y) != BLACK for y in range(buffer.height) for x in range(buffer.width)
    )


def fast_settings() -> Settings:
    return Settings(_env_file=None, polling_interval=0.001)


async def test_renders_each_poll_and_cleans_up() -> None:
    trains = [TrainArrival(line="F", status="5 mins", express=False)]
    source = StubSource([trains, trains])
    driver = StubDriver()
    await app.run(fast_settings(), source=source, driver=driver, max_frames=2)
    assert len(driver.frames) == 2
    assert lit(driver.frames[0])
    assert source.closed and driver.closed


async def test_source_error_renders_message_frame() -> None:
    source = StubSource([SourceError("boom")])
    driver = StubDriver()
    await app.run(fast_settings(), source=source, driver=driver, max_frames=1)
    assert len(driver.frames) == 1
    assert lit(driver.frames[0])  # the error message is drawn, not a blank frame


class RaisingCloseSource(StubSource):
    async def close(self) -> None:
        self.closed = True
        raise RuntimeError("close boom")


async def test_driver_closed_even_if_source_close_raises() -> None:
    trains = [TrainArrival(line="F", status="5 mins", express=False)]
    source = RaisingCloseSource([trains])
    driver = StubDriver()
    try:
        await app.run(fast_settings(), source=source, driver=driver, max_frames=1)
    except RuntimeError as exc:
        assert str(exc) == "close boom"
    assert source.closed is True
    assert driver.closed is True
