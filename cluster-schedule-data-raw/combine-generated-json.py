
import os

dataset_path = "../datasets/activity-schedule-json"
    

# for type in ["train","test"]:
#     file = open(os.path.join(dataset_path,f"cluster-all-{type}.json"),'w')
#     for persona in ["cluster0","cluster1","cluster2"]:
#         lines = (open(os.path.join(dataset_path,f"{persona}-{type}.json"))).readlines()
#         file.writelines(lines)

for type in ["train","test", "valid"]:
    file = open(os.path.join(dataset_path,f"persona-all-{type}.json"),'w')
    for num in range(4):
        persona = f"persona{num}"
        lines = (open(os.path.join(dataset_path,f"{persona}-{type}.json"))).readlines()
        file.writelines(lines)