from datetime import datetime, timedelta
import typing
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
            f"<END_TIME> {self.end.strftime('%H:%M')}",
        ]
        if self.anomalous:
            properties.append(f"<ANOMALY> {self.anomaly_reason if self.anomaly_reason else 'Unknown'}")
        if shuffle:
            random.shuffle(properties)
        return " ".join(properties)

    def get_start_time(self) -> str:
        return self.start.strftime('%H:%M')



class RoutineWrapper():

    _routine_info: typing.List[Event]

    def __init__(self, routine):

        self._routine_info = []
        self._day = routine["info"]["day"]

        self._routine = routine
        self._precompute_info()
    
    def _precompute_info(self):

        prev_start_time = None
        for i, act in enumerate(self._routine["schedule"]["activities"]):

            start_time_dt = datetime.strptime(self._routine["schedule"]["start_times"][i], "%H:%M")
            end_time_dt = datetime.strptime(self._routine["schedule"]["end_times"][i], "%H:%M")

            # correction for going across midnight:
            if prev_start_time is not None:
                if start_time_dt < prev_start_time:
                    start_time_dt += timedelta(days=1)
                    end_time_dt += timedelta(days=1)
            prev_start_time = start_time_dt

            self._routine_info.append(Event(act, start_time_dt, end_time_dt))

    def get_frequency(self, act_name:str) -> int:
        return len([act for act in self._routine_info if act.name == act_name])

    def get_first(self, act_name:str) -> Event:
        return self._routine_info[[act.name for act in self._routine_info].index(act_name)]

    def get_start_times(self, act_name: str) -> typing.List[datetime]:
        return [act.start for act in self._routine_info if act.name == act_name]

    def get_activity_list(self):
        return self._activity_list

    def add_activity(self, act_name:str, start_time, duration, remove_overlap=True, anomalous=False, anomaly_reason:str=""):

        if remove_overlap:
            remove_idx = []
            for idx in range(len(self._routine_info)):
                if self._routine_info[idx].start <= start_time + duration and self._routine_info[idx].start > start_time:
                    remove_idx.append(idx)
                if self._routine_info[idx].end > start_time and self._routine_info[idx].end < start_time + duration:
                    remove_idx.append(idx)
                if self._routine_info[idx].end > start_time + duration and self._routine_info[idx].start < start_time:
                    remove_idx.append(idx)
            # remove the events that overlap with the new activity
            self._routine_info = [self._routine_info[i] for i in range(len(self._routine_info)) if i not in remove_idx]


        insert_idx = len(self._routine_info)
        for idx, val in enumerate(self._routine_info):
            if val.start > start_time:
                insert_idx = idx
                break

        # code to verify there is no overlap before inserting activity
        if insert_idx < len(self._routine_info):
            # check if the event overlaps
            for idx in range(insert_idx):
                if self._routine_info[idx].end > start_time:
                    print("Activity overlaps!!!")
                    print(self._routine_info[idx])
                    print(start_time)
                    return False
            for idx in range(insert_idx, len(self._routine_info)):
                if self._routine_info[idx].start < start_time + duration:
                    print("Activity overlaps!!!")
                    print(self._routine_info[idx].start)
                    print(start_time + duration)
                    return False

        self._routine_info.insert(insert_idx, Event(act_name, start_time, start_time + duration, anomalous, anomaly_reason))
        return True

    def get_anomalous_activities(self) -> typing.List[typing.Union[int, Event]]:
        return [(idx, act) for idx, act in enumerate(self._routine_info) if act.anomalous]


    def generate_dataline(self, focus_activities: typing.List[str] = None) -> str:
        routine_txt = f'<DAY> {self._day} '
        for act in self._routine_info:
            if focus_activities is None or act.name in focus_activities:
                routine_txt += "<SEGMENT> "
                routine_txt += act.dataline()
                routine_txt += " "
        return routine_txt

    def has_activity(self, act_name:str) -> bool:
        for act in self._routine_info:
            if act.name == act_name:
                return True
        return False

    def have_all_activities(self, to_checked: typing.List[str]) -> bool:
        act_names = [act.name for act in self._routine_info]
        for act in to_checked:
            if act not in act_names:
                return False
        return True

    def have_at_least_one_of(self, to_checked: typing.List[str]) -> bool:
        act_names = [act.name for act in self._routine_info]
        for act in to_checked:
            if act in act_names:
                return True
        return False

    def none_of(self, to_checked: typing.List[str]) -> bool:
        return not self.have_at_least_one_of(to_checked)

    def get_events(self):
        return self._routine_info