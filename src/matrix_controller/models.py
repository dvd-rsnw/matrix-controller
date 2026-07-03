"""Data model for arrivals crossing the API boundary (see docs/api-contract.md)."""

from pydantic import BaseModel


class TrainArrival(BaseModel):
    line: str
    status: str
    express: bool = False
