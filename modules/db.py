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


def add(fields: dict[str], conn: sqlite3.Connection):
    """
    Adds a record to a database through the given connection
    

    Arguments
    -----------------------
    fields : dict[str]
        {field: value} dictionary of the entry to add
        entries are [year, month, day, type, amount, just]
    conn : sqlite3.Connection
        connection to a database/table pair


    Return value
    -----------------------
    None


    Raises
    -----------------------
    - ValueError if invalid date
    """

    logging.info('in db.add')

    d = fields['date']
    t = fields['type']
    a = float(fields['amount'])
    j = fields['justification']

    command = '''
        INSERT INTO expenses
            (date, type, amount, justification)
            VALUES (\'{}\', \'{}\', {}, \'{}\') ;
    '''.format(d, t, a, j)

    logging.info(command)

    conn.execute(command)
    conn.commit()


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
