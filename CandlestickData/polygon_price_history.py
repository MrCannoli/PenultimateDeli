##########################################################################
# @brief Script to grab price history for a given set of stock tickers   #
##########################################################################

import requests
import time

class CandlestickRequest:
    # This is a key to a free account, limited to 5 requests per second
    api_key = '5xDdaB3S8gsL0jTsxpCaiLMLHTqyD7tD'
    
    # We can only send 5 requests per minute on a free account
    REQ_LIMIT=5

    def __init__(self):
        # This array keeps track of the time of the last 5 requests made so we can avoid the limit
        self._request_times = [0,0,0,0,0]

    # URL used to make requests of the polygon API

    def set_api_key(new_key: str):
        api_key = new_key
    
    # Get the number of requests that have occurred in the last minute
    def get_request_counter(self):
        present_time = time.time()
        request_count = 0
        for t in self._request_times:
            if((present_time - t) < 60):
                request_count+=1
        return request_count


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

    ticker_code = 'GOOGL' # the trade symbol for the company you want to pull history for
    start_date = '2021-07-22' # free accounts are limited to 2 years worth of history
    end_date = '2021-07-23'

    ticker_list = ['AAPL', 'GOOGL', 'ABC', 'MORT', 'NFLX', 'AMC']
    
    for ticker in ticker_list:
        result=candle.make_ticker_request(ticker, start_date, end_date)
        
        for daily_value in result["results"]:
            print(f'Epoch: { daily_value["t"] }') 
            print(f'Open: ${ daily_value["o"] }')
            print(f'Close: ${ daily_value["c"] }\n')
