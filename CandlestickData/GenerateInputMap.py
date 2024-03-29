# Generate an input map from all files in the specified folder
import CandlestickRequest
import os
import argparse

# Parse command line inputs to get the target number of days
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num_days', type=int, default=0, dest='num_days', help='Number of recent days data used')
parser.add_argument('-d', '--data_dir', type=str, default=None, dest='data_dir', help='Directory base folder name. Not a full path.')
parser.add_argument('-s', '--setpoints', type=float, default=None, dest='setpoints', nargs='*', help='Binary setpoints to compare the high value of a day against the opening value of the day.' )
parser.add_argument('-t', '--timescale', type=str, default='day', dest='timescale', help='Time scale of the input files. Either hour or day.')
args = parser.parse_args()
num_days = args.num_days
base_folder = args.data_dir
setpoints = args.setpoints
timescale = args.timescale

if num_days == 0:
    raise ValueError("Need to supply number of days data the file is using! Use -n to specify.")

# Directory with the original files
original_dir = f"../CuttingBoard/{base_folder}"
new_dir = f"../CuttingBoard/ParsedData/{base_folder}/{num_days}_days/"

if not os.path.exists(original_dir):
    raise RuntimeError("Was unable to find the specified data directory")
if not os.path.exists(f"../CuttingBoard/ParsedData/{base_folder}"):
    os.mkdir(f"../CuttingBoard/ParsedData/{base_folder}")
if not os.path.exists(new_dir):
    os.mkdir(new_dir)

def recursive_clean(target_dir):
    old_list = os.listdir(target_dir)
    print(f"Cleaning {target_dir}...")
    for f in old_list:
        obj_path = os.path.join(target_dir, f)
        if os.path.isdir(obj_path):
            # Recursively clean subfolders
            recursive_clean(obj_path)
            os.rmdir(obj_path)
        else:
            # Delete the found file
            os.remove(obj_path)
    print(f"Cleaned {target_dir} of any old files")

recursive_clean(new_dir)
os.mkdir(f"{new_dir}/sim/")

c=CandlestickRequest.CandleParser()
file_list = os.listdir(original_dir)

print(f"Starting parsing for {len(file_list)} files")

for data_file in file_list:
    og_filepath = f"{original_dir}/{data_file}"
    new_filepath = f"{new_dir}/{data_file}_LIBSVM.csv"
    sim_filepath = f"{new_dir}/sim/{data_file}_sim.csv"
    
    c.generate_input_map(og_filepath, new_filepath, num_days, use_binary_setpoints=True, binary_setpoints=setpoints)
    c.generate_sim_from_daily(og_filepath, sim_filepath, num_days, setpoints)

print(CandlestickRequest.bcolors.OKGREEN + "Finished parsing data into unique LIBSVM formatted files" + CandlestickRequest.bcolors.ENDC)