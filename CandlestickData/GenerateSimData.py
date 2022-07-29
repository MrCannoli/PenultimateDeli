# Generate data for simulating how the sell algorithm will work
# General process: Take raw file, and reformat it with the following data order:
# Open price | Close Price | high price time segment 1 | Low price time segment 1 | high price time segment 2 | Low price time segment 2 | ...

# Command line inputs needed
# Directory with raw files
# Number of days' data used - Determines where we start processing data
# Timescale

import os
import csv
import argparse
import CandlestickData

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--daily_dir', type=str, default=None, dest='daily_dir', help='Directory base folder name for daily data in the CuttingBoard. Not a full path.')
parser.add_argument('-h', '--hourly_dir', type=str, default=None, dest='hourly_dir', help='Directory base folder name for hourly data in the CuttingBoard. Not a full path.')
parser.add_argument('-s', '--setpoints', type=float, default=None, dest='setpoints', nargs='*', help='Binary setpoints to compare the high value of a day against the opening value of the day.' )
args = parser.parse_args()

base_daily_folder = args.daily_dir
base_hourly_folder = args.hourly_dir
setpoints = args.setpoints

base_daily_file_dir = os.path.join("../CuttingBoard/", base_daily_folder)
base_hourly_file_dir = os.path.join("../CuttingBoard/", base_hourly_folder)

if not os.path.exists(base_daily_file_dir):
    raise ValueError("Was unable to find the specified daily data directory in the cutting board: " + base_daily_folder)
if not os.path.exists(base_hourly_file_dir):
    raise ValueError("Was unable to find the specified hourly data directory in the cutting board: " + base_hourly_file_dir)

# Create a generated file directory if it doesn't exist
generated_file_dir = os.path.join("../CuttingBoard/SimData/", base_daily_folder)
if(not os.path.exists(generated_file_dir)):
    os.mkdir(generated_file_dir)

# Clean the generated_file_dir so we don't start mixing the files up
old_list = os.listdir(generated_file_dir)
if len(old_list) != 0: # If there are files  in the directory, clean them
    print(f"Cleaning {generated_file_dir}...")
    for f in old_list:
        os.remove(os.path.join(generated_file_dir, f))
    print(f"Cleaned {generated_file_dir} of old files")

daily_file_list = os.listdir(base_daily_file_dir)
hourly_file_list = os.listdir(base_hourly_file_dir)

print(f"Starting parsing for {len(hourly_file_list)} files")

c = CandlestickData()

# Generate the sim files
for data_file in hourly_file_list:
    og_filepath = f"{base_hourly_file_dir}/{data_file}"
    sim_filepath = f"{generated_file_dir}/{data_file}_sim.csv"

    # Generate the simulator file
    c.generate_sim_from_hourly(og_filepath, sim_filepath, setpoints)