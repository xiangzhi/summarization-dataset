import json
import os
import typing
from queue import Queue
from constructor import Routine, plan_methods, utils

PRIORITY_LIST = {
    "taking_medication": 2,
    "lunch": 1,
    "dinner": 1,
    "breakfast": 1,
}

def generate_independent_plans(routine: Routine, focus_activities: typing.List[str] = None, style: str = "normal"):

    # validate inputs
    focus_activities = focus_activities or routine.get_activity_names()
    length_control = style.split("_")[0]
    seq_control = style.split("_")[1]
    # ref_contol = style.split("_")[2]

    events = [e for e in routine.get_events() if e.name in focus_activities]
    if seq_control == "priority":
        events.sort(key=lambda e: e.priority, reverse=True)
    elif seq_control == "sequential":
        pass
    else:
        raise ValueError(f"Invalid sequence control {seq_control}")

    # get dataline
    data_line = routine.generate_dataline()
    picked_plans = plan_methods.generate_plans_from_events(events)

    if length_control == "short":
        picked_plans = picked_plans[:3]
    elif length_control == "none":
        pass
    else:
        raise ValueError(f"Invalid length control method {length_control}")

    return picked_plans, f"{style},{data_line},'',{''.join(picked_plans)}\n"

def generate_n_day_dependent_plans(routine: Routine, prior_plans: typing.List[plan_methods.Plan], focus_activities: typing.List[str] = None, properties: typing.List[str] = None, style: str = "normal"):

    # validate inputs
    focus_activities = focus_activities or list(set(routine.get_activity_names()))
    properties = properties or ["duration", "start_time"]
    length_control = style.split("_")[0]
    seq_control = style.split("_")[1]

    picked_plans = []

    # find similarities with yesterdays 
    same_act_as_yesterday = []
    if len(prior_plans) > 0:
        for act_name in focus_activities:
            today_st = utils.remove_minutes(routine.get_start_times(act_name))
            (prev_day, prev_st) = plan_methods.search_for_start_times(act_name, prior_plans)
            prev_st = utils.remove_minutes(prev_st)
            # cases where the event is being
            if len(today_st) > 0 and prev_day < 0:
                if "start_time" not in properties or utils.compare_time_lists(today_st, prev_st, 0):        
                    same_act_as_yesterday.append(act_name)


    # add plans for prior days
    if len(same_act_as_yesterday) > 0:
        prev_day_plan = "<SE><PREV>"
        for same_act_name in same_act_as_yesterday:
            prev_day_plan += f"<NA>{same_act_name}"
        focus_activities = [act_name for act_name in focus_activities if act_name not in same_act_as_yesterday]
        picked_plans += [prev_day_plan]

    if seq_control == "priority" and len(prior_plans) > 0:
        
        # if priority event only happen today but not yesterday
        priority_events_yesterday = [name for name in prior_plans[-1].get_activity_names() if name in PRIORITY_LIST]
        # if the event isn't here today
        missing_events = [name for name in priority_events_yesterday if name not in routine.get_activity_names()]
        missing_plan = "<SE><MISSING>"
        for name in list(set(missing_events)):
            missing_plan += "<NA>" + name
        picked_plans += [missing_plan]

    events = [e for e in routine.get_events() if e.name in focus_activities]
    if seq_control == "priority":
        events.sort(key=lambda e: e.priority, reverse=True)
    elif seq_control == "sequential":
        pass
    else:
        raise ValueError(f"Invalid sequence control {seq_control}")

    # get dataline
    data_line = routine.generate_dataline()
    picked_plans += plan_methods.generate_plans_from_events(events)

    if length_control == "short":
        picked_plans = picked_plans[:3]
    elif length_control == "none":
        pass
    else:
        raise ValueError(f"Invalid length control method {length_control}")

    return picked_plans, f"{style},{data_line},'{prior_plans[-1].to_dataline() if len(prior_plans) > 0 else ''}',{''.join(picked_plans)}\n"


def main():

    dataset_path = os.path.join("datasets", DATASET_NAME)
    os.makedirs(dataset_path, exist_ok=True)

    for type_ in ["test", "train", "valid", "example"]:
        for persona in ["persona4", "persona-all", "individual0"]:
            input_path = os.path.join("datasets/activity-schedule-json-v3", f"{persona}-{type_}.json")
            lines = []
            dataset = ["type,data,prior,plans\n"]
            if not os.path.exists(input_path):
                continue
            with open(input_path, "r", encoding='UTF-8') as file:
                lines = file.readlines()

            # (1) get all routines for the data file
            all_routines = [Routine(json.loads(l)) for l in lines]
            # (1b) Inject interesting things to the routine.
            for routine in all_routines:
                for act in routine.get_events():
                    if act.name in PRIORITY_LIST:
                        act.priority = PRIORITY_LIST[act.name]
            # end --- 1(b) -----

            # (2) go through each style & length:
            for length in ["none", "short"]:
                #for sequence in ["sequential", "priority"]:
                for sequence in ["priority"]:
                    # (3) whether to reference to the past
                    #for ref in ["none", "ref"]:
                    for ref in ["ref"]:
                        # (4) go through each routine and generate summary
                        for i, routine in enumerate(all_routines):

                            # clear the prior summaries if window is full
                            if i % SUMMARY_WINDOW == 0:
                                prior_routines = Queue(maxsize=SUMMARY_WINDOW-1)
                                prior_plans = Queue(maxsize=SUMMARY_WINDOW-1)
                            # set the day to the window
                            routine.set_day(i % SUMMARY_WINDOW + 1)
                            # generate summaries
                            style = f"{length}_{sequence}_{ref}"

                            if ref == "none":
                                picked_plan, sample = generate_independent_plans(routine, FOCUS_ACTIVITY, style=style)
                            elif ref == "ref":
                                picked_plan, sample =generate_n_day_dependent_plans(routine, list(prior_plans.queue), FOCUS_ACTIVITY, style=style)

                            # convert pick_plan into plan object
                            plan = plan_methods.Plan(picked_plan)

                            # add to dataset
                            dataset.append(f"{sample}")

                            # if summary is full, pop oldest.
                            if prior_plans.full():
                                prior_plans.get()
                                prior_routines.get()
                            prior_plans.put(plan)
                            prior_routines.put(routine)

            # (5) save to dataset
            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w", encoding='UTF-8') as file:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                file.writelines(dataset)


if __name__ == "__main__":

    DATASET_NAME = "plan-full-v1"
    FOCUS_ACTIVITY = None  # None is all
    SUMMARY_WINDOW = 3  # how many days to look back at

    main()
