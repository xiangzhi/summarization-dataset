import random
import yaml
random.seed(42)

class WordGenerator():

    def __init__(self, res_path:str = "../res/word_bank.yaml") -> None:
        with open(res_path, 'r') as f:
            self._word_bank = yaml.safe_load(f)

    def get_activity_past_tense(self, act_name: str) -> str:
        if act_name not in self._word_bank["past"]:
            raise ValueError("Activity not in word bank")
        return random.choice(self._word_bank["past"][act_name])

    def get_activity_verb(self, act_name: str) -> str:
        if act_name not in self._word_bank["verb"]:
            raise ValueError("Activity not in word bank")
        return random.choice(self._word_bank["verb"][act_name])

    def get_relation_to_yesterday(self) -> str:
        return random.choice(["yesterday", "the day before"])