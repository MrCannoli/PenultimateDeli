##########################################################################
# @brief Script to grab price history for a given set of stock tickers   #
##########################################################################

import requests
import time
import csv
import os

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
            print("Hit request limit, waiting ", wait_time, " seconds before continuing.")
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
        raw_response = requests.get(request_url, params={ 'apiKey': CandlestickRequest.api_key }) # run GET request to polygon

        # Add the request time to the array after removing the oldest time
        self._request_times.pop(0)
        self._request_times.append(time.time())
        
        if(raw_response.status_code != 200): # 200 is OK
            raise RuntimeError(f"Failed HTTP request with status code: {raw_response.status_code}")
        else:
            print(f"Data grabbed successfully for {symbol} for the date range {start_date} to {end_date}")
        
        return raw_response.json()

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


'''
Additional fields within the daily_value to play with
resultsarray

c number
The close price for the symbol in the given time period.

h number
The highest price for the symbol in the given time period.

l number
The lowest price for the symbol in the given time period.

n number
The number of transactions in the aggregate window.

o number
The open price for the symbol in the given time period.

t integer
The Unix Msec timestamp for the start of the aggregate window.

v number
The trading volume of the symbol in the given time period.

vw number
The volume weighted average price.
'''

if __name__ == '__main__':
    # Test run
    candle = CandlestickRequest()

    start_date = '2021-06-10'
    end_date = '2021-06-30'

    # Test list includes 1 more stock than we can request in one minute
    ticker_list = ['AAPL', 'GOOGL', 'ABC', 'MORT', 'NFLX', 'AMC']
    
    if not os.path.exists('../DataDeli'):
        os.mkdir('../DataDeli')

    for ticker in ticker_list:
        csv_filename = "../DataDeli/" + ticker + '_s' + start_date + "_e" + end_date + ".csv"

        # Check if a CSV already exists for the desired data
        if(os.path.exists(csv_filename)):
            print("Data file for ticker " + ticker + " already exists! Skipping.")
            continue

        # Wait until the next time we can make a request for data
        candle.wait_for_next_req_time()

        # Get the data
        result=candle.make_ticker_request(ticker, start_date, end_date)

        with open(csv_filename, 'w', newline='') as csvfile:
            print("Writing data to ", csv_filename)
            csvwriter = csv.writer(csvfile)
            candle.parse_ticker_data(result, csvwriter)
