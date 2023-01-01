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

from PyQt6.QtCore import QDate, QRegularExpression
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton,\
        QCalendarWidget
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QValidator, QIntValidator,\
        QDoubleValidator, QRegularExpressionValidator

import sqlite3

import modules.common as common
from modules.common import EQLineEdit




class add_window(QWidget):
    """
    Form to obtain info about new elements


    Attributes
    -----------------------
    __cal : QCalendarWidget
        Calendar to select the date for the expense
    __txt_type : EQLineEdit
        Textbox for the expense type
    __txt_amount : EQLineEdit
        Textbox for the expense amount
    __txt_justif : EQLineEdit
        Textbox for the expense justification
    __but_accept : QPushButton
        Button to accept specified details


    Methods
    -----------------------
    __init_layout
        Returns the initialized layout with the widgets
        Sets up Validators in the EQLineEdits
    __init_connections
        Sets up connections between widgets


    Signals
    -----------------------
    insertion_requested = pyqtSignal(dict)
        broadcasts record to add to db
        transmits a dict of (key, value) pairs for the fields


    Slots
    -----------------------
    __request_insertion(self):
        Fetches query details from widgets,
        emits signal passing details as dictionary,
        sets focus on the calendar


    Connections
    -----------------------
    __cal.selectionChanged()
        -> __txt_type.setFocus

    __txt_type.editingFinished()
        -> __txt_amount.setFocus

    __txt_amount.editingFinished()
        -> __txt_justif.setFocus

    __txt_justif.editingFinished()
        -> __but_accept.setFocus

    __but_accept.clicked()
        -> __request_insertion
    """


    def __init__(self):
        super().__init__()

        self.__cal = None
        self.__txt_type = None
        self.__txt_amount = None
        self.__txt_justif = None
        self.__but_accept = None

        self.setLayout(__init_widgets())
        self.__init_connections()


    def __init_layout(self, conn: sqlite3.Connection) -> QVBoxLayout:
        """
        Initializes widget layout, sets up validators

        Arguments
        -----------------------
        conn
            Connection to table/database pair

        Return value
        -----------------------
        Returns the layout with the initialized widgets.
        """

        # calendar
        self.__cal = QCalendarWidget()
        self.__cal = common.lock_size(self.__cal)
        self.__cal = common.set_font_size(self.__cal, 18)

        # type textbox
        self.__txt_type = EQLineEdit(self)
        # getting list of valid types
        types = common.fetch_types(conn)
        # setup validator with gathered types
        self.__txt_type.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression('[' + ''.join(types) + ']')
                )
        )

        # amount textbox
        self.__txt_amount = EQLineEdit(self)
        # 2 digits after decimal point
        self.__txt_amount.setValidator(
                QDoubleValidator(-10000.0, +10000.0, 2)
        )

        # justification textbox
        self.__txt_justif = EQLineEdit(self)
        # Accepts up to 100 characters
        self.__txt_justif.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("^.{1,100}$")
                )
        )

        self.__but_accept = QPushButton('Add expense', self)

        lay = QVBoxLayout()
        lay.addWidget(self.__cal)
        lay.addSpacing(25)
        lay.addWidget(self.__txt_type)
        lay.addSpacing(25)
        lay.addWidget(self.__txt_amount)
        lay.addSpacing(25)
        lay.addWidget(self.__txt_justif)
        lay.addSpacing(50)
        lay.addWidget(self.__but_accept)

        return lay


    def __init_connections(self):
        """
        Inits connections
        """

        # each widget leaves focus to the following one
        self.__cal.selectionChanged.connect(
                self.__txt_type.setFocus
        )
        self.__txt_type.editingFinished.connect(
                self.__txt_amount.setFocus
        )
        self.__txt_amount.editingFinished.connect(
                self.__txt_justif.setFocus
        )
        self.__txt_justif.editingFinished.connect(
                self.__but_accept.setFocus
        )

        self.__but_accept.clicked.connect(self.__request_insertion)


    ####################### SIGNALS #######################

    insertion_requested = pyqtSignal(dict)
    """
        broadcasts record to add to db
        transmits a dict of (key, value) pairs for the fields
    """


    ####################### SLOTS #######################

    @QtCore.pyqtSlot()
    def __request_insertion(self):
        """
        Fetches query details from widgets,
        emits signal passing details as dictionary,
        sets focus on the calendar
        """

        fmt = Qt.DateFormat.ISODate
        date = self.__cal.selectedDate().toString(fmt)

        fields = {
            'date': date,
            'type': self.__txt_type.text(),
            'amount': self.__txt_amount.text(),
            'justification': self.__txt_justif.text()
        }

        self.__cal.setFocus()

        self.insertion_requested.emit(fields)
