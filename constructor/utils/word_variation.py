import random
import yaml
random.seed(42)
import os

class WordGenerator():

    _no_random: bool
    def __init__(self, res_path:str = "", first_only: bool = False) -> None:
        # get this file's path
        if res_path == "":
            res_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "res", "word_bank.yaml")

        with open(res_path, 'r') as f:
            self._word_bank = yaml.safe_load(f)
        self._no_random = first_only

    def get_activity_past_tense(self, act_name: str) -> str:
        if act_name not in self._word_bank["past"]:
            raise ValueError(f"Activity: {act_name} not in word bank")
        return random.choice(self._word_bank["past"][act_name]) if not self._no_random else self._word_bank["past"][act_name][0]

    def get_activity_verb(self, act_name: str) -> str:
        if act_name not in self._word_bank["verb"]:
            raise ValueError(f"Activity: {act_name} not in word bank")
        return random.choice(self._word_bank["verb"][act_name]) if not self._no_random else self._word_bank["verb"][act_name][0]

    def get_relation_to_yesterday(self) -> str:
        if self._no_random:
            return ["yesterday"]
        #return random.choice(["yesterday", "the day before"])
        return random.choice(["yesterday"])