import pytest

from matrix_controller.__main__ import build_settings, main, parse_args


def test_parse_args_demo_flag() -> None:
    assert parse_args(["--demo"]).demo is True
    assert parse_args([]).demo is False


def test_demo_flag_forces_demo_source_and_terminal_driver() -> None:
    settings = build_settings(parse_args(["--demo"]))
    assert settings.source == "demo"
    assert settings.driver == "terminal"


def test_startup_source_error_fails_fast(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("MATRIX_SOURCE", "api")
    monkeypatch.delenv("TRAIN_API_URL", raising=False)
    exit_code = main([])
    assert exit_code == 1
    assert "TRAIN_API_URL" in capsys.readouterr().err
