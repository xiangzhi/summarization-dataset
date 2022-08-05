import typing
import datetime
import numpy as np


def list_objects_in_str(sequence: typing.List[str], split_word: str = "and") -> str:
    """ Given a list of string, return it in a format that follow english grammar.
    Pass in split_word to change the word used to join the list.
    """

    str_ = ""
    for i in range(len(sequence) - 1):
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