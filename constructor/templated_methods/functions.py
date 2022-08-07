
from datetime import timedelta
import typing

from ..routine import Routine
from ..utils import functions, WordGenerator



def stringifyRoutineSequentially(routine: Routine, wg: WordGenerator, properties: typing.List[str], name: str = "the resident") -> typing.List[str]:

    summary = []
    for act in routine.get_events():
        str_ = ""
        str_ += f"{name} {wg.get_activity_past_tense(act.name)}"
        if "start_time" in properties:
            str_ += " at "
            str_ += act.get_start_time()
        if "duration" in properties:
            str_ += " for "
            str_ += act.get_duration_str()
        str_ += "."
        summary.append(str_.strip())
    return summary


def stringifyRoutineInAggregate(routine: Routine, wg: WordGenerator, properties: typing.List[str] = [], combined: typing.List[str] = [], name: str = "the resident") -> typing.List[str]:

    summary = []

    # get all the activities
    unique_activity_names = set(routine.get_activity_names())
    # sort by the start_time
    unique_activity_names = sorted(unique_activity_names, key=lambda x: routine.get_first(x).start)

    for act_name in unique_activity_names:
        str_ = f"{name} {wg.get_activity_past_tense(act_name)}"
        if "start_time" in properties:
            str_ += " at "
            str_ += functions.list_objects_in_str(routine.get_start_times(act_name, return_type="str"))
        if "duration" in properties:
            str_ += " for "
            if "duration" in combined:
                combined_duration = timedelta(0) 
                for d in routine.get_durations(act_name):
                    combined_duration += d
                str_ += functions.timedelta_to_str(combined_duration)
            else:
                str_ += functions.list_objects_in_str(routine.get_durations(act_name, return_type="str"))
        str_ += "."
        summary.append(str_.strip())
    return summary
