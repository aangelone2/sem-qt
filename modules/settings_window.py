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

from PyQt6.QtWidgets import QWidget, QPushButton,\
        QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import modules.common as common
from modules.config import config




# settings dialog
class settings_window(QWidget):

    ####################### INIT #######################

    def __init__(self):
        super().__init__()

        # ATTRIBUTE: QTableWidget of config elements
        # as (key, description) pairs
        self.__table = None
        # ATTRIBUTE: button, adds row at the end of self.__table
        self.__addb = None
        # ATTRIBUTE: deletes current row in self.__table
        self.__delb = None
        # ATTRIBUTE: accept button
        self.__accb = None
        # ATTRIBUTE: cancel button
        self.__canb = None

        self.resize(400, 400)

        # table generated but not filled
        layt = self.__init_table()

        layb = self.__init_buttons()

        lay = QVBoxLayout()
        lay.addLayout(layt)
        lay.addSpacing(50)
        lay.addLayout(layb)
        lay.addSpacing(20)

        # show() is missing, will be loaded from the main
        self.setLayout(lay)


    # creates add/remove and empty QWidgetTable
    # (content is mutable-dependent, see update())
    def __init_table(self) -> QHBoxLayout:
        self.__table = QTableWidget(0, 2, self)

        self.__table.horizontalHeader().hide()
        self.__table.verticalHeader().hide()

        self.__table = common.set_tw_behavior(self.__table, 'auto')
        self.__table.horizontalHeader().setStretchLastSection(True)

        self.__addb = QPushButton('+', self)
        self.__addb.clicked.connect(
                lambda: self.__table.insertRow(self.__table.rowCount())
        )

        self.__delb = QPushButton('-', self)
        self.__delb.clicked.connect(
                lambda: self.__table.removeRow(self.__table.currentRow())
        )

        layb = QVBoxLayout()
        layb.addWidget(self.__addb)
        layb.addWidget(self.__delb)

        lay = QHBoxLayout()
        lay.addWidget(self.__table)
        lay.addLayout(layb)

        return lay


    # creates the accept/cancel buttons
    def __init_buttons(self) -> QHBoxLayout:
        self.__accb = QPushButton('Accept', self)
        self.__accb.clicked.connect(self.__accept_changes)

        self.__canb = QPushButton('Cancel', self)
        self.__canb.clicked.connect(self.hide)

        lay = QHBoxLayout()
        lay.addSpacing(100)
        lay.addWidget(self.__accb)
        lay.addSpacing(100)
        lay.addWidget(self.__canb)
        lay.addSpacing(100)

        return lay


    ####################### SIGNALS #######################

    # custom signal to broadcast an accepted config change
    # transmits the new config
    changes_accepted = pyqtSignal(config)


    ####################### SLOTS #######################

    # signal acceptance of changes
    # broadcasts config created from table data
    @QtCore.pyqtSlot()
    def __accept_changes(self):
        contents = {}
        for row in range(self.__table.rowCount()):
            contents[self.__table.item(row, 0).text()] = self.__table.item(row, 1).text()

        self.changes_accepted.emit(config(dic = contents))

        self.hide()


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    @QtCore.pyqtSlot(config)
    def update(self, cfg: config):
        self.__table.setRowCount(0)

        for t, (l,d) in enumerate(cfg.tdict.items()):
            self.__table.insertRow(t)

            itm_l = QTableWidgetItem(l)
            if (t % 2 == 1):
                itm_l.setBackground(common.colors['lightgray'])

            itm_d = QTableWidgetItem(d)
            if (t % 2 == 1):
                itm_d.setBackground(common.colors['lightgray'])
                
            self.__table.setItem(t, 0, itm_l)
            self.__table.setItem(t, 1, itm_d)

        if (not self.isVisible()):
            self.show()
