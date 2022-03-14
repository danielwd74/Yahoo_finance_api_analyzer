from yahoo_fin import options
import requests as rq
import pandas as pd
import json
import datetime
import pgdata
import calendar

def get_unix_times(ticker: str):
    spy_dates = options.get_expiration_dates(ticker)
    new = [datetime.datetime.strptime(date, "%B %d, %Y") for date in spy_dates]
    print(new)
    unix_time = [str(int(calendar.timegm(newTime.timetuple()))) for newTime in new]
    print(unix_time)
    return unix_time


def get_usage():
    file = open('metadata/usage.txt', 'r')
    lines = file.read()
    lines = lines.split("\n")
    total = sum([int(number) for number in lines])
    file.close()
    return total


def request_tickers(ticker: str, usage_count: int, unix_time: str):
    #takes pandas series, returns new updated pandas series of string dates from unix
    #PLEASE NOTE: All time conversions are done in EST
    api_key = pgdata.API_KEY

    dt = str(datetime.datetime.now())
    dt = dt[:dt.find(' ')]

    def convert_date(pandas_series, series_name):
        new_str_date = []
        for day in pandas_series:
            new_str_date.append(datetime.datetime.fromtimestamp(day).strftime('%m/%d/%Y'))
        return pd.Series(new_str_date, name=series_name)

    def convert_date_hours_minuites(pandas_series, series_name):
        new_str_date = []
        for day in pandas_series:
            new_str_date.append(datetime.datetime.fromtimestamp(day).strftime('%m/%d/%Y %H:%M'))
        return pd.Series(new_str_date, name=series_name)

    if usage_count < 100:
        options = {}
        calls = []
        puts = []
        url = f'https://yfapi.net/v7/finance/options/{ticker}?date={unix_time}'
        personal_api_key = {'x-api-key': str(api_key)}

        response = rq.request("GET", url, headers=personal_api_key)
        responseJSON = json.loads(response.text)
        
        #make call options CSV
        callOptions = responseJSON['optionChain']['result'][0]['options'][0]['calls']
        df = pd.DataFrame(data=callOptions)
        
        #convert unix date to excel date
        df['expiration'].update(convert_date(df['expiration'], 'expiration'))
        df['lastTradeDate'].update(convert_date_hours_minuites(df['lastTradeDate'], 'lastTradeDate'))
            
        #interpolate data into a list form
        calls.append(df)

        #make put options CSV
        putOptions = responseJSON['optionChain']['result'][0]['options'][0]['puts']
        df2 = pd.DataFrame(data=putOptions)

        #convert unix date to excel date
        df2['expiration'].update(convert_date(df2['expiration'], 'expiration'))
        df2['lastTradeDate'].update(convert_date_hours_minuites(df2['lastTradeDate'], 'lastTradeDate'))
        
        #interpolate data into a list form
        puts.append(df2)

        #store puts and calls into dictonairy
        options['calls'] = calls
        options['puts'] = puts

        #print(options)
        return options
    else:
        print("Usage count maximum, used 100/100 calls to api")

def get_date_diff(tickers):
    dt = str(datetime.datetime.now())
    dt = dt[:dt.find(' ')]
    return_string = ''
    with open('metadata/date.txt', "r") as f2:
        data_in = (f2.read()).strip()
        readable_date = data_in.split("-")
        readable_date = readable_date[2] + "/" + readable_date[1] + "/" + readable_date[0]
        return_string += (f"Date read from file: {readable_date}\n")
        if data_in != dt:
            f2.close()
            f2 = open('metadata/date.txt', 'w')
            f3 = open('metadata/usage.txt', 'r+')
            f3.truncate(0)
            f2.truncate(0)
            return_string += (f"Current date time value: {dt}\n")
            f2.write(dt)
            f2.close()
            return_string += ("DATE DIFF DETECTED: Allowed maximum 100 reset\n")
            f3.close()
    f2.close()

    with open('metadata/usage.txt', "a") as f3:
        for ticker in tickers:
            f3.write(ticker + "\n")
    
    return return_string