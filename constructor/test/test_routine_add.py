from ..routine import Routine


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
    assert routine.get_frequency("e") == 0    
