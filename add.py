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


import sys

from PyQt6.QtCore import QRegularExpression

from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout

from PyQt6.QtGui import QValidator, QIntValidator, QRegularExpressionValidator


class add_window(QWidget):
    def init_textboxes(self):
        self.focused = 0

        yt = QLineEdit()
        yt.setValidator(QIntValidator(1000, 9999))

        mt = QLineEdit()
        mt.setValidator(QIntValidator(1, 12))

        dt = QLineEdit()
        dt.setValidator(QIntValidator(1, 31))

        tt = QLineEdit()
        tt.setValidator(
                QRegularExpressionValidator(
                    QRegularExpression("[IHFNER]")
                )
        )

        at = QLineEdit()

        jt = QLineEdit()
        
        return [yt, mt, dt, tt, at, jt]


    def check_state(self):
        tb = self.t[self.focused]
        state = tb.validator().validate(tb.text(), 0)[0]

        if (state == QValidator.State.Acceptable):
            color = 'lightgreen'
        elif (state == QValidator.State.Intermediate):
            color = 'lightyellow'
        else:
            color = 'lightred'

        self.t[self.focused].setStyleSheet('background-color: ' + color)


    def refocus(self):
        if (self.focused < len(self.t) - 1):
            self.focused += 1
            self.t[self.focused].setFocus()
        else:
            self.focused = -1
            self.b[0].setFocus()


    def init_connections(self):
        for it, ti in enumerate(self.t):
            ti.textChanged[str].connect(self.check_state)
            ti.editingFinished.connect(self.refocus)


    def __init__(self):
        super().__init__()

        self.resize(800, 700)

        self.l = [
            QLabel('Year'),
            QLabel('Month'),
            QLabel('Day'),
            QLabel('Type'),
            QLabel('Amount'),
            QLabel('Justification')
        ]

        self.t = self.init_textboxes()

        lay1 = QGridLayout()
        lay1.setSpacing(10)
        for idx, (li,ti) in enumerate(zip(self.l, self.t)):
            lay1.addWidget(li, idx, 0)
            lay1.addWidget(ti, idx, 1)

        ba = QPushButton('[A]dd expense')
        be = QPushButton('[E]dit expense')

        bq = QPushButton('[Q]uit')
        bq.clicked.connect(self.hide)

        self.b = [ba, be, bq]

        self.init_connections()
        
        lay2 = QHBoxLayout()
        for bi in self.b:
            lay2.addWidget(bi)

        lay3 = QVBoxLayout()
        lay3.addLayout(lay1)
        lay3.addLayout(lay2)

        # show() is missing, will be loaded from the main
        self.setLayout(lay3)
