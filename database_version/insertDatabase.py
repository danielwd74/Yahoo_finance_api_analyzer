import psycopg2
from psycopg2 import sql
import pgdata
import pandas as pd
import getData
import datetime

class cursorClass:
    def __init__(self, tableName, tableType):
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
        dataframe['volume'] = dataframe['volume'].fillna(0)
 
        #calculate new columns 3 new columns
        dataframe['atOrBelowBid'] = (dataframe['lastPrice'] <= dataframe['bid'])
        dataframe['atOrAboveAsk'] = (dataframe['lastPrice'] >= dataframe['ask'])
        dataframe['betweenTheMarket'] = (dataframe['lastPrice'] > dataframe['bid']) & (dataframe['lastPrice'] < dataframe['ask'])
        dataframe['requestDate'] = self.request_date
        #print(dataframe)
        #dataframe = dataframe.replace(r'^\s*$', None, regex=True)
        records = [list(row) for row in dataframe.itertuples(index=False)]

        insert_query = sql.SQL(''' INSERT INTO {} (contractSymbol, strike, currency, 
                                                    lastPrice, change, percentChange,
                                                    volume, openInterest, bid, ask, contractSize,
                                                    expiration, lastTradeDate, impliedVolatility,
                                                    inTheMoney, atOrBelowBid, atOrAboveAsk, betweenTheMarket,
                                                    requestDate)
                                    VALUES (%s, %s, %s, %s,
                                    %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s)
                                ''').format(sql.Identifier(self.table_full_name))
        for record in records:
            self.cursor.execute(insert_query, record[:])
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
            try:
                self.cursor.execute(query)
                self.conn.commit()
            except:
                print("Could not get data")
                return False
            else:
                if self.cursor.fetchone()[0] == self.request_date:
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
    tickerCalls=cursorClass(ticker, "calls")
    if tickerCalls.create_table_success and tickerCalls.can_insert():
        tickerPuts=cursorClass(ticker, "puts")
        if tickerPuts.create_table_success and tickerPuts.can_insert():
            tickers = getData.request_tickers(ticker, getData.get_usage())
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
            