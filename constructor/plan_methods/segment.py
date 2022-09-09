

from dataclasses import dataclass
from tkinter.font import names
from tracemalloc import start
import typing
from dataclasses import dataclass
from constructor import utils


@dataclass
class Segment:

    type: str
    names: typing.List[str]
    start_times: typing.List[str]
    durations: typing.List[str]
    anomalous: typing.List[bool]

    @staticmethod
    def from_dataline(dataline: str) -> 'Segment':

        # skip
        if dataline.startswith("<SE>"):
            dataline = dataline[4:]

        seg_type = dataline[1:dataline.find(">")]
        names = []
        start_times = []
        durations = []
        anomalous = []

        chunks = dataline[dataline.find(">")+1:].split(">")
        if len(chunks) > 2:

            def set_value(key, value):
                if key == "NA":
                    names.append(value)
                elif key == "ST":
                    start_times.append(utils.str_to_datetime(value))
                elif key == "DU":
                    durations.append(utils.str_duration_to_timedelta(value))
                elif key == "AN":
                    anomalous.append(value)
                else:
                    raise ValueError(f"Invalid key {key}")

            next_key = chunks[0][1:]
            for idx in range(1, len(chunks) - 1):
                value = chunks[idx][:chunks[idx].find("<")]
                set_value(next_key, value.strip())
                next_key = chunks[idx][chunks[idx].find("<")+1:]
            set_value(next_key, chunks[-1].strip())
        
        return Segment(seg_type, names, start_times, durations, anomalous)
