from datetime import datetime, timedelta
import typing
from .utils.functions import timedelta_to_str
from dataclasses import dataclass
import random
random.seed(42)


@dataclass
class Event:
    name: str
    start: datetime = None
    end: datetime = None
    _duration: timedelta = None
    anomalous: bool = False
    anomaly_reason: str = None
    priority: int = 0

    def dataline(self, shuffle:bool = True) -> str:
        properties = [
            f"<NA> {self.name}",
            f"<ST> {self.start.strftime('%H:%M')}",
            f"<DU> {self.get_duration_str(return_type='data_str')}",
            # f"<END_TIME> {self.end.strftime('%H:%M')}",
        ]
        if self.anomalous:
            properties.append(f"<AN> {self.anomaly_reason if self.anomaly_reason else 'Unknown'}")
        if shuffle:
            random.shuffle(properties)
        return " ".join(properties)

    @property
    def duration(self) -> timedelta:
        return self._duration if self._duration else self.end - self.start

    @duration.setter
    def duration(self, duration: timedelta) -> None:
        self._duration = duration

    def get_start_time(self) -> str:
        return self.start.strftime('%H:%M')

    def get_end_time(self) -> str:
        return self.end.strftime('%H:%M')

    def get_duration_str(self, return_type:str = "str") -> str:

        if return_type == "str" or return_type == "fuzzy":
            return timedelta_to_str(self.duration, return_type)
        elif return_type == "data_str":
            return f"{self.duration.seconds // 3600:02d}:{self.duration.seconds % 3600 // 60:02d}"
        else:
            raise ValueError(f"Invalid return type {return_type}")


