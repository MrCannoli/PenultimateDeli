# The number of transactions seems kinda like a useless bit of data - may just confuse the AI

import os
import csv

dir_to_strip = '../CuttingBoard/Data_6-5-2020-2022'
dir_w_strip = '../CuttingBoard/Data_6-5-2020-2022_stripped'

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
                writer.writerow((r[0], r[1], r[2], r[4], r[6], r[7]))