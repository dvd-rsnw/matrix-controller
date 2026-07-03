"""Train data sources and source selection."""

from typing import TYPE_CHECKING, Protocol

from matrix_controller.models import TrainArrival

if TYPE_CHECKING:
    from matrix_controller.config import Settings


class SourceError(Exception):
    """A source could not produce arrivals (network, bad payload, missing config)."""


class TrainSource(Protocol):
    async def fetch(self) -> list[TrainArrival]: ...

    async def close(self) -> None: ...


def create_source(settings: "Settings") -> TrainSource:
    if settings.resolved_source() == "api":
        if not settings.train_api_url:
            raise SourceError("MATRIX_SOURCE=api requires TRAIN_API_URL to be set")
        from matrix_controller.sources.http import HttpTrainSource

        return HttpTrainSource(settings.train_api_url)
    from matrix_controller.sources.demo import DemoTrainSource

    return DemoTrainSource()
