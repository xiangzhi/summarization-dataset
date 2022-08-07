from constructor.templated_methods import * 
from constructor.utils import WordGenerator
from constructor import Routine

def test_stringifyRoutineSequentially():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})
    wg = WordGenerator(first_only=True)
    
    summary = stringifyRoutineSequentially(routine, wg, ["start_time", "duration"])
    assert len(summary) == 3
    assert " ".join(summary) == "the resident ate lunch at 08:00 for 1 hour. the resident ate dinner at 09:00 for 2 hours. the resident ate lunch at 15:00 for 30 minutes."

    summary = stringifyRoutineSequentially(routine, wg, ["start_time" ])
    assert " ".join(summary) == "the resident ate lunch at 08:00. the resident ate dinner at 09:00. the resident ate lunch at 15:00."

    summary = stringifyRoutineSequentially(routine, wg, ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour. the resident ate dinner for 2 hours. the resident ate lunch for 30 minutes."

    summary = stringifyRoutineSequentially(routine, wg, [])
    assert " ".join(summary) == "the resident ate lunch. the resident ate dinner. the resident ate lunch."

def test_stringifyRoutineAggregate():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})
    wg = WordGenerator(first_only=True)
    
    summary = stringifyRoutineInAggregate(routine, wg, ["start_time", "duration"])
    assert len(summary) == 2
    assert " ".join(summary) == "the resident ate lunch at 08:00 and 15:00 for 1 hour and 30 minutes. the resident ate dinner at 09:00 for 2 hours."

    summary = stringifyRoutineInAggregate(routine, wg, ["start_time" ])
    assert " ".join(summary) == "the resident ate lunch at 08:00 and 15:00. the resident ate dinner at 09:00."

    summary = stringifyRoutineInAggregate(routine, wg, ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour and 30 minutes. the resident ate dinner for 2 hours."

    summary = stringifyRoutineInAggregate(routine, wg, ["duration"], ["duration"])
    assert " ".join(summary) == "the resident ate lunch for 1 hour and 30 minutes. the resident ate dinner for 2 hours."

    summary = stringifyRoutineInAggregate(routine, wg, [])
    assert " ".join(summary) == "the resident ate lunch. the resident ate dinner."
