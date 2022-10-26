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


from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QPushButton,\
        QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import modules.common as common
import modules.config as config

# color for odd rows in the QTableView,
# #D9D9D9 also a good choice, slightly darker
bcolor1 = '#E6E6E6'




# settings dialog
class settings_window(QWidget):
    def __init__(self):
        super().__init__()

        # ATTRIBUTE: accept button
        self.bacc = None
        # ATTRIBUTE: cancel button
        self.bcan = None
        # ATTRIBUTE: QTableWidget of config elements
        # as (key, description) pairs
        self.table = None
        # ATTRIBUTE: button, adds row at the end of self.table
        self.badd = None
        # ATTRIBUTE: deletes current row in self.table
        self.bdel = None

        self.resize(400, 400)

        # table generated but not filled
        self.setup_table()

        layb1 = self.setup_ad_buttons()

        lay1 = QHBoxLayout()
        lay1.addWidget(self.table)
        lay1.addLayout(layb1)

        self.bacc = QPushButton('Accept', self)
        self.bacc.clicked.connect(self.close)

        self.bcan = QPushButton('Cancel', self)
        self.bcan.clicked.connect(self.close)

        layb2 = QHBoxLayout()
        layb2.addSpacing(100)
        layb2.addWidget(self.bacc)
        layb2.addSpacing(100)
        layb2.addWidget(self.bcan)
        layb2.addSpacing(100)

        lay2 = QVBoxLayout()
        lay2.addLayout(lay1)
        lay2.addSpacing(50)
        lay2.addLayout(layb2)
        lay2.addSpacing(20)

        # show() is missing, will be loaded from the main
        self.setLayout(lay2)


    # creates the QWidgetTable but does not fill it
    # (content is mutable-dependent, see update())
    def setup_table(self):
        self.table = QTableWidget(0, 2, self)

        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()

        self.table = common.set_tw_behavior(self.table, 'auto')
        self.table.horizontalHeader().setStretchLastSection(True)


    # sets up the add/delete buttons
    def setup_ad_buttons(self) -> QVBoxLayout:
        self.badd = QPushButton('+', self)
        self.badd.clicked.connect(
                lambda: self.table.insertRow(self.table.rowCount())
        )

        self.bdel = QPushButton('-', self)
        self.bdel.clicked.connect(
                lambda: self.table.removeRow(self.table.currentRow())
        )

        lay = QVBoxLayout()
        lay.addWidget(self.badd)
        lay.addWidget(self.bdel)

        return lay


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    def update(self, cfg: config.config):
        self.table.setRowCount(0)

        for t, (l,d) in enumerate(cfg.tdict.items()):
            self.table.insertRow(t)

            itm_l = QTableWidgetItem(l)
            if (t % 2 == 1):
                itm_l.setBackground(QColor(bcolor1))

            itm_d = QTableWidgetItem(d)
            if (t % 2 == 1):
                itm_d.setBackground(QColor(bcolor1))
                
            self.table.setItem(t, 0, itm_l)
            self.table.setItem(t, 1, itm_d)

        if (not self.isVisible()):
            self.show()


    # return a configuration from the contents of self.table
    # using a dictionary as intermediate step
    def cfg(self) -> config.config:
        contents = {}

        for row in range(self.table.rowCount()):
            contents[self.table.item(row, 0).text()] = self.table.item(row, 1).text()

        return config.config(dic = contents)


    # custom signal to broadcast accepted changes in the cfg
    accepted_changes = pyqtSignal()


    # hides the window, emits a signal to broadcast acceptance
    def close(self):
        self.hide()

        if (self.sender().text() == 'Accept'):
            self.accepted_changes.emit()
