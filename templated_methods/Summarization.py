import typing
from .SummaryUtils import * 
import random
import numpy as np

random.seed(1234)
rng = np.random.default_rng(1234)

priority_list = [ 
    "taking_medication",
    "lunch",
    "breakfast",
    "dinner"
]
priority_weights = {
    "taking_medication": 10,
    "lunch": 6,
    "dinner": 5,
    "breakfast": 4,
}
priority_list = priority_weights.keys()

def verboseSummaryShortest(dict_routine: dict) -> typing.Tuple[str, str]:
    """ Most complete wordy summary shortest?
    """
    return "verbose-shorter", stringifyRoutineShortest(dict_routine)

def verboseSummary(dict_routine: dict) -> typing.Tuple[str, str]:
    """ Most complete wordy summary
    """
    return "verbose", stringifyRoutine(dict_routine)

def verboseUniqueActivity(dict_routine: dict) -> typing.Tuple[str, str]:
    """ Only talk about activity that happen once today.
    """
    unique_routine, repeated_act = pick_unique_routines_only(dict_routine)
    return "unique-act", stringifyRoutine(unique_routine)

def listActivitySummary(dict_routine: dict) -> typing.Tuple[str, str]:
    """ Summary that list the activities happen today
    """
    return "list", stringifyRoutineNamesTogether(dict_routine)

def listUniqueActivitySummary(dict_routine: dict) -> typing.Tuple[str, str]:
    """ Summary that only list unique activites that happen today.
    """
    unique_routine, repeated_act = pick_unique_routines_only(dict_routine)
    return "list-unique", stringifyRoutineNamesTogether(unique_routine)


def listNActivitiesByPrevalence(dict_routine: dict, n:int = 3) -> typing.Tuple[str, str]:
    """ Randomly pick three activities weighted by how often they happen + a priority list
    """

    # get frequency tables and update it with priority weights
    freq_table = np.array([act["times"] for act in dict_routine["frequencies"]])
    freq_table = freq_table + [ priority_weights[act["name"]] if act["name"] in priority_weights else 0 for act in dict_routine["frequencies"]]
    
    summary = "today, "

    chosen_activities = rng.choice(dict_routine["frequencies"], size=n, p=freq_table/np.sum(freq_table), replace=False)
    chosen_activity_name_sorted = []
    for act_name in dict_routine["schedule"]["activities"]:
        if act_name not in chosen_activity_name_sorted and act_name in [act["name"] for act in chosen_activities]:
            chosen_activity_name_sorted.append(act_name)

    for act_name in chosen_activity_name_sorted:
        summary += summarizeOneActivity(dict_routine, act_name)
    return f"list-{n}", summary

def listVariedActivitiesByPrevalence(dict_routine: dict) -> typing.List[typing.Tuple[str, str]]:
    num_act = len(dict_routine["frequencies"])
    summaries = []
    for i in range(1, num_act):
        summaries.append(listNActivitiesByPrevalence(dict_routine, n=i))
    return summaries

def listOnlyOneActivitySummary(dict_routine: dict) -> typing.Tuple[str, str]:
    """ List only one activity but according to a priority list (medication -> food -> random)
    """
    summary = "today, "

    for act_name in priority_list:
        if act_name in dict_routine["schedule"]["activities"]:
            return "list-single-priority", summary + summarizeOneActivity(dict_routine, act_name)
    
    # no activity in the priority list, pick a random activity
    randomly_picked = random.choice(dict_routine["schedule"]["activities"])
    return "list-single-priority", summary + summarizeOneActivity(dict_routine, randomly_picked)

