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

MAX_LENGTH = 140

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

def generate_summary_base(
        routine: Routine, 
        middle_proc: typing.Callable, 
        prior_routines: typing.List[Routine],
        prior_summaries: typing.List[str],
        properties: typing.List[str] = [],
        focus_activities: typing.List[str] = None, 
        style: str = "normal"
    ) -> typing.Tuple[str, str]:


    # validate the parameters
    focus_activities = routine.get_activity_names() if focus_activities is None else focus_activities

    # pass to some kind of location functions and get the names of the remaining activities.
    if middle_proc is not None:
        sentences, remaining_activities = middle_proc(routine, prior_routines, prior_summaries, properties, focus_activities, style)
    else:
        sentences = []
        remaining_activities = focus_activities

    # summarize the remaining activities if any:
    sentences +=  templated_methods.stringify_routines_sequentially_by_hour(routine, wg, properties, focus_activity_names=remaining_activities, name="the resident")

    # if the style is suppose to be short, cut it and then try to find sentences that can fit
    if style == "short":
        # note, the first sentence is always in the summary just in case it got super long.
        summary = sentences[0]
        for i in range(1, len(sentences)):
            slen = len(sentences[i])
            if (slen + len(summary)) <= MAX_LENGTH:
                summary += " " + sentences[i]
            if len(summary) > MAX_LENGTH:
                break
        summary = summary.strip()
    else:
        summary = " ".join(sentences)

    # ---- POST PROCESSING ---- #

    # cut lingering sentences & clean up
    summary = summary[:summary.rfind(".")] + "."
    summary = utils.make_sentence_upper_case(summary)

    if len(routine.get_activity_names()) == 0 or len(summary) == 0:
        summary = "The system did not detect any activity."

    # ---- END POST PROCESSING ---- #

    # generate the dataline and sample row 
    data_input = routine.generate_dataline(focus_activities)
    sample_row =f'{style},"{data_input}","{prior_summaries[-1] if len(prior_summaries) > 0 else  ""}","{summary}"\n'

    return summary, sample_row


def generate_summary_with_reference(routine: Routine, prior_routines: typing.List[Routine], prior_summaries: typing.List[str], properties: typing.List[str] = [], focus_activities: typing.List[str] = None, style: str = "normal") -> typing.Tuple[str, str]:

    def past_refrence_func(routine, prior_routines, prior_summaries, properties, focus_activities, style):

        sentences = []
        name = "the resident"
    
        def remove_minutes(time_list):
            for i in range(len(time_list)):
                time_list[i] = time_list[i].replace(minute=0)
            return time_list

        def compare_duration(today, prev):

            if len(today) != len(prev):
                return False
            for i in range(0, len(today)):
                if today[i].get_duration_str("fuzzy") != prev[i].get_duration_str("fuzzy"):
                    return False
            return True     

        # find activities that repeated at about the same time slots.
        act_happen_same_time_as_yesterday = []
        if len(prior_routines) > 0:
            for i, act in enumerate(focus_activities):
                today_st = remove_minutes(routine.get_start_times(act))
                prev_st = remove_minutes(prior_routines[-1].get_start_times(act))
                if len(today_st) > 0 and len(prev_st) > 0:
                    if "start_time" not in properties or functions.compare_time_lists(today_st, prev_st, 0):
                        if "duration" not in properties or compare_duration(routine.get_events(act), prior_routines[-1].get_events(act)):
                            act_happen_same_time_as_yesterday.append(act)
    
        if len(routine.get_activity_names()) > 0 and len(act_happen_same_time_as_yesterday)/len(routine.get_activity_names()) > 0.5:
            # talk about the change
            sentences.append("today is the same as yesterday, except")
            remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
            name = "they"
        elif len(act_happen_same_time_as_yesterday) > 1:
            daily_summary_sentences = templated_methods.stringify_routine_in_aggregate(routine, wg, [], focus_activity_names=act_happen_same_time_as_yesterday, name ="")
            sentences.append(f"the resident {functions.list_objects_in_str([s[:-1] for s in daily_summary_sentences])} at the same time as yesterday.")
            # remaining activities
            sentences.append("besides that,")
            name = "they"
            remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
        else:
            remaining_activities = routine.get_activity_names()

        return sentences, remaining_activities


    return generate_summary_base(
        routine,
        past_refrence_func,
        prior_routines,
        prior_summaries,
        properties,
        focus_activities,
        style
    )


def generate_summary(routine: Routine, properties: typing.List[str] = [], focus_activities: typing.List[str] = None, style: str = "normal") -> typing.Tuple[str, str]:

    return generate_summary_base(routine, None, [], [], properties, focus_activities, style)


if __name__ == "__main__":

    dataset_name = "schedule-by-hour"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid", "example"]:
        for persona in ["persona4", "persona-all","individual0"]:
        #for pid in range(0,20):
            #persona = f"individual{pid}"
            max_act = 0
            input_path = os.path.join("datasets/activity-schedule-json-v3", f"{persona}-{type_}.json")
            lines = []
            dataset = ["type,data,prior,summary\n"]
            if not os.path.exists(input_path):
                continue
            with open(input_path, "r") as f:
                lines = f.readlines()

            # generating variables
            focus_activities = None # None is all
            summary_window = 3 # how many days to look back at
            
            # (1) get all routines for the data file
            all_routines = [Routine(json.loads(l)) for l in lines]
            # (2) go through each style
            for style in ["normal", "short"]:
                # (3) whether to reference to the past
                for ref in ["ref", "no"]:
                    # (4) go through each routine and generate summary
                    for i, routine in enumerate(all_routines):

                        # clear the prior summaries if window is full
                        if i % summary_window == 0:
                            prior_routines = Queue(maxsize=summary_window-1)
                            prior_summaries = Queue(maxsize=summary_window-1)
                        # set the day to the window
                        routine.set_day(i % summary_window + 1)
                        # generate summaries
                        if ref == "ref":
                            summary, sample = generate_summary_with_reference(routine, list(prior_routines.queue), list(prior_summaries.queue), ["start_time", "duration"], copy.deepcopy(focus_activities), style=style)
                        else:
                            summary, sample = generate_summary(routine, ["start_time", "duration"], copy.deepcopy(focus_activities), style=style)
                        # add to dataset
                        dataset.append(f"{ref}-{sample}")

                        # if summary is full, pop oldest. 
                        if prior_summaries.full():
                            prior_summaries.get()
                            prior_routines.get()
                        prior_summaries.put(summary)
                        prior_routines.put(routine)

            # (5) save to dataset
            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

