from dataclasses import dataclass


@dataclass
class RenfeStop:
    stop_id: int
    stop_name: str
    stop_lat: float
    stop_lon: float
