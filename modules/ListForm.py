"""List window.

Classes
-----------------------
ListForm
    Form to display and summarize records.
"""

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
from PyQt6.QtCore import Qt, pyqtSignal, QPersistentModelIndex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QGroupBox,
)
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtSql import QSqlTableModel, QSqlQueryModel

from modules.Common import lockSize
from modules.CQTableView import CQTableView


class ListForm(QWidget):
    """Form to display and summarize records.

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
    __butClear : QPushButton
        Clears all data filters

    Public methods
    -----------------------
    __init__(QWidget)
        Construct class instance.
    setModels(QSqlTableModel)
        Set models for the CQTableView objects.
    selection() -> list[QPersistentModelIndex]
        Return the list of the indices of the selected rows.

    Private methods
    -----------------------
    __initWidgets() -> QHBoxLayout
        Return the initialized and arranged widgets.
    __initConnections()
        Init connections.

    Signals
    -----------------------
    filterRequested[list[str]]
        Broadcast request to update date filter.
    clearingRequested[]
        Broadcast request to clear date filter.

    Private slots
    -----------------------
    __requestFilter()
        Request data filtering.
    __requestClearing()
        Request table clearing.

    Connections
    -----------------------
    __butClear.clicked
        -> __requestClearing()
        -> clearingRequested()
    """

    def __init__(self, parent: QWidget):
        """Construct class instance.

        Parameters
        -----------------------
        parent: QWidget
            Parent QWidget
        """
        super().__init__(parent)

        self.__tabList = None
        self.__tabSum = None
        self.__calStart = None
        self.__calEnd = None
        self.__butClear = None

        lay = self.__initWidgets()
        self.setLayout(lay)

        self.__initConnections()

    def setModels(
        self,
        listModel: QSqlTableModel,
        sumModel: QSqlQueryModel,
    ):
        """Set models for the CQTableView objects.

        Parameters
        -----------------------
        listModel: QSqlTableModel
            Model for the list CQTableView
        sumModel: QSqQueryModel
            Model for the sum CQTableView
        """
        self.__tabList.setModel(listModel)
        self.__tabSum.setModel(sumModel)

    def selection(self) -> list[QPersistentModelIndex]:
        """Return the list of the indices of the selected rows."""
        return [
            QtCore.QPersistentModelIndex(model_idx)
            for model_idx in self.__tabList.selectionModel().selectedRows()
        ]

    def __initWidgets(self) -> QHBoxLayout:
        """Return the initialized and arranged widgets."""
        # expense list table
        self.__tabList = CQTableView(self)

        # sum table
        self.__tabSum = CQTableView(self)
        self.__tabSum.setMaximumHeight(120)
        self.__tabSum = lockSize(self.__tabSum)

        laySum = QVBoxLayout()
        laySum.addWidget(self.__tabSum)

        # sum group box
        gbxSum = QGroupBox("Expense summary")
        gbxSum.setLayout(laySum)

        # start date label
        labStart = QLabel("Start date [included]", self)
        labStart.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # start date calendar
        self.__calStart = QCalendarWidget(self)
        self.__calStart = lockSize(self.__calStart)

        # end date label
        labEnd = QLabel("End date [included]", self)
        labEnd.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # end date calendar
        self.__calEnd = QCalendarWidget(self)
        self.__calEnd = lockSize(self.__calEnd)

        # update button (graphical setup)
        self.__butUpdate = QPushButton("Update", self)

        # clear button (graphical setup)
        self.__butClear = QPushButton("Clear", self)

        # button layout
        layButtons = QHBoxLayout()
        layButtons.addWidget(self.__butUpdate)
        layButtons.addWidget(self.__butClear)

        # control layout
        layControls = QVBoxLayout()
        layControls.addWidget(labStart)
        layControls.addWidget(self.__calStart)
        layControls.addWidget(labEnd)
        layControls.addWidget(self.__calEnd)
        layControls.addLayout(layButtons)

        # control group box
        gbxControl = QGroupBox("Filter by date")
        gbxControl.setLayout(layControls)

        # control-sum layout
        layControlSum = QVBoxLayout()
        layControlSum.addWidget(gbxSum)
        layControlSum.addWidget(gbxControl)

        # overall layout
        lay = QHBoxLayout()
        lay.addWidget(self.__tabList)
        lay.addLayout(layControlSum)

        return lay

    def __initConnections(self):
        """Init connections."""
        self.__butUpdate.clicked.connect(self.__requestFilter)

        self.__butClear.clicked.connect(self.__requestClearing)

    filterRequested = pyqtSignal(list)
    """Broadcast request to update date filter.

    Parameters
    -----------------------
    dates : list[str]
        [startDate, endDate], 'yyyy-mm-dd'
        may be None
    """

    clearingRequested = pyqtSignal()
    """Broadcast request to clear date filter."""

    @QtCore.pyqtSlot()
    def __requestFilter(self):
        """Request data filtering.

        Fetches start and end dates
        and emits 'filterRequested' signal
        with start and end date as arguments
        """
        fmt = Qt.DateFormat.ISODate
        startDate = self.__calStart.selectedDate().toString(
            fmt
        )
        endDate = self.__calEnd.selectedDate().toString(fmt)

        self.filterRequested.emit([startDate, endDate])

    @QtCore.pyqtSlot()
    def __requestClearing(self):
        """Request table clearing.

        Emits 'filterRequested' signal with `None` argument,
        requesting clearing of date filters
        """
        self.clearingRequested.emit()
