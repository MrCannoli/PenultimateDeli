# PenultimateDeli
Taking some salami from diydsp/ultimateDeli

## General Guide

### Dependencies
To run this project you will need `xgboost` at a minimum.
If you want to automate data grabbing optimally, you'll need `at` and the python3 `requests` library.

### Getting Data
1. Go to polygon.io and get a free API key. Replace the key in CandlestickData/CandlestickRequest.py with your own.
2. Change directory to be in CandlestickData
3. Prep your linux box to start requesting data at midnight using `at midnight tomorrow`.
4. Request data by using the command line options for CandlestickRequest.py. Recommendation: `python3 CandlestickRequest.py -n 7200 -o 1 -t "../StockLists/polygon_stock_only_list.csv"`.
   If you have a free api key, you're limited to 5 requests a minute. If you want all ~12000 stocks data from polygon, you'll need your machine to run for a while.

### Processing Data
1. Change directory to be in CandlestickData
2. Optionally modify and run `FilterData.py` or another custom script to downselect stocks within a desired price range
3. Run `prep_cutting_board.sh <desired_num_days> <directory_with_stock_data>`.

Your data will be processed, tagged, and placed into subfolders of `CuttingBoard/ParsedData`.

### Running xgboost
1. Modify `BagelStation/butter.py` to point to your folder with parsed data
2. Update the hyper parameters of `butter.py` to your heart's desire.
3. Run the model and see how it trains by simply running `python3 butter.py`.
