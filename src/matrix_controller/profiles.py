"""Named starting-point presets for rpi-rgb-led-matrix options, per Pi model.

The values follow hzeller/rpi-rgb-led-matrix tuning guidance; ``pi-zero-2w``
is the configuration this project's own display runs on. They are starting
points, not gospel — see docs/hardware-tuning.md (or the matrix-hardware-tuning
skill, if you are an AI agent) for how to adjust them for your panel.

Raspberry Pi 5 is NOT supported by rpi-rgb-led-matrix (different GPIO block).
"""

from dataclasses import dataclass
from pathlib import Path

DEVICE_TREE_MODEL = Path("/proc/device-tree/model")


@dataclass(frozen=True)
class HardwareProfile:
    name: str
    gpio_slowdown: int  # GPIO pacing; too low -> flicker/glitches, too high -> lower refresh
    pwm_bits: int  # color depth vs CPU; 8 is plenty for a 2-color board
    pwm_lsb_nanoseconds: int  # base PWM pulse width; affects ghosting/brightness balance
    limit_refresh_rate_hz: int  # cap refresh to stabilize timing and heat
    brightness: int  # percent; also the main thermal lever
    cpu_affinity: frozenset[int] | None  # keep the app off the core the library spins on


PROFILES: dict[str, HardwareProfile] = {
    # Tuned on the author's display (thermal-constrained, quad-core A53).
    "pi-zero-2w": HardwareProfile(
        name="pi-zero-2w",
        gpio_slowdown=3,
        pwm_bits=8,
        pwm_lsb_nanoseconds=130,
        limit_refresh_rate_hz=120,
        brightness=40,
        cpu_affinity=frozenset({0, 1, 2}),
    ),
    "pi-3": HardwareProfile(
        name="pi-3",
        gpio_slowdown=2,
        pwm_bits=11,
        pwm_lsb_nanoseconds=130,
        limit_refresh_rate_hz=150,
        brightness=60,
        cpu_affinity=frozenset({0, 1, 2}),
    ),
    "pi-4": HardwareProfile(
        name="pi-4",
        gpio_slowdown=4,
        pwm_bits=11,
        pwm_lsb_nanoseconds=116,
        limit_refresh_rate_hz=180,
        brightness=60,
        cpu_affinity=frozenset({0, 1, 2}),
    ),
}

DEFAULT_PROFILE = "pi-3"

_MODEL_SUBSTRINGS = [
    ("Zero 2", "pi-zero-2w"),
    ("Pi 3", "pi-3"),
    ("Pi 4", "pi-4"),
]


def read_pi_model(path: Path = DEVICE_TREE_MODEL) -> str | None:
    """The device-tree model string, or None off-Pi."""
    try:
        return path.read_text().rstrip("\x00").strip()
    except OSError:
        return None


def profile_for_model(model: str | None) -> HardwareProfile:
    if model:
        for needle, name in _MODEL_SUBSTRINGS:
            if needle in model:
                return PROFILES[name]
    return PROFILES[DEFAULT_PROFILE]


def resolve_profile(name: str, model: str | None = None) -> HardwareProfile:
    """Look up a profile by name, or detect one when ``name`` is 'auto'."""
    if name == "auto":
        return profile_for_model(model if model is not None else read_pi_model())
    try:
        return PROFILES[name]
    except KeyError:
        raise ValueError(
            f"unknown hardware profile {name!r}; options: {sorted(PROFILES)} or 'auto'"
        ) from None
