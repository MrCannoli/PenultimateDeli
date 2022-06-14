# Combine all CSVs in one folder to a single file

import os
import csv
import argparse

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num_days', type=int, default=0, dest='num_days', help='Number of days data used')
parser.add_argument('-r', '--recent_num_days', type=int, default=0, dest='recent_num_days', help='Pull the most recent number of days data to combine')
parser.add_argument('-d', '--data_dir', type=str, default=None, dest='data_dir', help='Directory base folder name. Not a full path.')
args = parser.parse_args()
num_days = args.num_days
base_folder = args.data_dir
recent_num_days = args.recent_num_days

if num_days == 0:
    raise ValueError("Need to supply number of days data the file is using! Use -n to specify.")

top_dir = f"../CuttingBoard/ParsedData/{base_folder}/{num_days}_days"
train_dir = f"{top_dir}/train"
test_dir = f"{top_dir}/test"

if not os.path.exists(train_dir) or not os.path.exists(test_dir):
    raise ValueError(f"Unable to find the train and/or test directories in {top_dir}")

train_file_list = os.listdir(train_dir)
test_file_list = os.listdir(test_dir)

if(args.recent_num_days == 0):
    train_file_name = "combined_train.csv"
    test_file_name = "combined_test.csv"
else:
    train_file_name = f"combined_train_recent_{recent_num_days}.csv"
    test_file_name = f"combined_test_recent_{recent_num_days}.csv"

# Delete any old combined CSVs
if(os.path.exists(os.path.join(top_dir, train_file_name))):
    os.remove(os.path.join(top_dir, train_file_name))
if(os.path.exists(os.path.join(top_dir, train_file_name))):
    os.remove(os.path.join(top_dir, train_file_name))

print("Start combining all files in the train directory")
combined_train_list = []
for file in train_file_list:
    with open(f"{train_dir}/{file}", 'r', newline='') as next_file:
        print(f"Reading data from {file}")
        reader = csv.reader(next_file)
        # Get a list of the data, limited to the last number of days listed
        # If 0 (default), read the full list
        file_data = list(reader)[-recent_num_days:]
        for sublist in file_data:
            combined_train_list.append(sublist)

print(f"Writing all training data to {top_dir}/combined_train.csv")
with open(f"{top_dir}/{train_file_name}", 'w', newline='') as combined_train_file:
    csvwriter = csv.writer(combined_train_file)
    csvwriter.writerows(combined_train_list)

print("Start combining all files in the test directory")
combined_test_list = []
for file in test_file_list:
    with open(f"{test_dir}/{file}", 'r', newline='') as next_file:
        print(f"Reading data from {file}")
        reader = csv.reader(next_file)
        file_data = list(reader)
        for sublist in file_data:
            combined_test_list.append(sublist)

print(f"Writing all test data to {top_dir}/combined_test.csv")
with open(f"{top_dir}/{test_file_name}", 'w', newline='') as combined_test_file:
    csvwriter = csv.writer(combined_test_file)
    csvwriter.writerows(combined_test_list)