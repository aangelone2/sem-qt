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
from PyQt6.QtWidgets import QWidget
from PyQt6.QtSql import QSqlDatabase, QSqlQuery,\
        QSqlTableModel, QSqlQueryModel

from string import Template
import csv
import os



class DatabaseError(Exception):
    """
    Subclassed exception for errors in db Connection
    """
    pass



class ModelWrapper():
    """
    Wrapper for list and sum models

    Public attributes
    -----------------------
    listModel: QSqlTableModel
        Model for general expense data
    sumModel: QSqlQueryModel
        Model for expense amounts aggregated by type

    Private attributes
    -----------------------
    __parent: QWidget
        Parent QWidget
    __conn: QSqlDatabase
        Database connection

    Public methods
    -----------------------
    __init__()
        Constructor
    createDB(str)
        Creates and inits connection to new DB
    openDB(str)
        Creates and inits connection to existing DB
    initModels()
        Initializes list and sum models
    applyDateFilter(list[str])
        Apply filter to models with the specified dates
    importCSV(str)
        Appends the contents of a CSV file to the database
    saveCSV(str)
        Dumps the database to a CSV file
    closeDB()
        Closes connection with DB
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

        self.listModel = None
        self.sumModel = None
        self.__parent = None
        self.__conn = None
        self.__startDate = None
        self.__endDate = None

        self.__parent = parent



    def createDB(self, filename: str):
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

        # Closing connection if currently active
        if (self.__conn is not None):
            if (self.__conn.open()):
                self.__conn.close()

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase('QSQLITE')
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        if (not self.__conn.open()):
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



    def openDB(self, filename: str):
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

        # Closing connection if currently active
        if (self.__conn is not None):
            if (self.__conn.open()):
                self.__conn.close()

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase('QSQLITE')
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        if (not self.__conn.open()):
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



    def initModels(self):
        """
        Initializes list and sum models

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        """

        if (self.__conn is None):
            raise DatabaseError('Uninitialized connection')

        # using default connection
        self.listModel = QSqlTableModel(self.__parent)
        self.listModel.setTable('expenses')
        # sorting by date (newest first)
        self.listModel.setSort(
                0, Qt.SortOrder.DescendingOrder
        )

        # setting edit strategy
        self.listModel.setEditStrategy(
                QSqlTableModel.EditStrategy.OnRowChange
        )

        self.listModel.select()

        # sum model
        self.sumModel = QSqlQueryModel()

        # setting basic query
        self.sumModel.setQuery('''
            SELECT type, SUM(amount)
            FROM expenses
            GROUP BY type
            ORDER BY type ;
        ''')

        # has to be done after setting up the query
        # or names will be overridden by the query fields
        colnames = ['type', 'sum']
        for i,c in enumerate(colnames):
            self.sumModel.setHeaderData(
                    i, Qt.Orientation.Horizontal, c
            )



    def applyDateFilter(self, dates: list[str]):
        """
        Apply data filter to the model

        Arguments
        -----------------------
        dates : list[str]
            - [startDate, endDate], both included
            - `None` removes all filters

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        - DatabaseError if invalid date range
        """

        if (self.__conn is None):
            raise DatabaseError('Uninitialized connection')

        # string template for the sum model
        queryTemplate = Template('''
            SELECT type, SUM(amount)
            FROM expenses
            WHERE $flt
            GROUP BY type
            ORDER BY type ;
        ''')

        # setting query filter
        flt = 'TRUE'
        if (dates is not None):
            if (len(dates) != 2):
                raise DatabaseError('Invalid date interval')
            else:
                flt = f"date BETWEEN '{dates[0]}' AND '{dates[1]}'"

        # applying filters, setQuery() requires WHERE
        self.listModel.setFilter(flt)
        self.sumModel.setQuery(
                queryTemplate.substitute(flt = flt)
        )

        self.listModel.select()



    def importCSV(self, filename: str):
        """
        Appends the contents of a CSV file to the database

        Arguments
        -----------------------
        filename : str
            Filename of the output CSV file

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        - DatabaseError if file does not exist
        - DatabaseError if invalid file content
        """

        if (self.__conn is None):
            raise DatabaseError('Uninitialized connection')

        # setting batch edit strategy
        self.listModel.setEditStrategy(
                QSqlTableModel.EditStrategy.OnManualSubmit
        )

        # handreading of csv file required
        # (QSqlQuery cannot pass .mode commands,
        # and record() is not iterable)
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, quotechar = '"')

            for ir, row in enumerate(reader):
                rows = self.listModel.rowCount()
                # inserting a row at the end of the model
                if (not self.listModel.insertRows(rows, 1)):
                    raise DatabaseError(
                            f'Error in inserting row {ir}'
                    )

                for ic, col in enumerate(row):
                    index = self.listModel.index(rows, ic)
                    if (not self.listModel.setData(index, col)):
                        raise DatabaseError(
                                f'Error in inserting row {ir}, field {ic}'
                        )

            self.listModel.submitAll()
            self.listModel.select()

        # resetting default edit strategy
        self.listModel.setEditStrategy(
                QSqlTableModel.EditStrategy.OnRowChange
        )



    def saveCSV(self, filename: str):
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

        # number of fields
        COLS = 4

        # handwriting of csv file required
        # (QSqlQuery cannot pass .mode commands,
        # and record() is not iterable)
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, quotechar = '"',
                quoting = csv.QUOTE_NONNUMERIC)

            while query.next():
                writer.writerow([query.value(i)
                                 for i in range(COLS)])

        query.finish()



    def closeDB(self):
        """
        Closes connection with DB
        """

        if (self.__conn is None):
            raise DatabaseError('Uninitialized connection')

        self.__conn.close()
