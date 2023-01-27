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

import pandas as pd
from pandas import DataFrame as dataframe

from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QWidget, QLineEdit, QTableWidget,\
        QHeaderView, QTableView, QTableWidgetItem

import modules.common as common




class CQLineEdit(QLineEdit):
    """
    Custom QLineEdit, changes color based on content validity
    Content is checked and color changed on content change

    Methods
    -----------------------
    __init__(parent: QWidget)
        Constructor

    Slots
    -----------------------
    __check_state()
        Changes color based on validity of content

    Connections
    -----------------------
    textChanged[text]
        -> __check_state()
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

        # validity checked whenever content changed
        self.textChanged[str].connect(self.__check_state)




    @QtCore.pyqtSlot()
    def __check_state(self):
        """
        Changes color based on validity of content
        """

        if (self.hasAcceptableInput()):
            self.setStyleSheet('background-color: #7ce97c')
        else:
            self.setStyleSheet('background-color: #ff6666')




class CQTableWidget(QTableWidget):
    """
    Custom QTableWidget
    Builtin column width behavior and filling routines

    Members
    -----------------------
    __asc_order : bool
        Order of last performed sorting operation

    Methods
    -----------------------
    __init__(parent: QWidget)
        Constructor
    __repaint()
        Paints alternate rows and/or columns in grey
    clear()
        Clears all contents and resets table
    fill(df: dataframe, col: bool)
        Fills table with the given dataframe
        Colors alternate rows/columns based on context

    Slots
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

        # font sizes
        self.setStyleSheet('QTabWidget {font-size: 18px}')
        self.horizontalHeader().setStyleSheet(
                'QHeaderView {font-size: 20px}'
        )

        # sorting on column after click
        self.horizontalHeader().sectionClicked.connect(
                lambda ic: self.__sort(ic)
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
                        common.colors['lightgray']
                        if grey
                        else common.colors['white']
                )

                self.item(ir, ic).setBackground(color)




    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(0)




    def fill(self, df: dataframe, col: bool):
        """
        Fills table with the given dataframe
        Colors alternate rows/columns based on context

        Arguments
        -----------------------
        df : dataframe
            Dataframe containing the data
        col : bool
            If true, considers table as single-row,
            creating equal-width columns
        """

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
                # 2 digits after point (money)
                try:
                    float(val)
                    val = '{:.2f}'.format(val)
                except:
                    val = str(val)

                itm = QTableWidgetItem(val)
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(ir, ic, itm)

        self.__repaint()




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
