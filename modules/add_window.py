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

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QValidator, QIntValidator,\
    QDoubleValidator, QRegularExpressionValidator

import sqlite3

from modules.common import EQLineEdit
import modules.db as db
from modules.config import config




# form to add new elements to the dataframe
class add_window(QWidget):

    ####################### INIT #######################

    def __init__(self):
        super().__init__()

        # ATTRIBUTE: textbox list
        # mutable-dependent details set in update()
        self.__t = None
        # ATTRIBUTE: accept, edit and quit buttons
        self.__ab = None
        self.__eb = None
        self.__qb = None

        layf = self.__init_form()
        self.__reset_focus()

        layb = self.__init_buttons()

        lay = QVBoxLayout()
        lay.addSpacing(50)
        lay.addLayout(layf)
        lay.addSpacing(100)
        lay.addLayout(layb)
        lay.addSpacing(50)

        self.setLayout(lay)


    # inits textbox layout and sets up connections
    def __init_form(self) -> QFormLayout:
        lay = QFormLayout()

        # the checks here cannot protect against errors like '31
        # february': these will be intercepted later, in db.add
        yt = EQLineEdit(self)
        yt.setValidator(QIntValidator(1000, 9999))
        lay.addRow('Year', yt)

        mt = EQLineEdit(self)
        mt.setValidator(QIntValidator(1, 12))
        lay.addRow('Month', mt)

        dt = EQLineEdit(self)
        dt.setValidator(QIntValidator(1, 31))
        lay.addRow('Day', dt)

        # tt Validator is mutable-dependent (see update())
        tt = EQLineEdit(self)
        lay.addRow('Type', tt)

        at = EQLineEdit(self)
        # 2 digits after decimal point
        at.setValidator(QDoubleValidator(-10000.0, +10000.0, 2))
        lay.addRow('Amount', at)

        jt = EQLineEdit(self)
        # Accepts up to 100 characters
        jt.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("^.{1,100}$")
                )
        )
        lay.addRow('Justification', jt)

        self.__t = [yt, mt, dt, tt, at, jt]

        # Sets up connections for text completion signal
        for i,ti in enumerate(self.__t):
            ti.editingFinished.connect(
                lambda x = i: self.__t[(x + 1) % len(self.__t)].setFocus()
            )

        return lay


    # inits button layout and sets up connections
    def __init_buttons(self) -> QHBoxLayout:
        lay = QHBoxLayout()
        lay.addSpacing(25)

        self.__ab = QPushButton('[A]dd expense', self)
        lay.addWidget(self.__ab)
        lay.addSpacing(25)

        self.__eb = QPushButton('[E]dit expense', self)
        lay.addWidget(self.__eb)
        lay.addSpacing(25)

        self.__qb = QPushButton('[Q]uit', self)
        lay.addWidget(self.__qb)
        lay.addSpacing(25)

        self.__ab.clicked.connect(self.__request_insertion)
        self.__eb.clicked.connect(self.__reset_focus)
        self.__qb.clicked.connect(self.hide)

        return lay


    ####################### SIGNALS #######################

    # custom signal to broadcast accepted record to add to db
    # transmits a dict of (key, value) pairs for the fields
    insertion_requested = pyqtSignal(dict)


    ####################### SLOTS #######################

    # emits signal with field dictionary as argument,
    # resets focus to input new record
    @QtCore.pyqtSlot()
    def __request_insertion(self):
        fields = {
            'year': self.__t[0].text(),
            'month': self.__t[1].text(),
            'day': self.__t[2].text(),
            'type': self.__t[3].text(),
            'amount': self.__t[4].text(),
            'justification': self.__t[5].text()
        }

        self.insertion_requested.emit(fields)

        self.__reset_focus()


    # resets the focus at the first textbox, also initializes
    @QtCore.pyqtSlot()
    def __reset_focus(self):
        self.__t[0].setFocus()


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    @QtCore.pyqtSlot(config)
    def update(self, cfg: config):
        self.__t[3].setValidator(
                QRegularExpressionValidator(
                    QRegularExpression('[' + cfg.tstr + ']')
                )
        )

        if (not self.isVisible()):
            self.show()
