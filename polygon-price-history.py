import requests

# to get your own api_key just create a new account on polygon.io
# this key is just a temp account
api_key = 'Jri4lniDcRh6wK_BpvbK7VzsZnelNus9'
ticker_code = 'GOOGL' # the trade symbol for the company you want to pull history for
start_date = '2021-07-22' # free accounts are limited to 2 years worth of history
end_date = '2021-08-22'
aggregate_range = 'day' # this has down to the minute resolution if you want it
aggregate_step = '1' # each step is 1 day
aggregate_url = f'https://api.polygon.io/v2/aggs/ticker/{ticker_code}/range/{aggregate_step}/{aggregate_range}/{start_date}/{end_date}'

aggregate_response_raw = requests.get(aggregate_url , params={ 'apiKey': api_key }) # run GET request to polygon
print(aggregate_response_raw.url) # for debugging if the URL was built correctly 

aggregate_response = aggregate_response_raw.json() # pull and parse our response into a python dictionary
for daily_value in aggregate_response['results']: 
    print(f'Epoch: { daily_value["t"] }') # gotta use "" for ref strings here as '' are used for the f'' string FYI
    print(f'Open: ${ daily_value["o"] }')
    print(f'Close: ${ daily_value["c"] }\n')


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
