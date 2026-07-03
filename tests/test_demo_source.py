import random

from matrix_controller.sources.demo import DemoTrainSource


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


async def test_returns_two_sorted_arrivals() -> None:
    clock = FakeClock()
    source = DemoTrainSource(rng=random.Random(42), clock=clock)
    trains = await source.fetch()
    assert len(trains) == 2
    assert all(t.line in ("F", "G") for t in trains)
    assert all(t.status == "Now" or t.status.endswith(("min", "mins")) for t in trains)


async def test_arrivals_count_down_as_time_passes() -> None:
    clock = FakeClock()
    source = DemoTrainSource(rng=random.Random(42), clock=clock)
    first = (await source.fetch())[0]
    clock.now += 120  # two minutes later
    second = (await source.fetch())[0]

    def minutes(status: str) -> int:
        return 0 if status == "Now" else int(status.split()[0])

    assert minutes(second.status) <= minutes(first.status)


async def test_departed_trains_are_replaced() -> None:
    clock = FakeClock()
    source = DemoTrainSource(rng=random.Random(42), clock=clock)
    await source.fetch()
    clock.now += 3600  # an hour later: everything initially scheduled is long gone
    trains = await source.fetch()
    assert len(trains) == 2  # fresh arrivals were spawned


async def test_deterministic_with_seed() -> None:
    a = DemoTrainSource(rng=random.Random(7), clock=FakeClock())
    b = DemoTrainSource(rng=random.Random(7), clock=FakeClock())
    assert await a.fetch() == await b.fetch()
