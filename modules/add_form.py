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
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from PyQt6.QtCore import QDate, QRegularExpression
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton,\
        QCalendarWidget, QLabel, QGroupBox
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QValidator, QIntValidator,\
        QDoubleValidator, QRegularExpressionValidator

import sqlite3
import logging
import pandas as pd

import modules.db as db
import modules.common as common
from modules.common import EQLineEdit

af_width = 400



class add_form(QWidget):
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
    __init_layout() -> QVboxLayout
        Returns the initialized layout with the widgets
        Sets up Validators in the EQLineEdits
    __init_connections() -> None
        Sets up connections between widgets


    Signals
    -----------------------
    insertion_requested = pyqtSignal(dict)
        broadcasts record to add to db
        transmits a dict of (key, value: str) pairs:
        + date
        + type
        + amount
        + justification


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
        -> insertion_requested(fields)
    """


    def __init__(self, conn : sqlite3.Connection):
        """
        Constructor

        Arguments
        -----------------------
        conn
            Connection to table/database pair
        """

        super().__init__()

        self.__cal = None
        self.__txt_type = None
        self.__txt_amount = None
        self.__txt_justif = None
        self.__but_accept = None

        self.setMaximumWidth(af_width)
        self.setLayout(self.__init_layout(conn))
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
        self.__cal = QCalendarWidget(self)
        self.__cal = common.lock_size(self.__cal)
        self.__cal = common.set_font_size(self.__cal, 18)

        # type textbox
        self.__txt_type = EQLineEdit(self)
        # getting list of valid types
        types = db.fetch_types(conn)

        logging.info('fetched types = {}'.format(types))
        logging.info('type string = {}'.format(''.join(types)))

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

        # new entry details
        lay_det = QVBoxLayout()
        lay_det.addWidget(self.__cal)
        lay_det.addSpacing(25)

        lab_type = QLabel('Type', self)
        lab_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_det.addWidget(lab_type)
        lay_det.addSpacing(-25)
        lay_det.addWidget(self.__txt_type)
        lay_det.addSpacing(25)

        lab_amount = QLabel('Amount', self)
        lab_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_det.addWidget(lab_amount)
        lay_det.addSpacing(-25)
        lay_det.addWidget(self.__txt_amount)
        lay_det.addSpacing(25)

        lab_justif = QLabel('Justification', self)
        lab_justif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_det.addWidget(lab_justif)
        lay_det.addSpacing(-25)
        lay_det.addWidget(self.__txt_justif)

        gb = QGroupBox('Entry details', self)
        gb.setLayout(lay_det)

        # general layout
        lay = QVBoxLayout()
        lay.addWidget(gb)
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

    insertion_requested = pyqtSignal(pd.DataFrame)
    """
        broadcasts record to add to db
        transmits a pd.DataFrame containing the fields
    """


    ####################### SLOTS #######################

    @QtCore.pyqtSlot()
    def __request_insertion(self):
        """
        Fetches query details from widgets,
        emits signal passing details as dictionary,
        sets focus on the calendar
        """

        logging.info('in request_insertion')

        date = self.__cal.selectedDate().toString(
                format = Qt.DateFormat.ISODate
        )

        # single-row dataframe, still works
        df = pd.DataFrame({
            'date': [date],
            'type': [self.__txt_type.text()],
            'amount': [self.__txt_amount.text()],
            'justification': [self.__txt_justif.text()]
        })

        self.__cal.setFocus()

        self.insertion_requested.emit(df)
