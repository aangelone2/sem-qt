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
        QApplication
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import sqlite3

import modules.db as db
from modules.list_form import list_form


mw_width = 1300
mw_height = 400


# main screen
class main_window(QWidget):
    """
    Main program window


    Attributes
    -----------------------
    __lst_form : list_form
        Internal list_form widget
    __lay : QHBoxLayout
        Horizontal layout, contains widgets
        Will be extended/contracted to display/hide add_form
    __conn : sqlite3.Connection
        Connection to database-table pair


    Methods
    -----------------------
    __init_connections()
        Inits connections


    Connections
    -----------------------
    __lst_form.query_requested(start, end)
        -> <df = fetch(start, end)>
        -> __lst_form.update_tables(df)
    """


    def __init__(self, conn: sqlite3.Connection):
        """
        Constructor


        Arguments
        -----------------------
        conn : sqlite3.Connection
            Connection to table/database pair
        """

        super().__init__()

        self.resize(mw_width, mw_height)

        self.__lst_form = list_form()

        self.__lay = QHBoxLayout()
        self.__lay.addWidget(self.__lst_form)
        self.setLayout(self.__lay)

        self.__conn = conn

        self.__init_connections()

        self.show()


    def __init_connections(self):
        """
        Inits connections
        """

        # reconnects back to the window with the queried data
        self.__lst_form.query_requested.connect(
                lambda s,e: self.__lst_form.update_tables(
                    db.fetch(s, e, self.__conn)
                )
        )
