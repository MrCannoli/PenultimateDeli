# Clear out duplicates from test folder

import os

# New folders that the files will be moved to
train_dir_suffix = "/train"
test_dir_suffix = "/test"

# Top directory with files to be cleared
top_dir = f"../CuttingBoard/ParsedData/Data_6-5-2020-2022_stripped_good/2_days"

train_dir = f"{top_dir}/train"
test_dir = f"{top_dir}/test"

train_list = os.listdir(train_dir)
test_list = os.listdir(test_dir)

for tr in train_list:
    if tr in test_list:
        print(f"Removing duplicate file: {tr}")
        os.remove(os.path.join(test_dir, tr))