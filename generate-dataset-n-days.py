import json
import os
from queue import Queue

import datetime
import typing
import random
from constructor import utils

from constructor.utils import functions
random.seed(42)
from constructor.utils import WordGenerator
from constructor import Routine, Event, templated_methods
from constructor.templated_methods import stringify_one_act_in_aggregate
from constructor.anomaly_detect import describe_anomalies
import numpy as np
import copy
import itertools

wg = WordGenerator("res/word_bank.yaml")

# def generate_summaries_in_ref_for_one_type(routine: Routine, prev_routine: typing.List[Routine], type_name: str, sum_type:str) -> str:

#     if not routine.has_activity(type_name):
#         return f"the resident did not {wg.get_activity_verb(type_name)}. "
#     else:
#         summary = stringify_one_act_in_aggregate(routine, wg, type_name, ["start_time"])

#     # check how it is related to the past
#     if len(prev_routine) > 0:

#         prev_times = prev_routine[-1].get_start_times(type_name)
#         curr_times = routine.get_start_times(type_name)

#         if len(prev_times) > 0:
#             # if they are similar
#             # add some fuzzy logic here in the future.
#             if functions.compare_time_lists(curr_times, prev_times, 60):
#                 summary = f"the resident {wg.get_activity_past_tense(type_name)} at "
#                 if sum_type == "verbose":
#                     summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in curr_times])
#                     summary += " which is "

#                 if functions.compare_time_lists(curr_times, prev_times, 30):
#                     summary += f"the same time as {wg.get_relation_to_yesterday()}"
#                 else:
#                     summary += f"about the same time as {wg.get_relation_to_yesterday()}. "

#                 summary += ". "                
#             else:
                
#                 previous_day_anomalous = len([act for act in prev_routine[-1].get_events() if act.name == type_name and act.anomalous]) > 0

#                 if previous_day_anomalous:
#                     summary = summary = f"the resident is back to {wg.get_activity_past_tense(type_name)} at "
#                 else:
#                     summary = f"the resident {wg.get_activity_past_tense(type_name)} at "
#                 summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in curr_times])
#                 summary += " instead of "
#                 summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in prev_times])
#                 summary += " like yesterday"
#                 if previous_day_anomalous:
#                     summary += " which was an anomalous day"
#                 summary += ". "

#     return summary


def generate_summary_with_reference(routine: Routine, prior_routines: typing.List[Routine], prior_summaries: typing.List[str], properties: typing.List[str] = [], focus_activities: typing.List[str] = None, style: str = "sequential") -> typing.Tuple[str, str]:

    # generate the data line
    data_input = routine.generate_dataline(focus_activities)
    
    # cleanup
    focus_activities = routine.get_activity_names() if focus_activities is None else focus_activities

    summary = ""

    # talk about activities that happened at the same time as yesterday
    
    # find activities that repeated at about the same time.
    act_happen_same_time_as_yesterday = []
    if len(prior_routines) > 0:
        for i, act in enumerate(focus_activities):
            today_st = routine.get_start_times(act)
            prev_st = prior_routines[-1].get_start_times(act)
            if len(today_st) > 0 and len(prev_st) > 0:
                if functions.compare_time_lists(today_st, prev_st, 30):
                    act_happen_same_time_as_yesterday.append(act)
    
    if len(act_happen_same_time_as_yesterday)/len(routine.get_activity_names()) > 0.5:
        # talk about the change
        summary += "today is similar to yesterday. except the resident"
        remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
    elif len(act_happen_same_time_as_yesterday) > 0:
        if style == "sequential":
            daily_summary_sentences = templated_methods.stringiy_routine_sequentially(routine, wg, [], focus_activity_names=act_happen_same_time_as_yesterday, name ="")
        elif style == "aggregate":
            daily_summary_sentences = templated_methods.stringify_routine_in_aggregate(routine, wg, [], focus_activity_names=act_happen_same_time_as_yesterday, name ="")
        else:
            raise ValueError(f"style {style} is not supported")
        summary += f"the resident {functions.list_objects_in_str([s[:-1] for s in daily_summary_sentences])} at the same time as "  + wg.get_relation_to_yesterday() + ". "
        # remaining activities
        summary += "besides that, the resident "
        remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
    else:
        summary += "the resident "
        remaining_activities = routine.get_activity_names()
    
    # summarize remaining activities.
    if style == "sequential":
        daily_summary_sentences = templated_methods.stringiy_routine_sequentially(routine, wg, properties, focus_activity_names=remaining_activities, name ="")
    elif style == "aggregate":
        daily_summary_sentences = templated_methods.stringify_routine_in_aggregate(routine, wg, properties, focus_activity_names=remaining_activities, name ="")
    else:
        raise ValueError(f"style {style} is not supported")
    # put it in words
    summary += functions.list_objects_in_str([s[:-1] for s in daily_summary_sentences])

    # format the data_input_line
    model_input =f'{style},"{data_input}","{prior_summaries[-1] if len(prior_summaries) > 0 else ""}","{summary}"\n'

    return summary, model_input


if __name__ == "__main__":

    dataset_name = "schedule-prev-anomaly-window-v1"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid", "example"]:
        for persona in ["persona4", "persona-all"]:
            input_path = os.path.join("datasets/activity-schedule-json", f"{persona}-{type_}.json")
            lines = []
            dataset = ["type,data,prior,summary\n"]
            if not os.path.exists(input_path):
                continue
            with open(input_path, "r") as f:
                lines = f.readlines()

            all_routines = [Routine(json.loads(l)) for l in lines]
            focus_activities = None

            test_window = 3

            for i, routine in enumerate(all_routines):
                
                # clear the previous summary if window is full
                if i % test_window == 0:
                    prior_routines = Queue(maxsize=1)
                    prior_summaries = Queue(maxsize=1)

                for style in ["sequential", "aggregate"]:
                    summary, sample = generate_summary_with_reference(routine, list(prior_routines.queue), list(prior_summaries.queue), ["start_time", "duration"], copy.deepcopy(focus_activities), style=style)
                    dataset.append(sample)

                if prior_summaries.full():
                    prior_summaries.get()
                    prior_routines.get()
                prior_summaries.put(summary)
                prior_routines.put(routine)


            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

