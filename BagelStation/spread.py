# Test a provided AI model across files - see if we can find specific stocks that have minimal error

# Anticipated data format
# Open price | Close price | Hour 1 high | Hour 1 low | Hour 2 high | Hour 2 low ...

from multiprocessing.sharedctypes import Value
import xgboost as xgb
import csv
import os
from math import floor

# Data selection grouping
num_days = 3
base_data_folder_name = "All_Data_6-10"

# Trading parameters
confidence_threshold = 0.9 # Threshold at which we tell the model to try to sell
demon_percentage = 0.5 # Shannon's demon percentage used, scale 0-1

# Files being used
model_file = 'GeneratedModels/Test_3_days/Test_3_days.model'

# Folder with original daily data
og_data_dir= f"../CuttingBoard/{base_data_folder_name}/"

# Folder with sim data
sim_data_dir = f"../CuttingBoard/ParsedData/{base_data_folder_name}_stripped/{num_days}_days/sim/"

# Folder with SVM formatted data
parsed_data_dir = f"../CuttingBoard/ParsedData/{base_data_folder_name}_stripped/{num_days}_days/test/"

# Percentage the model was trained against
model_percentage = 0.005

# Starting cash amount to be trading
INITIAL_CASH = 10000

# Cash counter variables for different trading methods
cash_all_in = INITIAL_CASH # All money in for every trade
cash_demon = INITIAL_CASH  # Shannon's demon method - 50% of the pot with every trade

# Counters to track activity of the model
conf_met_count = 0
conf_not_met_count = 0
profit_sell_count = 0
stop_profit_sell_count = 0
loss_sell_count = 0
stop_loss_sell_count = 0
unclear_sell_count = 0
close_sell_count = 0

# Load the model
bst = xgb.Booster()
bst.load_model(model_file)

'''
# Set of random extra eval data for testing
randdata = xgb.DMatrix('inputdata.csv')

preds = bst.predict(randdata)
print("Predictions: ")
print(preds)

# Load the test file into a format the AI can parse
test_data = xgb.DMatrix(test_file)

# Generate predictions against the test file
preds = bst.predict(test_data)
'''


unsorted_sim_file_list = sorted(os.listdir(sim_data_dir))
sim_file_list = []

parsed_file_list = sorted(os.listdir(parsed_data_dir))

# Limit the sim file list to what is contained in the parsed file list
for f in parsed_file_list:
    for i in unsorted_sim_file_list:
        if f[0:15] == i[0:15]:
            sim_file_list.append(i)
            break
    #sim_file_list.append(i for i in unsorted_sim_file_list if f[0:15] == i[0:15])

# Since the sim and parsed lists come from the same source, they should have the same number of items
sim_file_len = len(sim_file_list)
parsed_file_len = len(parsed_file_list)
if sim_file_len != parsed_file_len:
    print("File numbers dont match: " + str(sim_file_len) + " " + str(parsed_file_len))
    raise ValueError

all_in_went_broke = False
demon_went_broke = False

individual_cash_all_in = [INITIAL_CASH] * sim_file_len
individual_cash_demon = [INITIAL_CASH] * sim_file_len
skip_list = []

for i in range(sim_file_len):
    # Ensure that the two files we are looking at are the same
    und_idx = sim_file_list[i].find('_')
    if (sim_file_list[i][0:und_idx] != parsed_file_list[i][0:und_idx]):
        print(sim_file_list[i])
        print(parsed_file_list[i])
        raise RuntimeError("The two files being looked at are different!")

    # Get the sim and parsed files
    sim_file = os.path.join(sim_data_dir, sim_file_list[i])
    parsed_file = os.path.join(parsed_data_dir, parsed_file_list[i])

    # Convert the parsed data to xgb format, use it for predictions
    parsed_data = xgb.DMatrix(parsed_file)
    preds = bst.predict(parsed_data)

    # Get the sim data from the file
    sim_file_data = []
    with open(sim_file, 'r', newline='') as source_file:
        source_reader=csv.reader(source_file)
        sim_file_data = list(source_reader)
    # Note: sim file data has format YMD, setpoint, open price, sell price, sell point

    confidence_met_for_stock = False

    for x in range(num_days, len(sim_file_data)-1):
        # Use predictions to determine sell point
        # We use the offset num_days to catch 
        if(preds[x-num_days] > confidence_threshold):
            confidence_met_for_stock = True
            conf_met_count += 1
            # Convert the data into a nice list
            split_data = list(map(float,sim_file_data[x][0].split()))

            # Calculate the number of stock bought and cost associated with doing so
            open_price = split_data[2]
            sell_price = split_data[3]
            sell_point_representation = split_data[4]

            profit_per_stock = sell_price - open_price

            bought_num_stock_all_in = floor(individual_cash_all_in[i] / open_price)
            bought_num_stock_demon = floor((individual_cash_demon[i] * demon_percentage) / open_price)

            individual_cash_all_in[i] = individual_cash_all_in[i] + (bought_num_stock_all_in * profit_per_stock)
            individual_cash_demon[i] = individual_cash_demon[i] + (bought_num_stock_demon * profit_per_stock)

            if sell_point_representation == 0: 
                # Sell point dependent on assumptions
                unclear_sell_count += 1
                if(sell_price > open_price):
                    profit_sell_count += 1
                else:
                    loss_sell_count +=1
            elif sell_point_representation == 1:
                # Sold for stop-profit
                stop_profit_sell_count +=1
                profit_sell_count += 1
            elif sell_point_representation == 2:
                # Sold for stop-profit
                stop_loss_sell_count +=1
                loss_sell_count +=1
            else:
                # Sold at close
                close_sell_count += 1
                if(sell_price > open_price):
                    profit_sell_count += 1
                elif (sell_price == open_price):
                    # Price didn't move - don't increment any counter
                    pass
                else:
                    loss_sell_count +=1
        
        else:
            conf_not_met_count += 1

    if(confidence_met_for_stock):
        print(f'Total cash all in for ${sim_file_list[i][0:und_idx]}: ${individual_cash_all_in[i]}')
        print(f'Total cash demon for  ${sim_file_list[i][0:und_idx]}: ${individual_cash_demon[i]}')
    else:
        print(f'Buy confidence never met for ${sim_file_list[i][0:und_idx]}')
        skip_list.append([x])

    '''
    if (cash_all_in < (INITIAL_CASH * 0.1)) and all_in_went_broke == True:
        # If we end up with less than 10% of our starting cash, we aren't doing too well
        print(f"Oh no! All in method went broke after {conf_met_count} rounds.")
    
    if (cash_demon < INITIAL_CASH * 0.1) and demon_went_broke == True:
        # If we end up with less than 10% of our starting cash, we aren't doing too well
        print(f"Oh no! Shannon's Demon method went broke after {conf_met_count} rounds.")
    
    if (demon_went_broke and all_in_went_broke):
        # Quit early since both methods went broke
        break
    '''

# Strip the skipped stocks
i = len(skip_list)
while i > 0:
    i -= 1
    individual_cash_all_in.pop(i)
    individual_cash_demon.pop(i)

# We've completed the full run. Get the average cash from testing
avg_cash_all_in = sum(individual_cash_all_in) / sim_file_len
avg_cash_demon = sum(individual_cash_demon) / sim_file_len

print("==========================================================================")
print("Results of test: ")
print(f"Times confidence interval was met:     {conf_met_count}")
print(f"Times confidence interval was not met: {conf_not_met_count}")
print(f"Times sold at profit:                  {profit_sell_count}")
print(f"Times sold at stop profit:             {stop_profit_sell_count}")
print(f"Times sold at loss:                    {loss_sell_count}")
print(f"Times sold at stop loss:               {stop_loss_sell_count}")
print(f"Times sold at assumed price:           {unclear_sell_count}")
print(f"Times sold at close:                   {close_sell_count}")
print("\n")
print(f"Final cash all in: {avg_cash_all_in}")
print(f"Final cash Shannon's demon {demon_percentage*100}%: {avg_cash_demon}")
print("==========================================================================")