# Script to continually poll and request ticker data from polygon.io, until the full ticker list is collated
# Note: This requires some manual touch up on the final generated file
import CandlestickRequest
import csv

candle = CandlestickRequest.CandlestickRequest()

search_key='A'
csv_filename = f"../StockLists/polygon_list.csv"

with open(csv_filename,'w', newline='') as parsed_data_file:
    csvwriter = csv.writer(parsed_data_file)

    for i in range(1000):
        # Wait until the next time we can make a request for data
        candle.wait_for_next_req_time()

        # Get the list of data starting at the search key
        print(f'Starting ticker request at search key {search_key}')
        ticker_list=candle.request_ticker_list(search_key)

        # Update the search key to be the last ticker received
        search_key = ticker_list['results'][-1]['ticker']

        candle.parse_ticker_list(ticker_list, csvwriter)