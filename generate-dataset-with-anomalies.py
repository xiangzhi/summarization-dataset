import json
import os
from queue import Queue

import yaml
from templated_methods.Summarization import *
import datetime

import random

from utils import functions
random.seed(1323)
import utils
from utils.RoutineWrapper import RoutineWrapper, Event

key = {
    "<NAME>": "activities",
    "<START_TIME>": "start_times",
    "<END_TIME>": "end_times",
    "<DURATION>": "durations",
}

def extract_data_as_line(routine, focus_activities: typing.List[str]):
    routine_txt = f'<DAY> {routine["info"]["day"]} '
    for i, act_name in enumerate(routine["schedule"]["activities"]):
        act_name.strip()
        if act_name in focus_activities:
            routine_txt += "<SEGMENT> "
            for prop in random.sample(key.keys(), len(key.keys())):
                routine_txt += f"{prop} {routine['schedule'][key[prop]][i]} "
    return routine_txt


input_count_list = []
summary_count_list = []


def times_similar(reference, target) -> typing.List[int]:

    mismatched = []
    for i, r in enumerate(reference):
        reference_time = datetime.datetime.strptime(r, "%H:%M")
        target_time = datetime.datetime.strptime(target[i], "%H:%M")
        if reference_time - target_time > datetime.timedelta(minutes=30):
            mismatched.append(i)
    return mismatched

class WordVariation():

    def __init__(self) -> None:
        with open("word_bank.yaml", 'r') as f:
            self._word_bank = yaml.safe_load(f)

    def get_activity_past_tense(self, act_name: str) -> str:
            return random.choice(self._word_bank["past"][act_name])

    def get_activity_verb(self, act_name: str) -> str:
            return random.choice(self._word_bank["verb"][act_name])

    def get_relation_to_yesterday(self) -> str:
        return random.choice(["yesterday", "the day before"])

wv = WordVariation()


def summarize_one_act_type(routine: RoutineWrapper, type_name: str, name:str = "the resident"):
    
    summary = f"{name} " + wv.get_activity_past_tense(type_name) + " at "
    act_start_times = [act.get_start_time() for act in routine.get_events() if act.name == type_name]
    summary += utils.list_objects_in_str(act_start_times, split_word="and")
    return summary + ". "


def generate_summaries_in_ref_for_one_type(routine: RoutineWrapper, prev_routine: typing.List[RoutineWrapper], type_name: str) -> str:

    if not routine.has_activity(type_name):
        return f"the resident did not {wv.get_activity_verb(type_name)}. "
    else:
        summary = summarize_one_act_type(routine, type_name)

    # check how it is related to the past
    if len(prev_routine) > 0:

        prev_times = prev_routine[-1].get_start_times(type_name)
        curr_times = routine.get_start_times(type_name)

        if len(prev_times) > 0:
            # if they are similar
            if functions.compare_time_lists(curr_times, prev_times):
                summary = f"the resident {wv.get_activity_past_tense(type_name)} at the same time as {wv.get_relation_to_yesterday()}. "
            elif functions.compare_time_lists(curr_times, prev_times, 60):
                summary = f"the resident {wv.get_activity_past_tense(type_name)} at about the same time as {wv.get_relation_to_yesterday()}. "
            else:
                
                previous_day_anomalous = len([act for act in prev_routine[-1].get_events() if act.name == type_name and act.anomalous]) > 0

                if previous_day_anomalous:
                    summary = summary = f"the resident is back to {wv.get_activity_past_tense(type_name)} at "
                else:
                    summary = f"the resident {wv.get_activity_past_tense(type_name)} at "
                summary += utils.list_objects_in_str([t.strftime("%H:%M") for t in curr_times])
                summary += " instead of "
                summary += utils.list_objects_in_str([t.strftime("%H:%M") for t in prev_times])
                summary += " like yesterday"
                if previous_day_anomalous:
                    summary += " which was an anomalous day"
                summary += ". "

    return summary



def generate_summaries_in_ref(routine: RoutineWrapper, prior_routines: typing.List[RoutineWrapper], prior_summaries: typing.List[str], focus_activities: typing.List[str] = [], anomalous_activities: typing.List[str] = []) -> typing.Tuple[str, str]:

    # generate the data line
    data_input = routine.generate_dataline(focus_activities)
    
    summary = ""

    mentioned_activities = []
    wv = WordVariation()

    # if there is an abnormal activity,
    if len(routine.get_anomalous_activities()) > 0:
        act: Event
        for (idx, act) in routine.get_anomalous_activities():
            summary += ("the resident " + wv.get_activity_past_tense(act.name) + " at " + act.get_start_time() + " today.")
            summary += " this is anomalous"
            mentioned_activities.append(act.name)
            if act.anomaly_reason is not None:
                summary += act.anomaly_reason
            summary += ". "
    
    # if all the activities we care about doesn't exist today
    if len(focus_activities) > 0 and routine.none_of(focus_activities):
        activities_in_str = utils.list_objects_in_str([wv.get_activity_verb(act) for act in focus_activities], split_word="nor")
        str_ = f"the resident did not {activities_in_str} today. "
        
        if len(prior_routines) > 0 and prior_routines[-1].none_of(focus_activities):
            str_ = random.choice(["again", "similar to yesterday", "like yesterday"]) + ", " + str_
        
        summary += str_ 
    else:
        # remove mentioned activities:
        focus_activities = [act for act in focus_activities if act not in mentioned_activities]
        # sort by priority
        focus_activities.sort(key=lambda act: 0 if routine.get_frequency(act) == 0 else routine.get_first(act).start.timestamp())

        # insert combine multiple activities that repeated
        act_happen_same_time_as_yesterday = []
        if len(prior_routines) > 0:
            for i, act in enumerate(list(focus_activities)):
                today_st = routine.get_start_times(act)
                prev_st = prior_routines[-1].get_start_times(act)
                if len(today_st) > 0 and len(prev_st) > 0:
                    if functions.compare_time_lists(today_st, prev_st):
                        act_happen_same_time_as_yesterday.append(act)
                        focus_activities.remove(act)

        if len(act_happen_same_time_as_yesterday) > 0:
            act_in_verbs = [wv.get_activity_past_tense(act) for act in act_happen_same_time_as_yesterday]
            summary += "the resident " + utils.list_objects_in_str(act_in_verbs, split_word="and") +  " at the same time as "  + wv.get_relation_to_yesterday() + ". "


        for act_name in focus_activities:
            summary += generate_summaries_in_ref_for_one_type(routine, list(prior_routines), act_name)


    # format the data_input_line
    model_input =f'"{data_input}","{prior_summaries[-1] if len(prior_summaries) > 0 else ""}","{summary}"\n'

    return summary, model_input


if __name__ == "__main__":

    dataset_name = "schedule-prev-anomaly-v1"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid"]:
        for persona in ["persona4", "persona-all"]:
            input_path = os.path.join("datasets/activity-schedule-json", f"{persona}-{type_}.json")
            lines = []
            dataset = ["text,prior,summary\n"]
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
                routine = RoutineWrapper(json.loads(line))

                if (routine._day+1)%7 != 0 and routine._day%7 != 0:
                    if i in anomaly_idx:
                        start_time = random.gauss(abnormal_data["start_time_mean"], abnormal_data["start_time_std"])
                        duration = random.gauss(abnormal_data["duration_mean"], abnormal_data["duration_std"])
                    else:
                        start_time = random.gauss(normal_data["start_time_mean"], normal_data["start_time_std"])
                        duration = random.gauss(normal_data["duration_mean"], normal_data["duration_std"])
                    routine.add_activity("working", start_time, duration, anomalous=(i in anomaly_idx), anomaly_reason=" because the resident usually work around 15:00")
                all_routines.append(routine)
            
            for focus_activities in [["working"], ["working", "taking_medication"], ["breakfast","lunch","dinner"],["breakfast","lunch","dinner","working"]]:
                
                prior_routines = Queue(maxsize=1)
                prior_summaries = Queue(maxsize=1)

                for routine in all_routines:
                    # generate the summary
                    summary, sample = generate_summaries_in_ref(routine, list(prior_routines.queue), list(prior_summaries.queue), copy.deepcopy(focus_activities))
                    dataset.append(sample)

                    # save for next
                    if prior_summaries.full():
                        prior_summaries.get()
                        prior_routines.get()
                    prior_summaries.put(summary)
                    prior_routines.put(routine)


            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

