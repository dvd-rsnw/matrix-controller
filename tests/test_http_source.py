import httpx
import pytest

from matrix_controller.sources import SourceError
from matrix_controller.sources.http import HttpTrainSource

URL = "http://api.test/trains"


def source_returning(handler: httpx.MockTransport) -> HttpTrainSource:
    return HttpTrainSource(URL, transport=handler)


async def test_fetch_parses_arrivals() -> None:
    payload = [
        {"line": "F", "status": "5 mins", "express": False},
        {"line": "G", "status": "8 mins", "express": False},
    ]
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=payload))
    source = source_returning(transport)
    trains = await source.fetch()
    assert [t.line for t in trains] == ["F", "G"]
    await source.close()


async def test_http_error_raises_source_error() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(503))
    source = source_returning(transport)
    with pytest.raises(SourceError):
        await source.fetch()
    await source.close()


async def test_invalid_json_shape_raises_source_error() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"nope": 1}))
    source = source_returning(transport)
    with pytest.raises(SourceError):
        await source.fetch()
    await source.close()


async def test_network_failure_raises_source_error() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    source = source_returning(httpx.MockTransport(boom))
    with pytest.raises(SourceError):
        await source.fetch()
    await source.close()
