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




# form to add new elements to the dataframe: contains
# + a list of labels identifying the fields (self.l)
# + a list of EQLineEdit which accept and validate the content
#   for each field (self.t)
# + an add record, edit record and quit button
class add_window(QWidget):

    # constructor
    # + conn: database connection
    def __init__(self, cfg: config.config, conn: sqlite3.Connection):
        super().__init__()

        # MEMBER: database connection for adding
        self.conn = conn

        self.resize(800, 700)

        # MEMBER: label list
        self.l = [
            QLabel('Year'),
            QLabel('Month'),
            QLabel('Day'),
            QLabel('Type'),
            QLabel('Amount'),
            QLabel('Justification')
        ]

        # MEMBER: textbox list, same order as self.l
        self.init_textboxes(cfg)

        # label-textbox layout
        lay1 = QGridLayout()
        lay1.setSpacing(10)
        for idx, (li,ti) in enumerate(zip(self.l, self.t)):
            lay1.addWidget(li, idx, 0)
            lay1.addWidget(ti, idx, 1)

        # MEMBER: button list
        self.b = [
            QPushButton('[A]dd expense'),
            QPushButton('[E]dit expense'),
            QPushButton('[Q]uit')
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
    def init_textboxes(self, cfg: config.config):

        # the checks here cannot protect against errors like '31
        # february': these will be intercepted later, in db.add
        yt = EQLineEdit()
        yt.setValidator(QIntValidator(1000, 9999))

        mt = EQLineEdit()
        mt.setValidator(QIntValidator(1, 12))

        dt = EQLineEdit()
        dt.setValidator(QIntValidator(1, 31))

        tt = EQLineEdit()
        tt.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression('[' + cfg.tstr + ']')
                )
        )

        at = EQLineEdit()
        # 2 digits after decimal point
        at.setValidator(QDoubleValidator(-10000.0, +10000.0, 2))

        jt = EQLineEdit()
        # Accepts up to 100 characters
        jt.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("^.{1,100}$")
                )
        )
        
        self.t = [yt, mt, dt, tt, at, jt]


    # called when editing terminates in any of the textboxes,
    # refocuses the following one or the first (if at the last)
    def refocus(self):
        if (self.focused < len(self.t) - 1):
            self.focused += 1
            self.t[self.focused].setFocus()
        else:
            self.focused = -1
            self.b[0].setFocus()


    # connects the refocusing events of the textboxes and the
    # clicked events of the buttons
    def init_connections(self):
        for ti in self.t:
            ti.editingFinished.connect(self.refocus)

        self.b[0].clicked.connect(self.add)
        self.b[1].clicked.connect(self.reset_focus)
        self.b[2].clicked.connect(self.hide)


    # resets the focus at the first textbox, also initializes
    def reset_focus(self):
        self.focused = 0
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
