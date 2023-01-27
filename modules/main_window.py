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


from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QAction, QIcon

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QApplication, QToolBar, QFileDialog, QMessageBox,\
        QInputDialog, QLineEdit
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import pandas as pd
from pandas import DataFrame as dataframe

import modules.db as db
from modules.list_form import list_form
from modules.add_form import add_form
from modules.import_dialog import import_dialog


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
    __lst_form : list_form
        Internal list_form widget
    __add_form : add_form
        Internal add_form widget
    __import_dialog : import_dialog
        Dialog to visualize file to import
    __hor_lay : QHBoxLayout
        Horizontal layout, contains widgets
        Extended/contracted to display/hide add_form
    __tb : QToolBar
        Toolbar widget
    __create_act : QAction
        The action of creating a new database
    __login_act : QAction
        The action of logging in to a new database
    __add_act : QAction
        The action of displaying/hiding the add_form
    __import_act : QAction
        The action of displaying the import dialog
    __export_act : QAction
        The action of saving the database to an external file
    __logout_act : QAction
        Prompts the user for logout
    __clear_act : QAction
        Prompts the user for clearing database

    Methods
    -----------------------
    __init__()
        Constructor
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

    Slots
    -----------------------
    __request_add(dataframe)
        Attempts addition of new data to the db
    __request_listing(str, str):
        Updates self.__lst_form with expenses
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
    __logout_db()
        Logs out from current database and clears tables
    __request_clearing()
        Collects filename from user and dumps database

    Connections
    -----------------------
    __lst_form.query_requested[start, end]
        -> __request_listing(start, end)
    __add_form.insertion_requested[df]
        -> __request_add(df)
    __import_dialog.import_requested[df]
        -> __request_add(df)
    __create_act.triggered
        -> __request_create()
    __login_act.triggered
        -> __request_login()
    __add_act.triggered
        -> __toggle_add()
    __import_act.triggered
        -> __import_dialog.load()
    __export_act.triggered
        -> __request_export()
    __logout_act.triggered
        -> __logout_db()
    __clear_act.triggered
        -> __request_clearing()
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__conn = None
        self.__lst_form = None
        self.__add_form = None
        self.__import_dialog = None
        self.__hor_lay = None
        self.__tb = None
        self.__create_act = None
        self.__login_act = None
        self.__add_act = None
        self.__import_act = None
        self.__export_act = None
        self.__clear_act = None

        # set to narrow size by default
        self.resize(mw_narrow, mw_height)

        # initializing forms and their layout
        self.__init_forms()

        # initializing dialogs
        self.__init_dialogs()

        # initializing toolbar
        self.__init_toolbar()

        # general layout, includes toolbar
        lay = QVBoxLayout()
        lay.setMenuBar(self.__tb)
        lay.addLayout(self.__hor_lay)

        self.setLayout(lay)

        self.__init_connections()
        self.__init_tb_connections()

        self.show()




    def __init_forms(self):
        """
        Inits the forms and the layout which contains them
        """

        self.__lst_form = list_form()
        self.__add_form = add_form()

        # no add form in the layout by default
        self.__hor_lay = QHBoxLayout()
        self.__hor_lay.addWidget(self.__lst_form)




    def __init_dialogs(self):
        """
        Inits dialogs
        """

        self.__import_dialog = import_dialog(self)




    def __init_toolbar(self):
        """
        Inits toolbar and the contained actions
        """

        self.__tb = QToolBar(self)
        self.__tb.setIconSize(QSize(30, 30))

        self.__create_act = QAction(QIcon('resources/create.png'), 'Create', self)
        self.__create_act.setToolTip('Create new database')

        self.__login_act = QAction(QIcon('resources/login.png'), 'Login', self)
        self.__login_act.setToolTip('Login to existing database')

        self.__add_act = QAction(QIcon('resources/add.png'), 'Add', self)
        self.__add_act.setCheckable(True)
        self.__add_act.setToolTip('Hide/show add form')

        self.__import_act = QAction(QIcon('resources/import.png'), 'Import', self)
        self.__import_act.setToolTip('Import external CSV file')

        self.__export_act = QAction(QIcon('resources/export.png'), 'Export', self)
        self.__export_act.setToolTip('Export database to CSV file')

        self.__logout_act = QAction(QIcon('resources/logout.png'), 'Logout', self)
        self.__logout_act.setToolTip('Logout')

        self.__clear_act = QAction(QIcon('resources/clear.png'), 'Clear', self)
        self.__clear_act.setToolTip('Remove all data from the database')

        self.__tb.addAction(self.__create_act)
        self.__tb.addAction(self.__login_act)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__add_act)
        self.__tb.addAction(self.__import_act)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__export_act)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__clear_act)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__logout_act)




    def __init_connections(self):
        """
        Inits form and dialog connections
        """

        # reconnects back to the window with the queried data
        self.__lst_form.query_requested.connect(
                lambda s,e: self.__request_listing(s,e)
        )

        # addition of new data to the db
        self.__add_form.insertion_requested.connect(
                lambda df: self.__request_add(df)
        )

        # bulk insertion of imported data requested
        self.__import_dialog.import_requested.connect(
                lambda df: self.__request_add(df)
        )




    def __init_tb_connections(self):
        """
        Inits connections of toolbar actions
        """

        # create action
        self.__create_act.triggered.connect(
                self.__request_create
        )

        # login action
        self.__login_act.triggered.connect(
                self.__request_login
        )

        # show/hide request for add_form
        self.__add_act.triggered.connect(
                self.__toggle_add
        )

        # show import dialog
        self.__import_act.triggered.connect(
                self.__import_dialog.load
        )

        # request exporting to CSV
        self.__export_act.triggered.connect(
                self.__request_export
        )

        # logout from current database
        self.__logout_act.triggered.connect(
                self.__logout_db
        )

        # request database clearing
        self.__clear_act.triggered.connect(
                self.__request_clearing
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
        Updates self.__lst_form with expenses
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
            self.__lst_form.update_tables(df)
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

        if (self.__add_form.isVisible() is False):
            # show add form
            self.resize(mw_wide, mw_height)
            self.__hor_lay.addWidget(self.__add_form)
            self.__add_form.show()
        else:
            # hide add form
            self.__add_form.hide()
            self.__hor_lay.removeWidget(self.__add_form)
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
    def __logout_db(self):
        """
        Logs out from current database and clears tables
        """

        if (self.__conn is None):
            QMessageBox.critical(None, 'Error', 'Operation failed')
            return

        self.__lst_form.clear_tables()

        self.__conn.close()
        self.__conn = None




    @QtCore.pyqtSlot()
    def __request_clearing(self):
        """
        Prompts the user for clearing database
        """

        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Warning)
        mb.setText("Database clearing requested.");
        mb.setInformativeText("Do you wish to proceed?");
        mb.setStandardButtons(
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
        )
        mb.setDefaultButton(QMessageBox.StandardButton.No)

        ret = mb.exec()

        try:
            if (ret == QMessageBox.StandardButton.Yes):
                db.clear(self.__conn)
        except db.DatabaseError as err:
            QMessageBox.critical(
                None, 'Error', 'Operation failed : {}'.format(err)
            )
            return
