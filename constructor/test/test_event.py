
from datetime import datetime
from constructor.event import Event

def test_event_duration_str():

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("08:40", "%H:%M"))
    assert e.get_duration_str() == "30 minutes"

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("08:11", "%H:%M"))
    assert e.get_duration_str() == "1 minute"

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("09:41", "%H:%M"))
    assert e.get_duration_str() == "1 hour and 31 minutes"

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("10:41", "%H:%M"))
    assert e.get_duration_str() == "2 hours and 31 minutes"

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("09:10", "%H:%M"))
    assert e.get_duration_str() == "1 hour"

def test_priority():

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("08:40", "%H:%M"), priority=1)
    assert e.priority == 1

    e = Event("hi", datetime.strptime("08:10", "%H:%M"), datetime.strptime("08:40", "%H:%M"))
    assert e.priority == 0