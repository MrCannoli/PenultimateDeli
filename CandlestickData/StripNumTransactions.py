# The number of transactions seems kinda like a useless bit of data - may just confuse the AI

import os
import csv
import argparse

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data_dir', type=str, default=None, dest='data_dir', help='Directory base folder name. Not a full path.')
args = parser.parse_args()
base_folder = args.data_dir

dir_to_strip = f'../CuttingBoard/{base_folder}'
dir_w_strip = f'../CuttingBoard/{base_folder}_stripped'

if not os.path.exists(dir_to_strip):
    raise RuntimeError(f"Was unable to find the specified data directory: {dir_to_strip}")
if not os.path.exists(dir_w_strip):
    os.mkdir(dir_w_strip)

file_list = os.listdir(dir_to_strip)

for datafile in file_list:
    print(f"Stripping file: {datafile}")
    full_filename = f'{dir_to_strip}/{datafile}'
    full_stripname = f'{dir_w_strip}/{datafile}'
    with open(full_filename, 'r') as og_file:
        reader = csv.reader(og_file)

        with open(full_stripname, 'w') as stripped_file:
            writer = csv.writer(stripped_file)

            # Write everything except the number of transactions
            for r in reader:
                writer.writerow((r[0], r[1], r[2], r[3], r[4], r[6], r[7]))