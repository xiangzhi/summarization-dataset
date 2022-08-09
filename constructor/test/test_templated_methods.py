from constructor.templated_methods import * 
from constructor.utils import WordGenerator
from constructor import Routine

def test_stringiy_routine_sequentially():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})
    wg = WordGenerator(first_only=True)
    
    summary = stringiy_routine_sequentially(routine, wg, ["start_time", "duration"])
    assert len(summary) == 3
    assert " ".join(summary) == "the resident ate lunch at 08:00 for 1 hour. the resident ate dinner at 09:00 for 2 hours. the resident ate lunch at 15:00 for 30 minutes."

    summary = stringiy_routine_sequentially(routine, wg, ["start_time" ])
    assert " ".join(summary) == "the resident ate lunch at 08:00. the resident ate dinner at 09:00. the resident ate lunch at 15:00."

    summary = stringiy_routine_sequentially(routine, wg, ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour. the resident ate dinner for 2 hours. the resident ate lunch for 30 minutes."

    summary = stringiy_routine_sequentially(routine, wg, [])
    assert " ".join(summary) == "the resident ate lunch. the resident ate dinner. the resident ate lunch."

def test_stringifyRoutineAggregate():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})
    wg = WordGenerator(first_only=True)
    
    summary = stringify_routine_in_aggregate(routine, wg, ["start_time", "duration", "count"])
    assert len(summary) == 2
    assert " ".join(summary) == "the resident ate lunch for 2 times at 08:00 and 15:00 for 1 hour and 30 minutes. the resident ate dinner for 1 time at 09:00 for 2 hours."

    summary = stringify_routine_in_aggregate(routine, wg, ["start_time" ])
    assert " ".join(summary) == "the resident ate lunch at 08:00 and 15:00. the resident ate dinner at 09:00."

    summary = stringify_routine_in_aggregate(routine, wg, ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour and 30 minutes. the resident ate dinner for 2 hours."

    summary = stringify_routine_in_aggregate(routine, wg, ["duration"], ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour and 30 minutes. the resident ate dinner for 2 hours."

    summary = stringify_routine_in_aggregate(routine, wg, [])
    assert " ".join(summary) == "the resident ate lunch. the resident ate dinner."

def test_focus_activites_in_stringify():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})
    wg = WordGenerator(first_only=True)
    
    summary = stringify_routine_in_aggregate(routine, wg, ["start_time", "duration"], focus_activity_names=["lunch"])
    assert len(summary) == 1
    assert " ".join(summary) == "the resident ate lunch at 08:00 and 15:00 for 1 hour and 30 minutes."

    summary = stringiy_routine_sequentially(routine, wg, ["start_time"], focus_activity_names=["lunch"])
    assert len(summary) == 2
    assert " ".join(summary) == "the resident ate lunch at 08:00. the resident ate lunch at 15:00."

def test_stringify_come_and_leave_home():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["leave_home", "come_home"], "start_times": ["08:00", "09:00"], "end_times": ["09:00", "9:10"]}})
    wg = WordGenerator(first_only=True)

    summary = stringify_routine_in_aggregate(routine, wg, ["start_time", "duration"])
    assert len(summary) == 2
    assert " ".join(summary) == "the resident left home at 08:00 for 1 hour. the resident came home at 09:00."