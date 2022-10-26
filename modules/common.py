# Copyright (c) 2022 Adriano Angelone
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
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
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QWidget, QSizePolicy, QMessageBox,\
        QLineEdit, QHeaderView, QTableView




# given a widget, returns it with its size policy changed,
# width is free to change while height is fixed to the default
def lock_height(widget: QWidget) -> QWidget:
    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget


# given a widget, returns it with its size policy changed,
# both width and height are fixed to the default
def lock_size(widget: QWidget) -> QWidget:
    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget




# wrapper to QMessageBox to generate error messages
def ErrorMsg(msg: str):
    QMessageBox.critical(None, 'Error', msg)




# subclass of QLineEdit
# + focusInEvent reimplemented to check and visualize validity
#   of content (through color change)
# + content validity also checked whenever content is changed
class EQLineEdit(QLineEdit):

    # reimplemented focusInEvent, checks validity of content
    # through check_state()
    def focusInEvent(self, event):
        self.check_state()
        QLineEdit.focusInEvent(self, event)


    # validation function for input, changes color based on
    # state (green/yellow/red for ok/possibly ok/invalid)
    def check_state(self):
        state = self.validator().validate(self.text(), 0)[0]

        if (state == QValidator.State.Acceptable):
            color = 'lightgreen'
        elif (state == QValidator.State.Intermediate):
            color = 'lightyellow'
        else:
            color = 'lightred'

        self.setStyleSheet('background-color: ' + color)


    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # validity checked whenever content changed
        self.textChanged[str].connect(self.check_state)




# accepts and returns a modified QTableView and a string value
# to set its behavior concerning field width:
# + 'equal' sets all fields to have the same width and stretch
#   to cover all available space
# + 'auto' sets all fields to change their size to fit the
#   longest item contained within them
# In both cases, fields become non-resizable by the user
def set_tw_behavior(tw: QTableView, behavior: str) -> QTableView:
    if (behavior == 'equal'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
        )
    elif (behavior == 'auto'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
        )

    return tw
