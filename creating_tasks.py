from deepflow_test import test_delegate_task
import os
task_dir = "data/task"
txt_files = [f for f in os.listdir(task_dir) if f.endswith(".txt")]

for txt_file in txt_files:
    sector=txt_file[:-4]
    print(sector)

    with open(f'data/task/{sector}.txt') as f:
        tasks=f.read()
    tasks=tasks.split("\nRelated occupations\n")
    i=0
    for task in tasks:
        test_delegate_task(task,f'{sector}_'+str(i))
        i+=1