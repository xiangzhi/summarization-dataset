
import csv
import os
from datetime import datetime
import pickle
from constructor import Routine


def activity_matching(str, time: datetime) -> str:
    if str == "Morning_Meds" or str == "Eve_Meds":
        return "taking_medication"
    elif str == "Kitchen_Activity" or str == "Dining_Rm_Activity":
        if time.hour < 10:
            return "breakfast"
        elif time.hour > 4:
            return "lunch"
        else:
            return "dinner"
    elif str == "Bed_to_Toilet" or str == "Guest_Bathroom" or str == "Master_Bathroom":
        return "going_to_the_bathroom"
    elif str == "Sleep":
        return "sleeping"
    elif str == "Watch_TV":
        return "watching_tv"
    elif str == "Chores":
        return "cleaning"
    elif str == "Leave_Home":
        return "leave_home"
    elif str == "Come_Home":
        return "come_home"
    elif str == "Read":
        return "reading"
    elif str == "Desk_Activity":
        return "computer_work"
    elif str == "Meditate":
        return "meditating"
    elif str == "Master_Bedroom_Activity":
        return "master_bedroom"
    else:
        raise ValueError(f"Unknown activity: {str}")
        

def main():
    # change to current file path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    routines = []

    with open("casas-raw/milan/data", 'r') as f:
        data = csv.reader(f, delimiter="\t")
        current_routine = Routine(None, "-1")
        in_progress = False
        start_time = None
        curr_day = None
        curr_activity = None
        prev_time = datetime(1970, 1, 1)

        act_list = {}
        nested_start_time = None
        nested_activity = None


        for i, row in enumerate(data):

            try:
                time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")

            if time < prev_time:
                continue
                raise ValueError(f"Time is not in order starting at {i}")
            prev_time = time

            if time.day != curr_day:
                print(time.day)
                routines.append(current_routine)
                curr_day = time.day
                current_routine = Routine(None, str(time.day))

            if len(row) > 3 and row[-1] != "":
                
                state = row[-1].split(" ")[1]
                activity_name = row[3].split(" ")[0]


                if state == "begin":

                    if curr_activity is not None:
                        if nested_activity is None:
                            nested_activity = activity_name
                            nested_start_time = start_time
                        else:
                            print(f"Activity {curr_activity} is not finished at {i}")
                    else:
                        start_time = time
                        curr_activity = activity_name
                else:
                    if curr_activity != activity_name:
                        if activity_name == nested_activity:
                            current_routine.add_activity(activity_matching(activity_name, start_time), start_time, nested_start_time, remove_overlap=True)
                            current_routine.add_activity(activity_matching(nested_activity, nested_start_time), nested_start_time, time, remove_overlap=True)
                            start_time = time
                            nested_activity = None
                    else:
                        current_routine.add_activity(activity_matching(activity_name, start_time), start_time, time, remove_overlap=True)
                        curr_activity = None
                        nested_activity = None

    if len(routines) > 0:
        print("days: ", len(routines))
        os.makedirs("datasets/casas", exist_ok=True)
        with open("datasets/casas/routines.pkl", 'wb') as f:
            pickle.dump(routines, f)


if __name__ == "__main__":
    main()