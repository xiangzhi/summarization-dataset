
class RoutineWrapper():

    def __init__(self, routine):
        self._routine = routine
        self._precompute_info()
    
    def _precompute_info(self):
        self._first_starttime = {}
        self._first_endtime = {}
        for i, act in enumerate(self._routine["schedule"]["activities"]):
            if act not in self._first_starttime:
                self._first_starttime[act] = self._routine["schedule"]["start_times"][i]
                self._first_endtime[act] = self._routine["schedule"]["end_times"][i]
        self._freq_table = {freq["name"]: freq for freq in self._routine["frequencies"]}

    def get_first_start_time(self, act:str) -> str:
        return self._first_starttime[act] 

    def get_frequency(self, act: str) -> int:
        return self._freq_table[act]["times"] if act in self._freq_table else 0