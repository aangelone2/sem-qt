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
from PyQt6.QtSql import QSqlTableModel

from modules.Common import lock_height, lock_size

from modules.CQTableWidget import CQTableWidget



SUM_TABLE_HEIGHT = 50



class ListForm(QWidget):
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
    __init__(QSqlTableModel)
        Constructor
    clear_tables()
        Clears all content

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

    def __init__(self, list_model: QSqlTableModel):
        """
        Constructor

        Arguments
        -----------------------
        list_model: QSqlTableModel
            Model for the list CQTableWidget
        """

        super().__init__()

        self.__tab_list = None
        self.__tab_sum = None
        self.__cal_start = None
        self.__cal_end = None
        self.__but_update = None

        lay_tab = self.__init_lay_tab()
        lay_cal_but = self.__init_lay_cal_but()

        # assigning SQL models
        self.__tab_list.setModel(list_model)

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

        # sum table
        self.__tab_sum = CQTableWidget(self)
        self.__tab_sum.setMaximumHeight(SUM_TABLE_HEIGHT)
        self.__tab_sum = lock_height(self.__tab_sum)

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

        # start date calendar
        self.__cal_start = QCalendarWidget(self)
        self.__cal_start = lock_size(self.__cal_start)

        # end date label
        lab_end = QLabel('End date [included]', self)
        lab_end.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # end date calendar
        self.__cal_end = QCalendarWidget(self)
        self.__cal_end = lock_size(self.__cal_end)

        # update button (graphical setup)
        self.__but_update = QPushButton('Update', self)

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
