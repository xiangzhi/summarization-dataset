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
        return self.end - self.start

    def get_start_time(self) -> str:
        return self.start.strftime('%H:%M')

    def get_end_time(self) -> str:
        return self.end.strftime('%H:%M')

    def get_duration_str(self, return_type:str = "str") -> str:

        duration = self.end - self.start
        if return_type == "str":
            return timedelta_to_str(duration)
        elif return_type == "data_str":
            return f"{duration.seconds // 3600}:{duration.seconds % 3600 // 60}"
        else:
            raise ValueError(f"Invalid return type {return_type}")


