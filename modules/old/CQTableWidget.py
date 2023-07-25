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

from pandas import DataFrame

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import QWidget, QTableWidget,\
        QHeaderView, QTableView, QTableWidgetItem,\
        QAbstractItemView

from modules.Common import colors



class CQTableWidget(QTableWidget):
    """
    Custom QTableWidget
    Builtin column width behavior and filling routines

    Members
    -----------------------
    __asc_order : bool
        Order of last performed sorting operation

    Public methods
    -----------------------
    __init__(parent: QWidget)
        Constructor
    clear()
        Clears all contents and resets table
    fill(df: DataFrame, col: bool)
        Fills table with the given DataFrame
        Colors alternate rows/columns based on context
    selected_rows() -> list[int]
        Returns list of indices of currently selected rows

    Private methods
    -----------------------
    __repaint()
        Paints alternate rows and/or columns in grey

    Private slots
    -----------------------
    __sort(ic: int)
        Sorts according to the specified column
        Order swaps after every ordering task

    Connections
    -----------------------
    horizontalHeader.sectionClicked[ic]
        -> __sort(ic)
    """

    def __init__(self, parent: QWidget):
        """
        Constructor

        Arguments
        -----------------------
        parent : QWidget
            Parent QWidget
        """

        super().__init__(parent)

        # first ordering will be flipped (irrelevant)
        self.__asc_order = True

        # hiding headers
        self.verticalHeader().hide()

        # equal-width columns
        self.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
        )

        # sorting on column after click
        self.horizontalHeader().sectionClicked.connect(
                lambda ic: self.__sort(ic)
        )

        # highlight entire rows on selection
        self.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
        )



    def __repaint(self):
        """
        Paints alternate rows and/or columns in grey
        """

        rows = (self.rowCount() > 1)

        # filling expense table
        for ir in range(self.rowCount()):
            for ic in range (self.columnCount()):
                grey = ((ir % 2 == 1) if rows else (ic % 2 == 1))

                color = (
                        colors.lightgray
                        if grey
                        else colors.white
                )

                self.item(ir, ic).setBackground(color)



    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(0)



    def fill(self,
             df: DataFrame,
             col: bool,
             floats: list[int] = None,
             last_bold: bool = False):
        """
        Fills table with the given DataFrame
        Colors alternate rows/columns based on context

        Arguments
        -----------------------
        df : DataFrame
            Dataframe containing the data
        col : bool
            If true, considers table as single-row,
            creating equal-width columns
        floats: list[int]
            List of column indices where numbers are
            to be considered floats ({.02f})
            If None (default), all columns as floats
        last_bold: bool
            If True, the last column is written in bold
        """

        if (floats is None):
            floats = list(range(df.shape[1]))

        self.clear()

        if (not col):
            # autosize columns
            self.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.ResizeToContents
            )

            # sets last column to take all available space
            self.horizontalHeader().setStretchLastSection(True)

        # setting up columns
        fields = df.columns.to_list()
        self.setColumnCount(len(fields))
        self.setHorizontalHeaderLabels(fields)

        # filling expense table
        for ir, (idx, row) in enumerate(df.iterrows()):
            self.insertRow(ir)

            for ic, (field, val) in enumerate(row.items()):
                if (ic in floats):
                    # 2 digits after point (money)
                    val = '{:.2f}'.format(val)
                else:
                    val = str(val)

                itm = QTableWidgetItem(val)
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if (last_bold and ic == (df.shape[1] - 1)):
                    font = QFont()
                    font.setBold(True)
                    itm.setFont(font)

                self.setItem(ir, ic, itm)

        self.__repaint()



    def selected_rows(self) -> list[int]:
        """
        Returns list of indices of currently selected rows
        """

        return [s.row()
                for s
                in self.selectionModel().selectedRows()]



    @QtCore.pyqtSlot(int)
    def __sort(self, ic: int):
        """
        Sorts according to the specified column
        Order swaps after every ordering task

        Arguments
        -----------------------
        ic : int
            Column index to sort according to
        """

        self.__asc_order = not self.__asc_order

        order = (
                Qt.SortOrder.AscendingOrder
                if self.__asc_order
                else Qt.SortOrder.DescendingOrder
        )

        self.sortItems(ic, order)
        self.__repaint()