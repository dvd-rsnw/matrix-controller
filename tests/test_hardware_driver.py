import importlib

from matrix_controller.drivers.hardware import matrix_options_kwargs
from matrix_controller.profiles import PROFILES


def test_module_imports_without_rgbmatrix() -> None:
    # Must not raise even though rgbmatrix is not installed here.
    importlib.import_module("matrix_controller.drivers.hardware")


def test_options_from_profile() -> None:
    values = matrix_options_kwargs(PROFILES["pi-zero-2w"], {})
    assert values == {
        "rows": 32,
        "cols": 64,
        "chain_length": 2,
        "parallel": 1,
        "hardware_mapping": "adafruit-hat",
        "disable_hardware_pulsing": True,
        "gpio_slowdown": 3,
        "pwm_bits": 8,
        "pwm_lsb_nanoseconds": 130,
        "limit_refresh_rate_hz": 120,
        "brightness": 40,
    }


def test_env_overrides_win() -> None:
    values = matrix_options_kwargs(PROFILES["pi-zero-2w"], {"brightness": 70, "pwm_bits": 11})
    assert values["brightness"] == 70
    assert values["pwm_bits"] == 11
    assert values["gpio_slowdown"] == 3  # untouched
