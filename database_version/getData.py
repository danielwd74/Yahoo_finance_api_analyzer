from yahoo_fin import options
import requests as rq
import pandas as pd
import json
import datetime
import pgdata
import calendar


def get_unix_times2(ticker:str):
    dates = options.get_expiration_dates(ticker)
    return dates

def get_unix_times(ticker: str):
    dates = options.get_expiration_dates(ticker)
    new = [datetime.datetime.strptime(date, "%B %d, %Y") for date in dates]
    unix_time = [str(int(calendar.timegm(newTime.timetuple()))) for newTime in new]
    new = [datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d') for unixtime in unix_time]
    return unix_time, new


def get_usage():
    file = open('metadata/usage.txt', 'r')
    lines = file.read()
    lines = lines.split("\n")
    total = sum([int(number) for number in lines])
    file.close()
    return total

def request_tickers2(ticker: str, expiration: str):
    dt = str(datetime.datetime.now())
    dt = dt[:dt.find(' ')]

    options_return = {}
    calls = options.get_calls(ticker, str(expiration))
    puts = options.get_puts(ticker, str(expiration))

    #remove unneeded calculated columns
    del calls['% Change']
    del puts['% Change']


    rename_dict = {'Contract Name': 'contract_name',
                    'Last Trade Date': 'last_trade_date',
                    'Strike': 'strike',
                    'Last Price': 'last_price',
                    'Bid': 'bid',
                    'Ask': 'ask',
                    'Change': 'change',
                    'Volume': 'volume',
                    'Open Interest': 'open_interest',
                    'Implied Volatility': 'implied_volatility'}

    calls = calls.rename(columns=rename_dict)
    puts = puts.rename(columns=rename_dict)

    #add new columns
    calls['expiration'] = datetime.datetime.strptime(expiration, '%B %d, %Y')
    calls['request_date'] = dt
    puts['expiration'] = datetime.datetime.strptime(expiration, '%B %d, %Y')
    puts['request_date'] = dt

    #filter the data, get rid of nulls or modify type
    calls['last_trade_date'] = [datetime.datetime.strptime(time[:-4], '%Y-%m-%d %I:%M%p') for time in calls['last_trade_date']]
    puts['last_trade_date'] = [datetime.datetime.strptime(time[:-4], '%Y-%m-%d %I:%M%p') for time in puts['last_trade_date']]
    calls['implied_volatility'] = [float(iv[:-2]) / 100 for iv in calls['implied_volatility']]
    puts['implied_volatility'] = [float(iv[:-2]) / 100 for iv in puts['implied_volatility']]
    calls = calls.replace({'volume': '-', 'open_interest': '-', 'bid': '-', 'ask': '-', 'last_price': '-'}, 0)
    puts = puts.replace({'volume': '-', 'open_interest': '-', 'bid': '-', 'ask': '-', 'last_price': '-'}, 0)

    #make sure volume and open interest INT
    calls[['volume', 'open_interest']] = calls[['volume', 'open_interest']].astype(int)
    calls[['last_price', 'bid', 'ask']] = calls[['last_price', 'bid', 'ask']].astype(float)
    puts[['volume', 'open_interest']] = puts[['volume', 'open_interest']].astype(int)
    puts[['last_price', 'bid', 'ask']] = puts[['last_price', 'bid', 'ask']].astype(float)

    #add to dictonairy
    options_return['calls'] = calls
    options_return['puts'] = puts

    return options_return
    
######################################################
########### OLD DEPRECIATED METHOD ###################
######################################################
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
        print(response.text)
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