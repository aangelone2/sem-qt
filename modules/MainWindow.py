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
from PyQt6.QtWidgets import QToolBar, QFileDialog, QMainWindow
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

from modules.Common import ErrorMsg
from modules.ModelWrapper import DatabaseError, ModelWrapper

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
    __formLst : ListForm
        Internal list_form widget
    __actCreate : QAction
        The action of creating a new database
    __actOpen : QAction
        The action of logging in to a new database
    __actAdd : QAction
        The action of manually adding expenses to the database
    __actRemove : QAction
        The action of removing the selected row
    __actImport : QAction
        The action of importing an external CSV file
    __actExport : QAction
        The action of saving the database to an external file

    Public methods
    -----------------------
    __init__()
        Constructor

    Private methods
    -----------------------
    __initForms()
        Inits the forms and the layout which contains them
    __initToolbar()
        Inits toolbar and the contained actions
    __initConnections()
        Inits form and dialog connections
    __initTbConnections()
        Inits connections of toolbar actions

    Private slots
    -----------------------
    __requestCreate()
        Attempts creation of database
    __requestOpen()
        Attempts to open existing database
    __requestAdd()
        Attempts to add expense to the view and then to the DB
    __requestRemove()
        Attempts to remove the selected row in the view
    __requestImport()
        Collects filename from user and loads CSV data
    __requestExport()
        Collects filename from user and dumps database

    Connections
    -----------------------
    __formLst.filterRequested(dates)
        -> __models.applyDateFilter(dates)
    __formLst.clearingRequested()
        -> __models.applyDateFilter(None)
    __actCreate.triggered
        -> __requestCreate()
    __actOpen.triggered
        -> __requestOpen()
    __actAdd.triggered
        -> __requestAdd()
    __actRemove.triggered
        -> __requestRemove()
    __actImport.triggered
        -> __requestImport()
    __actExport.triggered
        -> __requestExport()
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__models = None
        self.__formLst = None
        self.__actCreate = None
        self.__actOpen = None
        self.__actAdd = None
        self.__actRemove = None
        self.__actImport = None
        self.__actExport = None

        # set to narrow size by default
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        # setting window title
        self.setWindowTitle('Simple Expense Manager')

        # initializing model/DB wrapper
        self.__models = ModelWrapper(self)
        # initializing form
        self.__formLst = ListForm(self)
        # initializing toolbar
        self.__initToolbar()

        self.setCentralWidget(self.__formLst)

        self.__initConnections()
        self.__initTbConnections()



    def __initToolbar(self):
        """
        Inits toolbar and the contained actions
        """

        tb = QToolBar(self)
        tb.setIconSize(QSize(30, 30))

        self.__actCreate = QAction(QIcon('resources/create.png'), 'Create', self)
        self.__actCreate.setToolTip('Create new database')

        self.__actOpen = QAction(QIcon('resources/open.png'), 'Open', self)
        self.__actOpen.setToolTip('Open existing database')

        self.__actAdd = QAction(QIcon('resources/add.png'), 'Add', self)
        self.__actAdd.setToolTip('Add expenses manually')

        self.__actRemove = QAction(QIcon('resources/remove.png'), 'Remove', self)
        self.__actRemove.setToolTip('Remove selected expense')

        self.__actImport = QAction(QIcon('resources/import.png'), 'Import', self)
        self.__actImport.setToolTip('Import external CSV file')

        self.__actExport = QAction(QIcon('resources/export.png'), 'Export', self)
        self.__actExport.setToolTip('Export database to CSV file')

        tb.addAction(self.__actCreate)
        tb.addAction(self.__actOpen)
        tb.addSeparator()
        tb.addAction(self.__actAdd)
        tb.addAction(self.__actRemove)
        tb.addSeparator()
        tb.addAction(self.__actImport)
        tb.addAction(self.__actExport)

        self.addToolBar(tb)



    def __initConnections(self):
        """
        Inits form and dialog connections
        """

        self.__formLst.filterRequested.connect(
                lambda dates: self.__models.applyDateFilter(dates)
        )

        self.__formLst.clearingRequested.connect(
                lambda: self.__models.applyDateFilter(None)
        )



    def __initTbConnections(self):
        """
        Inits connections of toolbar actions
        """

        # create action
        self.__actCreate.triggered.connect(
                self.__requestCreate
        )

        # open action
        self.__actOpen.triggered.connect(
                self.__requestOpen
        )

        # add action
        self.__actAdd.triggered.connect(
                self.__requestAdd
        )

        # add action
        self.__actRemove.triggered.connect(
                self.__requestRemove
        )

        # request importing from CSV
        self.__actImport.triggered.connect(
                self.__requestImport
        )

        # request exporting to CSV
        self.__actExport.triggered.connect(
                self.__requestExport
        )



    @QtCore.pyqtSlot()
    def __requestCreate(self):
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
            self.__models.createDB(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return
        
        self.__models.initModels()
        self.__formLst.setModels(
                self.__models.listModel,
                self.__models.sumModel
        )



    @QtCore.pyqtSlot()
    def __requestOpen(self):
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
            self.__models.openDB(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return

        self.__models.initModels()
        self.__formLst.setModels(
                self.__models.listModel,
                self.__models.sumModel
        )



    @QtCore.pyqtSlot()
    def __requestAdd(self):
        """
        The action of manually adding expenses to the database
        """

        self.__models.addDefaultRecord()



    @QtCore.pyqtSlot()
    def __requestRemove(self):
        """
        Attempts to remove the selected row in the view
        """

        self.__models.removeRecords(
                self.__formLst.selection()
        )



    @QtCore.pyqtSlot()
    def __requestImport(self):
        """
        Collects filename from user and loads CSV data
        """

        filename = QFileDialog.getOpenFileName(
                self,
                'Specify file to import'
        )[0]

        if (filename == ''):
            return

        try:
            self.__models.importCSV(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return



    @QtCore.pyqtSlot()
    def __requestExport(self):
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
            self.__models.saveCSV(filename)
        except DatabaseError as err:
            ErrorMsg(err)
            return
