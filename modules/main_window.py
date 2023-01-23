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
        QApplication, QToolBar
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import sqlite3 as sql
from sqlite3 import Connection as connection

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
    __add_act : QAction
        The action of displaying/hiding the add_form
    __import_act : QAction
        The action of displaying the import dialog
    __export_act : QAction
        The action of saving the database to an external file

    Methods
    -----------------------
    __init_forms()
        Inits the forms and the layout which contains them
    __init_dialogs()
        Inits dialogs
    __init_toolbar()
        Inits toolbar and the contained actions
    __init_connections()
        Inits connections

    Slots
    -----------------------
    __toggle_add()
        Hides/shows the addition form
        Stretches/compresses the window as required

    Connections
    -----------------------
    __lst_form.query_requested[start, end]
        -> __lst_form.update_tables(data)
    __add_form.insertion_requested[df]
        -> db.add(__conn, df)
    __import_dialog.import_requested[df]
        -> db.add(__conn, df)
    __add_act.triggered()
        -> __toggle_add()
    __import_act.triggered()
        -> self.__import_dialog.load()
    """

    def __init__(self, conn: connection):
        """
        Constructor

        Arguments
        -----------------------
        conn : connection
            Connection to table/database pair
        """

        super().__init__()

        self.__conn = None
        self.__lst_form = None
        self.__add_form = None
        self.__import_dialog = None
        self.__hor_lay = None
        self.__tb = None
        self.__add_act = None
        self.__import_act = None
        self.__export_act = None

        self.__conn = conn

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

        self.show()




    def __init_forms(self):
        """
        Inits the forms and the layout which contains them
        """

        self.__lst_form = list_form()
        self.__add_form = add_form(self.__conn)

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

        self.__add_act = QAction(QIcon('resources/add.png'), 'Add', self)
        self.__add_act.setCheckable(True)
        self.__add_act.setToolTip('Hide/show add form')

        self.__import_act = QAction(QIcon('resources/import.png'), 'Import', self)
        self.__import_act.setToolTip('Import external CSV file')

        self.__export_act = QAction(QIcon('resources/export.png'), 'Export', self)
        self.__export_act.setToolTip('Export database to CSV file')

        self.__tb.addAction(self.__add_act)
        self.__tb.addAction(self.__import_act)
        self.__tb.addAction(self.__export_act)




    def __init_connections(self):
        """
        Inits connections
        """

        # reconnects back to the window with the queried data
        self.__lst_form.query_requested.connect(
                lambda s,e: self.__lst_form.update_tables(
                    db.fetch(self.__conn, s, e)
                )
        )

        # addition of new data to the db
        self.__add_form.insertion_requested.connect(
                lambda df: db.add(self.__conn, df)
        )

        # bulk insertion of imported data requested
        self.__import_dialog.import_requested.connect(
                lambda df: db.add(self.__conn, df)
        )

        # show/hide request for add_form
        self.__add_act.triggered.connect(
                self.__toggle_add
        )

        # exec import select dialog
        self.__import_act.triggered.connect(
                self.__import_dialog.load
        )




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
