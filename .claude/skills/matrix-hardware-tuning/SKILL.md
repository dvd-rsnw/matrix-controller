---
name: matrix-hardware-tuning
description: Evaluate the best rpi-rgb-led-matrix settings (gpio_slowdown, pwm_bits, brightness, refresh cap, CPU isolation) for the Raspberry Pi and panel this display runs on. Use when setting up the display on new hardware, when the panel flickers/ghosts/stutters, or when the user asks which settings to use.
---

# Matrix Hardware Tuning

Pick and validate the display's low-level matrix settings for whatever
hardware it is running on.

## Step 1: Gather facts

If you have shell access on the Pi, run:

```bash
python3 scripts/detect_hardware.py
```

It prints JSON: Pi model, revision, cores, `mem_mb`, `isolcpus`, CPU governor,
throttle flags, and a `recommended_profile`. If you are NOT on the Pi, ask
the user for: Pi model, panel size/chain (this project: 2× 64x32), power
supply rating, and what symptom they see.

**If throttle flags show under-voltage:** stop tuning. No setting fixes a
weak power supply — the panel needs its own 5V supply (~4A per 64x32 panel
at full white), and the Pi its own.

## Step 2: Start from the profile

Apply the recommended profile first (`MATRIX_HARDWARE_PROFILE=<name>`, or
rely on auto-detection). Starting values, from `src/matrix_controller/profiles.py`:

| Profile | gpio_slowdown | pwm_bits | pwm_lsb_ns | refresh cap | brightness |
|---|---|---|---|---|---|
| pi-zero-2w | 3 | 8 | 130 | 120 | 40 |
| pi-3 | 2 | 11 | 130 | 150 | 60 |
| pi-4 | 4 | 11 | 116 | 180 | 60 |

Why these move the way they do:
- `gpio_slowdown` compensates for faster SoC GPIO. Faster Pi ⇒ higher value.
  Too low: flicker/glitched pixels. Too high: refresh drops.
- `pwm_bits` trades color depth for CPU/refresh. This board renders 3 flat
  colors — 8 bits is visually identical and much cheaper. Keep 11 only on
  Pis with headroom.
- `pwm_lsb_nanoseconds` is the base PWM pulse. Lower ⇒ higher refresh but
  dimmer low-end and possible ghosting on slow panels.
- `limit_refresh_rate_hz` stabilizes timing (and heat) instead of letting
  refresh float.
- `brightness` is the main thermal lever, especially in an enclosure.
- Longer chains divide refresh: this project's chain of 2 is already in the
  table; if experimenting with 3–4 panels, expect to lower the refresh cap
  and consider `pwm_bits=7-8`.

## Step 3: Iterate on symptoms

Change ONE variable at a time, via env vars (override a single value without
editing code): `MATRIX_GPIO_SLOWDOWN`, `MATRIX_PWM_BITS`,
`MATRIX_PWM_LSB_NANOSECONDS`, `MATRIX_REFRESH_RATE_LIMIT`, `MATRIX_BRIGHTNESS`.

| Symptom | Try, in order |
|---|---|
| Random flicker, sparkle, wrong pixels | `MATRIX_GPIO_SLOWDOWN` +1 (max ~5) |
| Ghosting / faint duplicate glyphs | `MATRIX_PWM_LSB_NANOSECONDS` +20–50 |
| Visible brightness banding | `MATRIX_PWM_BITS` +1 (capped at 11; Pi 3/4 already at max, only Pi Zero 2W has headroom) |
| Stutter when the Pi is busy | add `isolcpus=3` to `/boot/cmdline.txt`, reboot (the library pins its update thread to core 3; the app already pins itself to cores 0–2) |
| Pi throttling / too hot | `MATRIX_BRIGHTNESS` −10, then `MATRIX_REFRESH_RATE_LIMIT` −30 |
| Dim or washed-out panel | raise `MATRIX_BRIGHTNESS`; verify PSU under-voltage first |

## Step 4: Verify

1. `python3 scripts/detect_hardware.py` again — `throttled.flags` must be empty
   after ~10 minutes of running.
2. Watch the panel through one full poll cycle (15 s) — no flicker during
   redraw (the driver swaps frames on vsync, so a visible blink means GPIO
   timing problems, not the app).
3. Record the winning values in `.env` so they survive restarts.

## Hard limits

- Raspberry Pi 5 is **not supported** by rpi-rgb-led-matrix. Pi 4 or older.
- Run as root (GPIO access). The Docker setup already handles this.
- This project's geometry (128x32, `adafruit-hat`) is fixed in
  `src/matrix_controller/drivers/hardware.py`.
