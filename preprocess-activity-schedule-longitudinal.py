import json
import os

import yaml
from templated_methods.Summarization import *
import datetime

import random

from utils import functions
random.seed(1323)
import utils
from utils.Routine import Routine

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

class WordGenerator():

    def __init__(self) -> None:
        with open("word_bank.yaml", 'r') as f:
            self._word_bank = yaml.safe_load(f)

    def get_activity_past_tense(self, act_name: str) -> str:
            return random.choice(self._word_bank["past"][act_name])

    def get_activity_verb(self, act_name: str) -> str:
            return random.choice(self._word_bank["verb"][act_name])

    def get_relation_to_yesterday(self) -> str:
        return random.choice(["yesterday", "the day before"])

wg = WordGenerator()


def generate_summaries_in_ref_to_yesterday_per_act(routine, prev_routine, focus_activity: str):

    if focus_activity not in routine["schedule"]["activities"]:
        summary = f"the resident did not {wg.get_activity_verb(focus_activity)}."
    else:
        summary = summarizeOneActivity(routine, focus_activity)

    # if similar as yesterday, say it's similar
    if prev_routine is not None:

        # get the start times of of the activity
        prev_med_times = [prev_routine["schedule"]["start_times"][i] for i,a in enumerate(prev_routine["schedule"]["activities"]) if a == focus_activity]
        today_med_times = [routine["schedule"]["start_times"][i] for i,a in enumerate(routine["schedule"]["activities"]) if a == focus_activity]
        pred_med_freq =  len(prev_med_times)
        today_med_freq =  len(today_med_times)

        freq_diff = today_med_freq - pred_med_freq
        if freq_diff == 0:
            # if they haven't do the event, today or yesterday.
            if today_med_freq == 0:
                summary = f"the resident did not {wg.get_activity_verb(focus_activity)}. "
            else:
                # check the times when they take it:
                time_deltas = utils.get_timedeltas(today_med_times, prev_med_times)
                if len([ t for t in time_deltas if t > 60]) == 0:
                    if len([ t for t in time_deltas if t > 30]) == 0:
                        summary = f"the resident {wg.get_activity_past_tense(focus_activity)} at the same time as {wg.get_relation_to_yesterday()}. "
                    else:
                        summary = f"the resident {wg.get_activity_past_tense(focus_activity)} at about the same time as {wg.get_relation_to_yesterday()}. "
                else:
                    summary = f"the resident {wg.get_activity_past_tense(focus_activity)} at "
                    summary += utils.list_objects_in_str(today_med_times)
                    summary += " instead of "
                    summary += utils.list_objects_in_str(prev_med_times)
                    summary += " like yesterday. "
        elif freq_diff > 0:
            summary = summarizeOneActivity(routine, focus_activity)
        elif today_med_freq == 0:
            summary = f"the resident did not {wg.get_activity_past_tense(focus_activity)} today but did it for {pred_med_freq} {'time' if pred_med_freq == 1 else 'times'} yesterday at " + utils.list_objects_in_str(prev_med_times) + ". "
        elif freq_diff < 0:
            summary = f"the resident only {wg.get_activity_past_tense(focus_activity)} for {today_med_freq} {'time' if today_med_freq == 1 else 'times'} today at " + utils.list_objects_in_str(today_med_times) + \
                f" but did it {pred_med_freq} {'time' if pred_med_freq == 1 else 'times'} yesterday at " + utils.list_objects_in_str(prev_med_times) + ". "
        else:
            print("ERROR")            

    return summary


def generate_prev_ref_summaries(routine, prev_routine, prev_summary: str, focus_activities: typing.List[str]):
    
    # get the data line about activities we care about:
    data_input = extract_data_as_line(routine, focus_activities)

    # wrapper for easy access
    rw = Routine(routine)
    if prev_routine is not None:
        prw = Routine(prev_routine)
    else:
        prw = None

    # if none of the activities we care about happen today
    if len([act for act in routine["schedule"]["activities"] if act in focus_activities]) == 0:
        activities_in_str = utils.list_objects_in_str([wg.get_activity_verb(act) for act in focus_activities], split_word="nor")
        summary = f"the resident did not {activities_in_str} today. "
        
        # if the missing routines are the same as yesterday.
        if prev_routine is not None and len([act for act in prev_routine["schedule"]["activities"] if act in focus_activities]) == 0:
            summary = random.choice(["again", "similar to yesterday", "like yesterday"]) + ", " + summary
    else:
        summary = "today. "

        # we reorder the activites by two things. The first is the lack of, followed by the time
        focus_activities.sort(key=lambda act: 0 if rw.get_frequency(act) == 0 else int(rw.get_first_start_time(act)[:2]))

       
        act_happen_same_time_as_yesterday = []
        if prev_routine is not None:
            for i, act in enumerate(list(focus_activities)):
                today_st = rw.get_start_times_of_event(act)
                prev_st = prw.get_start_times_of_event(act)
                if functions.compare_time_lists(today_st, prev_st) == 0:
                    act_happen_same_time_as_yesterday.append(act)
                    focus_activities.remove(act)

        if len(act_happen_same_time_as_yesterday) > 0:
            act_in_verbs = [wg.get_activity_past_tense(act) for act in act_happen_same_time_as_yesterday]
            summary += "the resident " + utils.list_objects_in_str(act_in_verbs, split_word="and") +  " at the same time as "  + wg.get_relation_to_yesterday() + ". "

        for act in focus_activities:
            summary += generate_summaries_in_ref_to_yesterday_per_act(routine, prev_routine, act)
        
    return summary, f"{data_input},\"{prev_summary}\",\"{summary}\"\n"




if __name__ == "__main__":

    dataset_name = "schedule-prev-day-ref-v4"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid"]:
        for persona in ["persona4", "persona-all"]:
            input_path = os.path.join("datasets/activity-schedule-json", f"{persona}-{type_}.json")
            lines = []
            dataset = ["text,prior,summary\n"]
            with open(input_path, "r") as f:
                lines = f.readlines()

            for act_list in [["taking_medication"], ["taking_medication","lunch"], ["lunch", "dinner","breakfast"], ["breakfast","taking_medication"]]:

                prev_summary = ""
                prev_routine = None
                prev_day = None
                
                for line in lines:
                    routine = json.loads(line)

                    if prev_day is None or routine["info"]["day"] < prev_day:
                        prev_summary = ""
                        prev_routine = None

                    cur_summary, sample = generate_prev_ref_summaries(routine, prev_routine, prev_summary, copy.deepcopy(act_list))
                    dataset.append(sample)
                    prev_summary = cur_summary
                    prev_routine = routine
                    prev_day = routine["info"]["day"] 

            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

