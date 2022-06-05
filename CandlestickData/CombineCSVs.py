# Combine all CSVs in one folder to a single file

import os
import csv

top_dir = "../DataDeli/ParsedData/Data_6-4-2020-2022"
train_dir = f"{top_dir}/train"
test_dir = f"{top_dir}/test"

if not os.path.exists(train_dir) or not os.path.exists(test_dir):
    raise ValueError(f"Unable to find the train and/or test directories in {top_dir}")

train_file_list = os.listdir(train_dir)
test_file_list = os.listdir(test_dir)

print("Start combining all files in the train directory")
combined_train_list = []
for file in train_file_list:
    with open(f"{train_dir}/{file}", 'r', newline='') as next_file:
        print(f"Reading data from {file}")
        reader = csv.reader(next_file)
        file_data = list(reader)
        for sublist in file_data:
            combined_train_list.append(sublist)

print(f"Writing all training data to {top_dir}/combined_train.csv")
with open(f"{top_dir}/combined_train.csv", 'w', newline='') as combined_train_file:
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
with open(f"{top_dir}/combined_test.csv", 'w', newline='') as combined_test_file:
    csvwriter = csv.writer(combined_test_file)
    csvwriter.writerows(combined_test_list)