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
        QLineEdit, QHeaderView




def lock_height(widget):
    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget


def lock_size(widget):
    widget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed
            )
    )

    return widget




def ErrorMsg(msg):
    QMessageBox.critical(None, 'Error', msg)




class EQLineEdit(QLineEdit):
    def focusInEvent(self, event):
        self.check_state()
        QLineEdit.focusInEvent(self, event)


    def check_state(self):
        state = self.validator().validate(self.text(), 0)[0]

        if (state == QValidator.State.Acceptable):
            color = 'lightgreen'
        elif (state == QValidator.State.Intermediate):
            color = 'lightyellow'
        else:
            color = 'lightred'

        self.setStyleSheet('background-color: ' + color)


    def __init__(self):
        super().__init__()

        self.textChanged[str].connect(self.check_state)




def set_tw_behavior(tw, behavior):
    if (behavior == 'equal'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
        )
    elif (behavior == 'auto'):
        tw.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
        )

    return tw
