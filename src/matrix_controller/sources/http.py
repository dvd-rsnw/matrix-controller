"""Fetches arrivals from a train API implementing docs/api-contract.md."""

import httpx
from pydantic import TypeAdapter

from matrix_controller.models import TrainArrival
from matrix_controller.sources import SourceError

_ARRIVALS = TypeAdapter(list[TrainArrival])


class HttpTrainSource:
    def __init__(
        self,
        url: str,
        timeout: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url = url
        self._client = httpx.AsyncClient(timeout=timeout, transport=transport)

    async def fetch(self) -> list[TrainArrival]:
        try:
            response = await self._client.get(self._url)
            response.raise_for_status()
            return _ARRIVALS.validate_json(response.content)
        except (httpx.HTTPError, ValueError) as exc:  # pydantic errors are ValueErrors
            raise SourceError(str(exc)) from exc

    async def close(self) -> None:
        await self._client.aclose()
