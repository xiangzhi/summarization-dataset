
from datetime import timedelta
import typing

from ..routine import Routine
from ..utils import functions, WordGenerator
from constructor import utils



def stringiy_routine_sequentially(routine: Routine, wg: WordGenerator, properties: typing.List[str], focus_activity_names:typing.List[str] = None, name: str = "the resident") -> typing.List[str]:

    summary = []
    for act in routine.get_events():
        if focus_activity_names is not None and act.name not in focus_activity_names:
            continue
        str_ = ""
        str_ += f"{name} {wg.get_activity_past_tense(act.name)}"
        if "start_time" in properties:
            str_ += " at "
            str_ += act.get_start_time()
        if "duration" in properties and act.name != "came_home":
            duration_str = act.get_duration_str()
            if duration_str:
                str_ += " for " + duration_str
        str_ += "."
        summary.append(str_.strip())
    return summary


def stringify_one_act_in_aggregate(routine: Routine, wg: WordGenerator, act_name: str, properties: typing.List[str] = [], combined: typing.List[str] = [], name: str = "the resident") -> str:
    str_ = f"{name} {wg.get_activity_past_tense(act_name)}"
    if "count" in properties:
        str_ += " for "
        count = routine.get_frequency(act_name)
        str_ += f"{count} time{'s' if count > 1 else ''}"
    if "start_time" in properties:
        str_ += " at "
        str_ += functions.list_objects_in_str(routine.get_start_times(act_name, return_type="str"))
    if "duration" in properties and act_name != "came_home":
        if "duration" in combined:
            combined_duration = timedelta(0) 
            for d in routine.get_durations(act_name):
                combined_duration += d
            if combined_duration > timedelta(0):
                str_ += f" for {functions.timedelta_to_str(combined_duration)}"
        else:
            durations = [d for d in routine.get_durations(act_name, return_type='str') if d]
            if len(durations) > 0:
                str_ += f" for {functions.list_objects_in_str(durations)}"
    return (str_ + ". ").strip()


def stringify_routine_in_aggregate(routine: Routine, wg: WordGenerator, properties: typing.List[str] = [], combined: typing.List[str] = [], focus_activity_names:typing.List[str] = [], name: str = "the resident") -> typing.List[str]:

    summary = []

    # get all the activities
    unique_activity_names = set(routine.get_activity_names())

    # if there is a focus, filter out
    if focus_activity_names is not None and len(focus_activity_names) > 0:
        unique_activity_names = unique_activity_names.intersection(focus_activity_names)

    # sort by the start_time
    unique_activity_names = sorted(unique_activity_names, key=lambda x: routine.get_first(x).start)

    for act_name in unique_activity_names:
        summary.append(stringify_one_act_in_aggregate(routine, wg, act_name, properties, combined, name).strip())
    return summary


def stringiy_routine_sequentially_combine(routine: Routine, wg: WordGenerator, properties: typing.List[str], focus_activity_names:typing.List[str] = None, name: str = "the resident") -> typing.List[str]:

    summary = []
    focus_activity_names = focus_activity_names or routine.get_activity_names()

    # go through each time
    first_start_time = routine.get_events()[0].start
    first_time = True

    for num_hour in range(first_start_time.hour, 24):
        num_hour = num_hour % 24
        str_ = ""
        if "start_time" in properties:
            str_ += f"at {num_hour:02d}:00, "
        str_ += name if first_time else "they"
        str_ += " "
        act_in_hour = [e for e in routine.get_events() if e.start.hour == num_hour and e.name in focus_activity_names]
        if len(act_in_hour) == 0:
            continue
        
        # get all activity sentencs:
        act_sentences = []
        for act in act_in_hour:
            act_str_ = wg.get_activity_past_tense(act.name)
            if "duration" in properties:
                act_str_ += " " + act.get_duration_str("fuzzy")
            act_sentences.append(act_str_.strip())
        str_ += functions.list_objects_in_str(act_sentences)
        str_ += "."
        summary.append(str_.strip())
        first_time = False
    return summary