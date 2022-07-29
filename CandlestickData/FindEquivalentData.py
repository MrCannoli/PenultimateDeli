# Find data used in one training set and grab the raws from the all_data folder

import os
import shutil

all_data_dir = "../CuttingBoard/All_Data_6-10"

new_raw_dir = "../CuttingBoard/SelectedData"
new_raw_dir_test = f"{new_raw_dir}/test"
new_raw_dir_train = f"{new_raw_dir}/train"

if not os.path.exists(new_raw_dir):
    os.mkdir(new_raw_dir)
    if not os.path.exists(new_raw_dir_test):
        os.mkdir(new_raw_dir_test)
        os.mkdir(new_raw_dir_train)

def recursive_clean(target_dir):
    old_list = os.listdir(target_dir)
    print(f"Cleaning {target_dir}...")
    for f in old_list:
        obj_path = os.path.join(target_dir, f)
        if os.path.isdir(obj_path):
            # Recursively clean subfolders
            recursive_clean(obj_path)
        else:
            # Delete the found file
            os.remove(obj_path)
    print(f"Cleaned {target_dir} of any old files")

recursive_clean(new_raw_dir)

source_dir = "../CuttingBoard/ParsedData/Data_6-5-2020-2022_stripped_good/2_days"
source_dir_test = f"{source_dir}/test"
source_dir_train = f"{source_dir}/train"

test_list = os.listdir(source_dir_test)
train_list = os.listdir(source_dir_train)

# Get the list of tickers
test_ticker_list = []
for t in test_list:
    ticker_eidx = t.find("_")
    ticker = t[0:ticker_eidx+1]
    test_ticker_list.append(ticker)

train_ticker_list = []
for t in train_list:
    ticker_eidx = t.find("_")
    ticker = t[0:ticker_eidx]
    train_ticker_list.append(ticker)

all_files_list = os.listdir(all_data_dir)

# Find the corresponding files in the all data list
for t in test_ticker_list:
    for j in all_files_list:
        if t in j:
            shutil.copyfile(os.path.join(all_data_dir,j),os.path.join(new_raw_dir_test,j))
            break

for t in train_ticker_list:
    for j in all_files_list:
        if t in j:
            shutil.copyfile(os.path.join(all_data_dir,j),os.path.join(new_raw_dir_train,j))
            break

