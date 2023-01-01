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

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QApplication
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import sqlite3
import logging

import modules.db as db
from modules.list_form import list_form
from modules.add_form import add_form


mw_narrow = 1200
mw_wide = 1600
mw_height = 400


# main screen
class main_window(QWidget):
    """
    Main program window


    Attributes
    -----------------------
    __lst_form : list_form
        Internal list_form widget
    __add_form : add_form
        Internal add_form widget
    __lay : QHBoxLayout
        Horizontal layout, contains widgets
        Extended/contracted to display/hide add_form
    __conn : sqlite3.Connection
        Connection to database-table pair


    Methods
    -----------------------
    __init_connections()
        Inits connections


    Slots
    -----------------------
    __toggle_add()
        hides/shows the addition form
        stretches/compresses the window as required


    Connections
    -----------------------
    __lst_form.query_requested(start, end)
        -> <df = fetch(start, end)>
        -> __lst_form.update_tables(df)

    __lst_form.add_requested()
        -> __toggle_add()

    __add_form.insertion_requested(fields)
        -> db.add(fields, __conn)
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

        # set to narrow size by default
        self.resize(mw_narrow, mw_height)

        self.__conn = conn

        self.__lst_form = list_form()
        self.__add_form = add_form(self.__conn)

        # no add form in the layout by default
        self.__lay = QHBoxLayout()
        self.__lay.addWidget(self.__lst_form)
        self.setLayout(self.__lay)

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

        self.__lst_form.add_requested.connect(
                self.__toggle_add
        )

        self.__add_form.insertion_requested.connect(
                lambda fields: db.add(fields, self.__conn)
        )


    ####################### SLOTS #######################

    @QtCore.pyqtSlot()
    def __toggle_add(self):
        """
        hides/shows the addition form
        stretches/compresses the window as required
        """

        logging.info('in toggle_add')

        if (self.__add_form.isVisible() is False):
            # show add form
            self.resize(mw_wide, mw_height)
            self.layout().addWidget(self.__add_form)
            self.__add_form.show()
        else:
            # hide add form
            self.__add_form.hide()
            self.layout().removeWidget(self.__add_form)
            self.resize(mw_narrow, mw_height)

        # re-centering the window horizontally
        screen = QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        x = (screen_geom.width() - self.width()) // 2
        self.move(x, self.y())
