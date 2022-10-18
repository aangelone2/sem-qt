# Copyright (c) 2022 Adriano Angelone
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sqlite3
import datetime
from urllib.request import pathname2url
import pandas as pd




# subclass of Exception associated to errors in db connection
class DatabaseError(Exception):
    pass




# establishes and returns a connection to a database
# + path: the path of the database as a string
# + table: the name of the table as a string
# returns the established connection
# throws DatabaseError if db or table are missing
def init(path: str, table: str) -> sqlite3.Connection:

    # procedure to verify if the database exists
    try:
        dburi = 'file:{}?mode=rw'.format(pathname2url(path))
        conn = sqlite3.connect(dburi, uri = True)
    except sqlite3.OperationalError:
        raise DatabaseError('Database not found')

    # searches in the 'sqlite_master' table for the name of the
    # desired table, throws if not found
    curs = conn.execute(
            '''
            SELECT count(name)
                FROM sqlite_master
                WHERE type = 'table' AND name = \'{}\' ;
            '''.format(table)
    )

    # fetchall() should yield [(1,)]
    if (curs.fetchall()[0][0] != 1):
        raise DatabaseError('Table not found')

    return conn


# adds a record to the database
# + fields: dictionary of strings with fields for year, month,
#   day, type, amount and justification, in this order
# + conn: connection to the database
def add(fields: dict[str], conn: sqlite3.Connection):

    # additional validity check on the date (e.g., checks
    # against things like '31 february')
    try:
        datetime.datetime(
                year = int(fields['year']),
                month = int(fields['month']),
                day = int(fields['day'])
        )
    except ValueError:
        print('Invalid date')
        return

    d = fields['year'] + '-' + fields['month'] + '-' + fields['day']
    t = fields['type']
    a = float(fields['amount'])
    j = fields['justification']

    command = '''
        INSERT INTO expenses
            (date, type, amount, justification)
            VALUES (\'{}\', \'{}\', {}, \'{}\') ;
    '''.format(d, t, a, j)

    conn.execute(command)
    conn.commit()


# extracts data from the database
# + start: starting date as a string, included
# + end: ending date as a string, included
# + conn: connection to the database
# converts the results to a pd.DataFrame, with proper column names
def fetch(start: str, end: str, conn: sqlite3.Connection) -> pd.DataFrame:
    curs = conn.execute('''
        SELECT rowid, date, type, amount, justification
            FROM expenses
            WHERE date BETWEEN \'{}\' AND \'{}\'
            ORDER BY date ;
        '''.format(start, end)
    )

    res_list = curs.fetchall()

    return pd.DataFrame(res_list,
                columns = [
                    'id', 'date', 'type', 'amount', 'justification'
                ]
           )
