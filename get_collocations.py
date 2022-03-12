from asyncio.windows_events import NULL
import sqlite3
import traceback
import sys

def connect_db(db_name):
    con = sqlite3.connect(db_name)
    return con

def query(cur,sql_query):
    try:
        cur.execute(sql_query)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

