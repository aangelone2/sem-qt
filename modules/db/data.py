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

from pandas import DataFrame
from sqlite3 import Connection

from modules.db.connect import DatabaseError



class InputError(Exception):
    """
    Subclassed exception for errors in data input
    """
    pass



def format_df(df: DataFrame)
    """
    Attempts formatting the columns of the passed DataFrame
    to fit with the required schema,
    raising InputError exceptions if data format is incorrect

    Arguments
    -----------------------
    df : DataFrame
        Data, [date, type, amount, justif] (order not relevant)

    Return value
    -----------------------
    Returns formatted DataFrame
    Columns are ordered as [date, type, amount, justification]

    Raises
    -----------------------
    - InputError with associated messages if invalid data
    """

    # Checking date
    if ('date' not in df.columns):
        raise InputError("Missing or mislabeled 'date' field")
    elif (df['date'].isnull().any()):
        raise InputError("Null entry in 'date' field")
    else:
        try:
            df['date'] = pd.to_datetime(
                    df['date'], infer_datetime_format = True, errors = 'raise'
            )
            df['date'] = df['date'].dt.date
        except ValueError:
            raise InputError("Invalid entry in 'date' field")

    # Checking type
    if ('type' not in df.columns):
        raise InputError("Missing or mislabeled 'type' field")
    elif (df['type'].isnull().any()):
        raise InputError("Null entry in 'type' field")
    else:
        # checking for identity with single uppercase letter
        pattern = re.compile('^[A-Z]$')

        if (df['type'].apply(pattern.match).isnull().any()):
            raise InputError("Invalid entry in 'type' field")
        else:
            df['type'] = df['type']

    # Checking amount
    if ('amount' not in df.columns):
        raise InputError("Missing or mislabeled 'amount' field")
    elif (df['amount'].isnull().any()):
        raise InputError("Null entry in 'amount' field")
    else:
        try:
            df['amount'] = df['amount'].astype(float)
        except ValueError:
            raise InputError("Invalid entry in 'amount' field")

    # Checking justification
    if ('justification' not in df.columns):
        raise InputError("Missing or mislabeled 'justification' field")
    elif (df['justification'].isnull().any()):
        raise InputError("Null entry in 'justification' field")
    # FIXME check length of justification field < 100
    else:
        df['justification'] = df['justification']

    return df



def add(conn: Connection, df: DataFrame)
    """
    Adds record(s) to a database through the given Connection

    Arguments
    -----------------------
    conn : Connection
        Connection to a database/table pair
    df : DataFrame
        Data, [date, type, amount, justif] (order not relevant)

    Raises
    -----------------------
    - DatabaseError if invalid Connection
    - InputError if invalid data
    """

    # Checking against empty Connection
    if (conn is None):
        raise DatabaseError('Uninitialized Connection')

    # Checking for data compatibility,
    # raising error to higher level
    try:
        df = format_df(df)
    except InputError:
        raise

    # FIXME Use pd.to_sql()
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



def fetch(conn: Connection,
          start: str, end: str) -> DataFrame:
    """
    Queries the database and returns query results

    Arguments
    -----------------------
    conn : Connection
        Connection to a database/table pair
    start : str
        Starting date as string, included in the query
    end : str
        Ending date as string, included in the query

    Return value
    -----------------------
    A DataFrame containing the query results
    Columns are [id, date, type, amount, justification]

    Raises
    -----------------------
    - DatabaseError if invalid Connection
    """

    if (conn is None):
        raise DatabaseError('Uninitialized Connection')

    command = '''
        SELECT rowid AS id, date, type, amount, justification
        FROM expenses
        WHERE date BETWEEN '{}' AND '{}'
        ORDER BY date ;
    '''.format(start, end)

    # FIXME Use pd.read_sql()
    return DataFrame(
            conn.execute(command).fetchall(),
            columns = [
                'id', 'date', 'type',
                'amount', 'justification'
            ]
    )



def delete(conn: Connection, rowids: list[int]):
    """
    Deletes specified rows from database

    Arguments
    -----------------------
    conn : Connection
        Connection to a database/table pair
    rowids : list[int]
        List of values of 'rowid' for lines to delete

    Raises
    -----------------------
    - DatabaseError if invalid Connection
    """

    if (conn is None):
        raise DatabaseError('Uninitialized Connection')

    # No checks necessary on the input,
    # possible missing indices will result in no-op
    for rowid in rowids:
        command = '''
            DELETE
            FROM expenses
            WHERE rowid = {} ;
        '''.format(rowid)

        conn.execute(command)

    conn.commit()
