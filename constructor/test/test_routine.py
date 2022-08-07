from ..routine import Routine
from datetime import timedelta

def test_routine_get_durations():
    
    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["a", "b", "a"], "start_times": ["08:00", "09:00", "10:00"], "end_times": ["09:00", "9:30", "10:10"]}})
    assert routine.get_durations("a") == [timedelta(minutes=60),   timedelta(minutes=10)]

    assert routine.get_durations("a", return_type="str") == ["1 hour", "10 minutes"]



def test_add_activity_to_routine():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["a", "b", "c"], "start_times": ["08:00", "09:00", "10:00"], "end_times": ["09:00", "10:00", "11:00"]}})
    routine.add_activity("d", "12:00", end_time="13:00")

    assert len(routine.get_events()) == 4
    assert routine.get_frequency("d") == 1
    assert routine.get_first("d").get_start_time() == "12:00"
    assert routine.get_first("d").get_end_time() == "13:00"

def test_add_activity_to_routine_with_overlap():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["a", "b", "c"], "start_times": ["08:00", "09:00", "10:00"], "end_times": ["09:00", "10:00", "11:00"]}})
    
    # with overlap at the beginning
    routine.add_activity("d", "10:30", end_time="13:00")

    assert len(routine.get_events()) == 3
    assert routine.get_frequency("d") == 1
    assert routine.get_frequency("c") == 0

    # with overlap at the end
    routine.add_activity("e", "10:10", end_time="10:40")

    assert len(routine.get_events()) == 3
    assert routine.get_frequency("e") == 1
    assert routine.get_frequency("d") == 0

    # overlap at the beginning and end
    routine.add_activity("f", "10:05", end_time="10:45")
    assert len(routine.get_events()) == 3
    assert routine.get_frequency("f") == 1
    assert routine.get_frequency("a") == 1
    assert routine.get_frequency("b") == 1
    assert routine.get_frequency("e") == 0    
