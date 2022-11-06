# Copyright (c) 2022 Adriano Angelone
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
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
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QTabWidget, QMainWindow, QApplication
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import sqlite3

import modules.db as db
from modules.config import config
from modules.add_window import add_window
from modules.list_window import list_window
from modules.settings_window import settings_window




# main screen
class main_window(QMainWindow):

    ####################### INIT #######################

    def __init__(self, version: str,
            cfg: config, conn: sqlite3.Connection):
        super().__init__()

        # ATTRIBUTE: stored configuration settings
        self.__cfg = None
        # ATTRIBUTE: add form
        self.__add_form = None
        # ATTRIBUTE: list form
        self.__list_form = None
        # ATTRIBUTE: settings dialog window
        self.__settings_dialog = None
        # ATTRIBUTE: tab widget to handle add and list forms
        self.__tabs = None

        self.resize(1800, 1000)

        self.__cfg = cfg

        self.__init_tab(conn)
        self.setCentralWidget(self.__tab)

        self.__init_menu()

        self.show()


    def __init_tab(self, conn: sqlite3.Connection):
        self.__add_form = add_window()
        # trick: slot with 2 args, signal returns 1
        self.__add_form.insertion_requested.connect(
                lambda fields: db.add(fields, conn)
        )
        # bootstrapping
        self.__add_form.update(self.__cfg)

        self.__list_form = list_window()
        # reconnects back to the window with the queried data
        self.__list_form.query_requested.connect(
                lambda s,e: self.__list_form.update_tables(
                    db.fetch(s, e, conn)
                )
        )
        # bootstrapping
        self.__list_form.update(self.__cfg)

        self.__settings_dialog = settings_window()
        self.__settings_dialog.changes_accepted.connect(
                self.update
        )

        self.__tab = QTabWidget(self)
        self.__tab.addTab(self.__add_form, 'Add expenses')
        self.__tab.addTab(self.__list_form, 'List expenses')


    def __init_menu(self):
        menubar = self.menuBar()
        menu_file = menubar.addMenu('File')

        act_settings = QAction('Settings...', self)
        act_settings.triggered.connect(
                lambda: self.__settings_dialog.update(self.__cfg)
        )
        menu_file.addAction(act_settings)



        #bq = QPushButton('[Q]uit', self)
        #bq.clicked.connect(QApplication.instance().quit)


    ####################### SLOTS #######################

    # local cfg <- new values, updates forms accordingly
    @QtCore.pyqtSlot(config)
    def update(self, cfg: config):
        self.__cfg = cfg

        self.__add_window.update(cfg)
        self.__list_window.update(cfg)
