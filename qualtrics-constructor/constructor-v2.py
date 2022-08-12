import numpy as np
import csv
import random
import json
import os
import copy
import re
import typing
import yaml
random.seed(42)


class QuestionGenerator():

    def __init__(self, path: str, q_obj: dict = None) -> None:

        self._q_obj = q_obj
        self._qid_counter = 10
        self._block_counter = 0
        self._flow_counter = 2
        with open(path, 'r') as f:
            self._question_bank = yaml.load(f, Loader=yaml.FullLoader)

    def _update_q_count(self, change: int = 1) -> None:
        self._q_obj['SurveyElements'][7]["SecondaryAttribute"] = str(
            change + int(self._q_obj['SurveyElements'][7]["SecondaryAttribute"]))

    def add_question(self, question_obj):
        self._q_obj['SurveyElements'].append(question_obj)
        self._update_q_count()
        return question_obj["PrimaryAttribute"]

    def generate_text_box(self, qid: str, text: str):
        text_block = copy.deepcopy(self._question_bank["types"]['text-box'])
        text_block['Payload']['QuestionText'] = text
        text_block["Payload"]["QuestionID"] = qid
        text_block["Payload"]["DataExportTag"] = qid
        text_block["PrimaryAttribute"] = qid
        return text_block

    def generate_text_entry(self, qid: str, text: str,  export_tag: str = ""):
        export_tag = export_tag if export_tag else qid
        text_block = copy.deepcopy(self._question_bank["types"]['text-entry'])
        text_block['Payload']['QuestionText'] = text
        text_block["Payload"]["QuestionID"] = qid
        text_block["Payload"]["DataExportTag"] = export_tag
        text_block["PrimaryAttribute"] = qid
        return text_block

    def generate_likert_question(self, qid: str, question_text: str, export_tag: str = "", required: bool = False) -> dict:
        export_tag = export_tag if export_tag else qid
        likert_question = copy.deepcopy(self._question_bank["types"]['likert-question'])
        likert_question['Payload']['QuestionText'] = question_text
        likert_question["Payload"]["QuestionID"] = qid
        likert_question["Payload"]["DataExportTag"] = export_tag
        likert_question["PrimaryAttribute"] = qid
        if required:
            likert_question["Payload"]["Validation"]["Settings"]["ForceResponse"] = 'ON'
        return likert_question

    def generate_timing(self, qid: str, export_tag: str = "") -> dict:
        export_tag = export_tag if export_tag else qid
        timing = copy.deepcopy(self._question_bank["types"]['timing'])
        timing["PrimaryAttribute"] = qid
        timing["Payload"]["QuestionID"] = qid
        timing["Payload"]["DataExportTag"] = export_tag
        return timing

    def generate_qid(self, restart: int = -1) -> str:
        if restart >= 0:
            self._qid_counter = restart
        self._qid_counter += 1
        return f"QID{self._qid_counter - 1}"

    def generate_block_id(self, restart: int = -1) -> str:
        if restart >= 0:
            self._block_counter = restart
        self._block_counter += 1
        return f"BL_{self._block_counter - 1}"

    def generate_flow_id(self, restart: int = -1) -> str:
        if restart >= 0:
            self._flow_counter = restart
        self._flow_counter += 1
        return f"FL_{self._flow_counter - 1}"

    def generate_activity_box(self, qid: str, export_tag: str = "") -> dict:
        box = copy.deepcopy(self._question_bank["types"]['activity-box'])
        export_tag = export_tag if export_tag else qid
        box["PrimaryAttribute"] = qid
        box["Payload"]["QuestionID"] = qid
        box["Payload"]["DataExportTag"] = export_tag
        box["Payload"]["AdditionalQuestions"]["1"]["DataExportTag"] = export_tag + "#1"
        box["Payload"]["AdditionalQuestions"]["1"]["QuestionID"] = qid + "#1"
        box["Payload"]["AdditionalQuestions"]["2"]["DataExportTag"] = export_tag + "#2"
        box["Payload"]["AdditionalQuestions"]["2"]["QuestionID"] = qid + "#2"
        box["Payload"]["AdditionalQuestions"]["3"]["DataExportTag"] = export_tag + "#3"
        box["Payload"]["AdditionalQuestions"]["3"]["QuestionID"] = qid + "#3"

        for i in range(1, 21):
            box["Payload"]["AdditionalQuestions"]["1"]["DefaultChoices"][str(i)] = {"14": {"Selected": True}}
            box["Payload"]["AdditionalQuestions"]["2"]["DefaultChoices"][str(i)] = {"9": {"Selected": True}}

        return box

    def create_flow_object(self, flow_id, type: str, **kwargs) -> str:

        if type == "b":
            return {
                "Type": "Block",
                "ID": kwargs["block_id"],
                "FlowID": flow_id,
                "Autofill": []
            }

    def create_block(self, block_id: str,  block_elements: typing.List[typing.Tuple[str, str]], description: str = "block") -> dict:

        if block_id == "BL_0":
            block_obj = {
                "Type": "Default",
                "Description": description,
                "ID": block_id,
                "BlockElements": []
            }
        else:
            block_obj = {
                "Type": "Standard",
                "SubType": "",
                "Description": description,
                "ID": block_id,
                "BlockElements": []
            }

        for element in block_elements:
            if element[0] == "b":
                block_obj["BlockElements"].append({"Type": "Page Break"})
            elif element[0] == "q":
                block_obj["BlockElements"].append({"Type": "Question", "QuestionID": element[1]})
            else:
                raise ValueError(f"Unknown type: {element[0]}")

        return block_obj

    def add_block(self, block_elements: typing.List[typing.Tuple[str, str]], description: str = "block") -> str:

        block_code = self.create_block(self.generate_block_id(), block_elements, description)
        block_id = block_code["ID"].split("_")[1]
        self._q_obj["SurveyElements"][0]["Payload"][block_id] = block_code
        return block_code["ID"]

    def create_flow_group(self, flow_objects, name: str = "Untitled Group") -> dict:
        return {
            "Type": "Group",
            "FlowID": self.generate_flow_id(),
            "Description": name,
            "Flow": flow_objects
        }

    def get_qsf(self) -> dict:
        return self._q_obj


def create_duc_elements(gen, tag):

    qid0 = gen.add_question(gen.generate_text_box(gen.generate_qid(
    ), "For each question, please try to assess the quality of the summary only with respect to the property that is described in the question."))

    qid1 = gen.add_question(gen.generate_likert_question(gen.generate_qid(
    ), "<strong>Grammaticality:</strong> The summaries should have no datelines, system-internal formatting, capitalization errors or obviously ungrammatical sentences (e.g., fragments, missing components) that make the texts difficult to read.", export_tag=f"{tag}-grammar", required=True))
    qid2 = gen.add_question(gen.generate_likert_question(gen.generate_qid(
    ), '<strong>Non-redundancy:</strong> There should be no unnecessary repetition in the summaries. Unnecessary repetition might take the form of whole sentences that are repeated, or repeated facts, or the repeated use of a noun or noun phrase (e.g., "Bill Clinton") when a pronoun ("he") would suffice.', export_tag=f"{tag}-non-redundancy", required=True))
    qid3 = gen.add_question(gen.generate_likert_question(gen.generate_qid(
    ), "<strong>Referential Clarity:</strong> It should be easy to identify who or what the pronouns and noun phrases in the summary are referring to. If a person or other entity is mentioned, it should be clear what their role in the story is. So, a reference would be unclear if an entity is referenced but its identity or relation to the story remains unclear.", export_tag=f"{tag}-clarity", required=True))
    qid4 = gen.add_question(gen.generate_likert_question(gen.generate_qid(
    ), "<strong>Focus:</strong> The summary should have a focus; sentences should only contain information that is related to the rest of the summary.", export_tag=f"{tag}-focus", required=True))
    qid5 = gen.add_question(gen.generate_likert_question(gen.generate_qid(
    ), "<strong>Structure and Coherence:</strong> The summary should be well-structured and well-organized. The summary should not just be a heap of related information, but should build from sentence to sentence to a coherent body of information about a topic.", export_tag=f"{tag}-structure", required=True))

    block_elements = [("q", qid0), ("q", qid1), ("q", qid2), ("q", qid3), ("q", qid4), ("q", qid5)]
    return block_elements

# def pick_summaries():
#     summaries = {}
#     with open("/home/xtan47/Dev/summarization-dataset/datasets/schedule-prev-anomaly-window-v2/persona-all.test.csv", 'r') as f:
#         reader = csv.reader(f)
#         next(reader)
#         for row in reader:
#             if row[0] not in summaries:
#                 summaries[row[0]] = []
#             summaries[row[0]].append(row[-1])
#     test_key = next(iter(summaries.keys()))
#     pairings = {}
#     for i in range(len(summaries[test_key]) - 1):
#         for k in summaries.keys():
#             if k not in pairings:
#                 pairings[k] = []
#             pairings[k].append((summaries["no-sequential"][i], summaries[k][i+1]))

#     selected = {}

#     # pick 16 idxs from length
#     idxs = random.sample(range(len(pairings[test_key])), 16)
#     for i in range(len(pairings[test_key])):
#         if i in idxs:
#             for k in pairings.keys():
#                 if k not in selected:
#                     selected[k] = []
#                 selected[k].append(pairings[k][i])

#     for k in pairings.keys():
#         assert len(selected[k]) == 16

#     return selected


balance_latin_square = np.array([
    [0, 1, 3, 2],
    [1, 2, 0, 3],
    [2, 3, 1, 0],
    [3, 0, 2, 1]
])


def picked_summaries():
    with open("hand_picked.yaml", 'r') as f:
        data = yaml.safe_load(f)
        summary_sets = []

        d1_summaries = [data[f"q{i}"]["d1"] for i in range(1, 5)]
        d2_summaries = [
            [s for s in data[f"q1"]["d2"]],
            [s for s in data[f"q2"]["d2"]],
            [s for s in data[f"q3"]["d2"]],
            [s for s in data[f"q4"]["d2"]],
        ]

        # this is the balanced latine square order for the summaries
        for i in range(0, 4):
            # i represents the order of the summaries.
            for j in range(0, 4):
                # j is the order of the summary types:
                set = []
                for k in range(0, 4):
                    # k is the inner looping of latin square
                    set.append((d1_summaries[balance_latin_square[i, k]],
                               d2_summaries[balance_latin_square[i, k]][balance_latin_square[j, k]]))
                summary_sets.append(set)

        return summary_sets


def main():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("base-v2.qsf", 'r') as f:
        qualtric_obj = json.load(f)

        qualtric_obj["SurveyEntry"]["SurveyName"] = "summary-control-list-v2"

        # clear out the exisiting information about the survey
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"] = []
        qualtric_obj['SurveyElements'][0]["Payload"].clear()
        qualtric_obj['SurveyElements'][7]["SecondaryAttribute"] = "0"
        qualtric_obj['SurveyElements'] = qualtric_obj['SurveyElements'][:8]

        # object to help generation
        gen = QuestionGenerator("./question_types.yaml", qualtric_obj)

        # add the introduction & block
        qid = gen.add_question(gen.generate_text_box(gen.generate_qid(
        ), "In this study, you will read summaries about 4 people's daily activities. You will be asked to read two summaries of two subsequent days. After each summary, you will be asked to reconstruct the activities that happen during the day. Some summaries on the second day may refer to the previous summaries of the same person."))
        qid_mturk = gen.add_question(gen.generate_text_entry(gen.generate_qid(), "mturk_id", "Please enter your MTurk ID:", export_tag="mturk_id", required=True))
        block_id = gen.add_block([("q", qid)], "intro_block")
        flow_code = gen.create_flow_object(gen.generate_flow_id(), "b", block_id=block_id)
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"].append(flow_code)

        qid1 = gen.add_question(gen.generate_text_box(gen.generate_qid(
        ), "<b> Day 1 </br> The resident socialized at 1:00 for 1 hour, listened to music at 17:00 for 30 minutes, had dinner at 18:00 for 30 minutes, washed dishes at 20:00 for 15 minutes, and watched tv at 23:00 for 30 minutes."))
        qid2 = gen.add_question(gen.generate_activity_box(gen.generate_qid()))
        #qid2 = gen.add_question(gen.generate_text_entry(gen.generate_qid(), "Please describe all activities you recall happened on day 2 with as much detail as possible."))
        qid3 = gen.add_question(gen.generate_timing(gen.generate_qid()))

        block_id = gen.add_block([("q", qid1), ("q", qid2), ("q", qid3)], "intro_block")
        flow_code = gen.create_flow_object(gen.generate_flow_id(), "b", block_id=block_id)
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"].append(flow_code)

        # add a randomizer flow block:
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"].append({
            "Type": "BlockRandomizer",
            "FlowID": gen.generate_flow_id(),
            "EvenPresentation": True,
            "SubSet": 1,
            "Flow": [
            ]
        })

        summary_set = picked_summaries()

        for option, set in enumerate(summary_set):

            block_list = []
            for i, s in enumerate(set):

                sum1 = s[0]
                sum2 = s[1]
                # print(f"question {i}")
                # print(sum1)
                # print(sum2)

                # intro
                start_text = gen.add_question(gen.generate_text_box(
                    gen.generate_qid(), "The following two summaries for a different person. Please read the summaries below carefully."))

                # day 1
                day1_sum = gen.add_question(gen.generate_text_box(gen.generate_qid(), f"<strong> Day 1:</strong> {sum1} <hr>"))
                day1_act = gen.add_question(gen.generate_activity_box(gen.generate_qid(), export_tag=f"{option}-{i}-d1"))
                #day1_act = gen.add_question(gen.generate_text_entry(gen.generate_qid(), "Please describe all activities you recall happened on day 2 with as much detail as possible.",export_tag=f"{option}-{s}-d1"))
                day1_timing = gen.add_question(gen.generate_timing(gen.generate_qid(), export_tag=f"{option}-{i}-d1"))

                day2_sum = gen.add_question(gen.generate_text_box(gen.generate_qid(), f"<strong> Day 2:</strong> {sum2} <hr>"))
                day2_act = gen.add_question(gen.generate_activity_box(gen.generate_qid(), export_tag=f"{option}-{i}-d2"))
                #day2_act = gen.add_question(gen.generate_text_entry(gen.generate_qid(), "Please describe all activities you recall happened on day 2 with as much detail as possible.",export_tag=f"{option}-{s}-d1"))

                day2_timing = gen.add_question(gen.generate_timing(gen.generate_qid(), export_tag=f"{option}-{i}-d2"))

                block_list += [("b",), ("q", start_text), ("b",), ("q", day1_sum), ("q", day1_act), ("q", day1_timing),
                               ("b",), ("q", day2_sum), ("q", day2_act), ("q", day2_timing), ("b",)]

                block_list += create_duc_elements(gen, f"group-{option}")

            summary_block_id = gen.add_block(block_list, f"group {option}")

            qualtric_obj['SurveyElements'][1]["Payload"]["Flow"][-1]["Flow"].append(
                gen.create_flow_object(gen.generate_flow_id(), "b", block_id=summary_block_id))

        qualtric_obj = gen.get_qsf()
        with open("base-v2-e.qsf", 'w') as f:
            json.dump(qualtric_obj, f, indent=4)


if __name__ == "__main__":
    main()
