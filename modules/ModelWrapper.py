"""Model wrapper.

Classes
-----------------------
DatabaseError
    Subclassed exception for errors in db Connection.
ModelWrapper
    Wrapper for list and sum models.
"""

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

from string import Template
import csv
import os
import datetime

from PyQt6.QtCore import Qt, QPersistentModelIndex
from PyQt6.QtWidgets import QWidget
from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    QSqlTableModel,
    QSqlQueryModel,
)


class DatabaseError(Exception):
    """Subclassed exception for errors in db Connection."""


class ModelWrapper:
    """Wrapper for list and sum models.

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
        Construct class instance.
    createDB(str)
        Create and init connection to new DB.
    openDB(str)
        Create and init connection to existing DB.
    initModels()
        Initialize list and sum models.
    applyDateFilter(list[str])
        Apply filter to models with the specified dates.
    addDefaultRecord()
        Add a default record to the end of the DB.
    removeRecords(list[QPersistentModelIndex])
        Remove the records with the given indices from the model.
    importCSV(str)
        Append the contents of a CSV file to the database.
    saveCSV(str)
        Dump the database to a CSV file.
    closeDB()
        Close connection with DB.
    """

    def __init__(self, parent: QWidget):
        """Construct class instance.

        Parameters
        -----------------------
        parent : QWidget
            Parent QWidget
        """
        super().__init__()

        self.listModel = None
        self.sumModel = None
        self.__parent = None
        self.__conn = None

        self.__parent = parent

    def createDB(self, filename: str):
        """Create and init connection to new DB.

        Parameters
        -----------------------
        filename : str
            Path of the database to create

        Raises
        -----------------------
        - DatabaseError if database exists
        - DatabaseError if other connection errors
        """
        # checking if db already exists
        if os.path.isfile(filename):
            raise DatabaseError("Database already exists")

        # Closing connection if currently active
        if self.__conn is not None:
            if self.__conn.isOpen():
                self.__conn.close()

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase("QSQLITE")
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        chk = self.__conn.open()
        if not chk:
            raise DatabaseError(self.__conn.lastError().text())

        query = QSqlQuery()

        # creating and indexing 'expenses' table
        # checks here because SQLite is "dynamically" typed
        command = """
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT
                    CHECK (TYPEOF(id) == ('integer')),
                date DATE NOT NULL
                    CHECK (DATE(date) IS date),
                type CHAR(1) NOT NULL
                    CHECK (LENGTH(type) == 1),
                amount DOUBLE PRECISION NOT NULL
                    CHECK (TYPEOF(amount) IN ('integer', 'real')),
                justification VARCHAR(100) NOT NULL
                    CHECK (LENGTH(justification) <= 100)
            ) ;
        """
        query.exec(command)
        query.exec(
            "CREATE INDEX date_index ON expenses(date) ;"
        )

        query.finish()

    def openDB(self, filename: str):
        """Create and init connection to existing DB.

        Parameters
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
        if not os.path.isfile(filename):
            raise DatabaseError("Database does not exists")

        # Closing connection if currently active
        if self.__conn is not None:
            if self.__conn.isOpen():
                self.__conn.close()

        # opening default connection
        self.__conn = QSqlDatabase.addDatabase("QSQLITE")
        self.__conn.setDatabaseName(filename)

        # misc errors in connection opening
        chk = self.__conn.open()
        if not chk:
            raise DatabaseError(self.__conn.lastError().text())

        query = QSqlQuery()

        # checking for existence of 'expenses' table
        if "expenses" not in self.__conn.tables():
            raise DatabaseError("Invalid database schema")

        # checking for validity of schema of 'expense' table
        query.exec("PRAGMA TABLE_INFO('expenses') ;")

        names, types, notnulls = [], [], []
        nm, tp, nn = 1, 2, 3

        # fetching table information based on index
        while query.next():
            names.append(query.value(nm))
            types.append(query.value(tp))
            notnulls.append(query.value(nn))

        # checking against expected output
        # (apparently for SQLite3 primary keys are not not-null...)
        if (
            names
            != [
                "id",
                "date",
                "type",
                "amount",
                "justification",
            ]
            or types
            != [
                "INTEGER",
                "DATE",
                "CHAR(1)",
                "DOUBLE PRECISION",
                "VARCHAR(100)",
            ]
            or notnulls != [0, 1, 1, 1, 1]
        ):
            raise DatabaseError("Corrupted table")

        query.finish()

    def initModels(self):
        """Initialize list and sum models.

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        """
        if self.__conn is None:
            raise DatabaseError("Uninitialized connection")

        # using default connection
        self.listModel = QSqlTableModel(self.__parent)
        self.listModel.setTable("expenses")
        # sorting by date (newest first)
        self.listModel.setSort(0, Qt.SortOrder.DescendingOrder)

        # setting edit strategy
        self.listModel.setEditStrategy(
            QSqlTableModel.EditStrategy.OnFieldChange
        )

        self.listModel.select()

        # sum model
        self.sumModel = QSqlQueryModel()

        # setting basic query
        self.sumModel.setQuery(
            """
            SELECT type, SUM(amount)
            FROM expenses
            GROUP BY type
            ORDER BY type ;
        """
        )

        # has to be done after setting up the query
        # or names will be overridden by the query fields
        colnames = ["type", "sum"]
        for i, c in enumerate(colnames):
            self.sumModel.setHeaderData(
                i, Qt.Orientation.Horizontal, c
            )

    def applyDateFilter(self, dates: list[str]):
        """Apply data filter to the model.

        Parameters
        -----------------------
        dates : list[str]
            - [startDate, endDate], both included
            - `None` removes all filters

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        - DatabaseError if invalid date range
        """
        if self.__conn is None:
            raise DatabaseError("Uninitialized connection")

        # string template for the sum model
        queryTemplate = Template(
            """
            SELECT type, SUM(amount)
            FROM expenses
            WHERE $flt
            GROUP BY type
            ORDER BY type ;
        """
        )

        # setting query filter
        flt = "TRUE"
        if dates is not None:
            if len(dates) != 2:
                raise DatabaseError("Invalid date interval")

            flt = f"date BETWEEN '{dates[0]}' AND '{dates[1]}'"

        # applying filters, setQuery() requires WHERE
        self.listModel.setFilter(flt)
        self.sumModel.setQuery(
            queryTemplate.substitute(flt=flt)
        )

        self.listModel.select()

    def addDefaultRecord(self):
        """Add a default record to the end of the DB.

        Raises
        -----------------------
        - DatabaseError if unsuccessful addition
        """
        # empty reference record
        record = self.listModel.record()

        # allowing to auto-set primary key
        record.remove(0)

        # setting default values for other fields
        # notice the realigned indices
        record.setValue(
            0, datetime.date.today().strftime("%Y-%m-%d")
        )
        record.setValue(1, "-")
        record.setValue(2, 0.0)
        record.setValue(3, "-")

        # inserting in last position
        chk = self.listModel.insertRecord(-1, record)
        if not chk:
            raise DatabaseError("Error in inserting record")

    def removeRecords(
        self, indices: list[QPersistentModelIndex]
    ):
        """Remove the records with the given indices from the model.

        Raises
        -----------------------
        - DatabaseError if unsuccessful removal
        """
        for i, index in enumerate(indices):
            chk = self.listModel.removeRow(index.row())
            if not chk:
                raise DatabaseError(
                    f"Error in deleting record {i}"
                )

        # updating changes
        self.listModel.select()

    def importCSV(self, filename: str):
        """Append the contents of a CSV file to the database.

        Parameters
        -----------------------
        filename : str
            Filename of the output CSV file

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        - DatabaseError if file does not exist
        - DatabaseError if invalid file content
        """
        if self.__conn is None:
            raise DatabaseError("Uninitialized connection")

        # handreading of csv file required
        # (QSqlQuery cannot pass .mode commands,
        # and record() is not iterable)
        with open(
            filename, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile, quotechar='"')

            try:
                for ir, row in enumerate(reader):
                    # empty record will contain info on the table schema
                    record = self.listModel.record()

                    # if 1st field is left unspecified, auto-assign
                    # (id, primary key, autoincrement integer)
                    # setting NULL does not work, found this solution
                    if row[0] == "":
                        record.remove(0)
                    else:
                        record.setValue(0, row[0])

                    # setting other fields
                    for ic, col in enumerate(row[1:]):
                        record.setValue(ic, col)

                    # inserting at last position
                    chk = self.listModel.insertRecord(
                        -1, record
                    )
                    if not chk:
                        raise DatabaseError(
                            f"Error in inserting record {ir + 1}"
                        )

                    # SQLite performs type-checking here
                    # inserting line-by-line to check lines
                    chk = self.listModel.submitAll()
                    if not chk:
                        raise DatabaseError(
                            f"Error in inserting row {ir + 1}"
                        )
            except csv.Error as err:
                raise DatabaseError(
                    f"CSV file error :: line {reader.line_num} :: {err}"
                )

            self.listModel.select()

    def saveCSV(self, filename: str):
        """Dump the database to a CSV file.

        Parameters
        -----------------------
        filename : str
            Filename of the output CSV file

        Raises
        -----------------------
        - DatabaseError if invalid Connection
        """
        if self.__conn is None:
            raise DatabaseError("Uninitialized connection")

        query = QSqlQuery()

        # extracting data from database
        query.exec("SELECT * FROM expenses ;")

        # number of fields
        COLS = query.record().count()

        # handwriting of csv file required
        # (QSqlQuery cannot pass .mode commands,
        # and record() is not iterable)
        with open(
            filename, "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(
                csvfile,
                quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC,
            )

            while query.next():
                writer.writerow(
                    [query.value(i) for i in range(COLS)]
                )

        query.finish()

    def closeDB(self):
        """Close connection with DB."""
        if self.__conn is None:
            raise DatabaseError("Uninitialized connection")

        self.__conn.close()
