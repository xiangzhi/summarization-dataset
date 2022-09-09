import typing
from constructor.plan_methods.segment import Segment


class Plan(object):

    _dataline: str

    def __init__(self, picked_plans: typing.List[str]) -> None:
        self._dataline = ""
        self._segments = []
        for plan in picked_plans:
            self.add_segment(plan)

    def to_dataline(self) -> str:
        return self._dataline

    def add_segment(self, dataline:str) -> None:
        self._dataline += dataline
        self._segments.append(Segment.from_dataline(dataline))

    def get_start_times(self, act_name:str = None) -> typing.List[str]:
        return [s.start_times[0] for s in self._segments if (s.type == "ACT" and (act_name is None or act_name in s.names))]

    def get_same_as_prior(self) -> typing.List[str]:
        return [(n for n in s.names) for s in self._segments if s.type == "PREV"]

    def get_activity_names(self) -> typing.List[str]:
        return [ s.names[0] for s in self._segments if s.type == "ACT"]

