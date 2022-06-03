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
    def wait_for_next_req_time(self):
        if(CandlestickRequest.get_request_counter(self) == CandlestickRequest.REQ_LIMIT):
            wait_time = 60.1 - (time.time() - max(self._request_times))
            print(bcolors.OKCYAN + f"Hit request limit, waiting {wait_time} seconds before continuing.")
            time.sleep(wait_time)

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
        # Generate the formatted request URL
        request_url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{step}/{time_range}/{start_date}/{end_date}'

        if(CandlestickRequest.get_request_counter(self) == CandlestickRequest.REQ_LIMIT):
            raise RuntimeError("Hit the request limit - slow down!")

        # Make the HTTP request for the stock ticker data
        raw_response = requests.get(request_url, params={ 'apiKey': CandlestickRequest.api_key })

        # Add the request time to the array after removing the oldest time
        self._request_times.pop(0)
        self._request_times.append(time.time())
        
        if(raw_response.status_code == 200): # 200 is OK
            print(bcolors.OKGREEN + f"Data grabbed successfully for {symbol} for the date range {start_date} to {end_date}")
        elif(raw_response.status_code == 429): # Calls happened too quickly
            raise RuntimeError("Made subsequent file calls too soon!")
        else:
            raise RuntimeError(f"Failed HTTP request with status code: {raw_response.status_code}")
        
        return raw_response.json()

    # Create a CSV file from a given set of JSON ticker data
    def parse_ticker_data(self, ticker_data, csvwriter):
        headers = ['Timestamp', 'Open price', 'High Price', 'Low Price', 'Close Price', 'Num Transactions', 'Trade volume', 'Volume Weighted Price']
        csvwriter.writerow(headers)

        parsed_data = [None] * 8
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

    # Get a random list of stocks from the given ticker file
    def pick_random_stocks(self, ticker_file, num_rand_stocks):
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



if __name__ == '__main__':
    # Default end date is present day, start date is two years prior 
    present_date = datetime.datetime.now()
    end_date = str(present_date)[0:10]
    start_date = str(present_date - datetime.timedelta(weeks=104))[0:10] # For some reason they don't support years?!

    # Default ticker list includes 1 more stock than we can request in one minute to test the request delay feature
    #ticker_list = ['AAPL', 'GOOGL', 'ABC', 'MORT', 'NFLX', 'AMC']
    ticker_list = []

    # Default to not using a file
    ticker_file = ''
    num_rand_stocks = 0

    # Parse command line inputs
    parser = argparse.ArgumentParser(description='Process requests for historical stock data')
    parser.add_argument('--start_date', type=str, nargs=1, dest=start_date, help='Start date for the request')
    parser.add_argument('--end_date', type=str, nargs=1, dest=end_date, help='End date for the request')
    parser.add_argument('--ticker_file', type=str, nargs=1, dest=ticker_file, help='File with tickers')
    parser.add_argument('--num_rand_stocks', type=int, nargs=1, dest=num_rand_stocks, help='Number of random stocks to pull from the ticker file')

    args = parser.parse_args()

    # Create the object to handle our request
    candle = CandlestickRequest()
    
    if not os.path.exists('../DataDeli'):
        os.mkdir('../DataDeli')

    # If a ticker file was provided, overwrite the ticker list with random set of stocks
    if ticker_file:
        ticker_list = candle.pick_random_stocks(ticker_file, num_rand_stocks)

    for ticker in ticker_list:
        csv_filename = f"../DataDeli/{ticker}_s{start_date}_e{end_date}.csv"

        # Check if a CSV already exists for the desired data
        if(os.path.exists(csv_filename)):
            print(bcolors.WARNING + f"Data file for ticker {ticker} for date range {start_date} to {end_date} already exists! Skipping.")
            continue

        # Wait until the next time we can make a request for data
        candle.wait_for_next_req_time()

        # Get the data
        result=candle.make_ticker_request(ticker, start_date, end_date)

        with open(csv_filename, 'w', newline='') as csvfile:
            print("Writing data to ", csv_filename)
            csvwriter = csv.writer(csvfile)
            candle.parse_ticker_data(result, csvwriter)