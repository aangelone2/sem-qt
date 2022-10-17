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




class DatabaseError(Exception):
    pass




def db_init(path, table):
    try:
        dburi = 'file:{}?mode=rw'.format(pathname2url(path))
        conn = sqlite3.connect(dburi, uri = True)
    except sqlite3.OperationalError:
        raise DatabaseError('Database not found')

    curs = conn.cursor()

    curs.execute(
            '''
            SELECT count(name)
                FROM sqlite_master
                WHERE type = 'table' AND name = \'{}\' ;
            '''.format(table)
    )

    if (curs.fetchone()[0] == 0):
        raise DatabaseError('Table not found')

    return conn


def db_add(fields, conn):
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


def db_fetch(start, end, conn):
    res_list = conn.execute('''
        SELECT rowid, date, type, amount, justification
            FROM expenses
            WHERE date BETWEEN \'{}\' AND \'{}\'
            ORDER BY date ;
        '''.format(start, end)
    )

    return pd.DataFrame(res_list,
            columns = [
                'id', 'date', 'type', 'amount', 'justification'
            ]
           )
