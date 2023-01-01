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
import logging

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

import modules.common as common
import modules.db as db

from modules.main_window import main_window




path = 'data/expenses.sqlite'
table = 'expenses'
version = '0.6.0'




def main():
    logging.basicConfig(level = logging.INFO)

    app = QApplication(sys.argv)

    # using system default font, just changing size
    app.setFont(QFont('Lato', 16))

    # checking for db connection errors
    try:
        db_conn = db.init(path, table)
    except db.DatabaseError:
        common.ErrorMsg('database error')
        sys.exit()

    w = main_window(db_conn)
    w.setWindowTitle('sem')

    out = app.exec()

    sys.exit(out)




main()
