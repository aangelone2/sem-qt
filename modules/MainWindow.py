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
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget, QApplication,\
        QToolBar, QFileDialog, QLineEdit
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

from modules.Common import ErrorMsg
from modules.ModelWrapper import ModelWrapper

from modules.ListForm import ListForm



MAIN_WINDOW_WIDTH = 1200
MAIN_WINDOW_HEIGHT = 400



class MainWindow(QMainWindow):
    """
    Main program window

    Attributes
    -----------------------
    __models: ModelWrapper
        Wrapper for list and sum models
    __form_lst : list_form
        Internal list_form widget
    __act_create : QAction
        The action of creating a new database
    __act_open : QAction
        The action of logging in to a new database
    __act_export : QAction
        The action of saving the database to an external file
    __act_close : QAction
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
    __request_create()
        Attempts creation of database
    __request_open()
        Attempts to open existing database
    __request_export()
        Collects filename from user and dumps database
    __close_db()
        Closes current database

    Connections
    -----------------------
    __act_create.triggered
        -> __request_create()
    __act_open.triggered
        -> __request_open()
    __act_export.triggered
        -> __request_export()
    __act_close.triggered
        -> __close_db()
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__models = None
        self.__form_lst = None
        self.__act_create = None
        self.__act_open = None
        self.__act_export = None
        self.__act_close = None

        # set to narrow size by default
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        # setting window title
        self.setWindowTitle('Simple Expense Manager')

        # initializing form
        self.__form_lst = ListForm(self)
        # initializing toolbar
        self.__init_toolbar()

        self.setCentralWidget(self.__form_lst)

        self.__init_connections()
        self.__init_tb_connections()



    def __init_toolbar(self):
        """
        Inits toolbar and the contained actions
        """

        self.menuBar() = QToolBar(self)
        self.menuBar().setIconSize(QSize(30, 30))

        self.__act_create = QAction(QIcon('resources/create.png'), 'Create', self)
        self.__act_create.setToolTip('Create new database')

        self.__act_open = QAction(QIcon('resources/open.png'), 'Open', self)
        self.__act_open.setToolTip('Open existing database')

        self.__act_export = QAction(QIcon('resources/export.png'), 'Export', self)
        self.__act_export.setToolTip('Export database to CSV file')

        self.__act_close = QAction(QIcon('resources/close.png'), 'Close', self)
        self.__act_close.setToolTip('Close current database')

        self.__tb.addAction(self.__act_create)
        self.__tb.addAction(self.__act_open)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_export)
        self.__tb.addSeparator()
        self.__tb.addAction(self.__act_close)



    def __init_connections(self):
        """
        Inits form and dialog connections
        """
        pass



    def __init_tb_connections(self):
        """
        Inits connections of toolbar actions
        """

        # create action
        self.__act_create.triggered.connect(
                self.__request_create
        )

        # open action
        self.__act_open.triggered.connect(
                self.__request_open
        )

        # request exporting to CSV
        self.__act_export.triggered.connect(
                self.__request_export
        )

        # close current database
        self.__act_close.triggered.connect(
                self.__close_db
        )



    @QtCore.pyqtSlot()
    def __request_create(self):
        """
        Attempts creation of database
        """

        filename = QFileDialog.getSaveFileName(
                self,
                'Select name for new database',
        )[0]

        if (filename == ''):
            return

        try:
            self.__models.create_db(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return
        
        self.__models.init_model()



    @QtCore.pyqtSlot()
    def __request_open(self):
        """
        Attempts to open database
        """

        filename = QFileDialog.getOpenFileName(
                self,
                'Select database to access'
        )[0]

        if (filename == ''):
            return

        try:
            self.__models.open_db(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return

        self.__models.init_model()



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
            self.__models.save_csv(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return



    @QtCore.pyqtSlot()
    def __close_db(self):
        """
        Logs out from current database
        """

        self.__models.close_db()
