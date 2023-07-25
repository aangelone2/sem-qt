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

from pandas import DataFrame
from sqlite3 import Connection

from modules.db.connect import DatabaseError
from modules.db.data import InputError, format_df



def parse_csv(filename: str) -> DataFrame:
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
    - InputError if file not found or invalid data
    """

    try:
        df = pd.read_csv(filename, encoding = 'iso-8859-1')
    except FileNotFoundError:
        raise InputError('CSV file not found')
    except UnicodeDecodeError:
        raise InputError('Incorrect character encoding')

    try:
        df = format_df(df)
    except InputError:
        raise

    return df



def save_csv(conn: Connection, filename: str):
    """
    Dumps the specified database/table to a CSV file

    Arguments
    -----------------------
    conn : Connection
        Connection to a database/table pair
    filename : str
        Filename of the output CSV file

    Raises
    -----------------------
    - DatabaseError if invalid Connection
    """

    if (conn is None):
        raise DatabaseError('Uninitialized connection')

    command = 'SELECT * FROM expenses ;'

    # FIXME Use pd.read_sql()
    DataFrame(
            conn.execute(command).fetchall(),
            columns = [
                'date', 'type', 'amount', 'justification'
            ]
    ).to_csv(
            filename, index = False
    )
