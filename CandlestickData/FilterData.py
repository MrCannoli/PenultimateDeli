# Create a filtered directory of data that only contains files with desired parameters
# In particular, only include stocks of a desired price range

import os
import shutil
import csv

source_dir = "../CuttingBoard/All_Data_6-10"
sorted_dir = "../CuttingBoard/filtered_data_6-10"

# Params for filtering
desired_vol_weighted_min = 3
desired_vol_weighted_max = 30

if(not os.path.exists(source_dir)):
    raise ValueError("Provided source dir couldn't be found!")
if(not os.path.exists(sorted_dir)):
    os.mkdir(sorted_dir)

old_list = os.listdir(sorted_dir)
print(f"Cleaning {sorted_dir}...")
for f in old_list:
    os.remove(os.path.join(sorted_dir, f))
print(f"Cleaned {sorted_dir} of any old files")

# Now sort the files
file_list = os.listdir(source_dir)

for file in file_list:
    last_vol_weight_avg = 0
    with open(f"{source_dir}/{file}", 'r', newline='') as next_file:
        print(f"Reading data from {file}")
        reader = csv.reader(next_file)
        reader = list(reader)
        last_vol_weight_avg = float(reader[-1][-1])
    if(desired_vol_weighted_min <= last_vol_weight_avg <= desired_vol_weighted_max):
        print(f"{file} has a last value of {last_vol_weight_avg}. Copying to filtered dir.")
        shutil.copyfile(f"{source_dir}/{file}", f"{sorted_dir}/{file}")

