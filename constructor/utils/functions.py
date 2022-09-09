import typing
import datetime
import numpy as np


def list_objects_in_str(sequence: typing.List[str], split_word: str = "and") -> str:
    """ Given a list of string, return it in a format that follow english grammar.
    Pass in split_word to change the word used to join the list.
    """

    str_ = ""
    for i in range(0, len(sequence) - 1):
        str_ += sequence[i]
        if i == 0 and len(sequence) == 2:
            str_ += f" {split_word} "
        elif i < len(sequence) - 2:
            str_ += ", "
        elif i == len(sequence) - 2:
            str_ += f", {split_word} "
    str_ += sequence[-1]
    return str_


def get_timedeltas(reference: typing.List[str], target: typing.List[str], format:str ="minutes") -> typing.List[int]:
    """ Given two lists of times in string, return a list of timedelta between the two.
    """

    deltas = []
    for i, r in enumerate(reference):
        reference_time = datetime.datetime.strptime(r, "%H:%M")
        target_time = datetime.datetime.strptime(target[i], "%H:%M")
        delta_in_sec = np.abs(reference_time - target_time).total_seconds()
        if format == "minutes":
            deltas.append(delta_in_sec // 60)
        elif format == "seconds":
            deltas.append(delta_in_sec)
        else:
            raise ValueError("format must be either 'minutes' or 'seconds'")
    return deltas

def compare_time_lists(reference: typing.List[datetime.datetime], target: typing.List[datetime.datetime], threshold: int = 30) -> bool:

    if len(reference) != len(target):
        return False
    
    for i, r in enumerate(reference):
        if np.abs((r - target[i]).total_seconds()/60) > threshold:
            return False
    return True

def compare_durations(reference: typing.List[datetime.timedelta], target: typing.List[datetime.timedelta], threshold: int = 30) -> bool:

    if len(reference) != len(target):
        return False
    
    for i, r in enumerate(reference):
        if np.abs((r - target[i]).total_seconds()/60) > threshold:
            return False
    return True

def str_duration_to_timedelta(str_: str) -> datetime.timedelta:
    duration_fake_time = datetime.datetime.strptime(str_, "%H:%M")
    return datetime.timedelta(hours=duration_fake_time.hour, minutes=duration_fake_time.minute)

def str_to_datetime(str_: str) -> datetime.datetime:
    return datetime.datetime.strptime(str_, "%H:%M").replace(year=2022)

def timedelta_to_str(delta: datetime.timedelta, return_type:str = "str") -> str:
    if return_type == "str":
        hour_count = delta.seconds//3600
        min_count = delta.seconds//60 - hour_count*60

        str_ = ""
        if hour_count > 0:
            str_ += f"{hour_count} hour{'s' if hour_count > 1 else ''}"
        if min_count > 0:
            if hour_count > 0:
                str_ += " and "
            str_ += f"{min_count} minute{'s' if min_count > 1 else ''}"
        return str_
    elif return_type == "fuzzy":
        if delta.seconds > (60*90):
            return "for a long time"
        elif delta.seconds > (60*50):
            return "for about 1 hour"
        elif delta.seconds > (60*25):
            return "for about 30 minutes"
        elif delta.seconds > (60*12):
            return "for about 15 minutes"
        else:
            return ""
    else:
        raise ValueError("return_type must be either 'str' or 'fuzzy'")

def make_sentence_upper_case(str_: str) -> str:

    # find all . in str_
    dot_idx = [i for i, l in enumerate(str_) if l == "."]
    # make the first letter of each sentence upper case
    str_ = str_.capitalize()
    for i in dot_idx:
        if i+2 < len(str_):
            str_ = str_[:i+2] + str_[i+2:].capitalize()

    return str_


def remove_minutes(time_list: typing.List[datetime.datetime]) -> typing.List[datetime.datetime]:
    for i in range(len(time_list)):
        time_list[i] = time_list[i].replace(minute=0)
    return time_list

