from pathlib import Path

import pytest

from matrix_controller.profiles import (
    PROFILES,
    profile_for_model,
    read_pi_model,
    resolve_profile,
)


def test_pi_zero_2w_profile_matches_tuned_values() -> None:
    p = PROFILES["pi-zero-2w"]
    assert (p.gpio_slowdown, p.pwm_bits, p.pwm_lsb_nanoseconds) == (3, 8, 130)
    assert (p.limit_refresh_rate_hz, p.brightness) == (120, 40)
    assert p.cpu_affinity == frozenset({0, 1, 2})


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("Raspberry Pi Zero 2 W Rev 1.0", "pi-zero-2w"),
        ("Raspberry Pi 3 Model B Plus Rev 1.3", "pi-3"),
        ("Raspberry Pi 4 Model B Rev 1.4", "pi-4"),
        ("Some Unknown Board", "pi-3"),  # conservative default
        (None, "pi-3"),
    ],
)
def test_profile_for_model(model: str | None, expected: str) -> None:
    assert profile_for_model(model).name == expected


def test_read_pi_model_strips_nul(tmp_path: Path) -> None:
    model_file = tmp_path / "model"
    model_file.write_bytes(b"Raspberry Pi Zero 2 W Rev 1.0\x00")
    assert read_pi_model(model_file) == "Raspberry Pi Zero 2 W Rev 1.0"


def test_read_pi_model_missing_file_returns_none(tmp_path: Path) -> None:
    assert read_pi_model(tmp_path / "nope") is None


def test_resolve_profile_explicit_and_invalid() -> None:
    assert resolve_profile("pi-4").name == "pi-4"
    assert resolve_profile("auto", model="Raspberry Pi Zero 2 W").name == "pi-zero-2w"
    with pytest.raises(ValueError, match="unknown hardware profile"):
        resolve_profile("pi-9000")
