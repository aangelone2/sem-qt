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

from PyQt6.QtWidgets import QApplication

import modules.common as common
import modules.db as db
import modules.config as config
import modules.main_window as mw
import modules.add_window as aw
import modules.list_window as lw




config_file = 'config/config'
version = '0.3.0'




def main():
    app = QApplication(sys.argv)

    # using system default font, just changing size
    font = app.font()
    font.setPointSize(22)
    app.setFont(font)

    try:
        cfg = config.config(config_file)
    except config.ConfigError:
        common.ErrorMsg('config setup error')
        sys.exit()

    table = 'expenses'

    try:
        db_conn = db.init(cfg.path, table)
    except db.DatabaseError:
        common.ErrorMsg('database error')
        sys.exit()

    w = mw.main_window(version, cfg, db_conn)
    w.setWindowTitle('sem')

    sys.exit(app.exec())




main()
