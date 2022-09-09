import os
import csv
import typing
import random
from constructor.utils import WordGenerator
from constructor import utils

random.seed(42)

DATASET_PATH = "datasets/plan-full-v1"
OUTPUT_DATASET_PATH = "datasets/plan-full-v1-text"

def prase_segment(segment: str) -> typing.Dict[str, str]:
    # the first element is the type
    type = segment[1:segment.find(">")]
    properties = {"type": type}

    chunks = segment[segment.find(">")+1:].split(">")
    next_key = chunks[0][1:]
    for idx in range(1, len(chunks) - 1):
        properties[next_key] = chunks[idx][:chunks[idx].find("<")]
        next_key = chunks[idx][chunks[idx].find("<")+1:]
    properties[next_key] = chunks[-1]
    return properties


def plan_to_text(wg: WordGenerator, plan: str, name: str = "The resident") -> typing.Tuple[str,str]:

    new_plan = "<SE>"
    partial_sentences = []
    for segment in plan.split("<SE>"):
        if segment == "":
            continue
        seg_prop = prase_segment(segment)
        str_ = f"{wg.get_activity_past_tense(seg_prop['NA'])}"
        new_plan += f"<{seg_prop['type']}><NA>{seg_prop['NA']}"

        if "ST" in seg_prop and random.random() < 0.5:
            str_ += " at "
            str_ += seg_prop["ST"]
            new_plan += f"<ST>{seg_prop['ST']}"
        if "DU" in seg_prop and seg_prop["NA"] != "came_home" and random.random() < 0.5:
            new_plan += f"<DU>{seg_prop['DU']}"
            duration_str = utils.timedelta_to_str(utils.str_duration_to_timedelta(seg_prop["DU"]), "fuzzy")
            if duration_str != "":
                str_ += " " + duration_str
        partial_sentences.append(str_)
    
    summary = f"{name} " + utils.list_objects_in_str(partial_sentences) + "."
    return new_plan, summary




def main():

    # word generator
    wg = WordGenerator()

    for type in ["test","valid","train"]:
        for persona in ["persona-all", "persona4"]:
            
            # open and read line by line
            with open(os.path.join(DATASET_PATH, f"{persona}.{type}.csv"), 'r', encoding='UTF-8') as file:
                dataset = csv.reader(file)
                next(dataset)

                samples = []
                for line in dataset:
                    plan_text = line[2]
                    augmented_plan, summary = plan_to_text(wg, plan_text)
                    samples.append((augmented_plan, summary))
                
                os.makedirs(OUTPUT_DATASET_PATH, exist_ok=True)
                with open(os.path.join(OUTPUT_DATASET_PATH, f"{persona}.{type}.csv"), 'w', encoding='UTF-8') as file:
                    print(f"{persona}-{type} --> number of samples:", len(samples))
                    file.write("plan,summary\n")
                    file.writelines([f"{segment},{summary}\n" for segment, summary in samples])


            
if __name__ == "__main__":
    main()