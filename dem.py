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


import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

import add


class main_window(QWidget):
    def __init__(self):
        super().__init__()

        self.add_dialog = add.add_window()

        self.resize(300, 700)

        ba = QPushButton('[A]dd expenses')
        ba.clicked.connect(self.add_dialog.show)

        bl = QPushButton('[L]ist expenses')
        bs = QPushButton('[S]ummarize expenses')

        bq = QPushButton('[Q]uit')
        bq.clicked.connect(QApplication.instance().quit)

        b = [ba, bl, bs, bq]

        lay = QVBoxLayout()
        lay.addStretch(1)
        for bi in b:
            lay.addWidget(bi)
            lay.addStretch(1)

        self.setLayout(lay)

        self.show()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 24))

    w = main_window()
    w.setWindowTitle('dem')

    sys.exit(app.exec())


main()
