from textwrap import indent
import numpy as np
import json
import datetime
import random
import os

random.seed(1323)
location_table = {
    "computer_work": ["office", "living_room"],
    "reading": ["bedroom", "living_room"],
    "breakfast": ["dining_room"],
    "lunch": ["dining_room"],
    "going_to_the_bathroom": ["bathroom"],
    "showering": ["bathroom"],
    "brushing_teeth": ["bathroom"],
    "taking_medication": ["bathroom", "kitchen"],
    "socializing": ["living_room", "dining_room"],
    "dinner": ["dining_room"]
}


def location_lookup(activity_name: str) -> str:
    if activity_name in location_table:
        return random.choice(location_table[activity_name])
    else:
        return "unknown"


def process_script(filename: str):
    print(f"processing {filename}")
    activities_lines = []
    with open(filename, "r") as f:

        # skip the first line
        f.readline()
        while True:
            line = f.readline()
            if line == "\n":
                break
            activities_lines.append(line)

    # keep track of frequency & total time spent
    freq_table = {}
    duration_table = {}

    output_obj = {"schedule": {"activities": [], "start_times": [],
                               "end_times": [], "durations": [], "locations": []}}
    for line in activities_lines:
        line_part = line.split("(")
        if (line_part[0].split("_")[-1].isdigit()):
            activity_name = "_".join(line_part[0].split("_")[:-1])
        else:
            activity_name = line_part[0].strip()

        if line_part[1].startswith("1day"):
            line_part[1] = line_part[1][7:]
            start_time = datetime.datetime.strptime(line_part[1][:5], "%H:%M")
            start_time += datetime.timedelta(days=1)
        else:
            start_time = datetime.datetime.strptime(line_part[1][:5], "%H:%M")
        if "1day" in line_part[1]:
            end_time = datetime.datetime.strptime(
                line_part[1][15:20], "%H:%M") + datetime.timedelta(days=1)

        else:
            end_time = datetime.datetime.strptime(line_part[1][8:13], "%H:%M")
        duration = end_time - start_time
        output_obj["schedule"]["activities"].append(activity_name)
        output_obj["schedule"]["start_times"].append(
            start_time.strftime("%H:%M"))
        output_obj["schedule"]["end_times"].append(end_time.strftime("%H:%M"))
        duration_str = str(duration)[:-3]
        output_obj["schedule"]["durations"].append(duration_str)
        output_obj["schedule"]["locations"].append(
            location_lookup(activity_name))
        if activity_name not in freq_table:
            freq_table[activity_name] = 0
            duration_table[activity_name] = datetime.timedelta(0)
        freq_table[activity_name] += 1
        duration_table[activity_name] += duration

    output_obj["frequencies"] = []
    for key, val in freq_table.items():
        duration_str = str(duration_table[key])[:-3]
        output_obj["frequencies"].append({
            "name": key,
            "times": val,
            "duration": duration_str
        })

    return output_obj


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
    if individual_file:
        try:
            os.mkdir(os.path.join(output_dir, persona_type))
            os.mkdir(os.path.join(output_dir, persona_type, "test"))
            os.mkdir(os.path.join(output_dir, persona_type, "train"))
        except(FileExistsError):
            pass

    for type in ["train", "test"]:
        buffer = []
        schedule_list = os.listdir(os.path.join(input_dir, f"scripts_{type}"))
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
                buffer.append(json.dumps(output) + "\n")

        if type == "train":
            if not individual_file:
                output_path = os.path.join(output_dir,f"{persona_type}-{type}.json")
                with open(output_path, "w") as f:
                    f.writelines(buffer)
        else:
            # test
            split = int(np.floor(len(buffer)/2))
            valid_output_path = os.path.join(output_dir,f"{persona_type}-valid.json")
            with open(valid_output_path, "w") as f:
                f.writelines(buffer[split:])            
            test_output_path = os.path.join(output_dir,f"{persona_type}-test.json")
            with open(test_output_path, "w") as f:
                f.writelines(buffer[:split])   


if __name__ == "__main__":

    for persona in ["persona0","persona1","persona2","persona3","persona4"]:
        batch_processing(f"clusters-20220711/{persona}", "../datasets/activity-schedule-json")    
