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

    # Rearrange the raw input data (from the source_filepath) into a format that is usable by the AI
    # In particular, map the specified last few days' data into a digestable row
    def generate_input_map(self, source_filepath, parsed_data_filepath, num_days):
        # Start at index num_days + 1 to go past the header
        # Input data is past days (sequentially), with last input being the present day's opening price
        # Test data is the high value for the present day
        formatted_list = []
        with open(source_filepath, 'r', newline='') as source_file:
            source_reader = csv.reader(source_file)
            source_list = list(source_reader)

            for i in range(1+num_days, len(source_list)):
                sublist = []
                for j in range(num_days):
                    # Include each row of inputs starting at oldest first
                    sublist.extend(source_list[i-(num_days-j)][1:8]) # start at 1 to skip the timestamp
                # Open price (input) and high price (test value) of the present day
                sublist.extend(source_list[i][1:3])
                formatted_list.append(sublist)

        # Write the parsed data to a new file at the specified location
        with open(parsed_data_filepath,'w', newline='') as parsed_data_file:
            csvwriter = csv.writer(parsed_data_file)
            csvwriter.writerows(formatted_list)


if __name__ == '__main__':
    # Default end date is present day, start date is two years prior 
    present_date = datetime.datetime.now()
    end_date = str(present_date)[0:10]
    start_date = end_date.replace('2022', '2020')

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

    args = parser.parse_args()
    if(args.start_date is not None and args.end_date is not None):
        start_date = args.start_date[0]
        end_date = args.end_date[0]
    ticker_file = args.ticker_file[0]
    num_rand_stocks = args.num_rand_stocks

    # Create the object to handle our request
    candle = CandlestickRequest()
    
    if not os.path.exists('../DataDeli'):
        os.mkdir('../DataDeli')

    # If a ticker file was provided, overwrite the ticker list with random set of stocks
    if ticker_file:
        ticker_list = candle.pick_random_stocks(ticker_file, num_rand_stocks)
        print(ticker_list)

    for ticker in ticker_list:
        csv_filename = f"../DataDeli/RawData/{ticker}_s{start_date}_e{end_date}.csv"

        # Check if a CSV already exists for the desired data
        if(os.path.exists(csv_filename)):
            print(bcolors.WARNING + f"Data file for ticker {ticker} for date range {start_date} to {end_date} already exists! Skipping." + bcolors.ENDC)
            continue

        # Wait until the next time we can make a request for data
        candle.wait_for_next_req_time()

        # Get the data
        result=candle.make_ticker_request(ticker, start_date, end_date)
        
        if result is not None:
            try:
                with open(csv_filename, 'w', newline='') as csvfile:
                    print("Writing data to ", csv_filename)
                    csvwriter = csv.writer(csvfile)
                    candle.parse_ticker_data(result, csvwriter)
            except KeyError:
                # Failed to parse data, so delete the CSV file
                os.remove(csv_filename)
