import math 
from textwrap import indent
import numpy as np
import json
import datetime
import random
import os
import re 

random.seed(1323)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def inject_failure_into_activity(activity: dict) -> dict:

    # 1% chance
    if random.random() < 0.01:
        # 10% of total failure and then randomly pick an action to start failure.
        if random.random() < 0.1:
            action_idx = 0
        else:
            action_idx = random.randint(0, len(activity["actions"])-1)
        for i in range(action_idx, len(activity["actions"])):
            activity["actions"][i]["state"] = "failure"
    
    return activity

def post_process_activity(activity: dict) -> dict:

    # inject failure into activity
    activity = inject_failure_into_activity(activity)

    # figure out location
    if activity["actions"][0]["name"] == "WALK":
        activity["location"] = activity["actions"][0]["properties"][0]

    # the state of the activity depends on the actions
    num_actions = len(activity["actions"])
    num_succeded_actions = len([act for act in activity["actions"] if act["state"] == "success"])

    if num_succeded_actions == num_actions:
        activity["state"] = "success"
    elif num_succeded_actions == 0:
        activity["state"] = "failure"
    else:
        activity["state"] = "partial"

    return activity


def process_script(filename: str):
    print(f"processing {filename}")

    activities = []
    init_state = True
    activity_start_times = []
    activity_end_times = []
    activity_index = 0
    action_start_time = None

    with open(filename, "r") as f:
        txt = f.readlines()

        curr_activity = None

        for idx,line in enumerate(txt):
            line = line.strip()
            if init_state and line == "":
                init_state = False
                continue

            if line == "":
                continue

            if init_state:
                # get the start and end time
                times = re.findall(r"[0-9]+:[0-9]+", line)
                activity_start_times.append(times[0])
                activity_end_times.append(times[1])

            if line.startswith("###"):
                if curr_activity is not None:
                    # figure out location
                    curr_activity = post_process_activity(curr_activity)
                    activities.append(curr_activity)

                activity_name = line.split(" ")[1].strip().split("-")[0]

                # calculate duration
                st_dt = datetime.datetime.strptime(activity_start_times[activity_index], "%H:%M")
                et_dt = datetime.datetime.strptime(activity_end_times[activity_index], "%H:%M")
                if et_dt < st_dt:
                    et_dt += datetime.timedelta(days=1)
                duration = et_dt - st_dt
                duration_str = str(duration)

                curr_activity = {
                    "name": activity_name,
                    "actions": [],
                    "start_time": activity_start_times[activity_index],
                    "end_time": activity_end_times[activity_index],
                    "duration": duration_str
                }
                action_start_time = activity_start_times[activity_index]
                activity_index += 1
                continue

            if curr_activity is not None:
                if line.startswith("["):
                    action_name = line[1:line.index("]")].strip()
                    next_action_start_time = re.findall(r"[0-9]+:[0-9]+", txt[idx+1])[0]
                    properties = re.findall(r"<[a-z_]*>", line)
                    properties = [p.strip("<>") for p in properties]

                    st_dt = datetime.datetime.strptime(action_start_time, "%H:%M")
                    et_dt = datetime.datetime.strptime(next_action_start_time, "%H:%M")
                    if et_dt < st_dt:
                        et_dt += datetime.timedelta(days=1)
                    duration = et_dt - st_dt
                    if duration == datetime.timedelta(0):
                        duration = datetime.timedelta(seconds=10)
                    duration_str = str(duration)

                    curr_activity["actions"].append({
                        "name": action_name,
                        "properties": properties,
                        "start_time": action_start_time,
                        "end_time": next_action_start_time,
                        "duration": duration_str,
                        "state": "success"
                    })
                    action_start_time = next_action_start_time
                        
                    
        if curr_activity is not None:
            curr_activity = post_process_activity(curr_activity)
            activities.append(curr_activity)

    return {
        "tasks": activities
    }


# input path is the base path
def batch_processing(input_dir: str, output_dir: str, individual_file: bool = False):
    """ Take output from the activity dataset and convert into JSON format

    Parameters
    ----------
    input_dir : str
        path to base file for each PERSONA
    output_dir : str
        base path to store the dataset
    individual_file : bool, optional
        Whether each day is save as one JSON file, by default False
    """

    persona_type = os.path.split(input_dir)[-1]
    # create directories if not exist
    os.makedirs(os.path.join(output_dir), exist_ok=True)
    if individual_file:
        os.makedirs(os.path.join(output_dir, persona_type, "test"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, persona_type, "train"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, persona_type, "valid"), exist_ok=True)

    for type in ["train", "test"]:
        buffer = []
        valid_path = os.path.join(input_dir, f"scripts_{type}")
        if not os.path.exists(valid_path):
            print(f"Warning: no scripts_{type} folder found at {valid_path}")
            continue
        schedule_list = os.listdir(valid_path)
        schedule_list.sort()
        for script_path in schedule_list:
            pid = script_path.split("/")[-1].split(".")[0]
            day_count = int(pid) + 1
            output = process_script(os.path.join(input_dir, f"scripts_{type}", script_path))
            output["info"] = {
                'day': day_count
            }
            if individual_file:
                with open(os.path.join(output_dir, persona_type, type, f"{pid}.json"),'w') as f:
                    json.dump(output, f, indent=4)
            else:
                buffer.append(json.dumps(output, indent=4) + "\n")

        if type == "train":
            if not individual_file:
                output_path = os.path.join(output_dir,f"{persona_type}-{type}.json")
                with open(output_path, "w") as f:
                    f.writelines(buffer)
        else:
            # test
            split = int(np.floor(len(buffer)/4))
            assert split != 0
            valid_output_path = os.path.join(output_dir,f"{persona_type}-valid.json")
            with open(valid_output_path, "w") as f:
                f.writelines(buffer[:split])            
            test_output_path = os.path.join(output_dir,f"{persona_type}-test.json")
            with open(test_output_path, "w") as f:
                f.writelines(buffer[split*3:])


if __name__ == "__main__":

    # change dir to current file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for persona in ["persona0","persona1","persona2","persona3","persona4"]:
        batch_processing(f"clusters-20220711/{persona}", "../datasets/activity-action-json")    

    # for i in  range(0,20):
    #     persona = f"individual{i}"
    #     batch_processing(f"individuals-20220810/{persona}", "../datasets/individual-schedule-json")    