import enum
import numpy as np
import copy
from datetime import datetime

from ..utils import WordGenerator
from ..utils import functions
from ..routine import Routine


def convert_to_duration_str(duration_arr):
    if("0" in duration_arr[0]):
        # no hours only minutes
        if("0" in duration_arr[1][0]):
            if(str(duration_arr[1][1]) == "1"):
                return str(duration_arr[1][1]) + " minute"
            else:
                return str(duration_arr[1][1]) + " minutes"
        else:
            return str(duration_arr[1]) + " minutes"
    else:
        hours = ""
        minutes = ""
        # hours present
        if(duration_arr[0] == "1"):
            hours = "1 hour"
        else:
            hours = duration_arr[0] + " hours"

        # check minutes
        if("0" in duration_arr[1][0]):
            if(str(duration_arr[1][1]) == "1"):
                minutes = str(duration_arr[1][1]) + " minute"
                return hours + " and " + minutes
            else:
                minutes = str(duration_arr[1][1]) + " minutes"
                return hours + " and " + minutes
        else:
            minutes = str(duration_arr[1]) + " minutes"
            return hours + " and " + minutes


def getPastTenseActivity(activity):
    if(activity == "going to the bathroom"):
        return "went to the bathroom"
    elif(activity == "breakfast"):
        return "had breakfast"
    elif(activity == "vaccuum cleaning"):
        return "vacuum cleaned"
    elif(activity == "brushing teeth"):
        return "brushed their teeth"
    elif(activity == "computer work"):
        return "worked on the computer"
    elif(activity == "listening to music"):
        return "listened to music"
    elif(activity == "showering"):
        return "showered"
    elif(activity == "reading"):
        return "read"
    elif(activity == "dinner"):
        return "had dinner"
    elif(activity == "watching tv"):
        return "watched tv"
    elif(activity == "playing music"):
        return "played music"
    elif(activity == "taking medication"):
        return "took medication"
    elif(activity == "laundry"):
        return "did laundry"
    elif(activity == "kitchen cleaning"):
        return "cleaned the kitchen"
    elif(activity == "getting out of bed"):
        return "got up from bed"
    elif(activity == "come home"):
        return "came home"
    elif(activity == "wash dishes"):
        return "washed dishes"
    elif(activity == "getting dressed"):
        return "got dressed"
    elif(activity == "leave home"):
        return "left home"
    elif(activity == "sleeping"):
        return "slept"
    elif(activity == "take out trash"):
        return "took out trash"
    elif(activity == "cleaning"):
        return "cleaned the house"
    elif(activity == "lunch"):
        return "had lunch"
    elif(activity == "socializing"):
        return "socialized"
    else:
        print("missing verb:" + activity)
        return activity


def stringifyRoutine(dict_routine, name: str = "the resident") -> str:

    str_ = ""
    for i, act_name in enumerate(dict_routine["schedule"]["activities"]):
        str_ += " At " + dict_routine["schedule"]["start_times"][i] + "," + f" {name} " + \
            getPastTenseActivity(" ".join(act_name.split("_"))) + " for " + \
            convert_to_duration_str(dict_routine["schedule"]["durations"][i].split(":")) + "."
    return str_


def stringifyRoutineShortest(dict_routine, name: str = "the resident") -> str:

    str_ = ""
    for i, act_name in enumerate(dict_routine["schedule"]["activities"]):
        str_ += f" {name} {getPastTenseActivity(' '.join(act_name.split('_')))} " + \
            f"from {dict_routine['schedule']['start_times'][i]} to {dict_routine['schedule']['end_times'][i]}."
    return str_


def stringifyRoutineNamesTogether(dict_routine, name: str = "the resident") -> str:
    """ This method combines all the given activity together.
    """

    str_ = f"today, {name} "
    for i, act_name in enumerate(dict_routine["schedule"]["activities"]):
        str_ += getPastTenseActivity(" ".join(act_name.split("_")))
        if i == len(dict_routine["schedule"]["activities"]) - 2:
            str_ += ", and "
        elif i < len(dict_routine["schedule"]["activities"]) - 2:
            str_ += ", "
    return str_


def summarize_one_type(routine: Routine, type_name: str, name: str = "the resident", wg: WordGenerator = None) -> str:
    
    if wg is None:
        wg = WordGenerator()

    summary = f"{name} " + wg.get_activity_past_tense(type_name) + " at "
    act_start_times = [act.get_start_time() for act in routine.get_events() if act.name == type_name]
    summary += functions.list_objects_in_str(act_start_times, split_word="and")
    return summary + ". "


def summarizeOneActivity(dict_routine, activity_name: str, name: str = "the resident") -> str:
    str_ = f"{name} "
    started = False

    # get the frequencies of this activity
    act_frequencies = next(act for act in dict_routine["frequencies"] if act["name"] == activity_name)["times"]

    act_index = 0
    for i, act_name in enumerate(dict_routine["schedule"]["activities"]):
        if act_name == activity_name:
            if not started:
                str_ += getPastTenseActivity(" ".join(act_name.split("_")))
                str_ += f' at {dict_routine["schedule"]["start_times"][i]}'
                started = True
            else:
                if act_frequencies == 2:
                    str_ += " and "
                elif act_index < (act_frequencies - 1):
                    str_ += ", "
                elif act_index == (act_frequencies - 1):
                    str_ += ", and "
                str_ += f'{dict_routine["schedule"]["start_times"][i]}'
            act_index += 1
    str_ += ". "
    return str_


def pick_unique_routines_only(routines):
    routines = copy.deepcopy(routines)
    repeated_activities = []
    for act in routines["frequencies"]:
        if act["times"] > 1:
            repeated_activities.append(act["name"])
    schedule_obj = routines["schedule"]
    remove_idx = []
    for i, a in enumerate(schedule_obj["activities"]):
        if a in repeated_activities:
            remove_idx.append(i)
    for i in reversed(remove_idx):
        del schedule_obj["activities"][i]
        del schedule_obj["start_times"][i]
        del schedule_obj["end_times"][i]
        del schedule_obj["durations"][i]
        del schedule_obj["locations"][i]
    routines["schedule"] = schedule_obj
    return routines, repeated_activities
