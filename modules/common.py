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
from PyQt6.QtGui import QColor, QValidator
from PyQt6.QtWidgets import QWidget, QSizePolicy, QMessageBox,\
        QLineEdit, QHeaderView, QTableView




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
