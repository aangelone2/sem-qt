# Copyright (c) 2023 Adriano Angelone
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

import modules.common as common
import modules.db as db

from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QDialog, QTableWidget,\
        QDialogButtonBox
from PyQt6.QtWidgets import QVBoxLayout


isd_width = 800
isd_height = 500


class import_show_dialog(QDialog):
    """
    Form to display imported CSV files


    Attributes
    -----------------------
    __table : QTableWidget
        Table showing the imported data
    __buttons : QDialogButtonBox
        Ok/Cancel buttons


    Methods
    -----------------------
    __init_widgets() -> QVBoxLayout
        Sets up widgets, returns the layout containing them


    Signals
    -----------------------


    Slots
    -----------------------
    load(filename: str)
        Loads a dataframe from the given file
        and displays it in the table


    Connections
    -----------------------
    __buttons.accepted.connect(accepted())
    __buttons.rejected.connect(rejected())
    """


    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.resize(isd_width, isd_height)

        self.__table = None

        lay = self.__init_widgets()

        self.__init_connections()

        self.setLayout(lay)


    def __init_widgets(self) -> QVBoxLayout:
        """
        Sets up widgets and layouts

        Return value
        -----------------------
        Returns the layout with the initialized widgets.
        """

        self.__table = QTableWidget(self)

        self.__buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
        )

        lay = QVBoxLayout()
        lay.addWidget(self.__table)
        lay.addWidget(self.__buttons)

        return lay


    def __init_connections(self):
        """
        Inits connections
        """

        self.__buttons.accepted.connect(self.accept)
        self.__buttons.rejected.connect(self.reject)


    ####################### SLOTS #######################

    @QtCore.pyqtSlot()
    def load(self, filename: str):
        self.show()

        try:
            df = db.parse_csv(filename)
        except db.DatabaseError:
            common.ErrorMsg('file error')

        logging.info('{}'.format(df))

        self.__table = common.fill_table_row(
                self.__table, df
        )
