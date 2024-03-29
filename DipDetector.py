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
number_of_dates_back = 30
number_of_lowest_values = 30


def render_header(header):
    os.system('clear')
    print("TEAM SPACEBEAR PRODUCTIONS \nAll rights reserved \n \n" + header + "\n")

def save_tickers_to_file(input_array, reload):
    tickers = []    
    if reload == False:
        #Read from file to combine
        try: 
            with open("Tickers.pickle", "rb") as f:
                tickers = pickle.load(f)
            os.system("rm Tickers.pickle")
        except IOError:
            print("File does not exist")
        for i in range(0, len(input_array)):
            tickers.append(input_array[i])
        #Write to file
        with open("Tickers.pickle", "wb") as f:
            pickle.dump(tickers, f)
        print("Saving tickers " + str(len(tickers)) + " to file....")

    elif reload == True:
        os.system("rm Tickers.pickle")
        with open("Tickers.pickle", "wb") as f:
            pickle.dump(input_array, f)
        print("Saving tickers " + str(len(input_array)) + " to file.... AS RELOAD")


def get_index_tickers(link, table_class, row_start, column_number, reload_tickers):
    tickers = []
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
    save_tickers_to_file(tickers , reload_tickers)
    print("------------------------------Finished ticker ----------------------------------------------")

def submit_own_tickers():
    render_header("TICKER SUBMITTER")
    ticker_input = raw_input("Please enter your tickers with a space inbetween(Ex: TSLA AAPL AMZN)")
    save_tickers_to_file(ticker_input.split(), False)
    print(ticker_input.split())
    raw_input("Press Enter to return...")



def get_data_from_yahoo(reload_file):
    #Loads tickers from tickers.pickle
    try:
        with open("Tickers.pickle", "rb") as f:
            tickers = pickle.load(f)
            print("Successfully loaded " + str(len(tickers)) + " tickers from file")
    except:
        print("Could not locate Tickers.pickle file")
    #Makes directory to store all stock data
    if reload_file == True:
        if os.path.exists("stock_dfs"):
            os.system('rm -r stock_dfs')
        if not os.path.exists("stock_dfs"):
            os.makedirs("stock_dfs")
            print("Made directory stock_dfs")
    elif reload_file == False:
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
    print(df.tail())
    df.plot(x='Date', y='Adj Close')
    plt.title(desired_ticker)
    plt.show()

def print_tickers_data():
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

def print_tickers():
    with open("Tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    for ticker in tickers:
        print(ticker)
    print("You have " + str(len(tickers)) + " tickers in total")
    raw_input("Press Enter to return...")

def calculate_dip():
    render_header("DIP CALCULATION")
    detection_range = 1
    #Ask about sensitivity of dipdetection
    user_choice = raw_input("How large would you like the detection margin be? \n(Lower yields more results) \nDefault: " + str(detection_range) + "\n \nDipMargin: ")
    try:
        detection_range = int(user_choice)
    except:
        return

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

            #Get the previous days Adj Close values
            most_recent_values = []
            for i in range(0, number_of_dates_back):
                most_recent_values.append(df.iloc[number_of_rows - 1 - i]['Adj Close'])
            #print("Most recent values of current ticker: \n ")
            #print(most_recent_values)

            # #Sort adj_close for this ticker. Lowest values at the top. Add lowest values to a list
            # df.sort_values('Adj Close', inplace=True)
            # lowest_values = []
            # for i in range(0, number_of_lowest_values):
            #     lowest_values.append(df.iloc[i]['Adj Close'])
            # print("Lowest values of current ticker: \n ")
            # print(lowest_values)

            # Compare todays value with recent values if they are marginly lower a dip is detected
            for i in range(0, len(most_recent_values)):
                if most_recent_row['Adj Close'] + detection_range < most_recent_values[i]:
                    print("RESULT: DIP DETECTED")
                    Dip_list.append("{}".format(entry).replace('.csv', ''))
                    break
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
    else:
        print("No tickers are experiencing a dip")
    raw_input("Press Enter to return...")

def start():
    while True:
        render_header("MENU")
        print(dt.date.today())
        user_input = input("What do you want to do? \n 1. Reload tickers and ticker data (Might take some minutes) \n 2. Load ticker data (Quick if you have the tickers) \n 3. Submit ticker \n 4. Visualize ticker \n 5. Print all tickers with data availible \n 6. Print every ticker\n 7. Calculate dip \n \n")
        if str(user_input) == "1":
            get_index_tickers("https://www.advfn.com/nasdaq/nasdaq.asp", 'market tab1', 2, 1, True)
            get_index_tickers("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", 'wikitable sortable', 1, 0, False)
            get_data_from_yahoo(True)
        elif str(user_input) == "2":
            get_data_from_yahoo(False)
        elif str(user_input) == "3":
            submit_own_tickers()
        elif str(user_input) == "4":
            visualize_ticker("")
        elif str(user_input) == "5":
            print_tickers_data()
        elif str(user_input) == "6":
            print_tickers()
        elif str(user_input) == "7":
            calculate_dip()
       
start()