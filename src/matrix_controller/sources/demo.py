"""Synthetic arrivals so the board runs with no API at all (--demo mode)."""

import itertools
import random
import time
from collections.abc import Callable

from matrix_controller.models import TrainArrival

_EXPRESS_CHANCE = 0.25  # F trains only
_MIN_HEADWAY_S = 4 * 60
_MAX_HEADWAY_S = 9 * 60
_LINGER_S = 45  # how long a "Now" train stays on the board before departing

_Arrival = tuple[str, bool, float]  # (line, express, arrival monotonic time)


class DemoTrainSource:
    def __init__(
        self,
        rng: random.Random | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._rng = rng or random.Random()
        self._clock = clock or time.monotonic
        self._lines = itertools.cycle(["F", "G"])
        self._arrivals: list[_Arrival] = []
        for _ in range(3):
            self._spawn(self._clock())

    def _spawn(self, now: float) -> None:
        line = next(self._lines)
        express = line == "F" and self._rng.random() < _EXPRESS_CHANCE
        last = max((t for _, _, t in self._arrivals), default=now)
        self._arrivals.append(
            (line, express, last + self._rng.uniform(_MIN_HEADWAY_S, _MAX_HEADWAY_S))
        )

    async def fetch(self) -> list[TrainArrival]:
        now = self._clock()
        self._arrivals = [a for a in self._arrivals if a[2] > now - _LINGER_S]
        while len(self._arrivals) < 3:
            self._spawn(now)
        self._arrivals.sort(key=lambda a: a[2])
        board = []
        for line, express, arrival_time in self._arrivals[:2]:
            minutes = max(0, round((arrival_time - now) / 60))
            if minutes == 0:
                status = "Now"
            elif minutes == 1:
                status = "1 min"
            else:
                status = f"{minutes} mins"
            board.append(TrainArrival(line=line, status=status, express=express))
        return board

    async def close(self) -> None:
        return None
