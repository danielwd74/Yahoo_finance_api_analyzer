import requests as rq
import pandas as pd
import json
import datetime

getTicker = input("Please enter a valid ticker: ")
ticker = str(getTicker).upper()

url = f'https://yfapi.net/v7/finance/options/{ticker}'
personal_api_key = 

response = rq.request("GET", url, headers=personal_api_key)
responseJSON = json.loads(response.text)

#print((responseJSON['optionChain']['result'][0]['options'][0]['calls'][2]))
#responseCallOptions = json.loads(responseJSON['optionChain']['result'][0]['options'][0]['calls'])
callOptions = responseJSON['optionChain']['result'][0]['options'][0]['calls']
#print(responseResult)
responseSTR = responseJSON

row_labels = ['contractSymbol']
df = pd.DataFrame(data=callOptions)

dt = str(datetime.datetime.now())
dt = dt[:dt.find(' ')]
#ts = datetime.timestamp(dt)
df.to_csv(f'{dt}_{ticker}.csv', sep=",")