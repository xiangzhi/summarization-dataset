import json
import os
from templated_methods.Summarization import *
import datetime

def extract_data_as_line(routine, focus_activities: typing.List[str]):
    routine_txt = f'<DAY> {routine["info"]["day"]} '
    for i, act_name in enumerate(routine["schedule"]["activities"]):
        act_name.strip()
        if act_name in focus_activities:
            routine_txt += f"<SEGMENT> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <END_TIME> {routine['schedule']['end_times'][i]} "
    return routine_txt


def generate_potential_topics(routine):
    # as an initial test, we only learn to talk about activities that happen at least twice per day.

    potential_topics = 

    for i, act_name in enumerate(routine["schedule"]["activities"]):
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} <DURATION> {routine['schedule']['durations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <LOCATION> {routine['schedule']['locations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <LOCATION> {routine['schedule']['locations'][i]} ")
        if act_name not in repeated_activities:
            picked_plans.append(str(idx + 2))
        idx += 6
    for i, act_name in enumerate(routine["frequencies"]):
        potential_topics.append(f"<SEGMENT> <FREQUENCIES> <NAME> {act_name} <TIMES> {routine['frequencies'][act_name]} ")
        idx += 1





def generate_potential_topics(routine, repeated_activities, randomize: bool = True):
    plan_str = "<unk> <blank> <s> </s> "
    picked_plans = []
    idx = 4
    potential_topics = []
    for i, act_name in enumerate(routine["schedule"]["activities"]):
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} <DURATION> {routine['schedule']['durations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <LOCATION> {routine['schedule']['locations'][i]} ")
        potential_topics.append(f"<SEGMENT> <ACTIVITY> <NAME> {act_name} <END_TIME> {routine['schedule']['end_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <LOCATION> {routine['schedule']['locations'][i]} ")
        if act_name not in repeated_activities:
            picked_plans.append(str(idx + 2))
        idx += 6
    for i, act_name in enumerate(routine["frequencies"]):
        potential_topics.append(f"<SEGMENT> <FREQUENCIES> <NAME> {act_name} <TIMES> {routine['frequencies'][act_name]} ")
        idx += 1

    if randomize:
        randomized_plan_list = []
        randomized_pick_list = copy.deepcopy(picked_plans)
        arrangement = list(range(0,len(potential_topics)))
        random.shuffle(arrangement)
        for n,idx in enumerate(arrangement):
            randomized_plan_list.append(potential_topics[idx])
            for i in range(0,len(picked_plans)):
                if int(picked_plans[i]) == idx+4:
                    randomized_pick_list[i] = str(n+4)
        picked_plans = randomized_pick_list
        potential_topics = randomized_plan_list

    return plan_str + " ".join(potential_topics) + "\n", " ".join(picked_plans) + "\n"

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
