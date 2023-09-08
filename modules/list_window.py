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
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QCalendarWidget, QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout,\
        QSizePolicy

import modules.common as common
import modules.db as db




class list_window(QWidget):
    def __init__(self, conn):
        super().__init__()

        self.conn = conn

        self.resize(1800, 1000)

        self.s_cal = QCalendarWidget()
        self.s_cal = common.lock_size(self.s_cal)
        self.s_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        self.e_cal = QCalendarWidget()
        self.e_cal = common.lock_size(self.e_cal)
        self.e_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        self.ub = QPushButton('Update')
        self.ub.clicked.connect(self.update)
        self.qb = QPushButton('Quit')
        self.qb.clicked.connect(self.hide)

        layb = QHBoxLayout()
        layb.addWidget(self.ub)
        layb.addWidget(self.qb)

        lay1 = QVBoxLayout()
        lay1.addWidget(self.s_cal)
        lay1.addWidget(self.e_cal)
        lay1.addLayout(layb)

        layt = self.init_table_layout()

        lay2 = QHBoxLayout()
        lay2.addSpacing(100)
        lay2.addLayout(lay1)
        lay2.addSpacing(100)
        lay2.addLayout(layt)
        lay2.addSpacing(100)

        # show() is missing, will be loaded from the main
        self.setLayout(lay2)


    def init_table_layout(self):
        self.table = QTableWidget(0, 5)
        self.table.verticalHeader().hide()

        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 525)

        headers = ['ID', 'Date', 'Type', 'Amount', 'Justification']
        for ih, h in enumerate(headers):
            self.table.setHorizontalHeaderItem(ih, QTableWidgetItem(h))

        label = QLabel('Total')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sum = QTableWidget(1, 5)
        self.sum.verticalHeader().hide()

        w = 225

        headers = ['E', 'H', 'I', 'N', 'R']
        for ih, h in enumerate(headers):
            self.sum.setColumnWidth(ih, w)
            self.sum.setHorizontalHeaderItem(ih, QTableWidgetItem(h))

        self.sum = common.lock_height(self.sum)

        layt = QVBoxLayout()
        layt.addWidget(self.table)
        layt.addSpacing(50)
        layt.addWidget(label)
        layt.addSpacing(10)
        layt.addWidget(self.sum)

        return layt


    def update(self):
        self.table.setRowCount(0)

        fmt = Qt.DateFormat.ISODate

        start_date = self.s_cal.selectedDate().toString(fmt)
        end_date = self.e_cal.selectedDate().toString(fmt)

        df = db.fetch(start_date, end_date, self.conn)

        for ir, row in df.iterrows():
            self.table.insertRow(ir)

            for ic, (field, val) in enumerate(row.items()):
                itm = QTableWidgetItem(str(val))
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.table.setItem(ir, ic, itm)

        asum = df.groupby('type').sum()
        asum = asum['amount']

        headers = ['E', 'H', 'I', 'N', 'R']
        for i,h in enumerate(headers):
            try:
                val = asum.loc[h]
            except KeyError:
                val = 0.0

            itm = QTableWidgetItem(str(val))
            itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.sum.setItem(0, i, itm)
