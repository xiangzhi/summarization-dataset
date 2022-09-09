from constructor import plan_methods
from constructor import Routine

def test_plan_generate():
    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["lunch", "dinner", "lunch"], "start_times": ["08:00", "09:00", "15:00"], "end_times": ["09:00", "11:00", "15:30"]}})

    summary = plan_methods.generate_all_plans(routine)

    assert len(summary) == 3
    assert summary[0] == "<SE><ACT><N>lunch<ST>08:00<D>01:00"
    assert summary[1] == "<SE><ACT><N>dinner<ST>09:00<D>02:00"
    assert summary[2] == "<SE><ACT><N>lunch<ST>15:00<D>00:30"

