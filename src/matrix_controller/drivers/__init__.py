"""Display drivers and driver selection."""

from typing import TYPE_CHECKING, Protocol

from matrix_controller.canvas import PixelBuffer

if TYPE_CHECKING:
    from matrix_controller.profiles import HardwareProfile


class DisplayDriver(Protocol):
    def show(self, buffer: PixelBuffer) -> None: ...

    def close(self) -> None: ...


def hardware_available() -> bool:
    """True when the rgbmatrix bindings are importable (i.e. we're on the Pi)."""
    try:
        import rgbmatrix  # noqa: F401
    except ImportError:
        return False
    return True


def create_driver(
    name: str, profile: "HardwareProfile", overrides: dict[str, int] | None = None
) -> DisplayDriver:
    """Build the driver for ``name`` ('auto' picks hardware when available)."""
    if name == "auto":
        name = "hardware" if hardware_available() else "terminal"
    if name == "hardware":
        from matrix_controller.drivers.hardware import HardwareDriver

        return HardwareDriver(profile, overrides)
    from matrix_controller.drivers.terminal import TerminalDriver

    return TerminalDriver()
