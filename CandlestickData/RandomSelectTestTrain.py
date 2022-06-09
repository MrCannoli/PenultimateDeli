# Randomly sort files into a set of Test and train data

import os
import random
import math
import argparse

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num_days', type=int, default=0, dest='num_days', help='Number of random stocks to pull from the ticker file')
args = parser.parse_args()
num_days = args.num_days

if num_days == 0:
    raise ValueError("Need to supply number of days data the file is using! Use -n to specify.")

# Percentage of files that should be used for training
train_percent = 0.90

# New folders that the files will be moved to
train_dir_suffix = "/train"
test_dir_suffix = "/test"

# Directory with files to be sorted
top_dir = f"../CuttingBoard/ParsedData/Data_6-5-2020-2022/{num_days}_days"

if not os.path.exists(top_dir):
    raise ValueError(f"Provided path could not be found: {top_dir}")

train_dir = top_dir + train_dir_suffix
test_dir = top_dir + test_dir_suffix

if not os.path.exists(train_dir):
    os.mkdir(train_dir)
if not os.path.exists(test_dir):
    os.mkdir(test_dir)

file_list = [f for f in os.listdir(top_dir) if os.path.isfile(os.path.join(top_dir, f))]

num_files = len(file_list)
num_train_files = math.floor(num_files * train_percent)

# Shuffle the file list randomly - makes random selection of chunks easy
random.shuffle(file_list)

train_list = file_list[0:num_train_files]
test_list = file_list[num_train_files:]

# Debug print liness
#print(len(train_list))
#print(train_list[0], " ", train_list[-1])
#print(len(test_list))
#print(test_list[0], " ", test_list[-1])

# Move the files to their appropriate new folders
for file in train_list:
    os.rename(f"{top_dir}/{file}", f"{train_dir}/{file}")
for file in test_list:
    os.rename(f"{top_dir}/{file}", f"{test_dir}/{file}")

print(f"Finished moving all files to {train_dir} and {test_dir}")