from ..anomaly_detect import describe_anomalies
from .. import Routine, Event
from ..utils import WordGenerator

def test_anomaly_detect():

    routine = Routine({"info": {"day": 0}, "schedule": {"activities": ["a", "b", "c"], "start_times": ["08:00", "09:00", "10:00"], "end_times": ["09:00", "10:00", "11:00"]}})
    wg = WordGenerator("/home/xtan47/Dev/summarization-dataset/res/word_bank.yaml")

    mentioned_event, summary = describe_anomalies(routine, wg)
    assert summary == ""
    assert len(mentioned_event) == 0

    # add anomalous activity
    routine.add_activity("working", "12:00", end_time="13:00", anomaly_reason="this is anomalous")

    mentioned_event, summary = describe_anomalies(routine, wg)
    assert summary != ""
    assert len(mentioned_event) != 0