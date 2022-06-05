# Generate an input map from all files in the specified folder
import CandlestickRequest
import os

# Directory with the original files
original_dir = "../DataDeli/Data_6-4-2020-2022"
new_dir = "../DataDeli/ParsedData/Data_6-4-2020-2022"

# Number of days' data you want to have as an input to the bot
num_days = 3

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