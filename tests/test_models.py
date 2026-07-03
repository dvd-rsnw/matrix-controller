import pytest
from pydantic import ValidationError

from matrix_controller.models import TrainArrival


def test_parses_api_shape() -> None:
    arrival = TrainArrival.model_validate({"line": "F", "status": "5 mins", "express": False})
    assert (arrival.line, arrival.status, arrival.express) == ("F", "5 mins", False)


def test_express_defaults_false() -> None:
    assert TrainArrival(line="G", status="Now").express is False


def test_missing_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        TrainArrival.model_validate({"line": "F"})
