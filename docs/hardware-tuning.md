# Hardware Tuning Guide

The display's low-level matrix rendering settings are pretuned per Raspberry Pi model and stored as named profiles in `src/matrix_controller/profiles.py`. The app auto-detects your Pi and applies the matching profile on startup. Every value can be overridden via environment variables without touching code, so you can experiment quickly. If you are an AI agent, see `.claude/skills/matrix-hardware-tuning/SKILL.md` instead.

## Profiles

Starting values from `src/matrix_controller/profiles.py`:

| Profile | gpio_slowdown | pwm_bits | pwm_lsb_ns | refresh cap | brightness |
|---|---|---|---|---|---|
| pi-zero-2w | 3 | 8 | 130 | 120 | 40 |
| pi-3 | 2 | 11 | 130 | 150 | 60 |
| pi-4 | 4 | 11 | 116 | 180 | 60 |

Each profile represents a balance point for its hardware: the Pi Zero 2W is thermally constrained and runs a narrower pipeline, so it keeps PWM bits low and caps refresh lower; the Pi 3 is middle-ground; the Pi 4 can run wider PWM and higher refresh. The values are starting points — if your panel flickers, ghosts, or the Pi throttles, you'll adjust them.

## What each setting does

**gpio_slowdown** paces GPIO signal timing. Faster Pi models output digital signals faster, which can confuse older panels or ones with long ribbon cables. Too low a value causes random flicker or glitched pixels (bits stuck in the wrong state); too high caps your refresh rate. It's your first lever when you see sparkle or glitches.

**pwm_bits** sets the number of bits per color channel during the PWM (pulse-width modulation) phase — the time spent toggling each pixel on and off to achieve brightness levels. 8 bits is 256 levels per channel; 11 bits is 2048. This board renders only 3 flat colors, so 8 bits is visually indistinguishable from 11 bits. You keep 11 only if your Pi has spare CPU headroom. Lowering pwm_bits gives you CPU and refresh back.

**pwm_lsb_nanoseconds** is the duration of the shortest PWM pulse, the unit step for brightness ramps. Lower values let you achieve higher refresh rates but can dim the low end of the brightness curve and cause ghosting on panels with slower response times. Raising it by 20–50 ns can eliminate ghost images if you see faint duplicates.

**limit_refresh_rate_hz** caps the refresh rate in Hertz, independent of how fast the Pi could theoretically scan the panel. This stabilizes timing (the driver stops thrashing) and reduces heat generation. It's especially useful in enclosures. Too high and you burn CPU and heat; too low and the panel might flicker. The refresh rate must stay well above 100 Hz to avoid visible flicker; the default profiles use 120–180 Hz and are unrelated to POLLING_INTERVAL, which controls only how often train data is fetched (default 15 s).

**brightness** is the master intensity knob — a percent from 1 to 100. This is your main lever for thermal control. Lowering brightness cuts power draw and heat significantly. In an enclosure or a summer setup, run 40–60% and cap refresh at 120–150 Hz. In open air with headroom, you can run higher.

## Troubleshooting by symptom

Change ONE variable at a time and test it for at least one full update cycle (15 seconds for this board). If you adjust multiple settings at once, you won't know which one fixed (or broke) things.

| Symptom | Try, in order |
|---|---|
| Random flicker, sparkle, wrong pixels | `MATRIX_GPIO_SLOWDOWN` +1 (max ~5) |
| Ghosting / faint duplicate glyphs | `MATRIX_PWM_LSB_NANOSECONDS` +20–50 |
| Visible brightness banding | `MATRIX_PWM_BITS` +1 (capped at 11; Pi 3/4 already at max, only Pi Zero 2W has headroom) |
| Stutter when the Pi is busy | add `isolcpus=3` to `/boot/cmdline.txt`, reboot (the library pins its update thread to core 3; the app already pins itself to cores 0–2) |
| Pi throttling / too hot | `MATRIX_BRIGHTNESS` −10, then `MATRIX_REFRESH_RATE_LIMIT` −30 |
| Dim or washed-out panel | raise `MATRIX_BRIGHTNESS`; verify PSU under-voltage first |

Once you find a stable set of values, record them in `.env`:

```bash
MATRIX_GPIO_SLOWDOWN=4
MATRIX_PWM_LSB_NANOSECONDS=150
MATRIX_BRIGHTNESS=50
MATRIX_REFRESH_RATE_LIMIT=120
```

The app loads them on every startup. You can also pin the profile with `MATRIX_HARDWARE_PROFILE=pi-4` if you want to lock in a profile and override only specific fields.

## Power

Under-voltage is a hard stop — no software tuning will fix a weak power supply. Each 64x32 panel draws roughly 4 A at full white (all LEDs on, max brightness). Two panels in series draw 8 A. Your Raspberry Pi also needs clean, isolated 5V.

**The fix:** provide a separate 5V supply rated for 8 A to the panel chain (via the input connectors on the first panel), and a separate 2.5 A supply to the Pi's Micro USB or USB-C input. Do NOT chain them. A flaky power supply causes throttling and heat as the Pi struggles; it's not a tuning problem.

**How to check:** Run `vcgencmd get_throttled` on the Pi, or use `python3 scripts/detect_hardware.py` — look for "under-voltage" flags in the output. Empty flags means you're good. If flags appear, add capacity to your PSU or isolate supplies.

## Isolating a CPU core

The rpi-rgb-led-matrix library runs a dedicated thread to scan the panel — it needs uninterrupted CPU time. By default it uses core 3 (the last core on a Pi 3 or Pi 4). The app already pins itself to cores 0–2, so the update thread and the app don't fight over the same core.

If you see stutter when the Pi is busy (background I/O, cron jobs, etc.), you can tell Linux to reserve core 3 entirely for the library using the kernel boot parameter `isolcpus=3`. This forces all other work onto cores 0–2.

**How to set it:**

1. Edit `/boot/cmdline.txt` on the Pi (on the SD card, or via `sudo nano /boot/cmdline.txt` on a live Pi).
2. Find the existing parameters (a single long line). At the end, before any `elevator=` or `quiet` flags, add `isolcpus=3`.
3. Example before: `console=serial0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes`
4. Example after: `console=serial0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes isolcpus=3`
5. Save and reboot.

After reboot, run `python3 scripts/detect_hardware.py` — it should report `"isolcpus": "3"`. If it does, the isolation is active. Your panel should no longer stutter during system load.
