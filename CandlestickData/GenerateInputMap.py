# Generate an input map from all files in the specified folder
import CandlestickRequest
import os
import argparse

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num_days', type=int, default=0, dest='num_days', help='Number of random stocks to pull from the ticker file')
args = parser.parse_args()
num_days = args.num_days

if num_days == 0:
    raise ValueError("Need to supply number of days data the file is using! Use -n to specify.")

# Directory with the original files
original_dir = "../CuttingBoard/Data_6-5-2020-2022_stripped"
new_dir = f"../CuttingBoard/ParsedData/Data_6-5-2020-2022/{num_days}_days/"

if not os.path.exists(original_dir):
    raise RuntimeError("Was unable to find the specified data directory")
if not os.path.exists(new_dir):
    os.mkdir(new_dir)

c=CandlestickRequest.CandleParser()
file_list = os.listdir(original_dir)

print(f"Starting parsing for {len(file_list)} files")

for data_file in file_list:
    og_filepath = f"{original_dir}/{data_file}"
    new_filepath = f"{new_dir}/{data_file}_LIBSVM.csv"
    c.generate_input_map(og_filepath, new_filepath, num_days)

print(CandlestickRequest.bcolors.OKGREEN + "Finished parsing data into unique LIBSVM formatted files" + CandlestickRequest.bcolors.ENDC)