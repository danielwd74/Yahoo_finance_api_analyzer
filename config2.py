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
        df['expiration'] = df['expiration'].apply(lambda x: f'=TEXT((({x} / 86400) + DATE(1970, 1, 1)), "mm/dd/yyyy")')
        df['lastTradeDate'] = df['lastTradeDate'].apply(lambda x: f'=TEXT((({x} / 86400) + DATE(1970, 1, 1)), "mm/dd/yyyy")')

        #ts = datetime.timestamp(dt)
        df.to_csv(f'call_options/{dt}_{ticker}_C.csv', sep=",")

        #make put options CSV
        putOptions = responseJSON['optionChain']['result'][0]['options'][0]['puts']
        df2 = pd.DataFrame(data=putOptions)
        
        df2.to_csv(f'put_options/{dt}_{ticker}_P.csv', sep=",")
else:
    print("Usage count maximum, used 100/100 calls to api")

f.close()

with open('date.txt', "r+") as f2:
    data_in = (f2.read()).strip()
    if data_in:
        if data_in != dt:
            f3 = open('usage.txt', 'r+')
            f3.truncate(0)
            f2.truncate(0)
            f2.write(dt)
            print("DATE DIFF DETECTED: Allowed maximum 100 reset")
            f3.close()
    else:
        f2.write(dt)
    
with open('usage.txt', "a") as f3:
    for ticker in tickers:
        f3.write(ticker + "\n")


    