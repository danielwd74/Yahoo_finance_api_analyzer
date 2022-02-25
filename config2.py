import requests as rq
import pandas as pd
import json
import datetime

getTicker = input("Please enter a valid ticker list seperated by comma and space: ")
ticker = str(getTicker).upper()

tickers = ticker.split(", ")
f = open('apikey.txt', 'r')
api_key = (f.read()).strip()

with open('usage.txt', 'r') as f3:
    usage = f3.read()
    usage_count = len(usage.split("\n"))
    print(f"The number of ticker calls used is {usage_count}/100")

dt = str(datetime.datetime.now())
dt = dt[:dt.find(' ')]

#takes pandas series, returns new updated pandas series of string dates from unix
#PLEASE NOTE: All time conversions are done in EST
def convert_date(pandas_series, series_name):
    new_str_date = []
    for day in pandas_series:
        new_str_date.append(datetime.datetime.fromtimestamp(day).strftime('%m/%d/%Y'))
    return pd.Series(new_str_date, name=series_name)


if usage_count < 100:
    for ticker in tickers:
        url = f'https://yfapi.net/v7/finance/options/{ticker}'
        personal_api_key = {'x-api-key': str(api_key)}

        response = rq.request("GET", url, headers=personal_api_key)
        responseJSON = json.loads(response.text)

        #make call options CSV
        callOptions = responseJSON['optionChain']['result'][0]['options'][0]['calls']
        df = pd.DataFrame(data=callOptions)

        #convert unix date to excel date
        #old method
        #df['expiration'] = df['expiration'].apply(lambda x: f'=TEXT((({x} / 86400) + DATE(1970, 1, 1)), "mm/dd/yyyy")')
        #new method
        df['expiration'].update(convert_date(df['expiration'], 'expiration'))

        #old method
        #df['lastTradeDate'] = df['lastTradeDate'].apply(lambda x: f'=TEXT((({x} / 86400) + DATE(1970, 1, 1)), "mm/dd/yyyy")')
        #new method
        df['lastTradeDate'].update(convert_date(df['lastTradeDate'], 'lastTradeDate'))
            
        df.to_csv(f'call_options/{dt}_{ticker}_C.csv', sep=",")

        #make put options CSV
        putOptions = responseJSON['optionChain']['result'][0]['options'][0]['puts']
        df2 = pd.DataFrame(data=putOptions)

        #convert unix date to excel date
        df2['expiration'].update(convert_date(df2['expiration'], 'expiration'))
        df2['lastTradeDate'].update(convert_date(df2['lastTradeDate'], 'lastTradeDate'))
        
        df2.to_csv(f'put_options/{dt}_{ticker}_P.csv', sep=",")
else:
    print("Usage count maximum, used 100/100 calls to api")

f.close()

with open('date.txt', "r") as f2:
    data_in = (f2.read()).strip()
    print(f"Date read from file: {data_in}")
    if data_in != dt:
        f2.close()
        f2 = open('date.txt', 'w')
        f3 = open('usage.txt', 'r+')
        f3.truncate(0)
        f2.truncate(0)
        print(f"Current date time value: {dt}")
        f2.write(dt)
        f2.close()
        print("DATE DIFF DETECTED: Allowed maximum 100 reset")
        f3.close()
f2.close()
    
with open('usage.txt', "a") as f3:
    for ticker in tickers:
        f3.write(ticker + "\n")


    