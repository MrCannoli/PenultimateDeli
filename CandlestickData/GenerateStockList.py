import csv

polygon_basefile = '../StockLists/polygon_list.csv'
polygon_stockfile = '../StockLists/polygon_stock_only_list.csv'

filtered_list = []

with open(polygon_basefile, 'r', newline='') as stock_file:
    print(f"Reading data from {polygon_basefile}")
    reader = csv.reader(stock_file)

    stock_list = list(reader)
    stock_list_size = len(stock_list)

    for i in range(stock_list_size):
        if(stock_list[i][1] == 'stocks'):
            filtered_list.append(stock_list[i])

with open(polygon_stockfile, 'w', newline='') as filtered_file:
    csvwriter = csv.writer(filtered_file)
    csvwriter.writerows(filtered_list)