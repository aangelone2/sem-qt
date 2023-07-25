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

from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import os



class DatabaseError(Exception):
    """
    Subclassed exception for errors in db Connection
    """
    pass



class Model():
    """
    Model wrapper class

    Public attributes
    -----------------------
    list_model: QSqlTableModel
        Model for general expense data

    Private attributes
    -----------------------
    __parent: QWidget
        Parent QWidget
    __conn: QSqlDatabase
        Database connection
    __start_date: str
        Starting date for model data
    __end_date: str
        Starting date for model data

    Public methods
    -----------------------
    __init__()
        Constructor
    create_db(str)
        Creates and inits connection to new DB
    open_db(str)
        Creates and inits connection to existing DB
    init_model()
        Initializes list model
    close()
        Closes connection with DB
    save_csv(str)
        Dumps the database to a CSV file
    """

    def __init__(self, parent: QWidget):
        """
        Constructor

        Arguments
        -----------------------
        parent : QWidget
            Parent QWidget
        """

        super().__init__()

        self.list_model = None
        self.__parent = None
        self.__conn = None
        self.__start_date = None
        self.__end_date = None

        self.__parent = parent



    def create_db(self, filename: str):
        """
        Creates and inits connection to new DB

        Arguments
        -----------------------
        filename : str
            Path of the database to create

        Raises
        -----------------------
        - DatabaseError if database exists
        - DatabaseError if other connection errors
        """

        # checking if db already exists
        if (os.path.isfile(filename)):
            raise DatabaseError('Database already exists')

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase('QSQLITE')
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        if not self.__conn.open():
            raise DatabaseError(self.__conn.lastError().text())

        query = QSqlQuery()

        # creating and indexing 'expenses' table
        command = '''
            CREATE TABLE expenses (
                'date' DATE NOT NULL,
                'type' CHAR(1) NOT NULL,
                'amount' DOUBLE PRECISION NOT NULL,
                'justification' VARCHAR(100) NOT NULL
            ) ;
        '''
        query.exec(command)
        query.exec('CREATE INDEX date_index ON expenses(date) ;')

        query.finish()



    def open_db(self, filename: str):
        """
        Creates and inits connection to existing DB

        Arguments
        -----------------------
        filename : str
            Path of the database to open

        Raises
        -----------------------
        - DatabaseError if database not found
        - DatabaseError if other connection errors
        - DatabaseError if 'expenses' table not found
        - DatabaseError if schema of 'expenses' is not valid
        """

        # checking if db already exists
        if (not os.path.isfile(filename)):
            raise DatabaseError('Database does not exists')

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase('QSQLITE')
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        if not self.__conn.open():
            raise DatabaseError(self.__conn.lastError().text())

        query = QSqlQuery()

        # checking for existence of 'expenses' table
        if (self.__conn.tables() != ['expenses']):
            raise DatabaseError('Invalid database schema')

        # checking for validity of schema of 'expense' table
        query.exec("PRAGMA TABLE_INFO('expenses') ;")

        names, types, notnulls = [], [], []
        nm, tp, nn = 1,2,3

        # fetching table information based on index
        while query.next():
            names.append(query.value(nm))
            types.append(query.value(tp))
            notnulls.append(query.value(nn))

        # checking against expected output
        if (names != ['date', 'type', 'amount', 'justification']
            or types != ['DATE', 'CHAR(1)', 'DOUBLE PRECISION', 'VARCHAR(100)']
            or notnulls != [1, 1, 1, 1]):
            raise DatabaseError('Corrupted table')
        
        query.finish()



    def init_model(self):
        """
        Initializes list model
        """

        # using default connection
        self.list_model = QSqlTableModel(self.__parent)
        self.list_model.setTable('expenses')
        # sorting by date
        self.list_model.setSort(
                0, Qt.SortOrder.DescendingOrder
        )

        colnames = ['date', 'type', 'amount', 'justification']
        for i,c in enumerate(colnames):
            self.list_model.setHeaderData(i, Qt.Horizontal, c)

        # no filter for initialization
        self.list_model.select()



    def close(self):
        """
        Closes connection with DB
        """

        self.__conn.close()



    def save_csv(self, filename: str):
        """
        Dumps the database to a CSV file
    
        Arguments
        -----------------------
        filename : str
            Filename of the output CSV file
    
        Raises
        -----------------------
        - DatabaseError if invalid Connection
        """
    
        if (self.__conn is None):
            raise DatabaseError('Uninitialized connection')
    
        query = QSqlQuery()

        # extracting data from database
        query.exec('SELECT * FROM expenses ;')

        # handwriting of csv file required
        # (QSqlQuery cannot pass .mode commands,
        # and record() is not iterable)
        with open(filename, 'w'):
            print('date,type,amount,justification', out)

            while query.next():
                row = '{},{},{},{}'.format(
                    query.value(0), query.value(1),
                    query.value(2), query.value(3)
                )
                print(row, out)
