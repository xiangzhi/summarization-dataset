
import os

dataset_path = "../datasets/activity-schedule-json-v3"
    

# for type in ["train","test"]:
#     file = open(os.path.join(dataset_path,f"cluster-all-{type}.json"),'w')
#     for persona in ["cluster0","cluster1","cluster2"]:
#         lines = (open(os.path.join(dataset_path,f"{persona}-{type}.json"))).readlines()
#         file.writelines(lines)

# set current path to file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

for type in ["train","test", "valid"]:
    file = open(os.path.join(dataset_path,f"persona-all-{type}.json"),'w')
    for num in range(4):
        persona = f"persona{num}"
        lines = (open(os.path.join(dataset_path,f"{persona}-{type}.json"))).readlines()
        file.writelines(lines)