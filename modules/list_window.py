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


from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QCalendarWidget, QTableWidget, QTableWidgetItem,\
        QHeaderView
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout,\
        QSizePolicy

import sqlite3

import modules.common as common
import modules.db as db
import modules.config as config

# color for odd columns in the QTableView,
# #D9D9D9 also a good choice, slightly darker
bcolor1 = '#E6E6E6'




# form to display and summarize records
class list_window(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()

        # ATTRIBUTE: database connection for adding
        self.conn = None
        # ATTRIBUTE: QCalendarWidget for start date
        self.s_cal = None
        # ATTRIBUTE: QCalendarWidget for end date
        self.e_cal = None
        # ATTRIBUTE: query update button
        self.ub = None
        # ATTRIBUTE: quit button
        self.qb = None
        # ATTRIBUTE: record listing table
        self.table = None
        # ATTRIBUTE: aggregation table, columns added in update()
        self.sum = None
        # ATTRIBUTE: expense type list
        self.tlist = []

        self.conn = conn

        self.resize(1800, 1000)

        # init calendar-button group
        layc = self.init_cal_layout()

        # init table group
        # mutable-dependent details not set (see update())
        layt = self.init_table_layout()

        lay2 = QHBoxLayout()
        lay2.addSpacing(100)
        lay2.addLayout(layc)
        lay2.addSpacing(100)
        lay2.addLayout(layt)
        lay2.addSpacing(100)

        # show() is missing, will be loaded from the main
        self.setLayout(lay2)


    # inits the QVBoxLayout containing QCalendarWidgets and buttons
    def init_cal_layout(self) -> QVBoxLayout:
        self.s_cal = QCalendarWidget(self)
        self.s_cal = common.lock_size(self.s_cal)
        self.s_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        self.e_cal = QCalendarWidget(self)
        self.e_cal = common.lock_size(self.e_cal)
        self.e_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        self.ub = QPushButton('Update', self)
        self.ub.clicked.connect(self.update_tables)

        self.qb = QPushButton('Quit', self)
        self.qb.clicked.connect(self.hide)

        layb = QHBoxLayout()
        layb.addWidget(self.ub)
        layb.addWidget(self.qb)

        label1 = QLabel('Start date [included]', self)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label2 = QLabel('End date [included]', self)
        label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layc = QVBoxLayout()
        layc.addSpacing(50)
        layc.addWidget(label1)
        layc.addWidget(self.s_cal)
        layc.addSpacing(50)
        layc.addWidget(label2)
        layc.addWidget(self.e_cal)
        layc.addSpacing(50)
        layc.addLayout(layb)
        layc.addSpacing(50)

        return layc


    # inits the QVBoxLayout containing the QTableView and the label
    def init_table_layout(self) -> QVBoxLayout:
        self.table = QTableWidget(0, 5, self)
        # hide record index number in the record table
        self.table.verticalHeader().hide()

        self.table = common.set_tw_behavior(self.table, 'equal')

        # set header names in the record table
        self.table.setHorizontalHeaderLabels(
            ['ID', 'Date', 'Type', 'Amount', 'Justification']
        )

        label = QLabel('Total', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sum = QTableWidget(1, 0, self)
        # hide record index number in the sum table
        self.sum.verticalHeader().hide()
        self.sum = common.set_tw_behavior(self.sum, 'equal')

        self.sum = common.lock_height(self.sum)

        layt = QVBoxLayout()
        layt.addWidget(self.table)
        layt.addSpacing(50)
        layt.addWidget(label)
        layt.addSpacing(10)
        layt.addWidget(self.sum)

        return layt


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    def update(self, cfg: config.config):
        self.tlist = list(cfg.tstr)

        # create required number of columns
        self.sum.setColumnCount(0)
        for i in range(len(self.tlist)):
            self.sum.insertColumn(i)

        # set header names in the sum table
        self.sum.setHorizontalHeaderLabels(self.tlist)

        if (not self.isVisible()):
            self.show()



    # updates the record selection visualized in the upper
    # table, as well as the sum visualized in the lower one
    def update_tables(self):
        self.table.setRowCount(0)

        fmt = Qt.DateFormat.ISODate

        start_date = self.s_cal.selectedDate().toString(fmt)
        end_date = self.e_cal.selectedDate().toString(fmt)

        df = db.fetch(start_date, end_date, self.conn)

        self.table = common.set_tw_behavior(self.table, 'auto')
        # sets last column in self.table to take all available space
        self.table.horizontalHeader().setStretchLastSection(True)

        for ir, row in df.iterrows():
            self.table.insertRow(ir)

            for ic, (field, val) in enumerate(row.items()):
                itm = QTableWidgetItem(str(val))
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if (ic % 2 == 1):
                    itm.setBackground(QColor(bcolor1))

                self.table.setItem(ir, ic, itm)

        asum = df.groupby('type').sum()
        asum = asum['amount']

        for i,h in enumerate(self.tlist):
            # if no expense with a certain key is present,
            # return 0.0 (could be done in SQL, simpler here)
            try:
                val = asum.loc[h]
            except KeyError:
                val = 0.0

            itm = QTableWidgetItem(str(val))
            itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if (i % 2 == 1):
                itm.setBackground(QColor(bcolor1))

            self.sum.setItem(0, i, itm)
