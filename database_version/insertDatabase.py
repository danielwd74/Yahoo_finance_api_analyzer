from distutils.log import error
import psycopg2
from psycopg2 import sql
import pgdata
import pandas as pd
import getData
import datetime
import getDayDiff

class cursorClass:
    def __init__(self, tableName, tableType, expiration):
        self.conn = psycopg2.connect(user=pgdata.USER, 
                                password=pgdata.PASSOWRD, 
                                host=pgdata.HOST, 
                                database=pgdata.DATABASE)
        self.cursor = self.conn.cursor()
        self.table_name = tableName
        self.table_type = tableType
        self.table_full_name = self.table_name + "_" + self.table_type
        self.create_table_success =  self.create_table2()
        dt = str(datetime.datetime.now())
        dt = dt[:dt.find(' ')]
        self.request_date = dt
        self.expiration = expiration
        self.datetime_expiration_string = str(datetime.datetime.strptime(self.expiration, '%B %d, %Y'))
    
    def create_table2(self):
        query = sql.SQL('''CREATE TABLE IF NOT EXISTS {} (
                            id SERIAL UNIQUE,
                            contract_name VARCHAR(150),
                            strike INTEGER,
                            last_trade_date date,
                            expiration DATE,
                            request_date DATE,
                            last_price DOUBLE PRECISION,
                            bid DOUBLE PRECISION,
                            ask DOUBLE PRECISION,
                            change DOUBLE PRECISION,
                            volume INTEGER,
                            open_interest INTEGER,
                            implied_volatility DOUBLE PRECISION,
                            at_or_below_bid BOOLEAN,
                            at_or_above_ask BOOLEAN,
                            between_the_market BOOLEAN   
                        )''').format(sql.Identifier(self.table_full_name))
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except psycopg2.Error as error:
            print("ERROR: ", error)
            print("Could not create reg table")
            return False
        else:
            return True


    def insert_data2(self, dataframe: pd.DataFrame):
        #calculate new columns 3 new columns
        dataframe['at_or_below_bid'] = (dataframe['last_price'] <= dataframe['bid'])
        dataframe['at_or_above_ask'] = (dataframe['last_price'] >= dataframe['ask'])
        dataframe['between_the_market'] = (dataframe['last_price'] > dataframe['bid']) & (dataframe['last_price'] < dataframe['ask'])

        #convert to records
        records = dataframe.to_dict(orient='records')
        insert_query = sql.SQL('''INSERT INTO {} (contract_name, strike, last_trade_date,
                                                  expiration, request_date, last_price, bid,
                                                  ask, change, volume, open_interest,
                                                  implied_volatility, at_or_below_bid,
                                                  at_or_above_ask, between_the_market)
                                   VALUES(%(contract_name)s, %(strike)s, %(last_trade_date)s, %(expiration)s,
                                   %(request_date)s, %(last_price)s, %(bid)s, %(ask)s, %(change)s, %(volume)s,
                                   %(open_interest)s, %(implied_volatility)s, %(at_or_below_bid)s, %(at_or_above_ask)s,
                                   %(between_the_market)s)
                                ''').format(sql.Identifier(self.table_full_name))
        try:
            self.cursor.executemany(insert_query, records)
            self.conn.commit()
        except psycopg2.Error as error:
            print("ERROR: ", error)
            print("Could not insert into reg table")
            return False
        else:
            return True
        


    def create_table_diff(self):
        create_query = sql.SQL('''CREATE TABLE IF NOT EXISTS {} (
                                    id SERIAL UNIQUE,
                                    contractsymbol VARCHAR(150),
                                    strike INTEGER,
                                    delta_volume INTEGER,
                                    delta_openinterest INTEGER,
                                    delta_impliedvolatility_percent DOUBLE PRECISION,
                                    delta_impliedvolatility DOUBLE PRECISION
                                )''').format(sql.Identifier(self.table_full_name + '_diff'))
        try:
            self.cursor.execute(create_query)
            self.conn.commit()
        except:
            print("Could not create table diff")
            return False
        else:
            return True

    def insert_table_diff(self, dataframe: pd.DataFrame):
        insert_query = sql.SQL('''INSERT INTO {} (contractsymbol, strike, delta_volume, delta_openinterest,
                                            delta_impliedvolatility_percent, delta_impliedvolatility)
                                  VALUES(%s, %s, %s, %s, %s, %s)
                                ''').format(sql.Identifier(self.table_full_name + '_diff'))
        dataframe = list(dataframe.itertuples(index=False, name=None))
        print(dataframe)
        try:
            self.cursor.executemany(insert_query, dataframe)
            self.conn.commit()
        except:
            print("Could not insert into diff table")
            return False
        else:
            return True

    def can_insert(self):
        #see if table even exists
        query = sql.SQL('''SELECT COUNT(*)
                            FROM {}''').format(sql.Identifier(self.table_full_name))
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]

        if count > 0:
            #get the newest date entered
            query = sql.SQL('''SELECT CAST(request_date AS varchar)
                        FROM {}
                        ORDER BY request_date DESC''').format(sql.Identifier(self.table_full_name))
            
            check_entry_exists = sql.SQL('''SELECT COUNT(*)
                                    FROM {}
                                    WHERE expiration = %s and request_date = %s
                                    ''').format(sql.Identifier(self.table_full_name))
            try:
                newRequestDate = datetime.datetime.strptime(self.request_date, '%Y-%m-%d')
                newDatetimeExpiration = datetime.datetime.strptime(self.datetime_expiration_string[:10], '%Y-%m-%d')
                self.cursor.execute(check_entry_exists, (newDatetimeExpiration, newRequestDate))
                count = int(self.cursor.fetchone()[0])
            except psycopg2.Error as error:
                print("ERROR: ", error)
                print("Could not get can insert info")
                return False
            else:
                if count <= 0:
                    print("Can still insert into database, info with expiration and request date does not exist")
                    return True
                else:
                    print("Cannot insert into database, values with given expiration and request date exist")
                    return False
        else:
            return True

    def close(self):
        if self.conn:
            self.conn.close()
            self.cursor.close()
            table_full_name = self.table_name + "_"  + self.table_type
            print(f"Sucessfully closed database {table_full_name}")


if __name__ == "__main__":
    ticker = str(input("Please enter a ticker: "))
    
    expirations = getData.get_unix_times2(ticker)
    for expiration in expirations:
        tickerCalls = cursorClass(ticker, "calls", expiration)
        tickerPuts = cursorClass(ticker, "puts", expiration)
        if tickerCalls.create_table_success and tickerCalls.can_insert():
            if tickerPuts.create_table_success and tickerPuts.can_insert():
                tickers = getData.request_tickers2(ticker, expiration)
                for key, value in tickers.items():
                    if key == 'puts':
                        tickerPuts.insert_data2(value)
                    elif key == 'calls':
                        tickerCalls.insert_data2(value)
    
    
    '''usage = getData.get_usage()

    file = open('metadata/usage.txt', 'r')
    prev_use = int(file.readline())
    ticker_expirations_unixtimes, ticker_expiration_datetime = getData.get_unix_times(ticker)
    predicted_usage = prev_use + int(len(ticker_expirations_unixtimes))
    if (predicted_usage < 100):
        print(f"Predicted usage at {predicted_usage} / 100")
        for expiration_unix, expiration_datetime in zip(ticker_expirations_unixtimes, ticker_expiration_datetime):
            tickerCalls = cursorClass(ticker, "calls", expiration_unix, expiration_datetime)
            tickerPuts = cursorClass(ticker, "puts", expiration_unix, expiration_datetime)
            if tickerCalls.create_table_success and tickerCalls.can_insert():
                if tickerPuts.create_table_success and tickerPuts.can_insert():
                    for unix_expiration in ticker_expirations_unixtimes:
                        print(tickerCalls.datetime_expiration_string)
                        tickers = getData.request_tickers2(ticker, getData.get_usage(), tickerCalls.datetime_expiration_string)
                        for key, value in tickers.items():
                            for dataframe in value:
                                if key == 'puts':
                                    tickerPuts.insert_data(dataframe)
                                elif key == 'calls':
                                    tickerCalls.insert_data(dataframe)
                        if getDayDiff.check_prev_exists(tickerCalls):
                            date_diff_dataframe_calls = getDayDiff.get_day_diff(tickerCalls)
                            if tickerCalls.create_table_diff():
                                tickerCalls.insert_table_diff(date_diff_dataframe_calls)
                            date_diff_dataframe_puts = getDayDiff.get_day_diff(tickerPuts)
                            if tickerPuts.create_table_diff():
                                tickerPuts.insert_table_diff(date_diff_dataframe_puts)
                        else:
                            print("Previous data does not exist, cannot get difference")
                else:
                    print("Could not insert into ticker puts")
            else:
                print("Could not insert into ticker calls")
            tickerPuts.close()
            tickerCalls.close()
    else:
        print(f"Maximum predicted usage met: {predicted_usage} / 100")
   
    current_use = len(ticker_expirations_unixtimes) + prev_use
    file = open('metadata/usage.txt', 'w')
    file.write(str(current_use))
    file.close()'''


    if False:
        if (usage < 100):
            print(f"Usage at {usage}/100")
            ticker_expirations = getData.get_unix_times(ticker)
            for expiration in ticker_expirations:
                tickerCalls=cursorClass(ticker, "calls", expiration)
                if tickerCalls.create_table_success and tickerCalls.can_insert():
                    tickerPuts=cursorClass(ticker, "puts", expiration)
                    if tickerPuts.create_table_success and tickerPuts.can_insert():
                        tickers = getData.request_tickers(ticker, getData.get_usage(), expiration)
                        #T.insert_data()
                        for key, value in tickers.items():
                            for dataframe in value:
                                if key == 'puts':
                                    tickerPuts.insert_data(dataframe)
                                elif key == 'calls':
                                    tickerCalls.insert_data(dataframe)
                    else:
                        print("Could not insert into table puts") 
                    tickerPuts.close()
                else:
                    print("Could not insert into table calls") 
                tickerCalls.close()
        else:
            print(f"Maximum usage met, usage at {usage}/100")

        file = open('metadata/usage.txt', 'r')
        prev_use = int(file.readline())
        current_use = len(ticker_expirations) + prev_use

        file = open('metadata/usage.txt', 'w')
        file.write(str(current_use))
        file.close()