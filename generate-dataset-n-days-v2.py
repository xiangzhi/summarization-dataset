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


def generate_summary_with_reference(routine: Routine, prior_routines: typing.List[Routine], prior_summaries: typing.List[str], properties: typing.List[str] = [], focus_activities: typing.List[str] = None, style: str = "sequential") -> typing.Tuple[str, str]:

    # generate the data line
    data_input = routine.generate_dataline(focus_activities)
    
    # cleanup
    focus_activities = routine.get_activity_names() if focus_activities is None else focus_activities

    summary_sentences = []
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
                if "start_time" not in properties or functions.compare_time_lists(today_st, prev_st, 61):
                    if "duration" not in properties or compare_duration(routine.get_events(act), prior_routines[-1].get_events(act)):
                        act_happen_same_time_as_yesterday.append(act)
    
    if len(routine.get_activity_names()) > 0 and len(act_happen_same_time_as_yesterday)/len(routine.get_activity_names()) > 0.5:
        # talk about the change
        summary_sentences.append("today is the same as yesterday, except")
        remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
        name = "they"
    elif len(act_happen_same_time_as_yesterday) > 1:
        daily_summary_sentences = templated_methods.stringify_routine_in_aggregate(routine, wg, [], focus_activity_names=act_happen_same_time_as_yesterday, name ="")
        summary_sentences.append(f"the resident {functions.list_objects_in_str([s[:-1] for s in daily_summary_sentences])} at the same time as yesterday.")
        # remaining activities
        summary_sentences.append("besides that,")
        name = "they"
        remaining_activities = [act_name for act_name in routine.get_activity_names() if act_name not in act_happen_same_time_as_yesterday]
    else:
        remaining_activities = routine.get_activity_names()
    
    # filter by focus
    remaining_activities = [act for act in remaining_activities if act in focus_activities]

    # summarize remaining activities.
    summary_sentences += templated_methods.stringiy_routine_sequentially_combine(routine, wg, properties, focus_activity_names=remaining_activities, name=name)

    # if it is short, try to find sentences that can fit in the summary.
    if style == "short":
        summary = ""
        for i in range(len(summary_sentences)):
            slen = len(summary_sentences[i])
            if (slen + len(summary)) <= MAX_LENGTH:
                summary += " " + summary_sentences[i]
            if len(summary) > MAX_LENGTH:
                break
        summary = summary.strip()
    else:
        summary = " ".join(summary_sentences)

    # special cases for noting
    if len(routine.get_activity_names()) == 0 or len(summary) == 0:
        summary = "the resident did not do anything today."

    # In case we have lingering sentences, find last . in the summary and cut.
    summary = summary[:summary.rfind(".")] + "."

    summary = utils.make_sentence_upper_case(summary)

    # format the data_input_line
    model_input =f'{style},"{data_input}","{prior_summaries[-1] if len(prior_summaries) > 0 else ""}","{summary}"\n'

    return summary, model_input

def generate_summary(routine: Routine, properties: typing.List[str] = [], focus_activities: typing.List[str] = None, style: str = "sequential") -> typing.Tuple[str, str]:

    # generate the data line
    data_input = routine.generate_dataline(focus_activities)
    
    # cleanup
    focus_activities = routine.get_activity_names() if focus_activities is None else focus_activities
    remaining_activities = routine.get_activity_names()
    remaining_activities = [act for act in remaining_activities if act in focus_activities]


    # summarize remaining activities.
    daily_summary_sentences = templated_methods.stringiy_routine_sequentially_combine(routine, wg, properties, focus_activity_names=remaining_activities, name="the resident")


    # if it is short, try to find sentences that can fit in the summary.
    if style == "short":
        summary = ""
        for i in range(len(daily_summary_sentences)):
            slen = len(daily_summary_sentences[i])
            if (slen + len(summary)) <= MAX_LENGTH:
                summary += " " + daily_summary_sentences[i]
            if len(summary) > MAX_LENGTH:
                break
        summary = summary.strip()
    else:
        summary = " ".join(daily_summary_sentences)

    # if style == "short":
    #     assert len(summary) <= MAX_LENGTH, f"The summary is too long: {summary}"

    # special cases for noting
    if len(routine.get_activity_names()) == 0 or len(summary) == 0:
        summary = "The resident did not do anything today."

    # In case we have lingering sentences, find last . in the summary and cut.
    summary = summary[:summary.rfind(".")] + "."

    summary = utils.make_sentence_upper_case(summary)

    # format the data_input_line
    model_input =f'{style},"{data_input}","","{summary}"\n'

    return summary, model_input

if __name__ == "__main__":

    dataset_name = "schedule-by-hour-examples"
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

            all_routines = [Routine(json.loads(l)) for l in lines]
            
            activity_count_list = [len(r.get_activity_names()) for r in all_routines]
            print("max activity count:", max(activity_count_list))
            print("min activity count:", min(activity_count_list))
            print("mean activity count:", np.mean(activity_count_list))

            # activity_count = {}
            # for routine in all_routines:
            #     for act in routine.get_activity_names():
            #         if act not in activity_count:
            #             activity_count[act] = 0
            #         activity_count[act] += 1
            
            # activity_count = list(activity_count.items())
            # activity_count.sort(key=lambda x: x[1], reverse=True)
            # focus_activities = [ a[0] for a in activity_count[:10]]
            focus_activities = None

            test_window = 3

            for i, routine in enumerate(all_routines):
                
                # clear the previous summary if window is full
                if i % test_window == 0:
                    prior_routines = Queue(maxsize=test_window-1)
                    prior_summaries = Queue(maxsize=test_window-1)

                #for ref in ["ref", "no"]:
                for ref in ["ref"]:
                    #for style in ["sequential", "short"]:
                    for style in ["sequential"]:
                        if ref == "ref":
                            summary, sample = generate_summary_with_reference(routine, list(prior_routines.queue), list(prior_summaries.queue), ["start_time", "duration"], copy.deepcopy(focus_activities), style=style)
                        else:
                            summary, sample = generate_summary(routine, ["start_time", "duration"], copy.deepcopy(focus_activities), style=style)
                        dataset.append(f"{ref}-{sample}")

                if prior_summaries.full():
                    prior_summaries.get()
                    prior_routines.get()
                prior_summaries.put(summary)
                prior_routines.put(routine)


            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

