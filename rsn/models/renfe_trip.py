from dataclasses import dataclass
from datetime import datetime, time


@dataclass
class RenfeTrip():
    line: str
    train_id: int
    departure_time_str: str
    arrival_time_str: str
    duration: str
    accessibility: bool

    departure_time: time = None

    def __post_init__(self):
        if type(self.train_id) == str:
            self.train_id = int(self.train_id)

        self.departure_time = datetime.strptime(
            self.departure_time_str, '%H:%M').time()
