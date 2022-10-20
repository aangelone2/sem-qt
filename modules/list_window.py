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

# color for odd columns in the QTableView,
# #D9D9D9 also a good choice, slightly darker
bcolor1 = '#E6E6E6'




# form to display and summarize records: contains
# + two QCalendarWidget, to select start (self.s_cal) and end
#   (self.e_cal) date for the queries
# + an update and a quit button
# + two QTableView, the upper one displaying the records within
#   the date interval (self.table) and the lower one displaying
#   the sum of the amounts for each expense type (self.sum).
#   form to display and summarize records
# + a label between the two tables
class list_window(QWidget):

    # constructor
    # + conn: database connection
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()

        # MEMBER: database connection for adding
        self.conn = conn

        self.resize(1800, 1000)

        # init calendar-button group
        layc = self.init_cal_layout()

        # init table group
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

        # MEMBER: QCalendarWidget for start date
        self.s_cal = QCalendarWidget()
        self.s_cal = common.lock_size(self.s_cal)
        self.s_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        # MEMBER: QCalendarWidget for end date
        self.e_cal = QCalendarWidget()
        self.e_cal = common.lock_size(self.e_cal)
        self.e_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        # MEMBER: query update button
        self.ub = QPushButton('Update')
        self.ub.clicked.connect(self.update)
        # MEMBER: quit button
        self.qb = QPushButton('Quit')
        self.qb.clicked.connect(self.hide)

        layb = QHBoxLayout()
        layb.addWidget(self.ub)
        layb.addWidget(self.qb)

        label1 = QLabel('Start date [included]')
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label2 = QLabel('End date [included]')
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

        # MEMBER: record listing table
        self.table = QTableWidget(0, 5)
        # hide record index number in the record table
        self.table.verticalHeader().hide()

        self.table = common.set_tw_behavior(self.table, 'equal')

        # set header names in the record table
        headers = ['ID', 'Date', 'Type', 'Amount', 'Justification']
        for ih, h in enumerate(headers):
            self.table.setHorizontalHeaderItem(ih, QTableWidgetItem(h))

        label = QLabel('Total')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # MEMBER: aggregation table
        self.sum = QTableWidget(1, 5)
        # hide record index number in the sum table
        self.sum.verticalHeader().hide()
        self.sum = common.set_tw_behavior(self.sum, 'equal')

        # set header names in the sum table
        headers = ['E', 'H', 'I', 'N', 'R']
        for ih, h in enumerate(headers):
            self.sum.setHorizontalHeaderItem(ih, QTableWidgetItem(h))

        self.sum = common.lock_height(self.sum)

        layt = QVBoxLayout()
        layt.addWidget(self.table)
        layt.addSpacing(50)
        layt.addWidget(label)
        layt.addSpacing(10)
        layt.addWidget(self.sum)

        return layt


    # updates the record selection visualized in the upper
    # table, as well as the sum visualized in the lower one
    def update(self):
        # resets the number of rows
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

                # odd columns are colored in light gray
                if (ic % 2 == 1):
                    itm.setBackground(QColor(bcolor1))

                self.table.setItem(ir, ic, itm)

        asum = df.groupby('type').sum()
        asum = asum['amount']

        headers = ['E', 'H', 'I', 'N', 'R']
        for i,h in enumerate(headers):

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
