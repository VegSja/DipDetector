import bs4 as bs
import datetime as dt 
import matplotlib.pyplot as plt
from matplotlib import style
import os
import fnmatch
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests

#Sets the style of the graphs
style.use('ggplot')


#Setting up values
detection_range = 1
tickers = []

def save_tickers_to_file():
    with open("Tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    print("Saving tickers to file....")

def get_index_tickers(link, table_class, row_start, column_number):
    resp = requests.get(link)
    soup = bs.BeautifulSoup(resp.text, "lxml")
    #Gets the table html
    table = soup.find('table', {'class':table_class})
    #Goes through each row in the table except the first two and extracts text from column 2 which is the ticker column
    for row in table.findAll('tr')[row_start:]:
        ticker = row.findAll('td')[column_number].text
        #Removes different symbols which yahoo doesnt understand
        ticker = ticker.replace('\n', '')
        ticker = ticker.replace('.', '-')
        tickers.append(ticker)
        print("Retriving ticker: " + ticker)

def get_data_from_yahoo():
    #Loads tickers from tickers.pickle
    with open("Tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
        print("Successfully loaded " + str(len(tickers)) + " tickers from file")
    #Makes directory to store all stock data
    if not os.path.exists("stock_dfs"):
        os.makedirs("stock_dfs")
        print("Made directory stock_dfs")
    
    start = dt.datetime(2010,1,1)
    print("Today's date: " + str(dt.date.today()))
    end = dt.date.today()
    
    #Pulls data from yahoo and stores it in an individual .csv file for each ticker
    for ticker in tickers:
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            df = web.DataReader(ticker, 'yahoo', start, end)
            print("Successfully pulled data from Yahoo for ticker: " + ticker)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print("Already have {}".format(ticker))
    print("-----------------------------------------Finished Yahoo pull----------------------------")

def visualize_ticker(desired_ticker):
    if desired_ticker == "":
        desired_ticker = raw_input("Which ticker do you want to visualize? \n \n Ticker: ")
    df = pd.read_csv('stock_dfs/{}.csv'.format(str(desired_ticker)))
    df.plot(x='Date', y='Close')
    plt.title(desired_ticker)
    plt.show()

def print_tickers():
    listOfFiles = os.listdir('./stock_dfs')
    pattern = "*.csv"
    i = 0
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            print(entry.replace('.csv',''))
            i += 1
    print("Number of tickers:" + str(i))
    raw_input("Press Enter to return...")
    return

def calculate_dip():
    Dip_list = []
    #Get dataframe for this ticker
    listOfFiles = os.listdir('./stock_dfs')
    pattern = "*.csv"
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            print("-------------Ticker: {}-----------------".format(entry))
            df = pd.read_csv('stock_dfs/{}'.format(entry))
            df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

            #Get today's Adj Close value
            number_of_rows = len(df.index)
            print("This ticker has: " + str(number_of_rows) + " rows")
            most_recent_row = df.iloc[number_of_rows - 1]
            print("Most recent value of current ticker: " + str(most_recent_row['Adj Close']))

            #Sort adj_close for this ticker. Lowest values at the top
            df.sort_values('Adj Close', inplace=True)
            print("Lowest value of current ticker: " + str(df.iloc[0]['Adj Close']))

            # Compare todays value with other low values
            if most_recent_row['Adj Close'] - detection_range < df.iloc[0]['Adj Close']:
                print("DIP DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                Dip_list.append("{}".format(entry).replace('.csv', ''))
            else:
                print("NO DIP")
    if len(Dip_list) > 0:
        print("\n These tickers are experiencing a dip: \n")
        for i in range(0, len(Dip_list)):
            print(Dip_list[i])
        choice = raw_input("Do you want to visualize these tickers?(y/n): ")
        if choice == "y":
            for i in range(0, len(Dip_list)):
                visualize_ticker(Dip_list[i])
        else:
            return
    raw_input("Press Enter to return...")

def start():
    while True:
        os.system("clear")
        print(dt.date.today())
        user_input = input("What do you want to do? \n 1. Reload tickers and ticker data \n 2. Reload ticker data \n 3. Visualize ticker \n 4. Print all tickers availible \n 5. Calculate dip \n \n")
        if str(user_input) == "1":
            get_index_tickers("https://www.advfn.com/nasdaq/nasdaq.asp", 'market tab1', 2, 1)
            get_index_tickers("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", 'wikitable sortable', 1, 0)
            print("-----------------------Finished tickerretrieve-------------------------- \n Number of tickers: " + str(len(tickers)))
            save_tickers_to_file()
            get_data_from_yahoo()
        elif str(user_input) == "2":
            get_data_from_yahoo()
        elif str(user_input) == "3":
            visualize_ticker("")
        elif str(user_input) == "4":
            print_tickers()
        elif str(user_input) == "5":
            calculate_dip()
       
start()