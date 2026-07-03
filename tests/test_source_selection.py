import pytest

from matrix_controller.config import Settings
from matrix_controller.sources import SourceError, create_source
from matrix_controller.sources.demo import DemoTrainSource
from matrix_controller.sources.http import HttpTrainSource


def settings(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def test_auto_without_url_is_demo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRAIN_API_URL", raising=False)
    monkeypatch.delenv("MATRIX_SOURCE", raising=False)
    assert isinstance(create_source(settings()), DemoTrainSource)


def test_auto_with_url_is_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRIX_SOURCE", raising=False)
    monkeypatch.setenv("TRAIN_API_URL", "http://api.test/trains")
    assert isinstance(create_source(settings()), HttpTrainSource)


def test_api_without_url_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRAIN_API_URL", raising=False)
    monkeypatch.setenv("MATRIX_SOURCE", "api")
    with pytest.raises(SourceError, match="TRAIN_API_URL"):
        create_source(settings())
