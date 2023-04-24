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

from os.path import isfile

from PyQt6 import QtCore
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QIcon

from PyQt6.QtWidgets import QWidget, QApplication,\
        QToolBar, QFileDialog, QMessageBox,\
        QInputDialog, QLineEdit
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import pandas as pd
from pandas import DataFrame as dataframe

import modules.db as db

from modules.windows.list_form import list_form
from modules.windows.add_form import add_form
from modules.windows.import_dialog import import_dialog


mw_narrow = 1200
mw_wide = 1600
mw_height = 400

id_width = 900
id_height = 500




class main_window(QWidget):
    """
    Main program window

    Attributes
    -----------------------
    __conn: connection
        Connection to database-table pair
    __form_lst : list_form
        Internal list_form widget
    __form_add : add_form
        Internal add_form widget
    __dialog_import : import_dialog
        Dialog to visualize file to import
    __lay_hor : QHBoxLayout
        Horizontal layout, contains widgets
        Extended/contracted to display/hide add_form
    __tb : QToolBar
        Toolbar widget
    __act_create : QAction
        The action of creating a new database
    __act_login : QAction
        The action of logging in to a new database
    __act_add : QAction
        The action of displaying/hiding the add_form
    __act_import : QAction
        The action of displaying the import dialog
    __act_export : QAction
        The action of saving the database to an external file
    __act_delete : QAction
        Deletes selected rows
    __act_logout : QAction
        Logs the user out

    Public methods
    -----------------------
    __init__()
        Constructor

    Private methods
    -----------------------
    __init_forms()
        Inits the forms and the layout which contains them
    __init_dialogs()
        Inits dialogs
    __init_toolbar()
        Inits toolbar and the contained actions
    __init_connections()
        Inits form and dialog connections
    __init_tb_connections()
        Inits connections of toolbar actions

    Private slots
    -----------------------
    __request_add(dataframe)
        Attempts addition of new data to the db
    __request_listing(str, str):
        Updates self.__form_lst with expenses
        comprised between the two given dates
    __request_create()
        Attempts creation of encrypted database,
        sets self.__conn to the resulting connection
    __request_login()
        Attempts login to encrypted database,
        sets self.__conn to the resulting connection
    __toggle_add()
        Hides/shows the addition form
        Stretches/compresses the window as required
    __request_export()
        Collects filename from user and dumps database
    __request_deletion()
        Requests deletion of selected rows, updates display
    __logout_db()
        Logs out from current database and clears tables

    Connections
    -----------------------
    __form_lst.query_requested[start, end]
        -> __request_listing(start, end)
    __form_add.insertion_requested[df]
        -> __request_add(df)
    __dialog_import.import_requested[df]
        -> __request_add(df)
    __act_create.triggered
        -> __request_create()
    __act_login.triggered
        -> __request_login()
    __act_add.triggered
        -> __toggle_add()
    __act_import.triggered
        -> __dialog_import.load()
    __act_export.triggered
        -> __request_export()
    __act_delete.triggered
        -> __request_deletion()
    __act_logout.triggered
        -> __logout_db()
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__conn = None
        self.__form_lst = None
        self.__form_add = None
        self.__dialog_import = None
        self.__lay_hor = None
        self.__tb = None
        self.__act_create = None
        self.__act_login = None
        self.__act_add = None
        self.__act_import = None
        self.__act_export = None
        self.__act_delete = None
        self.__act_logout = None

        # set to narrow size by default
        self.resize(mw_narrow, mw_height)
        # setting window title
        self.setWindowTitle('Simple Expense Manager')

        # initializing forms and their layout
        self.__init_forms()

        # initializing dialogs
        self.__init_dialogs()

        # initializing toolbar
        self.__init_toolbar()

        # general layout, includes toolbar
        lay = QVBoxLayout()
        lay.setMenuBar(self.__tb)
        lay.addLayout(self.__lay_hor)

        self.setLayout(lay)

        self.__init_connections()
        self.__init_tb_connections()




    def __init_forms(self):
        """
        Inits the forms and the layout which contains them
        """

        self.__form_lst = list_form()
        self.__form_add = add_form()

        # no add form in the layout by default
        self.__lay_hor = QHBoxLayout()
        self.__lay_hor.addWidget(self.__form_lst)




    def __init_dialogs(self):
        """
        Inits dialogs
        """

        self.__dialog_import = import_dialog(self)




    def __init_toolbar(self):
        """
        Inits toolbar and the contained actions
        """

        self.__tb = QToolBar(self)
        self.__tb.setIconSize(QSize(30, 30))

        self.__act_create = QAction(QIcon('resources/create.png'), 'Create', self)
        self.__act_create.setToolTip('Create new database')

        self.__act_login = QAction(QIcon('resources/login.png'), 'Login', self)
        self.__act_login.setToolTip('Login to existing database')

        self.__act_add = QAction(QIcon('resources/add.png'), 'Add', self)
        self.__act_add.setCheckable(True)
        self.__act_add.setToolTip('Hide/show add form')

        self.__act_import = QAction(QIcon('resources/import.png'), 'Import', self)
        self.__act_import.setToolTip('Import external CSV file')

        self.__act_export = QAction(QIcon('resources/export.png'), 'Export', self)
        self.__act_export.setToolTip('Export database to CSV file')

        self.__act_delete = QAction(QIcon('resources/delete.png'), 'Delete', self)
        self.__act_delete.setToolTip('Deletes selected expenses from database')

        self.__act_logout = QAction(QIcon('resources/logout.png'), 'Logout', self)
        self.__act_logout.setToolTip('Logout')

        self.__tb.addAction(self.__act_create)
        self.__tb.addAction(self.__act_login)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_add)
        self.__tb.addAction(self.__act_import)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_export)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_delete)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_logout)




    def __init_connections(self):
        """
        Inits form and dialog connections
        """

        # reconnects back to the window with the queried data
        self.__form_lst.query_requested.connect(
                lambda s,e: self.__request_listing(s,e)
        )

        # addition of new data to the db
        self.__form_add.insertion_requested.connect(
                lambda df: self.__request_add(df)
        )

        # bulk insertion of imported data requested
        self.__dialog_import.import_requested.connect(
                lambda df: self.__request_add(df)
        )




    def __init_tb_connections(self):
        """
        Inits connections of toolbar actions
        """

        # create action
        self.__act_create.triggered.connect(
                self.__request_create
        )

        # login action
        self.__act_login.triggered.connect(
                self.__request_login
        )

        # show/hide request for add_form
        self.__act_add.triggered.connect(
                self.__toggle_add
        )

        # show import dialog
        self.__act_import.triggered.connect(
                self.__dialog_import.load
        )

        # request exporting to CSV
        self.__act_export.triggered.connect(
                self.__request_export
        )

        # request selected expenses deletion
        self.__act_delete.triggered.connect(
                self.__request_deletion
        )

        # logout from current database
        self.__act_logout.triggered.connect(
                self.__logout_db
        )




    @QtCore.pyqtSlot()
    def __request_add(self, df: dataframe):
        """
        Attempts addition of new data to the db

        Arguments

        -----------------------
        df : dataframe
            Data to add to the database
        """

        try:
            db.add(self.__conn, df)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return




    @QtCore.pyqtSlot()
    def __request_listing(self, start: str, end: str):
        """
        Updates self.__form_lst with expenses
        comprised between the two given dates

        Arguments

        -----------------------
        start : str
            Starting date (included)
        end : str
            Final date (included)
        """

        try:
            df = db.fetch(self.__conn, start, end)
            self.__form_lst.update_tables(df)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return




    @QtCore.pyqtSlot()
    def __request_create(self):
        """
        Attempts creation of encrypted database,
        sets self.__conn to the resulting connection
        """

        filename = QFileDialog.getSaveFileName(
                self,
                'Select name for new database',
        )[0]

        if (filename == ''):
            return

        # Checking if database exists
        if (isfile(filename)):
            QMessageBox.critical(
                None, 'Error', 'Operation failed : database exists'
            )
            return

        pssw = QInputDialog.getText(
                self,
                'Password input',
                'Select a password',
                QLineEdit.EchoMode.Password
        )[0]

        try:
            self.__conn = db.create(filename, pssw)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return




    @QtCore.pyqtSlot()
    def __request_login(self):
        """
        Attempts login to encrypted database,
        sets self.__conn to the resulting connection
        """

        filename = QFileDialog.getOpenFileName(
                self,
                'Select database to access'
        )[0]

        if (filename == ''):
            return

        pssw = QInputDialog.getText(
                self,
                'Password input',
                'Input the password',
                QLineEdit.EchoMode.Password
        )[0]

        try:
            self.__conn = db.login(filename, pssw)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return




    @QtCore.pyqtSlot()
    def __toggle_add(self):
        """
        Hides/shows the addition form
        Stretches/compresses the window as required
        """

        if (self.__form_add.isVisible() is False):
            # show add form
            self.resize(mw_wide, mw_height)
            self.__lay_hor.addWidget(self.__form_add)
            self.__form_add.show()
        else:
            # hide add form
            self.__form_add.hide()
            self.__lay_hor.removeWidget(self.__form_add)
            self.resize(mw_narrow, mw_height)

        # re-centering the window horizontally
        screen = QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        x = (screen_geom.width() - self.width()) // 2
        self.move(x, self.y())




    @QtCore.pyqtSlot()
    def __request_export(self):
        """
        Collects filename from user and dumps database
        """

        filename = QFileDialog.getSaveFileName(
                self,
                'Specify file for exporting',
                None,
                'CSV files (*.csv)'
        )[0]

        if (filename == ''):
            return

        try:
            db.save_csv(self.__conn, filename)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return




    @QtCore.pyqtSlot()
    def __request_deletion(self):
        """
        Requests deletion of selected rows, updates display
        """

        rowids = self.__form_lst.selected_rowids()
        db.delete(self.__conn, rowids)




    @QtCore.pyqtSlot()
    def __logout_db(self):
        """
        Logs out from current database and clears tables
        """

        if (self.__conn is None):
            QMessageBox.critical(None, 'Error', 'Operation failed')
            return

        self.__form_lst.clear_tables()

        self.__conn.close()
        self.__conn = None
