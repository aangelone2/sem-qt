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
from pandas import DataFrame as dataframe

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QValidator
from PyQt6.QtWidgets import QWidget, QLineEdit, QTableWidget,\
        QHeaderView, QTableView, QTableWidgetItem

import modules.common as common




class CQLineEdit(QLineEdit):
    """
    Custom QLineEdit, changes color based on content validity
    Content is checked and color changed on content change

    Methods
    -----------------------
    __init__()
        Constructor

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
        """
        Constructor

        Arguments
        -----------------------
        parent : QWidget
            parent QWidget
        """

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




class CQTableWidget(QTableWidget):
    """
    Custom QTableWidget
    Builtin column width behavior and filling routines

    Methods
    -----------------------
    __init__()
        Constructor

    Slots
    -----------------------
    fill()
        Fills table with the given dataframe
        Colors alternate rows/columns based on context
    """

    def __init__(self, parent: QWidget):
        """
        Constructor

        Arguments
        -----------------------
        parent : QWidget
            parent QWidget
        """

        super().__init__(parent)

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




    @QtCore.pyqtSlot()
    def fill(self, df: dataframe):
        """
        Fills table with the given dataframe
        Colors alternate rows/columns based on context

        Arguments
        -----------------------
        df : dataframe
            dataframe containing the data
        """

        # clearing table
        self.setRowCount(0)
        self.setColumnCount(0)

        # row/column filling
        rows = (df.shape[0] > 1)

        if (rows):
            # autosize columns
            self.horizontalHeader().setSectionResizeMode(
                    QHeaderView.ResizeMode.ResizeToContents
            )

            # sets last column to take all available space
            self.horizontalHeader().setStretchLastSection(True)

        # setting up columns
        fields = df.columns.to_list()
        logging.info('fields = {}'.format(fields))
        self.setColumnCount(len(fields))
        self.setHorizontalHeaderLabels(fields)

        # filling expense table
        for ir, (idx, row) in enumerate(df.iterrows()):
            logging.info('ir = {}'.format(ir))
            self.insertRow(ir)

            for ic, (field, val) in enumerate(row.items()):
                itm = QTableWidgetItem(str(val))
                if (field != 'justification'):
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # greying odd rows/columns
                grey = ((ir % 2 == 1) if rows else (ic % 2 == 1))
                if (grey):
                    itm.setBackground(common.colors['lightgray'])

                self.setItem(ir, ic, itm)
