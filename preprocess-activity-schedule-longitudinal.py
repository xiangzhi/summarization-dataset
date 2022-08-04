import json
import os

import yaml
from templated_methods.Summarization import *
import datetime

import random
random.seed(1323)


def extract_data_as_line(routine, focus_activities: typing.List[str]):
    routine_txt = f'<DAY> {routine["info"]["day"]} '
    for i, act_name in enumerate(routine["schedule"]["activities"]):
        act_name.strip()
        if act_name in focus_activities:
            routine_txt += f"<SEGMENT> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <END_TIME> {routine['schedule']['end_times'][i]} "
    return routine_txt


input_count_list = []
summary_count_list = []

class RoutineWrapper():

    def __init__(self, routine):
        self._routine = routine
        self._precompute_info()
    
    def _precompute_info(self):
        self._first_starttime = {}
        self._first_endtime = {}
        for i, act in enumerate(self._routine["schedule"]["activities"]):
            if act not in self._first_starttime:
                self._first_starttime[act] = self._routine["schedule"]["start_times"][i]
                self._first_endtime[act] = self._routine["schedule"]["end_times"][i]
        self._freq_table = {freq["name"]: freq for freq in self._routine["frequencies"]}

    def get_first_start_time(self, act:str) -> str:
        return self._first_starttime[act] 

    def get_frequency(self, act: str) -> int:
        return self._freq_table[act]["times"] if act in self._freq_table else 0




def times_similar(reference, target) -> typing.List[int]:

    mismatched = []
    for i, r in enumerate(reference):
        reference_time = datetime.datetime.strptime(r, "%H:%M")
        target_time = datetime.datetime.strptime(target[i], "%H:%M")
        if reference_time - target_time > datetime.timedelta(minutes=30):
            mismatched.append(i)
    return mismatched


def list_times(times: typing.List[str], split_word:str = "and") -> str:

    str_ = ""
    for i in range(len(times) - 1):
        str_ += times[i]
        if i == 0 and len(times) == 2:
            str_ += f" {split_word} "
        elif i < len(times) - 2:
            str_ += ", "
        elif i == len(times) - 2:
            str_ += f", {split_word} "
    str_ += times[-1]
    return str_

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


def generate_summaries_in_ref_to_yesterday_per_act(routine, prev_routine, focus_activity: str):

    if focus_activity not in routine["schedule"]["activities"]:
        summary = f"the resident did not {wv.get_activity_verb(focus_activity)}."
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
                summary = f"the resident did not {wv.get_activity_verb(focus_activity)}. "
            else:
                # check the times when they take it:
                mismatched_times = times_similar(today_med_times, prev_med_times)
                if len(mismatched_times) == 0:
                    if len(today_med_times) == 1:
                        summary = f"the resident {wv.get_activity_past_tense(focus_activity)} at the same time as {wv.get_relation_to_yesterday()}. "
                    else:
                        summary = f"the resident did not {wv.get_activity_past_tense(focus_activity)}. "
                else:
                    summary = f"the resident {wv.get_activity_past_tense(focus_activity)} at "
                    summary += list_times(today_med_times)
                    summary += " instead of "
                    summary += list_times(prev_med_times)
                    summary += " like yesterday. "
        elif freq_diff > 0:
            summary = summarizeOneActivity(routine, focus_activity)
        elif today_med_freq == 0:
            summary = f"the resident did not {wv.get_activity_past_tense(focus_activity)} today but did it for {pred_med_freq} {'time' if pred_med_freq == 1 else 'times'} yesterday at " + list_times(prev_med_times) + ". "
        elif freq_diff < 0:
            summary = f"the resident only {wv.get_activity_past_tense(focus_activity)} for {today_med_freq} {'time' if today_med_freq == 1 else 'times'} today at " + list_times(today_med_times) + \
                f" but did it {pred_med_freq} {'time' if pred_med_freq == 1 else 'times'} yesterday at " + list_times(prev_med_times) + ". "
        else:
            print("ERROR")            

    return summary


def generate_prev_ref_summaries(routine, prev_routine, prev_summary: str, focus_activities: typing.List[str]):
    
    # get the data line about activities we care about:
    data_input = extract_data_as_line(routine, focus_activities)

    # wrapper for easy access
    rw = RoutineWrapper(routine)

    # if none of the activities we care about happen today
    if len([act for act in routine["schedule"]["activities"] if act in focus_activities]) == 0:
        activities_in_str = list_times([wv.get_activity_verb(act) for act in focus_activities], split_word="nor")
        summary = f"the resident did not {activities_in_str} today. "
        
        # if the missing routines are the same as yesterday.
        if prev_routine is not None and len([act for act in prev_routine["schedule"]["activities"] if act in focus_activities]) == 0:
            summary = random.choice(["again", "similar to yesterday", "like yesterday"]) + ", " + summary
    else:
        summary = "today. "

        # we reorder the activites by two things. The first is the lack of, followed by the time
        focus_activities.sort(key=lambda act: 0 if rw.get_frequency(act) == 0 else int(rw.get_first_start_time(act)[:2]))

        for act in focus_activities:
            summary += generate_summaries_in_ref_to_yesterday_per_act(routine, prev_routine, act)
        
    return summary, f"{data_input},\"{prev_summary}\",\"{summary}\"\n"




if __name__ == "__main__":

    dataset_name = "longitudinal-schedule"
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

                    cur_summary, sample = generate_prev_ref_summaries(routine, prev_routine, prev_summary, act_list)
                    dataset.append(sample)
                    prev_summary = cur_summary
                    prev_routine = routine
                    prev_day = routine["info"]["day"] 

            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)

