
from datetime import datetime
import typing
from .. import Routine, Event
from .plan import Plan

def generate_plans_from_events(events: typing.List[Event]) -> typing.List[str]:

    plans = []
    for act in events:
        plans.append(f"<SE><ACT><NA>{act.name}<ST>{act.get_start_time()}<DU>{act.get_duration_str('data_str')}")
    return plans

def generate_all_plans(routine: Routine, focus_activities: typing.List[str] = None) -> typing.List[str]:

    # validate inputs
    focus_activities = focus_activities or routine.get_activity_names()

    return generate_plans_from_events([e for e in routine.get_events() if e.name in focus_activities])

def search_for_start_times(act_name:str, prior_plans: typing.List[Plan]) -> typing.Tuple[int, typing.List[datetime]]:

    counter = 0
    for plan in reversed(prior_plans):
        counter -= 1
        # check if start_time exist
        start_times = plan.get_start_times(act_name)
        if len(start_times) > 0:
            return (counter, start_times)
        # check if prior same
        if act_name in plan.get_same_as_prior():
            continue
        break
    return (0, [])