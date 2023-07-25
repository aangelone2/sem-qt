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

import os
from sqlite3 import Connection, connect



class DatabaseError(Exception):
    """
    Subclassed exception for errors in db Connection
    """
    pass



def create(filename: str) -> Connection:
    """
    Creates database and establishes Connection

    Arguments
    -----------------------
    filename : str
        Path of the database to create

    Return value
    -----------------------
    Returns the established Connection

    Raises
    -----------------------
    - DatabaseError if database exists
    """

    # Checking if db already exists
    if (os.path.isfile(filename)):
        raise DatabaseError('Database already exists')

    # Creating db and establishing Connection
    conn = connect(filename)

    command = '''
        CREATE TABLE expenses (
            'date' DATE NOT NULL,
            'type' CHAR(1) NOT NULL,
            'amount' DOUBLE PRECISION NOT NULL,
            'justification' VARCHAR(100) NOT NULL
        ) ;
    '''
    conn.execute(command)
    conn.execute('CREATE INDEX date_index ON expenses(date) ;')
    conn.commit()

    return conn



def open(filename: str) -> Connection:
    """
    Establishes Connection to existing database

    Arguments
    -----------------------
    filename : str
        Path of the database to connect to

    Return value
    -----------------------
    Returns the established Connection

    Raises
    -----------------------
    - DatabaseError if database not found
    - DatabaseError if 'expenses' table not found
    - DatabaseError if schema of 'expenses' is not valid
    """

    # Checking if db already exists
    if (not os.path.isfile(filename)):
        raise DatabaseError('Database does not exist')

    # Establishing Connection
    conn = connect(filename)

    # Checking existence of 'expenses' table
    command = '''
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
            AND name = 'expenses' ;
    '''
    # Query should yield a non-empty list
    if (not conn.execute(command).fetchall()):
        raise DatabaseError('Table not found')

    # Checking columns of 'expenses' table
    command = "PRAGMA TABLE_INFO('expenses') ;"
    columns = dataframe(
            conn.execute(command).fetchall(),
            columns = [
                'cid', 'name', 'type',
                'notnull', 'dflt_value', 'pk'
            ]
    )

    # Checking against expected output
    names = ['date', 'type', 'amount', 'justification']
    types = ['DATE', 'CHAR(1)', 'DOUBLE PRECISION', 'VARCHAR(100)']
    notnulls = [1, 1, 1, 1]

    if (columns['name'].to_list() != names
        or columns['type'].to_list() != types
        or columns['notnull'].to_list() != notnulls):
        raise DatabaseError('Corrupted table')

    return conn



def close(conn: Connection)
    """
    Closes the passed Connection

    Arguments
    -----------------------
    conn: Connection
        Connection to close

    Raises
    -----------------------
    - DatabaseError if invalid connection
    """

    if (conn is None):
        raise DatabaseError('Uninitialized Connection')

    conn.close()
