"""CLI entry point: ``python -m matrix_controller`` or ``matrix-controller``."""

import argparse
import asyncio
import contextlib
import signal
import sys

from matrix_controller import app
from matrix_controller.config import Settings
from matrix_controller.sources import SourceError


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="matrix-controller",
        description="LED matrix train arrival board (see README for configuration)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="run with synthetic data on the terminal simulator (no hardware, no API)",
    )
    return parser.parse_args(argv)


def build_settings(args: argparse.Namespace) -> Settings:
    settings = Settings()
    if args.demo:
        settings = settings.model_copy(update={"source": "demo", "driver": "terminal"})
    return settings


async def _run_until_signal(settings: Settings) -> None:
    loop = asyncio.get_running_loop()
    task = asyncio.ensure_future(app.run(settings))
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):  # e.g. Windows
            loop.add_signal_handler(sig, task.cancel)
    with contextlib.suppress(asyncio.CancelledError):
        await task


def main(argv: list[str] | None = None) -> int:
    settings = build_settings(parse_args(argv))
    try:
        with contextlib.suppress(KeyboardInterrupt):
            asyncio.run(_run_until_signal(settings))
    except SourceError as exc:
        # Config-time errors (e.g. MATRIX_SOURCE=api without TRAIN_API_URL)
        # fail fast with an actionable message instead of a traceback.
        # Runtime fetch errors are handled inside the loop and keep polling.
        print(f"matrix-controller: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
