import psycopg2
from psycopg2 import sql
import pgdata
import pandas as pd

class cursorClass:
    def __init__(self, tableName):
        self.conn = psycopg2.connect(user=pgdata.USER, 
                                password=pgdata.PASSOWRD, 
                                host=pgdata.HOST, 
                                database=pgdata.DATABASE)
        self.cursor = self.conn.cursor()
        self.table_name = tableName
    
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
                    inTheMoney BOOLEAN
                )''').format(sql.Identifier(self.table_name))
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self):
        calls_dataframe = pd.read_csv('2022-03-01_T_C.csv', sep=',')
        #records = [x for x in calls_dataframe.to_records(index=False)]
        #records = calls_dataframe.to_dict()
        #result = records
        #for res in result:
        #print(records)
        contractSymbol = [x for x in calls_dataframe['contractSymbol']]
        strike = [x for x in calls_dataframe['strike']]

        insert_query = sql.SQL(''' INSERT INTO {} (contractSymbol, strike, currency, 
                                                    lastPrice, change, percentChange,
                                                    volume, openInterest, bid, ask, contractSize,
                                                    expiration, lastTradeDate, impliedVolatility,
                                                    inTheMoney)
                                    VALUES (%(contractSymbol)s, %(strike)s, %(currency)s, %(lastPrice)s,
                                    %(change)s, %(percentChange)s, %(volume)s, %(openInterest)s, %(bid)s,
                                    %(ask)s, %(contactSize)s, %(expiration)s, %(lastTradeDate)s, %(impliedVolatility)s,
                                    %(inTheMoney)s)
                                ''').format(sql.Identifier(self.table_name))
        self.cursor.execute(insert_query, (contractSymbol, strike, ))
        print(self.cursor.fetchall())
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.cursor.close()
            print("Sucessfully closed database")


if __name__ == "__main__":
    T=cursorClass('T')
    T.create_table()
    T.insert_data()
    T.close()