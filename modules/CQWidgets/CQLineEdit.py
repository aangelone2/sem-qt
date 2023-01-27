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

from PyQt6.QtWidgets import QWidget, QLineEdit




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
