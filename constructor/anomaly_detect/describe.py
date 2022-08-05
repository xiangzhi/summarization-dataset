import typing
from .. import Routine, Event
from ..utils import WordGenerator

def describe_anomalies(routine: Routine, wg: WordGenerator) -> typing.Tuple[typing.List[int], str]:
    
    mentioned_activities = []
    summary = ""
    # if there is an abnormal activity,
    if len(routine.get_anomalous_activities()) > 0:
        act: Event
        for (idx, act) in routine.get_anomalous_activities():
            summary += ("the resident " + wg.get_activity_past_tense(act.name) + " at " + act.get_start_time() + " today.")
            summary += " this is anomalous"
            mentioned_activities.append(idx)
            if act.anomaly_reason is not None:
                summary += " " + act.anomaly_reason
            summary += ". "
    return mentioned_activities, summary