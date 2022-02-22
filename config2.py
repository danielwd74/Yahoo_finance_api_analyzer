import requests as rq
import pandas as pd
import json
import datetime

getTicker = input("Please enter a valid ticker list seperated by comma and space: ")
ticker = str(getTicker).upper()

tickers = ticker.split(", ")
f = open('apikey.txt', 'r')
api_key = (f.read()).strip()

f_usage_count = open('usage.txt', 'r')

for ticker in tickers:
    url = f'https://yfapi.net/v7/finance/options/{ticker}'
    personal_api_key = {'x-api-key': str(api_key)}

    response = rq.request("GET", url, headers=personal_api_key)
    responseJSON = json.loads(response.text)

    #make call options CSV
    callOptions = responseJSON['optionChain']['result'][0]['options'][0]['calls']
    df = pd.DataFrame(data=callOptions)

    dt = str(datetime.datetime.now())
    dt = dt[:dt.find(' ')]
    #ts = datetime.timestamp(dt)
    df.to_csv(f'call_options/{dt}_{ticker}_C.csv', sep=",")

    #make put options CSV
    putOptions = responseJSON['optionChain']['result'][0]['options'][0]['puts']
    df2 = pd.DataFrame(data=putOptions)
    
    df2.to_csv(f'put_options/{dt}_{ticker}_P.csv', sep=",")
f.close()

with open('date.txt', "r+") as f2:
    data_in = (f2.read()).strip()
    if data_in:
        if data_in != dt:
            f3 = open('usage.txt', 'r+')
            f3.truncate(0)
            f2.truncate(0)
            f2.write(dt)
            f3.close()
    else:
        f2.write(dt)
    
with open('usage.txt', "w") as f3:
    for ticker in tickers:
        f3.write(ticker + "\n")