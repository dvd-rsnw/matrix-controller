# Agent Guide

LED matrix train arrival board: polls a JSON API (or generates demo data)
and renders NYC subway arrivals on a 128x32 RGB LED matrix — or a
pixel-accurate ANSI simulation in your terminal.

## Setup and everyday commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"        # no hardware deps; works on any machine

python3 -m pytest              # full test suite
ruff check . && ruff format .  # lint + format
mypy                           # strict type check
python3 -m matrix_controller --demo   # run the board in your terminal
```

## The one rule that matters

**`rgbmatrix` (the LED hardware library) cannot be installed on dev
machines.** It may only be imported lazily inside
`src/matrix_controller/drivers/hardware.py` (and the availability probe in
`drivers/__init__.py`). Everything else must import, run, and pass tests
without it. If you add code that touches the hardware, keep it behind the
`DisplayDriver` interface and test the logic as pure functions
(see `matrix_options_kwargs`).

## Map

- `src/matrix_controller/canvas.py` — PixelBuffer; ALL drawing goes through it
- `src/matrix_controller/rendering/` — shapes, text, and the TrainBoard layout
- `src/matrix_controller/fonts.py` — BDF rasterizer (fonts in `assets/fonts/`)
- `src/matrix_controller/drivers/` — terminal (ANSI) and hardware outputs
- `src/matrix_controller/sources/` — http (real API) and demo (synthetic)
- `src/matrix_controller/profiles.py` — per-Pi-model matrix settings
- `src/matrix_controller/config.py` — every env var, documented in README
- `scripts/detect_hardware.py` — stdlib-only; keep its profile map in sync
  with `profiles.py`
- `docs/api-contract.md` — the JSON shape a backend must serve

## Rendering changes and golden frames

Board layout is snapshot-tested: frames render to ASCII art in
`tests/golden/`. After an intentional visual change run
`python3 -m pytest --update-golden`, then LOOK at the regenerated frames and
include them in your commit. An unreviewed golden update is a review reject.

## Hardware tuning

Use the `matrix-hardware-tuning` skill
(`.claude/skills/matrix-hardware-tuning/SKILL.md`) when asked about flicker,
ghosting, brightness, or setting up new hardware.

## Constraints

- Editable install required (`pip install -e .`): fonts resolve relative to
  the repo root.
- Matrix geometry (128x32, two chained panels, adafruit-hat) is intentionally
  NOT configurable.
- Python ≥3.11. Keep `ruff check`, `ruff format --check`, `mypy`, and
  `pytest` green — CI runs exactly those.
