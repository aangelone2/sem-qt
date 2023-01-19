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
import sqlite3
import logging
import datetime
from urllib.request import pathname2url
import pandas as pd




class DatabaseError(Exception):
    """
    Subclassed exception for errors in db connection
    """
    pass




def init(path: str, table: str) -> sqlite3.Connection:
    """
    Establishes connection to database
    

    Arguments
    -----------------------
    path : str
        path of the database
    table : str
        name of the table to connect to


    Return value
    -----------------------
    Returns the established connection


    Raises
    -----------------------
    - DatabaseError if database or table not found
    """

    # procedure to verify if the database exists
    try:
        dburi = 'file:{}?mode=rw'.format(pathname2url(path))
        conn = sqlite3.connect(dburi, uri = True)
    except sqlite3.OperationalError:
        raise DatabaseError('database not found')

    # searches in the 'sqlite_master' table for the name of the
    # desired table, throws if not found
    curs = conn.execute(
            '''
            SELECT count(name)
                FROM sqlite_master
                WHERE type = 'table' AND name = \'{}\' ;
            '''.format(table)
    )

    # Last query should yield [(1,)]
    if (curs.fetchall()[0][0] != 1):
        raise DatabaseError('table not found')

    return conn


def add(conn: sqlite3.Connection,
        dct: dict[str] = None, df: pd.DataFrame = None):
    """
    Adds a record to a database through the given connection
    

    Arguments
    -----------------------
    conn : sqlite3.Connection
        connection to a database/table pair
    dct : dict[str]
        {field: value} dictionary of the entry to add
        entries are [date, type, amount, justif]
    df : pd.DataFrame
        allows bulk importing from dataframe
        columns should be [date, type, amount, justif]
    """

    logging.info('in db.add')
    logging.info('types = {}'.format(df.dtypes))

    def insert(d: str, t: str, a: str, j: str):
        command = '''
            INSERT INTO expenses
                (date, type, amount, justification)
                VALUES (\'{}\', \'{}\', {}, \'{}\') ;
        '''.format(d, t, float(a), j) ;

        logging.info(command)

        conn.execute(command)
        conn.commit()

    if (dct is not None):
        insert(dct['date'], dct['type'],
               dct['amount'], dct['justification'])
    elif (df is not None):
        for idx, row in df.iterrows():
            insert(row['date'], row['type'],
                   row['amount'], row['justification'])


def fetch(start: str, end: str,
          conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Queries the database and returns query results
    

    Arguments
    -----------------------
    start : str
        Starting date as string, included in the query
    end : str
        Ending date as string, included in the query
    conn : sqlite3.Connection
        connection to a database/table pair


    Return value
    -----------------------
    A pd.DataFrame containing the query results
    Columns are [id, date, type, amount, justification]
    """

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


def fetch_types(conn: sqlite3.Connection) -> list[str]:
    """
    Returns a list of the expense character types


    Arguments
    -----------------------
    conn : sqlite3.Connection
        connection to a database/table pair


    Return value
    -----------------------
    List of the characters of the expense types
    """

    curs = conn.execute('SELECT DISTINCT type FROM expenses ;')
    # Returns types such as [('R',), ('E',)]
    lst = curs.fetchall()
    # Cleanup
    lst = [l[0] for l in lst]

    return lst


def parse_csv(filename: str) -> pd.DataFrame:
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
    pd.DataFrame containing the parsed data
    columns are ordered as [date, type, amount, justification]


    Raises
    -----------------------
    - DatabaseError if file not found or data is invalid
    """

    res = pd.DataFrame()

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
