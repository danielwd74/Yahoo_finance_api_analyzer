import psycopg2
from psycopg2 import sql
from insertDatabase import cursorClass
import pgdata
import pandas as pd
import getData
#import datetime
from datetime import datetime, timedelta

def check_prev_exists(object: cursorClass):
    #check if previous day exists in database
    current_day_dt = datetime.strptime(object.request_date, '%Y-%m-%d')
    prev_day_dt = current_day_dt - timedelta(1)
    prev_day_str = (str(prev_day_dt)[:10]).strip()

    get_prev_day_query = sql.SQL('''SELECT COUNT(*) FROM {} WHERE requestdate = %s''').format(sql.Identifier(object.table_full_name))
    object.cursor.execute(get_prev_day_query, (prev_day_str,))
    result = int(object.cursor.fetchone()[0])
    if (result > 0):
        return True
    else:
        return False

def get_day_diff(object: cursorClass):
    #5 and 6 are Saturday and Sunday respectively
    #Create datetime object
    current_day_dt = datetime.strptime(object.request_date, '%Y-%m-%d')
    prev_day_dt = current_day_dt - timedelta(1)

    prev_day_str = (str(prev_day_dt)[:10]).strip()
    current_day_str = (str(current_day_dt)[:10]).strip()

    tableName = sql.Identifier(object.table_full_name)
    get_days_query = sql.SQL('''SELECT contractsymbol, t1.strike, expiration, (t2.volume - t1.volume) as delta_volume, 
                                    (t2.openinterest - t1.openinterest) as delta_openinterest,
                                    (t2.impliedvolatility*100 - t1.impliedvolatility*100) as delta_impliedvolatility_percent,
                                    (t2.impliedvolatility - t1.impliedvolatility) as delta_impliedvolatility
                                FROM {} AS t1 INNER JOIN (SELECT strike, volume, openinterest, impliedvolatility
                                                            FROM {}
                                                            WHERE requestdate = %s and expiration = %s) AS t2
                                                ON t1.strike = t2.strike
                                WHERE t1.requestdate = %s AND t1.expiration = %s AND id between 0 and 366
                                ''').format(tableName, tableName)
    object.cursor.execute(get_days_query, (current_day_str, object.datetime_expiration_string, prev_day_str, object.datetime_expiration_string))
    result = object.cursor.fetchall()
    #print(result)
    df = pd.DataFrame(result, columns=['contractsymbol', 'strike', 'expiration', 'delta_volume', 'delta_openinterest', 'delta_impliedvolatility_percent', 'delta_impliedvolatility'])
    object.conn.commit()
    return df
