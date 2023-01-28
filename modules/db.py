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
import datetime

from pysqlcipher3 import dbapi2 as sql
from pysqlcipher3.dbapi2 import Connection as connection

import pandas as pd
from pandas import DataFrame as dataframe




class DatabaseError(Exception):
    """
    Subclassed exception for errors in db connection
    """
    pass




def create(filename: str, pssw: str) -> connection:
    """
    Creates encrypted database and establishes connection
    
    Arguments
    -----------------------
    filename : str
        Path of the database to connect to
    pssw : str
        Passphrase to access the database
        Will be verified by the database when connecting

    Return value
    -----------------------
    Returns the established connection

    Raises
    -----------------------
    - DatabaseError if database exists
    """

    # Attempting connection, checking credentials
    conn = sql.connect(filename)
    conn.execute("PRAGMA key = '{}' ;".format(pssw))
    conn.execute('PRAGMA cypher_compatibility = 3 ;')

    command = '''CREATE TABLE expenses (
            'date' DATE NOT NULL,
            'type' CHAR(1) NOT NULL,
            'amount' DOUBLE PRECISION NOT NULL,
            'justification' VARCHAR(100) NOT NULL
    ) ;'''
    conn.execute(command)
    conn.commit()

    return conn




def login(filename: str, pssw: str) -> connection:
    """
    Establishes connection to existing database

    Arguments
    -----------------------
    filename : str
        Path of the database to connect to
    pssw : str
        Passphrase to access the database
        Will be verified by the database when connecting

    Return value
    -----------------------
    Returns the established connection

    Raises
    -----------------------
    - DatabaseError if database not found
    - DatabaseError if credentials are incorrect
    - DatabaseError if 'expenses' table not found
    """

    # Attempting connection, checking credentials
    try:
        conn = sql.connect(filename)
        conn.execute("PRAGMA key = '{}' ;".format(pssw))
        conn.execute('PRAGMA cypher_compatibility = 3 ;')
        conn.execute('SELECT * from sqlite_master ;')
    except sql.DatabaseError:
        raise DatabaseError('invalid credentials')

    # Checking existence of 'expenses' table
    command = '''
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
            AND name = 'expenses' ;
        '''

    # Query should yield a non-empty list
    # Cannot use pd.read_sql(), problems with pysqlcipher3
    if (not conn.execute(command).fetchall()):
        raise DatabaseError('table not found')

    # Checking columns of 'expenses' table
    command = '''PRAGMA TABLE_INFO('expenses') ;'''

    # Cannot use pd.read_sql(), problems with pysqlcipher3
    columns = dataframe(
            conn.execute(command).fetchall(),
            columns = [
                'cid', 'name', 'type',
                'notnull', 'dflt_value', 'pk'
            ]
    )

    names = ['date', 'type', 'amount', 'justification']
    types = ['DATE', 'CHAR(1)', 'DOUBLE PRECISION', 'VARCHAR(100)']
    notnulls = [1, 1, 1, 1]

    if (columns['name'].to_list() != names
        or columns['type'].to_list() != types
        or columns['notnull'].to_list() != notnulls):
        raise DatabaseError('corrupted table')

    return conn




def add(conn: connection, df: dataframe):
    """
    Adds record(s) to a database through the given connection
    
    Arguments
    -----------------------
    conn : connection
        Connection to a database/table pair
    df : dataframe
        Data, [date, type, amount, justif] (order not relevant)
    """

    if (conn is None):
        raise DatabaseError('uninitialized connection')

    # Cannot use pd.to_sql(), problems with pysqlcipher3
    for ir, r in df.iterrows():
        command = '''
            INSERT INTO expenses
            (date, type, amount, justification)
            VALUES
            ('{}', '{}', {}, '{}') ;
        '''.format(
                r['date'], r['type'],
                r['amount'], r['justification']
        )

        conn.execute(command)

    conn.commit()




def fetch(conn: connection,
          start: str, end: str) -> dataframe:
    """
    Queries the database and returns query results
    
    Arguments
    -----------------------
    conn : connection
        Connection to a database/table pair
    start : str
        Starting date as string, included in the query
    end : str
        Ending date as string, included in the query

    Return value
    -----------------------
    A dataframe containing the query results
    Columns are [id, date, type, amount, justification]
    """

    if (conn is None):
        raise DatabaseError('uninitialized connection')

    command = '''
        SELECT rowid AS id, date, type, amount, justification
        FROM expenses
        WHERE date BETWEEN '{}' AND '{}'
        ORDER BY date ;
    '''.format(start, end)

    # Cannot use pd.read_sql(), problems with pysqlcipher3
    return dataframe(
            conn.execute(command).fetchall(),
            columns = [
                'id', 'date', 'type',
                'amount', 'justification'
            ]
    )




def parse_csv(filename: str) -> dataframe:
    """
    Parses a CSV file containing a list of expenses,
    returns a DataFrame containing the data if valid

    Arguments
    -----------------------
    filename : str
        Name of the CSV file to parse
        Should include [date, type, amount, justification] fields
        Order may be different, other fields are ignored

    Return value
    -----------------------
    Dataframe containing the parsed data
    Columns are ordered as [date, type, amount, justification]

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

    # Checking justification
    if ('justification' not in df.columns):
        raise DatabaseError("missing or mislabeled 'justification' field")
    elif (df['type'].isnull().any()):
        raise DatabaseError("null entry in 'justification' field")
    else:
        res['justification'] = df['justification']

    return res




def save_csv(conn: connection, filename: str):
    """
    Dumps the specified database/table to a CSV file

    Arguments
    -----------------------
    conn : connection
        Connection to a database/table pair
    filename : str
        Filename of the output CSV file
    """

    if (conn is None):
        raise DatabaseError('uninitialized connection')

    command = 'SELECT * FROM expenses ;'

    # Cannot use pd.read_sql(), problems with pysqlcipher3
    dataframe(
            conn.execute(command).fetchall(),
            columns = [
                'date', 'type', 'amount', 'justification'
            ]
    ).to_csv(
            filename, index = False
    )




def clear(conn: connection):
    """
    Clears the specified database/table

    Arguments
    -----------------------
    conn : connection
        Connection to a database/table pair
    """

    if (conn is None):
        raise DatabaseError('uninitialized connection')

    command = 'DELETE FROM expenses ;'
    conn.execute(command)

    conn.commit()
