from datetime import datetime, timedelta
import typing
from .utils.functions import timedelta_to_str
from dataclasses import dataclass
import random
random.seed(42)

key = {
    "name": "<NAME>",
    "start": "<START_TIME>",
    "end": "<END_TIME>",
}

@dataclass
class Event:
    name: str
    start: datetime
    end: datetime
    _duration: timedelta = None
    anomalous: bool = False
    anomaly_reason: str = None

    def dataline(self, shuffle:bool = True) -> str:
        properties = [
            f"<NAME> {self.name}",
            f"<START_TIME> {self.start.strftime('%H:%M')}",
            f"<DURATION> {self.get_duration_str(return_type='data_str')}",
            # f"<END_TIME> {self.end.strftime('%H:%M')}",
        ]
        if self.anomalous:
            properties.append(f"<ANOMALY> {self.anomaly_reason if self.anomaly_reason else 'Unknown'}")
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

        if return_type == "str":
            return timedelta_to_str(self.duration)
        elif return_type == "data_str":
            return f"{self.duration.seconds // 3600}:{self.duration.seconds % 3600 // 60}"
        if return_type == "fuzzy":
            
            if self.duration.seconds > (60*90):
                return "for a long time"
            elif self.duration.seconds > (60*50):
                return "for about 1 hour"
            elif self.duration.seconds > (60*25):
                return "for about 30 minutes"
            elif self.duration.seconds > (60*12):
                return "for about 15 minutes"
            else:
                return ""
        else:
            raise ValueError(f"Invalid return type {return_type}")


