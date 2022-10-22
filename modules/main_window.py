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


from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QApplication
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import sqlite3

import modules.config as config
import modules.add_window as aw
import modules.list_window as lw
import modules.settings_window as sw




# main splash screen: contains
# + two labels with program name and version number
# + buttons to call up the add/list/settings forms and quit
class main_window(QWidget):
    def __init__(self, version: str,
            cfg: config.config, conn: sqlite3.Connection):
        super().__init__()

        self.resize(700, 700)

        l1 = QLabel('Simple Expense Manager')
        l1.setStyleSheet('QLabel {font-size: 40px}')

        l2 = QLabel('Version {}'.format(version))

        self.cfg = cfg

        lay1 = QVBoxLayout()
        lay1.addSpacing(100)
        lay1.addWidget(l1)
        lay1.addSpacing(50)
        lay1.addWidget(l2)
        lay1.addSpacing(100)

        # MEMBER: add dialog window
        self.add_dialog = aw.add_window(conn)
        # MEMBER: list dialog window
        self.list_dialog = lw.list_window(conn)
        # MEMBER: settings dialog window
        self.settings_dialog = sw.settings_window()

        ba = QPushButton('[A]dd expenses')
        ba.clicked.connect(
                lambda: self.add_dialog.update(self.cfg)
        )

        bl = QPushButton('[L]ist expenses')
        bl.clicked.connect(
                lambda: self.list_dialog.update(self.cfg)
        )

        bs = QPushButton('[S]ettings')
        bs.clicked.connect(
                lambda: self.settings_dialog.update(self.cfg)
        )

        bq = QPushButton('[Q]uit')
        bq.clicked.connect(QApplication.instance().quit)

        b = [ba, bl, bs, bq]

        lay2 = QVBoxLayout()
        lay2.addSpacing(100)
        for bi in b:
            lay2.addWidget(bi)
            lay2.addSpacing(100)

        lay3 = QHBoxLayout()
        lay3.addSpacing(100)
        lay3.addLayout(lay1)
        lay3.addSpacing(100)
        lay3.addLayout(lay2)
        lay3.addSpacing(100)

        self.setLayout(lay3)

        self.show()
