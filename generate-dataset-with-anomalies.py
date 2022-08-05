import json
import os
from queue import Queue

import datetime
import typing
import random

from constructor.utils import functions
random.seed(42)
from constructor.utils import Routine, Event, WordGenerator
from constructor.templated_methods.summarization import summarize_one_type
from constructor.anomaly_detect import describe_anomalies
import numpy as np
import copy
import itertools

wg = WordGenerator("res/word_bank.yaml")

def generate_summaries_in_ref_for_one_type(routine: Routine, prev_routine: typing.List[Routine], type_name: str, sum_type:str) -> str:

    if not routine.has_activity(type_name):
        return f"the resident did not {wg.get_activity_verb(type_name)}. "
    else:
        summary = summarize_one_type(routine, type_name, wg=wg)

    # check how it is related to the past
    if len(prev_routine) > 0:

        prev_times = prev_routine[-1].get_start_times(type_name)
        curr_times = routine.get_start_times(type_name)

        if len(prev_times) > 0:
            # if they are similar
            # add some fuzzy logic here in the future.
            if functions.compare_time_lists(curr_times, prev_times, 60):
                summary = f"the resident {wg.get_activity_past_tense(type_name)} at "
                if sum_type == "verbose":
                    summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in curr_times])
                    summary += " which is "

                if functions.compare_time_lists(curr_times, prev_times, 30):
                    summary += f"the same time as {wg.get_relation_to_yesterday()}"
                else:
                    summary += f"about the same time as {wg.get_relation_to_yesterday()}. "

                summary += ". "                
            else:
                
                previous_day_anomalous = len([act for act in prev_routine[-1].get_events() if act.name == type_name and act.anomalous]) > 0

                if previous_day_anomalous:
                    summary = summary = f"the resident is back to {wg.get_activity_past_tense(type_name)} at "
                else:
                    summary = f"the resident {wg.get_activity_past_tense(type_name)} at "
                summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in curr_times])
                summary += " instead of "
                summary += functions.list_objects_in_str([t.strftime("%H:%M") for t in prev_times])
                summary += " like yesterday"
                if previous_day_anomalous:
                    summary += " which was an anomalous day"
                summary += ". "

    return summary



def generate_summaries_in_ref(routine: Routine, prior_routines: typing.List[Routine], prior_summaries: typing.List[str], focus_activities: typing.List[str] = [], sum_type: str = "short") -> typing.Tuple[str, str]:

    # generate the data line
    data_input = routine.generate_dataline(focus_activities)
    
    # base summary
    summary = ""

    # describe anomalous activities
    mentioned_activities, anomalous_summary = describe_anomalies(routine, wg)
    summary += anomalous_summary

    # remove mentioned_activities
    # TODO: we cannot handle two anomalous things right now. e.g. Brush teeth morning okay but evening is anomalous
    focus_activities = [act_name for act_name in focus_activities if routine.get_index(act_name) not in mentioned_activities]

    # talk about activities that didn't happen today together
    if len(focus_activities) > 0:
        missing_activities = [act_name for act_name in focus_activities if routine.get_index(act_name) == -1]
        if len(missing_activities) > 0:
            activities_in_str = functions.list_objects_in_str([wg.get_activity_verb(act) for act in missing_activities], split_word="nor")
            str_ = f"the resident did not {activities_in_str} today. "
            if len(prior_routines) > 0:
                prior_missing_activities = [act_name for act_name in missing_activities if prior_routines[-1].get_index(act_name) == -1]
                if prior_missing_activities == missing_activities:
                    str_ = random.choice(["again", "similar to yesterday", "like yesterday"]) + ", " + str_
            summary += str_ 
            # remove activities we talked about
            focus_activities = [act_name for act_name in focus_activities if routine.get_index(act_name) != -1]


    # sort by priority
    focus_activities.sort(key=lambda act: 0 if routine.get_frequency(act) == 0 else -1 * routine.get_first(act).start.timestamp(), )

    if sum_type != "verbose":
        # insert combine multiple activities that repeated
        act_happen_same_time_as_yesterday = []
        if len(prior_routines) > 0:
            for i, act in enumerate(focus_activities):
                today_st = routine.get_start_times(act)
                prev_st = prior_routines[-1].get_start_times(act)
                if len(today_st) > 0 and len(prev_st) > 0:
                    if functions.compare_time_lists(today_st, prev_st):
                        act_happen_same_time_as_yesterday.append(act)
                        focus_activities.remove(act)

        if len(act_happen_same_time_as_yesterday) > 0:
            act_in_verbs = [wg.get_activity_past_tense(act) for act in act_happen_same_time_as_yesterday]
            summary += "the resident " + functions.list_objects_in_str(act_in_verbs, split_word="and") +  " at the same time as "  + wg.get_relation_to_yesterday() + ". "

    for act_name in focus_activities:
        summary += generate_summaries_in_ref_for_one_type(routine, list(prior_routines), act_name, sum_type)


    # if TLDR, only one sentence is allowed
    if sum_type == "tldr":
        summary = summary.split(".")[0] + ". "

    # format the data_input_line
    model_input =f'{sum_type},"{data_input}","{prior_summaries[-1] if len(prior_summaries) > 0 else ""}","{summary}"\n'

    return summary, model_input


if __name__ == "__main__":

    dataset_name = "schedule-prev-anomaly-v1"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid"]:
        for persona in ["persona4", "persona-all"]:
            input_path = os.path.join("datasets/activity-schedule-json", f"{persona}-{type_}.json")
            lines = []
            dataset = ["type,data,prior,summary\n"]
            with open(input_path, "r") as f:
                lines = f.readlines()

            # --- anomaly injection ---- #
            anomaly_percent = 0.05 # 5% of the data is anomalous
            anomaly_idx = np.random.choice(len(lines), int(anomaly_percent * len(lines)), replace=False)

            # anomly data draw
            normal_data = {
                "start_time_mean" : datetime.datetime.strptime("15:00", "%H:%M"),
                "start_time_std" : datetime.timedelta(minutes=10),
                "duration_mean" : datetime.timedelta(minutes=90),
                "duration_std" : datetime.timedelta(minutes=30),
            }
            abnormal_data = {
                "start_time_mean" : datetime.datetime.strptime("21:00", "%H:%M"),
                "start_time_std" : datetime.timedelta(minutes=10),
                "duration_mean" : datetime.timedelta(minutes=90),
                "duration_std" : datetime.timedelta(minutes=30),
            }


            all_routines = []

            for i, line in enumerate(lines):
                routine = Routine(json.loads(line))

                if (routine._day+1)%7 != 0 and routine._day%7 != 0:
                    if i in anomaly_idx:
                        start_time = random.gauss(abnormal_data["start_time_mean"], abnormal_data["start_time_std"])
                        duration = random.gauss(abnormal_data["duration_mean"], abnormal_data["duration_std"])
                    else:
                        start_time = random.gauss(normal_data["start_time_mean"], normal_data["start_time_std"])
                        duration = random.gauss(normal_data["duration_mean"], normal_data["duration_std"])
                    routine.add_activity("working", start_time, duration=duration, anomalous=(i in anomaly_idx), anomaly_reason=("because the resident usually work around 15:00" if i in anomaly_idx else ""))
                all_routines.append(routine)
            
            activities = ["showering", "working", "breakfast", "lunch", "dinner"]

            for sum_type in ["tldr", "short", "verbose", "independent"]:
                for com_length in range(2, len(activities)):
                    for focus_activities in itertools.combinations(activities, com_length):
                        
                        prior_routines = Queue(maxsize=1)
                        prior_summaries = Queue(maxsize=1)

                        for routine in all_routines:
                            # generate the summary
                            summary, sample = generate_summaries_in_ref(routine, list(prior_routines.queue), list(prior_summaries.queue), copy.deepcopy(focus_activities), sum_type=sum_type)
                            dataset.append(sample)

                            # save for next
                            if sum_type != "independent":
                                if prior_summaries.full():
                                    prior_summaries.get()
                                    prior_routines.get()
                                prior_summaries.put(summary)
                                prior_routines.put(routine)


            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

