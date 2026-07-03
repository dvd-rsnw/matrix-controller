#!/usr/bin/env python3
"""Report Raspberry Pi facts relevant to LED-matrix tuning, as JSON.

Usage:  python3 scripts/detect_hardware.py

Stdlib-only so it runs on a bare Pi before the project is installed. Used by
the matrix-hardware-tuning skill (and curious humans) to pick a hardware
profile. Keep the model->profile map in sync with
src/matrix_controller/profiles.py.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

PROFILE_MAP = [("Zero 2", "pi-zero-2w"), ("Pi 3", "pi-3"), ("Pi 4", "pi-4")]
DEFAULT_PROFILE = "pi-3"

# Bit meanings for vcgencmd get_throttled (see Raspberry Pi docs).
THROTTLE_FLAGS = {
    0: "under-voltage now",
    1: "arm frequency capped now",
    2: "throttled now",
    3: "soft temperature limit now",
    16: "under-voltage occurred since boot",
    17: "arm frequency capped since boot",
    18: "throttling occurred since boot",
    19: "soft temperature limit occurred since boot",
}


def _read(path: Path) -> str | None:
    try:
        return path.read_text().rstrip("\x00").strip()
    except OSError:
        return None


def _throttle_state() -> dict[str, object] | None:
    if not shutil.which("vcgencmd"):
        return None
    try:
        out = subprocess.run(
            ["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=5
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"throttled=(0x[0-9a-fA-F]+)", out)
    if not match:
        return None
    raw = int(match.group(1), 16)
    return {
        "raw": match.group(1),
        "flags": [text for bit, text in THROTTLE_FLAGS.items() if raw >> bit & 1],
    }


def detect(root: Path = Path("/")) -> dict[str, object]:
    model = _read(root / "proc/device-tree/model")

    revision = None
    cpuinfo = _read(root / "proc/cpuinfo") or ""
    match = re.search(r"^Revision\s*:\s*(\S+)", cpuinfo, re.MULTILINE)
    if match:
        revision = match.group(1)

    mem_mb = None
    meminfo = _read(root / "proc/meminfo") or ""
    match = re.search(r"^MemTotal:\s*(\d+)\s*kB", meminfo, re.MULTILINE)
    if match:
        mem_mb = int(match.group(1)) // 1024

    isolcpus = None
    cmdline = _read(root / "proc/cmdline") or ""
    match = re.search(r"isolcpus=(\S+)", cmdline)
    if match:
        isolcpus = match.group(1)

    recommended = DEFAULT_PROFILE
    notes: list[str] = []
    if model:
        for needle, name in PROFILE_MAP:
            if needle in model:
                recommended = name
                break
        else:
            if "Pi 5" in model:
                notes.append(
                    "Raspberry Pi 5 is not supported by rpi-rgb-led-matrix; "
                    "this display needs a Pi 4 or older."
                )
            notes.append(f"no profile for {model!r}; defaulting to {DEFAULT_PROFILE}")
    else:
        notes.append(f"not a Raspberry Pi (no device-tree model); defaulting to {DEFAULT_PROFILE}")
    if isolcpus is None:
        notes.append(
            "isolcpus not set — for steadier refresh add 'isolcpus=3' to /boot/cmdline.txt"
        )

    return {
        "model": model,
        "revision": revision,
        "cores": os.cpu_count(),
        "mem_mb": mem_mb,
        "isolcpus": isolcpus,
        "governor": _read(root / "sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
        "throttled": _throttle_state(),
        "recommended_profile": recommended,
        "notes": notes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="/", help="filesystem root (for tests)")
    args = parser.parse_args(argv)
    print(json.dumps(detect(Path(args.root)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
