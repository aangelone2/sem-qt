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

import logging
import pandas as pd

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QValidator
from PyQt6.QtWidgets import QWidget, QSizePolicy, QMessageBox,\
        QLineEdit, QHeaderView, QTableView, QTableWidget,\
        QTableWidgetItem




colors = {
        'lightgray': QColor('#E6E6E6')
}
"""
Custom colors
"""




def lock_height(widget: QWidget) -> QWidget:
    """
    Changes size policy locking height at free width
    
    Arguments
    -----------------------
    widget : QWidget
        widget whose size policy will be changed

    Return value
    -----------------------
    Returns the modified widget.
    """

    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget


def lock_size(widget: QWidget) -> QWidget:
    """
    Changes size policy locking both height and width
    
    Arguments
    -----------------------
    widget : QWidget
        widget whose size policy will be changed

    Return value
    -----------------------
    Returns the modified widget.
    """

    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget


def set_font_size(widget: QWidget, size: int) -> QWidget:
    """
    Changes font size
    
    Arguments
    -----------------------
    widget : QWidget
        widget whose font size will be changed

    Return value
    -----------------------
    Returns the modified widget.
    """

    widget.setStyleSheet(
            '{} {{font-size: {}px}}'.format(
                type(widget).__name__, size
            )
    )

    return widget


def set_tw_behavior(tw: QTableView, behavior: str) -> QTableView:
    """
    Sets the behavior of column widths in a QTableView
    Fields become non-resizable by the user
    
    Arguments
    -----------------------
    tw : QTableView
        widget whose column size behavior will be changed
    behavior : str
        'equal' : equal-size, stretching fields
        'auto'  : fields fit content

    Return value
    -----------------------
    Returns the modified widget.
    """

    if (behavior == 'equal'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
        )
    elif (behavior == 'auto'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
        )

    return tw


def fill_table_row(table: QTableWidget,
                   df: pd.DataFrame) -> QTableWidget:
    """
    Fills a table by row with the data passed in a dataframe
    Colors in grey odd rows

    Arguments
    -----------------------
    table: QTableView
        table widget to be filled with the data
    df : pd.DataFrame
        dataframe containing the data

    Return value
    -----------------------
    Returns the filled table.
    """

    # clearing table
    table.setRowCount(0)
    table.setColumnCount(0)

    table = set_tw_behavior(table, 'auto')
    # sets last column (justification) to take all available space
    table.horizontalHeader().setStretchLastSection(True)

    # setting up columns
    fields = df.columns.to_list()
    for ic, field in enumerate(fields):
        table.insertColumn(ic)
    table.setHorizontalHeaderLabels(fields)

    # filling expense table
    for ir, row in df.iterrows():
        table.insertRow(ir)

        for ic, (field, val) in enumerate(row.items()):
            itm = QTableWidgetItem(str(val))
            if (field != 'justification'):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # greying odd rows
            if (ir % 2 == 1):
                itm.setBackground(colors['lightgray'])

            table.setItem(ir, ic, itm)

    return table


def fill_table_col(table: QTableWidget,
                   ser: pd.Series) -> QTableWidget:
    """
    Fills single-row table with the data passed in a series
    Colors in grey odd columns

    Arguments
    -----------------------
    table : QTableView
        table widget to be filled with the data
    ser : pd.Series
        series containing the data

    Return value
    -----------------------
    Returns the filled table.
    """

    # clearing table
    table.setColumnCount(0)
    # adding the only row
    table.insertRow(0)

    # filling sum table
    for ic, val in enumerate(ser):
        table.insertColumn(ic)

        itm = QTableWidgetItem(str(val))
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # greying odd columns
        if (ic % 2 == 1):
            itm.setBackground(colors['lightgray'])

        table.setItem(0, ic, itm)

    # setting header names to the ones in the current df
    table.setHorizontalHeaderLabels(ser.index.to_list())

    return table




def ErrorMsg(msg: str):
    """
    Wraps QMessageBox to generate an error message
    
    Arguments
    -----------------------
    msg : str
        the message to report
    """
    QMessageBox.critical(None, 'Error', msg)




class EQLineEdit(QLineEdit):
    """
    Subclass of QLineEdit
    Enhanced QLineEdit, changes color based on content validity
    Content is checked and color changed on content change


    Slots
    -----------------------
    __check_state()
        Changes color based on validity of content
        (green/yellow/red for ok/possibly ok/invalid)


    Connections
    -----------------------
    textChanged
        -> __check_state()
    """


    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # validity checked whenever content changed
        self.textChanged[str].connect(self.__check_state)


    @QtCore.pyqtSlot()
    def __check_state(self):
        """
        Changes color based on validity of content
        (green/yellow/red for ok/possibly ok/invalid)
        """

        state = self.validator().validate(self.text(), 0)[0]

        if (state == QValidator.State.Acceptable):
            color = 'lightgreen'
        elif (state == QValidator.State.Intermediate):
            color = 'lightyellow'
        else:
            color = 'lightred'

        self.setStyleSheet('background-color: ' + color)
