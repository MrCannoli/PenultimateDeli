##########################################################################
# @brief Script to grab price history for a given set of stock tickers   #
##########################################################################

import argparse
import requests
import time
import csv
import os
import argparse
import datetime
import random

# Class with ANSI escape sequences denoting printed text colors.
# Snagged from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CandlestickRequest:
    # This is a key to a free account, limited to 5 requests per second
    api_key = '5xDdaB3S8gsL0jTsxpCaiLMLHTqyD7tD'
    
    # We can only send 5 requests per minute on a free account
    REQ_LIMIT=5

    def __init__(self):
        # This array keeps track of the time of the last 5 requests made so we can avoid the limit
        self._request_times = [0,0,0,0,0]

    # Update the API key
    def set_api_key(new_key:str):
        CandlestickRequest.api_key = new_key
    
    # Get the number of requests that have occurred in the last minute
    def get_request_counter(self):
        present_time = time.time()
        request_count = 0
        for t in self._request_times:
            if((present_time - t) < 60):
                request_count+=1
        return request_count

    # Wait until the next time we can make a request for data
    def wait_for_next_req_time(self, force_wait=False):
        if(CandlestickRequest.get_request_counter(self) == CandlestickRequest.REQ_LIMIT):
            wait_time = 60.01 - (time.time() - max(self._request_times))
            print(bcolors.OKCYAN + f"Hit request limit, waiting {wait_time} seconds before continuing." + bcolors.ENDC)
            time.sleep(wait_time)
        elif(force_wait):
            time.sleep(60)

    # Update the request time array. Should be ran after a polygon API call.
    def update_request_time(self):
        # Add the request time to the array after removing the oldest time
        self._request_times.pop(0)
        self._request_times.append(time.time())

    # Check the status of a request
    def check_response(self, raw_response):
        if(raw_response.status_code == 429): # Calls happened too quickly
            raise RuntimeError("Made subsequent file calls too soon!")
        elif(raw_response.status_code != 200): # 200 is OK
            raise RuntimeError(f"Failed HTTP request with status code: {raw_response.status_code}")

    # Request 1000 tickers that are available on polygon.io, starting with the search key provided
    def request_ticker_list(self, search_key):
        request_url = f'https://api.polygon.io/v3/reference/tickers?active=true&sort=ticker&ticker.gte={search_key}&order=asc&limit=1000&apiKey={CandlestickRequest.api_key}'

        # Make the HTTP request for the stock ticker list
        raw_response = requests.get(request_url, params={ 'apiKey': CandlestickRequest.api_key })

        self.update_request_time()
        self.check_response(raw_response)

        # Convert the readings into JSON for ease of use
        results_json = raw_response.json()

        return results_json
    
    # Parse data from a provided ticker list
    def parse_ticker_list(self, ticker_list, csvwriter):
        # Note, this writes the header every time this function is called
        headers = ['Ticker Name', 'Market', 'Currency Symbol', 'locale']
        csvwriter.writerow(headers)

        parsed_data = [None] * 4

        for sample in ticker_list['results']:
            try:
                parsed_data[0]=sample['ticker']
                parsed_data[1]=sample['market']
                parsed_data[2]=sample['currency_name']
                parsed_data[3]=sample['locale']
                
                csvwriter.writerow(parsed_data)
            except KeyError:
                print(bcolors.WARNING + f"{sample['ticker']} lacks parameters required for parsing. Not adding to list" + bcolors.ENDC)

    #########################################################################################
    # @brief Request the candlestick data for a ticker using the presently configured set   #
    #                                                                                       #
    # @param[in] symbol: Stock ticker symbol                                                #
    # @param[in] start_date: Starting date (YYYY-MM-DD) to request data                     #
    # @param[in] end_date: Ending date (YYYY-MM-DD) to request data                         #
    # @param[in] step: Size of steps between readings. This is in the length of time_range. #
    # @param[in] time_range: Range with which to gather the data.                           #
    #########################################################################################
    def make_ticker_request(self, symbol, start_date, end_date, step='1', time_range='day'):
        # Generate the formatted request URLs
        check_availability_url = f'https://api.polygon.io/vX/reference/tickers?sort=ticker&ticker.gte=B&ticker.lt=C'
        request_url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{step}/{time_range}/{start_date}/{end_date}'

        if(CandlestickRequest.get_request_counter(self) == CandlestickRequest.REQ_LIMIT):
            raise RuntimeError("Hit the request limit - slow down!")

        # Make the HTTP request for the stock ticker data
        raw_response = requests.get(request_url, params={ 'apiKey': CandlestickRequest.api_key })

        self.update_request_time()
        self.check_response(raw_response)

        # Convert the readings into JSON for ease of use
        results_json = raw_response.json()

        if(results_json['resultsCount'] == 0):
            print(bcolors.FAIL + f"Stock request for {symbol} failed - no data available" + bcolors.ENDC)
            results_json = None 
        else:
            print(bcolors.OKGREEN + f"Data grabbed successfully for {symbol} for the date range {start_date} to {end_date}" + bcolors.ENDC)

        return results_json

    # Parse ticker data into a consumable array and write it to a CSV file
    def parse_ticker_data(self, ticker_data, csvwriter):
        headers = ['Timestamp', 'Open price', 'High Price', 'Low Price', 'Close Price', 'Num Transactions', 'Trade volume', 'Volume Weighted Price']
        csvwriter.writerow(headers)

        parsed_data = [None] * 8

        try:
            for sample in ticker_data['results']:
                parsed_data[0]=sample['t'] # Timestamp
                parsed_data[1]=sample['o'] # Open price
                parsed_data[2]=sample['h'] # High price
                parsed_data[3]=sample['l'] # Low price
                parsed_data[4]=sample['c'] # close price
                parsed_data[5]=sample['n'] # Number of transactions
                parsed_data[6]=sample['v'] # Trading volume
                parsed_data[7]=sample['vw'] # Volume weighted price
                
                csvwriter.writerow(parsed_data)
        except KeyError:
            print(bcolors.FAIL + f"Stock lacks parameters required for parsing. Deleting." + bcolors.ENDC)
            raise

    # Get a random list of stocks from the given ticker file
    def pick_random_stocks(self, ticker_file, num_rand_stocks):
        if num_rand_stocks == 0:
            raise ValueError("No random stocks requested.")
        if not os.path.exists(ticker_file):
            raise ValueError(f"Provided file does not exist! Check and confirm the path is correct: {ticker_file}")

        with open(ticker_file, 'r', newline='') as stock_file:
            print(f"Reading data from {ticker_file}")
            reader = csv.reader(stock_file)
            stock_list = list(reader)
            stock_list_size = len(stock_list)

            out_stock_list = [None] * num_rand_stocks
            
            # Get a random set of unique numbers within the range of the stock list
            rand_indices = random.sample(range(1, stock_list_size), num_rand_stocks)
            
            # Form a list of stocks using the random indices
            for i in range(num_rand_stocks):
                out_stock_list[i] = stock_list[rand_indices[i]][0]

            return out_stock_list

class CandleParser:
    MS_PER_DAY = 86400000
    MS_PER_HOUR = 3600000

    # Get the day value of a given timestamp
    def get_day(timestamp_ms):
        date_rep = datetime.datetime.fromtimestamp(timestamp_ms/1000)
        return date_rep.strftime("%d")

    
    # Get the year-month-day string of a given timestamp
    def get_ymd(self,timestamp_ms):
        date_rep = datetime.datetime.fromtimestamp(timestamp_ms/1000)
        return date_rep.strftime("%y%m%d")

    # Rearrange the raw input data (from the source_filepath) into a format that is usable by the AI
    # In particular, map the specified last few days' data into a digestable row
    # This follows LIBSVM format: https://catboost.ai/en/docs/concepts/input-data_libsvm
    def generate_input_map(self, source_filepath, parsed_data_filepath, num_days, use_binary_setpoints=False, binary_setpoints=[0]):
        formatted_list = []
        with open(source_filepath, 'r', newline='') as source_file:
            source_reader = csv.reader(source_file)
            source_list = list(source_reader)

            # Start at index num_days + 1 to go past the header
            for i in range(1+num_days, len(source_list)):
                for setpoint in binary_setpoints:
                    sublist = []
                    simlist = []

                    # First value needs to be the "label" value - Choice of which depends on whether this is a binary check or not
                    if use_binary_setpoints:
                        # First value is a binary representation of whether the high value is greater than the open value times the setpoint
                        # E.g. If high value for day is 5, open is 4.98, setpoint is 0.01, then this would return a 0.
                        # Check if the difference is past the setpoint.
                        if((float(source_list[i][2]) - (float(source_list[i][1]) * (setpoint + 1))) > 0):
                            sublist.extend(['1'])
                        else:
                            sublist.extend(['0'])
                        # Add the setpoint value we are using
                        #sublist.extend([str(setpoint)])
                    else:
                        # Label value is the high price of the day
                        sublist.extend(source_list[i][2:3])
                    
                    # First input is the open price of the present day
                    sublist.extend(source_list[i][1:2])

                    '''
                    # Add the difference between the present and last timestamp in units of days
                    num_days_since_last_data = (int(source_list[i][0]) - int(source_list[i-1][0])) / 86400000 # num ms in day
                    sublist.extend([str(num_days_since_last_data)])'''

                    for j in range(1, num_days+1):
                        '''
                        if(j < num_days:
                            if((i-j-1) == 0):
                                # We are reading back earlier than the start of the data set. Assume 1 day has past.
                                sublist.extend(['1'])
                            else:
                                # Add the difference between the present and last timestamp in units of days
                                num_days_since_last_data = (int(source_list[i-j][0]) - int(source_list[i-j-1][0])) / 86400000 # num ms in day
                                sublist.extend([str(num_days_since_last_data)])'''

                        # Include each row of inputs starting at most recent day first
                        sublist.extend(source_list[i-j][1:]) # start at 1 to skip the timestamp

                    formatted_list.append(sublist)
        
        # Update the list with input labels
        for sublist in formatted_list:
            for i in range(1, len(sublist)):
                sublist[i] = f"{i}:{sublist[i]}"


        # Write the parsed data to a new file at the specified location
        with open(parsed_data_filepath,'w', newline='') as parsed_data_file:
            print(f"Writing LIBSVM formatted data to {parsed_data_filepath}")
            csvwriter = csv.writer(parsed_data_file, delimiter=' ')
            csvwriter.writerows(formatted_list)


    # Generate simulator data from hourly inputs on stock data
    # Output format: year-month-date string, setpoint value, sell point representation
    # Sell point is -1 for sold at low price, 0 for close price, +1 for high price 
    def generate_sim_from_hourly(self, source_filepath, sim_filepath, binary_setpoints=[0.005], low_sell_method="proportional"):
        formatted_simlist = []

        with open(source_filepath, 'r', newline='') as source_file:
            source_reader=csv.reader(source_file)
            source_list = list(source_reader)

            # Skip the first day as we read as we aren't guaranteed to have the first hourly read of the day
            day = self.get_day(int(source_list[i][0]))
            while(self.get_day(int(source_list[i][0])) == day):
                i = i + 1

            # Now move on to create the sim list from the file
            while(i < len(source_list)):
                for setpoint in binary_setpoints:
                    simlist = []
                    # First thing to write is the date-time representation
                    simlist.extend(self.get_ymd(int(source_list[i][0])))

                    # Write the setpoint value
                    simlist.extend(str(setpoint))

                    # Starting open price of the day
                    open_price = float(source_list[i][1:2])
                    # Determine the sell prices based on the setpoint
                    high_sell_price = open_price * (1 + setpoint)
                    # This division is so that the loss is relative; a 50% loss is not recouped by a 50% gain the following day
                    # However with the division, an equal gain the following day would recoup all money lost
                    low_sell_price = open_price * (1 / (1 + setpoint))

                    if(low_sell_method == "raw"): 
                        low_sell_price = open_price * (1 - setpoint)

                    #simlist.extend(source_list[i][1:2])
                    # Second is the close price of the day
                    # This is stubbed with a bad value, it is replaced later
                    #simlist.extend([None])

                    # Search through the end of the present day to see if we hit the high or low sell price first. If neither, use the close price.
                    # Sell point represents the value we sold at: -1 = sold at low, 0 = sold at close, 1 = sold at high
                    present_day = self.get_day(int(source_list[i][0]))
                    sell_point = 0
                    while(self.get_day(int(source_list[i][0])) == present_day):
                        high_price = float(source_list[i][2])
                        low_price = float(source_list[i][3])
                        if((high_price > high_sell_price) and (low_price < low_sell_price)):
                            # Market was too volatile in the hour for us to know which it sold at
                            # Continue to the next data point to make a check
                            pass
                        elif(high_price > high_sell_price):
                            sell_point = 1
                            break
                        elif(low_price < low_sell_price):
                            sell_point = -1
                            break

                        i = i + 1
                        if (i >= len(source_list)):
                            # reached the end of the list. Break to prevent errors
                            break
                    
                    # Write the sellpoint value representation
                    simlist.extend(str(sell_point))
                    # Append the day's list to the full list
                    formatted_simlist.append(simlist)

        # Write the sim data to the new file
        with open(sim_filepath,'w', newline='') as sim_file:
            print(f"Writing simulator data to {sim_filepath}")
            csvwriter = csv.writer(sim_file, delimiter=' ')
            csvwriter.writerows(formatted_simlist)

    # Generate simulator data from hourly inputs on stock data
    # Output format: year-month-date string, setpoint value, open price, sell price, sell point representation
    def generate_sim_from_daily(self, source_filepath, sim_filepath, binary_setpoints=[0.005], low_sell_method="proportional", ambiguity_eval_method = "close_estimate"):
        formatted_simlist = []

        with open(source_filepath, 'r', newline='') as source_file:
            source_reader=csv.reader(source_file)
            source_list = list(source_reader)

            # Now move on to create the sim list from the file
            for setpoint in binary_setpoints:
                i = 1
                while(i < len(source_list)):
                    simlist = []


                    # Starting open price of the day
                    open_price = float(source_list[i][1])

                    # Determine the sell prices based on the setpoint
                    high_sell_price = open_price * (1 + setpoint)
                    # This division is so that the loss is relative; a 50% loss is not recouped by a 50% gain the following day
                    # However with the division, an equal gain the following day would recoup all money lost
                    # This method is equivalent to low_sell_method = "proportional", but really is the default case
                    low_sell_price = open_price * (1 / (1 + setpoint))

                    if(low_sell_method == "raw"): 
                        low_sell_price = open_price * (1 - setpoint)

                    # Search through the end of the present day to see if we hit the high or low sell price first. If neither, use the close price.
                    # Sell point represents the value we sold at: -1 = sold at low, 0 = sold at close, 1 = sold at high
                    sell_point = 0
                    high_price = float(source_list[i][2])
                    low_price = float(source_list[i][3])
                    close_price = float(source_list[i][4])
                    if((high_price > high_sell_price) and (low_price < low_sell_price)):
                        # Market was too volatile in the hour for us to know which it sold at for sure
                        if ambiguity_eval_method == "close_estimate":
                            if close_price < open_price:
                                # Ended lower - assume high price was hit early on in the day
                                sell_price = high_price
                            else:
                                # Ended higher - assume low price was hit early on in the day
                                sell_price = low_price
                        else:
                            # Skip method - set sell price to open price
                            sell_price = open_price
                        sell_point = 0
                    elif(high_price > high_sell_price):
                        sell_price = high_price
                        sell_point = 1
                    elif(low_price < low_sell_price):
                        sell_price = low_price
                        sell_point = 2
                    else:
                        sell_price = close_price
                        sell_point = 3
                    
                    # First thing to write is the date-time representation
                    simlist.extend([self.get_ymd(int(source_list[i][0]))])
                    # Write the setpoint value
                    simlist.extend([setpoint])
                    # Write open value
                    simlist.extend([open_price])
                    # Write the sell value
                    simlist.extend([sell_price])
                    # Write the representation of the sellpoint for analysis
                    simlist.extend([sell_point])
                    # Append the day's list to the full list
                    formatted_simlist.append(simlist)

                    i = i + 1

        # Write the sim data to the new file
        with open(sim_filepath,'w', newline='') as sim_file:
            print(f"Writing simulator data to {sim_filepath}")
            csvwriter = csv.writer(sim_file, delimiter=' ')
            csvwriter.writerows(formatted_simlist)


    # Determine the percentage with highs, lows, and highs and lows above/below setpoints for daily data
    def calculate_high_low_percentages(self, source_filepath, binary_setpoints=[0.005]):
        with open(source_filepath, 'r', newline='') as source_file:
            source_reader = csv.reader(source_file)
            source_list = list(source_reader)

            high_count = 0
            low_count = 0
            hl_count = 0
            close_count = 0

            i = 1
            for setpoint in binary_setpoints:
                while(i < len(source_list)):
                    # Starting open price of the day
                    open_price = float(source_list[i][1])
                    # Determine the sell prices based on the setpoint
                    high_sell_price = open_price * (1 + setpoint)
                    low_sell_price = open_price * (1 / (1 + setpoint))

                    high_price = float(source_list[i][2])
                    low_price = float(source_list[i][3])

                    high_benchmark_met = (high_price > high_sell_price)
                    low_benchmark_met = (low_price < low_sell_price)

                    if  high_benchmark_met and not low_benchmark_met:
                        high_count += 1
                    elif low_benchmark_met and not high_benchmark_met:
                        low_count += 1
                    elif low_benchmark_met and high_benchmark_met:
                        hl_count += 1
                    else:
                        close_count += 1
                    i+=1
                
                print(f"Stats for setpoint value {setpoint}")
                print(f"Days with price above high, but not low: {high_count}")
                print(f"Days with price below low, but not high: {low_count}")
                print(f"Days with price below low AND above high: {hl_count}")
                print(f"Days with price never reaching setpoint: {close_count}")



    #!!!!!!! This version does not work very well due to issues with polygon's hourly data !!!!!!!
    # Rearrange the raw input data (from the source_filepath) into a format that is usable by the AI
    # In particular, map the specified last few days' data into a digestable row
    # This follows LIBSVM format: https://catboost.ai/en/docs/concepts/input-data_libsvm
    # This differs from the last function by handling hourly data, only working for binary setpoints, and generating sim files for later testing
    def generate_binary_map_and_sim(self, source_filepath, parsed_data_filepath, sim_filepath, num_days, timescale='day', binary_setpoints=[0.005]):
        formatted_ailist = []
        formatted_simlist = []
        with open(source_filepath, 'r', newline='') as source_file:
            source_reader = csv.reader(source_file)
            source_list = list(source_reader)

            # Start at index num_days + 1 to go past the header
            i = 1
            try:
                for _ in range(num_days + 1):
                    # Skip rows until we get to the desired start day
                    # Skip an extra day for safety
                    day = self.get_day(int(source_list[i][0]))
                    while(self.get_day(int(source_list[i][0])) == day):
                        i = i + 1
            except IndexError:
                print(f"File {source_filepath} does not have enough data to use!")
                return

            while(i < len(source_list)):
                for setpoint in binary_setpoints:
                    ailist = [] # Data list for training the AI
                    simlist = [] # Data list for running the trained AI against a simulator

                    # First value is a binary representation of whether the high value is greater than the open value times the setpoint
                    # E.g. If high value for day is 5, open is 4.98, setpoint is 0.01, then this would return a 0.
                    # Fill it with a stubbed bad value - this will be filled in later
                    ailist.extend([None])
                    
                    # Add the setpoint value we are using
                    ailist.extend([str(setpoint)])

                    open_price = float(source_list[i][1])
                    
                    # First input is the open price of the present day
                    ailist.extend(source_list[i][1:2])

                    # Generate the simlist
                    # First value of the simlist is the open price of the present day
                    simlist.extend(source_list[i][1:2])
                    # Second is the close price of the day
                    # This is stubbed with a bad value, it is replaced later
                    simlist.extend([None])

                    '''
                    # Add the difference between the present and last timestamp in units of days
                    num_days_since_last_data = (int(source_list[i][0]) - int(source_list[i-1][0])) / 86400000 # num ms in day
                    ailist.extend([str(num_days_since_last_data)])'''

                    # Create an offset value to index back from i
                    offset = 1
                    # Collate data from the whole day onto the list
                    for _ in range(num_days):
                        prev_day = self.get_day(int(source_list[i - offset][0]))
                        while((i != offset) and (self.get_day(int(source_list[i - offset][0])) == prev_day)):
                            ailist.extend(source_list[i - offset][1:]) # start at 1 to skip the timestamp
                            simlist.extend(source_list[i - offset][2:4]) # Add the high and low price to the test list
                            offset = offset + 1

                    present_day = self.get_day(int(source_list[i][0]))
                    # Search for the end of the present day to get the closing price
                    # In the mean time, find the highest price throughout the day
                    high_price = 0
                    while(self.get_day(int(source_list[i][0])) == present_day):
                        if(float(source_list[i][2]) > high_price):
                            high_price = float(source_list[i][2])
                        i = i + 1
                        if(i >= len(source_list)):
                            # reached the end of the list. Break to prevent errors
                            break
                    
                    # Check if the highest price of the day was above the setpoint
                    if((high_price - (open_price * (setpoint + 1))) > 0):
                        ailist[0] = '1'
                    else:
                        ailist[0] = '0'
                        
                    
                    # Add the closing price for the day
                    ailist.extend(source_list[i-1][4:5])
                    # Update the simlist to have the correct closing price
                    simlist[1] = source_list[i-1][4]
                    '''
                    if(j < num_days:
                        if((i-j-1) == 0):
                            # We are reading back earlier than the start of the data set. Assume 1 day has past.
                            ailist.extend(['1'])
                        else:
                            # Add the difference between the present and last timestamp in units of days
                            num_days_since_last_data = (int(source_list[i-j][0]) - int(source_list[i-j-1][0])) / 86400000 # num ms in day
                            ailist.extend([str(num_days_since_last_data)])'''

                    # Add the collated lists as new rows to the two full lists
                    formatted_ailist.append(ailist)
                    formatted_simlist.append(simlist)
        
        # Update the ailist with input labels
        for ailist in formatted_ailist:
            for i in range(1, len(ailist)):
                ailist[i] = f"{i}:{ailist[i]}"


        # Write the parsed data to a new file at the specified location
        with open(parsed_data_filepath,'w', newline='') as parsed_data_file:
            print(f"Writing LIBSVM formatted data to {parsed_data_filepath}")
            csvwriter = csv.writer(parsed_data_file, delimiter=' ')
            csvwriter.writerows(formatted_ailist)
        
        # Write the sim data to the new file
        with open(sim_filepath,'w', newline='') as sim_file:
            print(f"Writing simulator data to {sim_filepath}")
            csvwriter = csv.writer(sim_file, delimiter=' ')
            csvwriter.writerows(formatted_simlist)


if __name__ == '__main__':
    # Default end date is present day, start date is two years prior 
    present_date = datetime.datetime.now()
    end_date = str(present_date)[0:10]
    start_date = end_date.replace('2022', '2020')

    # Default time scale to request is days. Can be updated to hours or minutes.
    timescale = 'day'

    # Default ticker list includes 1 more stock than we can request in one minute to test the request delay feature
    ticker_list = ['AAPL', 'GOOGL', 'ABC', 'MORT', 'NFLX', 'AMC']

    # Default to not using a file
    ticker_file = ''
    num_rand_stocks = 0

    # Parse command line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_date', type=str, nargs=1, default=None, dest='start_date', help='Start date for the request')
    parser.add_argument('-e', '--end_date', type=str, nargs=1, default=None, dest='end_date', help='End date for the request')
    parser.add_argument('-t', '--ticker_file', type=str, nargs=1, default=None, dest='ticker_file', help='File with tickers')
    parser.add_argument('-n', '--num_rand_stocks', type=int, default=0, dest='num_rand_stocks', help='Number of random stocks to pull from the ticker file')
    parser.add_argument('-o', '--ordered_read', type=int, nargs=1, default=0, dest='ordered_read', help='Command an ordered read. 0 = unordered, 1 = alphabetical order, 2 = reverse alphabetical')
    parser.add_argument('--timescale', type=str, nargs=1, default=None, dest='timescale', help='Timescale of data requests. Should be day, hour, or minute.')

    args = parser.parse_args()
    if(args.start_date is not None and args.end_date is not None):
        start_date = args.start_date[0]
        end_date = args.end_date[0]
    ticker_file = args.ticker_file[0]
    num_rand_stocks = args.num_rand_stocks
    print(args.timescale)
    if(args.timescale[0] is not None):
        timescale = args.timescale[0]

    # Create the object to handle our request
    candle = CandlestickRequest()
    
    if not os.path.exists('../CuttingBoard/RawData'):
        os.mkdir('../CuttingBoard/RawData')

    # If a ticker file was provided, overwrite the ticker list with random set of stocks
    if ticker_file:
        if(args.ordered_read[0] in [1, 2]):
            with open(ticker_file, 'r', newline='') as stock_file:
                print(f"Reading data from {ticker_file}")
                reader = csv.reader(stock_file)
                ticker_list = list(reader)
                ticker_list_size = len(ticker_list)
                print(ticker_list[0:5])
                if(args.ordered_read[0] == 2):
                    print("Reverse read order!")
                    ticker_list.reverse()
                    print(ticker_list[0:5])
                new_ticker_list = []
                for ticker in ticker_list:
                    new_ticker_list.append(ticker[0]) 
                ticker_list = new_ticker_list
                #print(ticker_list)
        else:
            ticker_list = candle.pick_random_stocks(ticker_file, num_rand_stocks)

        #print(ticker_list)

    for ticker in ticker_list:
        csv_filename = f"../CuttingBoard/RawData/{ticker}_s{start_date}_e{end_date}.csv"

        # Check if a CSV already exists for the desired data
        if(os.path.exists(csv_filename)):
            print(bcolors.WARNING + f"Data file for ticker {ticker} for date range {start_date} to {end_date} already exists! Skipping." + bcolors.ENDC)
            continue

        # Wait until the next time we can make a request for data
        candle.wait_for_next_req_time()

        # Get the data
        result=candle.make_ticker_request(ticker, start_date, end_date, time_range=timescale)
        
        if result is not None:
            try:
                with open(csv_filename, 'w', newline='') as csvfile:
                    print("Writing data to ", csv_filename)
                    csvwriter = csv.writer(csvfile)
                    candle.parse_ticker_data(result, csvwriter)
            except KeyError:
                # Failed to parse data, so delete the CSV file
                os.remove(csv_filename)
