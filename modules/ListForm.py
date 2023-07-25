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

from modules.Common import lockHeight, lockSize
from modules.CQTableView import CQTableView



SUM_TABLE_HEIGHT = 50



class ListForm(QWidget):
    """
    Form to display and summarize records

    Attributes
    -----------------------
    __tabList : CQTableView
        Contains the expenses with dates between the two
        selected dates, lists all fields
    __tabSum : CQTableView
        Contains the sum of the expenses with dates between the
        two selected dates, grouped by category
    __calStart : QCalendarWidget
        QCalendarWidget used to select start date in queries
    __calEnd : QCalendarWidget
        QCalendarWidget used to select end date in queries
    __butUpdate : QPushButton
        Updates the tables based on selected dates.
        Also refreshes expense categories

    Public methods
    -----------------------
    __init__(QWidget)
        Constructor
    setModels(QSqlTableModel)
        Set models for the CQTableView objects

    Private methods
    -----------------------
    __initLayTab() -> QVBoxLayout
        Returns the initialized table layout, empty tables
    __initLayCalBut() -> QVBoxLayout
        Returns the initialized calendar + buttons layout
    __initConnections()
        Inits connections

    Signals
    -----------------------
    queryRequested[str, str]
        Broadcasts expense list request

    Private slots
    -----------------------
    __requestQuery()
        Fetches start and end dates
        and emits 'queryRequested' signal
        with start and end date as arguments

    Connections
    -----------------------
    __butUpdate.clicked
        -> __requestQuery()
        -> queryRequested(start_date, end_date)
    """

    def __init__(self, parent: QWidget):
        """
        Constructor

        Arguments
        -----------------------
        parent: QWidget
            Parent QWidget
        """

        super().__init__(parent)

        self.__tabList = None
        self.__tabSum = None
        self.__calStart = None
        self.__calEnd = None
        self.__butUpdate = None

        layTab = self.__initLayTab()
        layCalBut = self.__initLayCalBut()

        # generating main layout
        layGen = QHBoxLayout()
        layGen.addSpacing(25)
        layGen.addLayout(layTab)
        layGen.addSpacing(75)
        layGen.addLayout(layCalBut)
        layGen.addSpacing(25)

        self.setLayout(layGen)

        self.__initConnections()



    def setModels(self, listModel: QSqlTableModel):
        """
        Set models for the CQTableView objects

        Arguments
        -----------------------
        listModel: QSqlTableModel
            Model for the list CQTableView
        """

        self.__tabList.setModel(listModel)



    def __initLayTab(self) -> QVBoxLayout:
        """
        Returns the initialized table layout, empty tables
        """

        # expense list table
        self.__tabList = CQTableView(True, self)

        # label for sum table
        label = QLabel('Summary', self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # sum table
        self.__tabSum = CQTableView(False, self)
        self.__tabSum.setMaximumHeight(SUM_TABLE_HEIGHT)
        self.__tabSum = lockHeight(self.__tabSum)

        # setting up layout
        lay = QVBoxLayout()
        lay.addWidget(self.__tabList)
        lay.addSpacing(50)
        lay.addWidget(label)
        lay.addSpacing(10)
        lay.addWidget(self.__tabSum)

        return lay



    def __initLayCalBut(self) -> QVBoxLayout:
        """
        Returns the initialized calendar + button layout
        """

        # start date label
        labStart = QLabel('Start date [included]', self)
        labStart.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # start date calendar
        self.__calStart = QCalendarWidget(self)
        self.__calStart = lockSize(self.__calStart)

        # end date label
        labEnd = QLabel('End date [included]', self)
        labEnd.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # end date calendar
        self.__calEnd = QCalendarWidget(self)
        self.__calEnd = lockSize(self.__calEnd)

        # update button (graphical setup)
        self.__butUpdate = QPushButton('Update', self)

        # setting up query details layout
        layDet = QVBoxLayout()
        layDet.addWidget(labStart)
        layDet.addWidget(self.__calStart)
        layDet.addSpacing(80)
        layDet.addWidget(labEnd)
        layDet.addWidget(self.__calEnd)
        layDet.addSpacing(80)
        layDet.addWidget(self.__butUpdate)

        # group box
        gbxCal = QGroupBox('Query details')
        gbxCal.setLayout(layDet)

        # general layout
        lay = QVBoxLayout()
        lay.addSpacing(10)
        lay.addWidget(gbxCal)
        lay.addSpacing(10)

        return lay



    def __initConnections(self):
        """
        Inits connections
        """

        self.__butUpdate.clicked.connect(
                self.__requestQuery
        )



    queryRequested = pyqtSignal(str, str)
    """
    Broadcasts expense list request

    Arguments
    -----------------------
    startDate : str
        Starting date for the requested query, 'yyyy-mm-dd'
    endDate : str
        Ending date for the requested query, 'yyyy-mm-dd'
    """



    @QtCore.pyqtSlot()
    def __requestQuery(self):
        """
        Emits signal with start and end date as arguments
        """

        fmt = Qt.DateFormat.ISODate
        startDate = self.__calStart.selectedDate().toString(fmt)
        endDate = self.__calEnd.selectedDate().toString(fmt)

        self.queryRequested.emit(startDate, endDate)
