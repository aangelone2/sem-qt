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

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QCalendarWidget, QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout,\
        QSizePolicy

import sqlite3
import pandas as pd

import modules.common as common
from modules.config import config




# form to display and summarize records
class list_window(QWidget):

    ####################### INIT #######################

    def __init__(self):
        super().__init__()

        # ATTRIBUTE: QCalendarWidget for start date
        self.__s_cal = None
        # ATTRIBUTE: QCalendarWidget for end date
        self.__e_cal = None
        # ATTRIBUTE: query update button
        self.__ub = None
        # ATTRIBUTE: record listing table
        self.__table = None
        # ATTRIBUTE: aggregation table, columns added in update()
        self.__sum = None
        # ATTRIBUTE: expense type list
        self.__tlist = []

        self.resize(1800, 1000)

        # init calendar-button group
        layc = self.__init_cal_layout()

        # init table group
        # mutable-dependent details not set (see update())
        layt = self.__init_table_layout()

        lay = QHBoxLayout()
        lay.addSpacing(100)
        lay.addLayout(layc)
        lay.addSpacing(100)
        lay.addLayout(layt)
        lay.addSpacing(100)

        # show() is missing, will be loaded from the main
        self.setLayout(lay)


    # inits the QVBoxLayout containing QCalendarWidgets and buttons
    def __init_cal_layout(self) -> QVBoxLayout:
        label1 = QLabel('Start date [included]', self)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__s_cal = QCalendarWidget(self)
        self.__s_cal = common.lock_size(self.__s_cal)
        self.__s_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        label2 = QLabel('End date [included]', self)
        label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__e_cal = QCalendarWidget(self)
        self.__e_cal = common.lock_size(self.__e_cal)
        self.__e_cal.setStyleSheet('QCalendarWidget\
                {font-size: 18px}')

        self.__ub = QPushButton('Update', self)
        self.__ub.clicked.connect(self.__request_query)

        lay = QVBoxLayout()
        lay.addSpacing(50)
        lay.addWidget(label1)
        lay.addWidget(self.__s_cal)
        lay.addSpacing(50)
        lay.addWidget(label2)
        lay.addWidget(self.__e_cal)
        lay.addSpacing(50)
        lay.addWidget(self.__ub)
        lay.addSpacing(50)

        return lay


    # inits the QVBoxLayout containing the QTableView and the label
    def __init_table_layout(self) -> QVBoxLayout:
        self.__table = QTableWidget(0, 5, self)
        # hide record index number in the record table
        self.__table.verticalHeader().hide()

        self.__table = common.set_tw_behavior(self.__table, 'equal')

        # set header names in the record table
        self.__table.setHorizontalHeaderLabels(
            ['ID', 'Date', 'Type', 'Amount', 'Justification']
        )

        label = QLabel('Total', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__sum = QTableWidget(1, 0, self)
        # hide record index number in the sum table
        self.__sum.verticalHeader().hide()
        self.__sum = common.set_tw_behavior(self.__sum, 'equal')

        self.__sum = common.lock_height(self.__sum)

        lay = QVBoxLayout()
        lay.addWidget(self.__table)
        lay.addSpacing(50)
        lay.addWidget(label)
        lay.addSpacing(10)
        lay.addWidget(self.__sum)

        return lay


    ####################### SIGNALS #######################

    # custom signal to broadcast expense list request
    # transmits the start and end date as 'yyyy-mm-dd' strings
    query_requested = pyqtSignal(str, str)


    ####################### SLOTS #######################

    # emits signal with start and end date as arguments
    @QtCore.pyqtSlot()
    def __request_query(self):
        fmt = Qt.DateFormat.ISODate
        start_date = self.__s_cal.selectedDate().toString(fmt)
        end_date = self.__e_cal.selectedDate().toString(fmt)

        self.query_requested.emit(start_date, end_date)


    # updates dialog with the current snapshot of mutable data:
    # + config
    # to be called whenever reloading the dialog
    @QtCore.pyqtSlot(config)
    def update(self, cfg: config):
        self.__table.setRowCount(0)

        self.__tlist = list(cfg.tstr)

        # create required number of columns
        self.__sum.setColumnCount(0)
        for i in range(len(self.__tlist)):
            self.__sum.insertColumn(i)

        # set header names in the sum table
        self.__sum.setHorizontalHeaderLabels(self.__tlist)


    # updates the content of self.__table and self.__sum
    # with an externally provided dataframe
    @QtCore.pyqtSlot(pd.DataFrame)
    def update_tables(self, df: pd.DataFrame):
        self.__table.setRowCount(0)

        self.__table = common.set_tw_behavior(self.__table, 'auto')
        # sets last column in self.__table to take all available space
        self.__table.horizontalHeader().setStretchLastSection(True)

        for ir, row in df.iterrows():
            self.__table.insertRow(ir)

            for ic, (field, val) in enumerate(row.items()):
                itm = QTableWidgetItem(str(val))
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if (ic % 2 == 1):
                    itm.setBackground(common.colors['lightgray'])

                self.__table.setItem(ir, ic, itm)

        asum = df.groupby('type').sum()
        asum = asum['amount']

        for i,h in enumerate(self.__tlist):
            # if no expense with a certain key is present,
            # return 0.0 (could be done in SQL, simpler here)
            try:
                val = asum.loc[h]
            except KeyError:
                val = 0.0

            itm = QTableWidgetItem(str(val))
            itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if (i % 2 == 1):
                itm.setBackground(common.colors['lightgray'])

            self.__sum.setItem(0, i, itm)
