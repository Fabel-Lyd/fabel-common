from dataclasses import dataclass


@dataclass(frozen=True)
class OrderResponse:
    location: str
