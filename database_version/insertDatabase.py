import psycopg2
from psycopg2 import sql
import pgdata
import pandas as pd
import getData
import datetime

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
        self.create_table_success =  self.create_table()
        dt = str(datetime.datetime.now())
        dt = dt[:dt.find(' ')]
        self.request_date = dt
        self.expiration = expiration
    
    def create_table(self):
        query = sql.SQL('''CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL UNIQUE,
                    contractSymbol VARCHAR(100),
                    strike INTEGER,
                    currency VARCHAR(10),
                    lastPrice DOUBLE PRECISION,
                    change DOUBLE PRECISION,
                    percentChange DOUBLE PRECISION,
                    volume INTEGER,
                    openInterest INTEGER,
                    bid DOUBLE PRECISION,
                    ask DOUBLE PRECISION,
                    contractSize VARCHAR(100),
                    expiration DATE,
                    lastTradeDate DATE,
                    impliedVolatility DOUBLE PRECISION,
                    inTheMoney BOOLEAN,
                    atOrBelowBid BOOLEAN,
                    atOrAboveAsk BOOLEAN,
                    betweenTheMarket BOOLEAN,
                    requestDate DATE
                )''').format(sql.Identifier(self.table_full_name))
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except:
            return False
        else:
            return True

    def insert_data(self, dataframe: pd.DataFrame):
        #REPLACE NULL/NaN values in volume with 0  to indicate no volume
        dataframe['volume'].fillna(value=int(0), inplace=True)
        dataframe['openInterest'].fillna(value=int(0), inplace=True)
        dataframe[['volume', 'openInterest']] = dataframe[['volume', 'openInterest']].astype(int)
        if dataframe['volume'].isnull().values.any():
            print("NULL VALUES DETECTED")
        else:
            print("GOOD")
 
        #calculate new columns 3 new columns
        dataframe['atOrBelowBid'] = (dataframe['lastPrice'] <= dataframe['bid'])
        dataframe['atOrAboveAsk'] = (dataframe['lastPrice'] >= dataframe['ask'])
        dataframe['betweenTheMarket'] = (dataframe['lastPrice'] > dataframe['bid']) & (dataframe['lastPrice'] < dataframe['ask'])
        dataframe['requestDate'] = self.request_date

        #dataframe = dataframe.replace(r'^\s*$', None, regex=True)
        records = dataframe.to_dict(orient='records')#[list(row) for row in dataframe.itertuples(index=False)]
        
        #records = [row for row in dataframe.to_dict()]

        insert_query = sql.SQL(''' INSERT INTO {} (contractSymbol, strike, currency, 
                                                    lastPrice, change, percentChange,
                                                    volume, openInterest, bid, ask, contractSize,
                                                    expiration, lastTradeDate, impliedVolatility,
                                                    inTheMoney, atOrBelowBid, atOrAboveAsk, betweenTheMarket,
                                                    requestDate)
                                    VALUES (%(contractSymbol)s, %(strike)s, %(currency)s, %(lastPrice)s,
                                    %(change)s, %(percentChange)s, %(volume)s, %(openInterest)s, %(bid)s,
                                    %(ask)s, %(contractSize)s, %(expiration)s, %(lastTradeDate)s, %(impliedVolatility)s,
                                    %(inTheMoney)s, %(atOrBelowBid)s, %(atOrAboveAsk)s, %(betweenTheMarket)s, %(requestDate)s)
                                ''').format(sql.Identifier(self.table_full_name))

        self.cursor.executemany(insert_query, records)
        self.conn.commit()

    def can_insert(self):
        #see if table even exists
        query = sql.SQL('''SELECT COUNT(*)
                            FROM {}''').format(sql.Identifier(self.table_full_name))
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]

        if count > 0:
            #get the newest date entered
            query = sql.SQL('''SELECT CAST(requestDate AS varchar)
                        FROM {}
                        ORDER BY requestDate DESC''').format(sql.Identifier(self.table_full_name))
            
            newestExpiration = sql.SQL('''SELECT CAST(expiration AS varchar)
                                    FROM {}
                                    ORDER BY expiration DESC''').format(sql.Identifier(self.table_full_name))
            try:
                self.cursor.execute(query)
                found_date = self.cursor.fetchone()[0]
                self.cursor.execute(newestExpiration)
                newest_expiration = self.cursor.fetchone()[0]
                self.conn.commit()
            except:
                print("Could not get request date or nearest expiration")
                return False
            else:
                if newest_expiration != self.expiration:
                    return True
                elif found_date == self.request_date:
                    print("Cannot add to end of table, data already requested today")
                    return False
                else:
                    return True
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
    usage = getData.get_usage()
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