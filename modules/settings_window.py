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


from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QPushButton,\
        QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import modules.common as common
import modules.config as config

# color for odd rows in the QTableView,
# #D9D9D9 also a good choice, slightly darker
bcolor1 = '#E6E6E6'




# settings dialog: contains
# + a QWidgetTable which will display a config when updated
# + add/delete buttons for table rows (config elements)
# + accept/cancel buttons
class settings_window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(400, 400)

        # table generated but not filled
        self.setup_table()

        layb1 = self.setup_ad_buttons()

        lay1 = QHBoxLayout()
        lay1.addWidget(self.table)
        lay1.addLayout(layb1)

        # MEMBER: accept button
        self.bacc = QPushButton('Accept')
        # FIXME add code to emit event

        # MEMBER: cancel button
        self.bcan = QPushButton('Cancel')
        # current table contents will be ignored,
        # the dialog will simply be hidden
        self.bcan.clicked.connect(self.hide)

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

        # MEMBER: QTableWidget containing config elements
        # as (key, description) pairs
        self.table = QTableWidget(0,2)

        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()

        self.table = common.set_tw_behavior(self.table, 'auto')
        self.table.horizontalHeader().setStretchLastSection(True)


    # sets up the add/delete buttons
    def setup_ad_buttons(self) -> QVBoxLayout:

        # MEMBER: adds row in the last position of self.table
        self.badd = QPushButton('+')
        self.badd.clicked.connect(
                lambda: self.table.insertRow(self.table.rowCount())
        )

        # MEMBER: deletes current row in self.table
        self.bdel = QPushButton('-')
        # FIXME connect clicked signal

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
    def return_cfg(self) -> config.config:
        contents = {}

        with t as self.table:
            for row in range(t.rowCount()):
                contents[t.item(row, 0).text()] = t.item(row, 1)

        return config.config(contents)
