import pytest

from matrix_controller.config import Settings


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("TRAIN_API_URL", "POLLING_INTERVAL", "MATRIX_SOURCE", "MATRIX_DRIVER"):
        monkeypatch.delenv(var, raising=False)
    s = Settings(_env_file=None)
    assert s.train_api_url is None
    assert s.polling_interval == 15.0
    assert (s.source, s.driver, s.hardware_profile) == ("auto", "auto", "auto")
    assert s.matrix_overrides() == {}


def test_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRAIN_API_URL", "http://example.local:8000/trains")
    monkeypatch.setenv("POLLING_INTERVAL", "30")
    monkeypatch.setenv("MATRIX_DRIVER", "terminal")
    monkeypatch.setenv("MATRIX_BRIGHTNESS", "70")
    monkeypatch.setenv("MATRIX_REFRESH_RATE_LIMIT", "150")
    s = Settings(_env_file=None)
    assert s.train_api_url == "http://example.local:8000/trains"
    assert s.polling_interval == 30.0
    assert s.driver == "terminal"
    assert s.matrix_overrides() == {"brightness": 70, "limit_refresh_rate_hz": 150}


def test_resolved_source_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRAIN_API_URL", raising=False)
    monkeypatch.delenv("MATRIX_SOURCE", raising=False)
    assert Settings(_env_file=None).resolved_source() == "demo"
    monkeypatch.setenv("TRAIN_API_URL", "http://example.local/x")
    assert Settings(_env_file=None).resolved_source() == "api"


def test_explicit_source_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRAIN_API_URL", "http://example.local/x")
    monkeypatch.setenv("MATRIX_SOURCE", "demo")
    assert Settings(_env_file=None).resolved_source() == "demo"


def test_invalid_polling_interval_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLLING_INTERVAL", "0")
    with pytest.raises(ValueError):
        Settings(_env_file=None)
