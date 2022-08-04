import json
import os
from templated_methods.Summarization import *


def extract_data_as_line(routine):
    routine_txt = ""
    for i, act_name in enumerate(routine["schedule"]["activities"]):
        act_name.strip()
        routine_txt += f"<SEGMENT> <NAME> {act_name} <START_TIME> {routine['schedule']['start_times'][i]} <DURATION> {routine['schedule']['durations'][i]} <END_TIME> {routine['schedule']['end_times'][i]} "
    return routine_txt


input_count_list = []
summary_count_list = []

if __name__ == "__main__":

    dataset_name = "activity-schedule-summaries-various"
    dataset_path = os.path.join("datasets", dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    # summarization_methods = [verboseSummaryShortest]
    # many_summarization_methods = []

    summarization_methods = [verboseSummary, verboseUniqueActivity, listActivitySummary, listUniqueActivitySummary, listOnlyOneActivitySummary]
    many_summarization_methods = [listVariedActivitiesByPrevalence]

    for type_ in ["test", "train", "valid"]:
        for persona in ["persona4", "persona-all"]:
            input_path = os.path.join("datasets/activity-schedule-json", f"{persona}-{type_}.json")
            lines = []
            dataset = ["text,summary\n"]
            with open(input_path, "r") as f:
                lines = f.readlines()
            for line in lines:
                routine = json.loads(line)
                input_data = extract_data_as_line(routine)

                def add_summary(summary_type, summary):
                    # append type to input data
                    length_appended_input = f"<TYPE> {summary_type} {input_data}"
                    sample = f'{length_appended_input.strip()},"{summary.strip()}"'
                    dataset.append(sample + "\n")

                # create a list of summaries
                for summarizer in summarization_methods:
                    summary_type, summary = summarizer(routine)
                    add_summary(summary_type, summary)


                for summarizer in many_summarization_methods:
                    summaries = summarizer(routine)
                    for (summary_type, summary) in summaries:
                        add_summary(summary_type, summary)


            output_path = os.path.join(dataset_path, f"{persona}.{type_}.csv")
            with open(output_path, "w") as f:
                print(f"{persona}-{type_} --> number of samples:", len(dataset) - 1)
                f.writelines(dataset)
