# Copyright (c) 2022 Adriano Angelone
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem.
#
# This file may be used under the terms of the GNU General
# Public License version 3.0 as published by the Free Software
# Foundation and appearing in the file LICENSE included in the
# packaging of this file.  Please review the following
# information to ensure the GNU General Public License version
# 3.0 requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import re
import logging
import datetime
from urllib.request import pathname2url

import sqlite3 as sql
from sqlite3 import Connection as connection

import pandas as pd
from pandas import DataFrame as dataframe




class DatabaseError(Exception):
    """
    Subclassed exception for errors in db connection
    """
    pass




def init(path: str) -> connection:
    """
    Establishes connection to database
    
    Arguments
    -----------------------
    path : str
        path of the database

    Return value
    -----------------------
    Returns the established connection

    Raises
    -----------------------
    - DatabaseError if database or 'expenses' table not found
    """

    # procedure to verify if the database exists
    try:
        dburi = 'file:{}?mode=rw'.format(pathname2url(path))
        conn = sql.connect(dburi, uri = True)
    except sql.OperationalError:
        raise DatabaseError('database not found')

    # searches in the 'sqlite_master' table
    # for the name of the desired table, throws if not found
    command = '''SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = 'expenses' ;'''

    # Query should yield a non-empty dataframe
    if (pd.read_sql(command, conn).empty):
        raise DatabaseError('table not found')

    return conn




def add(conn: connection, df: dataframe):
    """
    Adds record(s) to a database through the given connection
    
    Arguments
    -----------------------
    conn : connection
        connection to a database/table pair
    df : dataframe
        data, [date, type, amount, justif] (order not relevant)
    """

    logging.info('in db.add')

    df.to_sql('expenses', conn,
              if_exists = 'append', index = False)




def fetch(conn: connection,
          start: str, end: str) -> dataframe:
    """
    Queries the database and returns query results
    
    Arguments
    -----------------------
    conn : connection
        connection to a database/table pair
    start : str
        Starting date as string, included in the query
    end : str
        Ending date as string, included in the query

    Return value
    -----------------------
    A dataframe containing the query results
    Columns are [id, date, type, amount, justification]
    """

    command = '''SELECT rowid AS id, date, type, amount, justification
        FROM expenses WHERE date BETWEEN '{}' AND '{}'
        ORDER BY date ;'''.format(start, end)

    return pd.read_sql(command, conn)




def fetch_types(conn: connection) -> list[str]:
    """
    Returns a list of the expense character types

    Arguments
    -----------------------
    conn : connection
        connection to a database/table pair

    Return value
    -----------------------
    List of the characters of the expense types
    """

    command = 'SELECT DISTINCT type FROM expenses ;'
    return pd.read_sql(command, conn)['type'].to_list()




def parse_csv(filename: str) -> dataframe:
    """
    Parses a CSV file containing a list of expenses,
    returns a DataFrame containing the data if valid


    Arguments
    -----------------------
    filename : str
        name of the CSV file to parse
        should include [date, type, amount, justification] fields
        order may be different, other fields are ignored


    Return value
    -----------------------
    dataframe containing the parsed data
    columns are ordered as [date, type, amount, justification]


    Raises
    -----------------------
    - DatabaseError if file not found or data is invalid
    """

    res = dataframe()

    try:
        df = pd.read_csv(filename, encoding = 'iso-8859-1')
    except FileNotFoundError:
        raise DatabaseError('CSV file not found')
    except UnicodeDecodeError:
        raise DatabaseError('incorrect character encoding')

    logging.info('file read')

    # Checking date
    if ('date' not in df.columns):
        raise DatabaseError("missing or mislabeled 'date' field")
    elif (df['date'].isnull().any()):
        raise DatabaseError("null entry in 'date' field")
    else:
        try:
            res['date'] = pd.to_datetime(
                    df['date'], infer_datetime_format = True, errors = 'raise'
            )
            res['date'] = res['date'].dt.date
        except ValueError:
            raise DatabaseError("invalid entry in 'date' field")

    logging.info('date checked')

    # Checking type
    if ('type' not in df.columns):
        raise DatabaseError("missing or mislabeled 'type' field")
    elif (df['type'].isnull().any()):
        raise DatabaseError("null entry in 'type' field")
    else:
        # checking for identity with single uppercase letter
        pattern = re.compile('^[A-Z]$')

        if (df['type'].apply(pattern.match).isnull().any()):
            raise DatabaseError("invalid entry in 'type' field")
        else:
            res['type'] = df['type']

    logging.info('type checked')

    # Checking amount
    if ('amount' not in df.columns):
        raise DatabaseError("missing or mislabeled 'amount' field")
    elif (df['type'].isnull().any()):
        raise DatabaseError("null entry in 'amount' field")
    else:
        try:
            res['amount'] = df['amount'].astype(float)
        except ValueError:
            raise DatabaseError("invalid entry in 'amount' field")

    logging.info('amount checked')

    # Checking justification
    if ('justification' not in df.columns):
        raise DatabaseError("missing or mislabeled 'justification' field")
    elif (df['type'].isnull().any()):
        raise DatabaseError("null entry in 'justification' field")
    else:
        res['justification'] = df['justification']

    logging.info('justification checked')

    return res
