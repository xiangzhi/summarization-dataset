from .event import Event
from datetime import datetime, timedelta
from time import time
import typing
import random
random.seed(42)


class Routine():

    _routine_info: typing.List[Event]
    _routine_name_list: typing.List[str]

    def __init__(self, routine, day = "0"):

        self._routine_info = []
        self._routine_name_list = []

        if routine is not None:
            self._day = routine["info"]["day"]

            self._routine = routine
            self._precompute_info()
        else:
            self._day = day

    def set_day(self, day: typing.Union[int, str]) -> None:
        if isinstance(day, int):
            day = str(day)
        self._day = day    

    def _precompute_info(self):

        prev_start_time = None
        for i, act in enumerate(self._routine["schedule"]["activities"]):

            start_time_dt = datetime.strptime(self._routine["schedule"]["start_times"][i], "%H:%M").replace(year=2022)
            end_time_dt = datetime.strptime(self._routine["schedule"]["end_times"][i], "%H:%M").replace(year=2022)

            # use the datetime to hack timedelta
            if "durations" in self._routine["schedule"]:
                duration_fake_time = datetime.strptime(self._routine["schedule"]["durations"][i], "%H:%M")
                duration = timedelta(hours=duration_fake_time.hour, minutes=duration_fake_time.minute)
            else:
                duration = end_time_dt - start_time_dt

            # --------------------------------------------------
            # unique code to handle leave and coming home:
            if act == "leave_home":
                # the next act should be come home
                end_time_dt = datetime.strptime(self._routine["schedule"]["start_times"][i+1], "%H:%M").replace(year=2022)
            elif act == "come_home":
                # the act of coming home is the same time.
                end_time_dt = start_time_dt
            # -------------------------------------------------

            # correction for going across midnight:
            if prev_start_time is not None:
                if start_time_dt < prev_start_time:
                    start_time_dt += timedelta(days=1)
                    end_time_dt += timedelta(days=1)
            prev_start_time = start_time_dt


            self._routine_info.append(Event(act, start_time_dt, end_time_dt, _duration=duration))

        self._routine_name_list = [act.name for act in self._routine_info]

    def get_frequency(self, act_name: str) -> int:
        return self._routine_name_list.count(act_name)

    def get_first(self, act_name: str) -> Event:
        idx = self.get_index(act_name)
        if idx < 0:
            raise ValueError(f"Event {act_name} not found")
        return self._routine_info[idx]

    def get_index(self, act_name: str) -> int:
        try:
            return self._routine_name_list.index(act_name)
        except ValueError:
            return -1

    def get_start_times(self, act_name: str, return_type:str = "datetime") -> typing.Union[typing.List[datetime], typing.List[str]]:
        if return_type == "datetime":
            return [act.start for act in self._routine_info if act.name == act_name]
        elif return_type == "str":
            return [act.start.strftime("%H:%M") for act in self._routine_info if act.name == act_name]

    def get_durations(self, act_name: str, return_type:str = "timedelta") -> typing.Union[typing.List[timedelta], typing.List[str]]:
        if return_type == "timedelta":
            return [act.end - act.start for act in self._routine_info if act.name == act_name]
        elif return_type == "str":
            return [act.get_duration_str() for act in self._routine_info if act.name == act_name]

    def get_activity_names(self):
        return self._routine_name_list

    def add_activity(self,
                     act_name: str,
                     start_time: typing.Union[str, datetime],
                     end_time: typing.Union[str, datetime] = None,
                     duration: typing.Union[str, timedelta] = None,
                     remove_overlap=True,
                     anomalous=False,
                     anomaly_reason: str = ""
                     ) -> None:

        if start_time is not None and isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M").replace(year=2022)
        if end_time is not None and isinstance(end_time, str):
            end_time = datetime.strptime(end_time, "%H:%M").replace(year=2022)

        if duration is None:
            duration = end_time - start_time
            if duration < timedelta(0):
                raise ValueError("End time is before start time")

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
            self._routine_name_list = [act.name for act in self._routine_info]

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

        # add to our datastructure.

        self._routine_info.insert(insert_idx, Event(act_name, start_time, end=start_time + duration, _duration=duration, anomalous= (anomalous or anomaly_reason != ""), anomaly_reason=anomaly_reason))
        self._routine_name_list.insert(insert_idx, act_name)

        return True

    def get_anomalous_activities(self) -> typing.List[typing.Union[int, Event]]:
        return [(idx, act) for idx, act in enumerate(self._routine_info) if act.anomalous]

    def generate_dataline(self, focus_activities: typing.List[str] = None) -> str:
        routine_txt = f'<DA> {self._day} '
        for act in self._routine_info:
            if focus_activities is None or act.name in focus_activities:
                routine_txt += "<SE> "
                routine_txt += act.dataline()
                routine_txt += " "
        return routine_txt

    def has_activity(self, act_name: str) -> bool:
        return act_name in self._routine_name_list

    def have_all_activities(self, to_checked: typing.List[str]) -> bool:
        for act in to_checked:
            if act not in self._routine_name_list:
                return False
        return True

    def have_at_least_one_of(self, to_checked: typing.List[str]) -> bool:
        for act in to_checked:
            if act in self._routine_name_list:
                return True
        return False

    def none_of(self, to_checked: typing.List[str]) -> bool:
        return not self.have_at_least_one_of(to_checked)

    def get_events(self, act_name:str = None):
        if act_name is not None:
            return [act for act in self._routine_info if act.name == act_name]
        return self._routine_info
