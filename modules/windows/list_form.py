# Copyright (c) 2022 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem.
#
# This file may be used under the terms of the GNU General
# Public License version 3.0 as published by the Free Software
# Foundation and appearing in the file LICENSE included in the
# packaging of this file.  Please review the following
# information to ensure the GNU General Public License version
# 3.0 requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
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
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton,\
        QCalendarWidget, QGroupBox
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

import pandas as pd
from pandas import DataFrame as dataframe

import modules.common as common

from modules.CQWidgets.CQTableWidget import CQTableWidget




class list_form(QWidget):
    """
    Form to display and summarize records

    Attributes
    -----------------------
    __tab_list : CQTableWidget
        Contains the expenses with dates between the two
        selected dates, lists all fields
    __tab_sum : CQTableWidget
        Contains the sum of the expenses with dates between the
        two selected dates, grouped by category
    __cal_start : QCalendarWidget
        QCalendarWidget used to select start date in queries
    __cal_end : QCalendarWidget
        QCalendarWidget used to select end date in queries
    __but_update : QPushButton
        Updates the tables based on selected dates.
        Also refreshes expense categories

    Public methods
    -----------------------
    __init__()
        Constructor
    clear_tables()
        Clears all content
    update_tables(dataframe)
        Updates the tables from a provided dataframe
    selected_rowids() -> list[int]:
        Returns list of rowids of selected rows in __tab_list

    Private methods
    -----------------------
    __init_lay_tab() -> QVBoxLayout
        Returns the initialized table layout, empty tables
    __init_lay_cal_but() -> QVBoxLayout
        Returns the initialized calendar + buttons layout
    __init_connections()
        Inits connections

    Signals
    -----------------------
    query_requested[str, str]
        Broadcasts expense list request

    Private slots
    -----------------------
    __request_query()
        Fetches start and end dates
        and emits 'query_requested' signal
        with start and end date as arguments

    Connections
    -----------------------
    __but_update.clicked
        -> __request_query()
        -> query_requested(start_date, end_date)
    """

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__tab_list = None
        self.__tab_sum = None
        self.__cal_start = None
        self.__cal_end = None
        self.__but_update = None

        lay_tab = self.__init_lay_tab()
        lay_cal_but = self.__init_lay_cal_but()

        # generating main layout
        lay_gen = QHBoxLayout()
        lay_gen.addSpacing(25)
        lay_gen.addLayout(lay_tab)
        lay_gen.addSpacing(75)
        lay_gen.addLayout(lay_cal_but)
        lay_gen.addSpacing(25)

        self.setLayout(lay_gen)

        self.__init_connections()




    def __init_lay_tab(self) -> QVBoxLayout:
        """
        Returns the initialized table layout, empty tables
        """

        # expense list table
        self.__tab_list = CQTableWidget(self)

        # label for sum table
        label = QLabel('Summary', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = common.set_font_size(label, 20)

        # sum table
        self.__tab_sum = CQTableWidget(self)
        self.__tab_sum.setMaximumHeight(58)
        self.__tab_sum = common.lock_height(self.__tab_sum)

        # setting up layout
        lay = QVBoxLayout()
        lay.addWidget(self.__tab_list)
        lay.addSpacing(50)
        lay.addWidget(label)
        lay.addSpacing(10)
        lay.addWidget(self.__tab_sum)

        return lay




    def __init_lay_cal_but(self) -> QVBoxLayout:
        """
        Returns the initialized calendar + button layout
        """

        # start date label
        lab_start = QLabel('Start date [included]', self)
        lab_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lab_start = common.set_font_size(lab_start, 20)

        # start date calendar
        self.__cal_start = QCalendarWidget(self)
        self.__cal_start = common.lock_size(self.__cal_start)
        self.__cal_start = common.set_font_size(self.__cal_start, 16)

        # end date label
        lab_end = QLabel('End date [included]', self)
        lab_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lab_end = common.set_font_size(lab_end, 20)

        # end date calendar
        self.__cal_end = QCalendarWidget(self)
        self.__cal_end = common.lock_size(self.__cal_end)
        self.__cal_end = common.set_font_size(self.__cal_end, 16)

        # update button (graphical setup)
        self.__but_update = QPushButton('Update', self)
        self.__but_update = common.set_font_size(self.__but_update, 20)

        # setting up query details layout
        lay_det = QVBoxLayout()
        lay_det.addWidget(lab_start)
        lay_det.addWidget(self.__cal_start)
        lay_det.addSpacing(80)
        lay_det.addWidget(lab_end)
        lay_det.addWidget(self.__cal_end)
        lay_det.addSpacing(80)
        lay_det.addWidget(self.__but_update)

        # group box
        gbx_cal = QGroupBox('Query details')
        gbx_cal.setLayout(lay_det)

        # general layout
        lay = QVBoxLayout()
        lay.addSpacing(10)
        lay.addWidget(gbx_cal)
        lay.addSpacing(10)

        return lay




    def __init_connections(self):
        """
        Inits connections
        """

        self.__but_update.clicked.connect(
                self.__request_query
        )




    def clear_tables(self):
        """
        Clears all content
        """

        self.__tab_list.clear()
        self.__tab_sum.clear()




    def update_tables(self, df: dataframe):
        """
        Updates the tables from a provided dataframe

        Arguments
        -----------------------
        df : dataframe
            Dataframe used to fill the tables
            __tab_sum will only contain the categories in df
        """

        # Filling expense table
        self.__tab_list.fill(
                df,
                col = False,
                floats = [3]
        )

        # filling sum table
        try:
            ser = df.groupby('type')['amount'].sum()
            ser['Total'] = ser.sum()

            self.__tab_sum.fill(
                    ser.to_frame().T,
                    col = True,
                    floats = None,
                    last_bold = True
            )
        except KeyError:
            # empty result set
            pass




    def selected_rowids(self) -> list[int]:
        """
        Returns list of selected rows in __tab_list
        """

        rows = self.__tab_list.selected_rows()
        return [
                int(self.__tab_list.item(r,0).text())
                for r
                in rows
        ]




    query_requested = pyqtSignal(str, str)
    """
    Broadcasts expense list request

    Arguments
    -----------------------
    start_date : str
        Starting date for the requested query, 'yyyy-mm-dd'
    end_date : str
        Ending date for the requested query, 'yyyy-mm-dd'
    """




    @QtCore.pyqtSlot()
    def __request_query(self):
        """
        Emits signal with start and end date as arguments
        """

        fmt = Qt.DateFormat.ISODate
        start_date = self.__cal_start.selectedDate().toString(fmt)
        end_date = self.__cal_end.selectedDate().toString(fmt)

        self.query_requested.emit(start_date, end_date)
