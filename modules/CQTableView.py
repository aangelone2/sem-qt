"""Custom table widget.

Classes
-----------------------
CQTableView
    Custom QTableView.
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

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget, QHeaderView, QTableView


class CQTableView(QTableView):
    """Custom QTableView.

    Builtin column width/sorting behavior and coloring
    routines.

    Public methods
    -----------------------
    __init__(parent: QWidget)
        Constructor
    """

    def __init__(self, parent: QWidget):
        """Construct class instance.

        Parameters
        -----------------------
        parent : QWidget
            Parent QWidget
        """
        super().__init__(parent)

        # sets sorting as activated on column click
        # ascending/descending order is toggled
        self.setSortingEnabled(True)

        # setting color palette
        gray = QColor("#E6E6E6")

        p = self.palette()
        p.setBrush(QPalette.ColorRole.AlternateBase, gray)
        self.setPalette(p)

        # autosize columns
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        # sets last column to take all available space
        self.horizontalHeader().setStretchLastSection(True)

        # alternating row colors
        self.setAlternatingRowColors(True)
