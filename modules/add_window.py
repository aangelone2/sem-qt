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


from PyQt6.QtCore import QRegularExpression
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QValidator, QIntValidator,\
    QDoubleValidator, QRegularExpressionValidator

import sqlite3

from modules.common import EQLineEdit
import modules.db as db
import modules.config as config




# form to add new elements to the dataframe
class add_window(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()

        # ATTRIBUTE: database connection for adding
        self.conn = None
        # ATTRIBUTE: label list
        self.l = None
        # ATTRIBUTE: textbox list, same order as self.l
        # mutable-dependent details not set (see update)
        self.t = None
        # ATTRIBUTE: button list
        self.b = None

        self.conn = conn

        self.resize(800, 700)

        self.l = [
            QLabel('Year', self),
            QLabel('Month', self),
            QLabel('Day', self),
            QLabel('Type', self),
            QLabel('Amount', self),
            QLabel('Justification', self)
        ]

        self.t = self.init_textboxes()

        # label-textbox layout
        lay1 = QGridLayout()
        lay1.setSpacing(10)
        for idx, (li,ti) in enumerate(zip(self.l, self.t)):
            lay1.addWidget(li, idx, 0)
            lay1.addWidget(ti, idx, 1)

        self.b = [
            QPushButton('[A]dd expense', self),
            QPushButton('[E]dit expense', self),
            QPushButton('[Q]uit', self)
        ]

        # init connections and reset cursor to first textbox
        self.init_connections()
        self.reset_focus()

        # button layout
        lay2 = QHBoxLayout()
        for bi in self.b:
            lay2.addWidget(bi)

        # master layout
        lay3 = QVBoxLayout()
        lay3.addLayout(lay1)
        lay3.addLayout(lay2)

        # show() is missing, will be loaded from the main
        self.setLayout(lay3)


    # prepares the list of enhanced textboxes:
    # year/month/day/type/amount/justification
    def init_textboxes(self) -> list[EQLineEdit]:

        # the checks here cannot protect against errors like '31
        # february': these will be intercepted later, in db.add
        yt = EQLineEdit(self)
        yt.setValidator(QIntValidator(1000, 9999))

        mt = EQLineEdit(self)
        mt.setValidator(QIntValidator(1, 12))

        dt = EQLineEdit(self)
        dt.setValidator(QIntValidator(1, 31))

        # tt Validator is mutable-dependent (see update())
        tt = EQLineEdit(self)

        at = EQLineEdit(self)
        # 2 digits after decimal point
        at.setValidator(QDoubleValidator(-10000.0, +10000.0, 2))

        jt = EQLineEdit(self)
        # Accepts up to 100 characters
        jt.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("^.{1,100}$")
                )
        )
        
        return [yt, mt, dt, tt, at, jt]


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    def update(self, cfg: config.config):
        self.t[3].setValidator(
                QRegularExpressionValidator(
                    QRegularExpression('[' + cfg.tstr + ']')
                )
        )

        if (not self.isVisible()):
            self.show()


    # connects the refocusing events of the textboxes and the
    # clicked events of the buttons
    def init_connections(self):
        for i,ti in enumerate(self.t):
            ti.editingFinished.connect(
                lambda x = i: self.t[(x + 1) % len(self.t)].setFocus()
            )

        self.b[0].clicked.connect(self.add)
        self.b[1].clicked.connect(self.reset_focus)
        self.b[2].clicked.connect(self.hide)


    # resets the focus at the first textbox, also initializes
    def reset_focus(self):
        self.t[0].setFocus()


    # collects textbox values and passes a dictionary to db.add,
    # resetting focus to add another record
    def add(self):
        fields = {
            'year': self.t[0].text(),
            'month': self.t[1].text(),
            'day': self.t[2].text(),
            'type': self.t[3].text(),
            'amount': self.t[4].text(),
            'justification': self.t[5].text()
        }

        db.add(fields, self.conn)
        self.reset_focus()
