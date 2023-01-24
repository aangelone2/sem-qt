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


from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QDialog, QLineEdit,\
        QPushButton
from PyQt6.QtWidgets import QFormLayout, QVBoxLayout,\
        QHBoxLayout




class login_dialog(QDialog):
    """
    Form to obtain/establish login credentials

    Attributes
    -----------------------
    __txt_user : QLineEdit
        Textbox for the username
    __txt_pssw : QLineEdit
        Textbox for the password
    __but_login : QPushButton
        Login button
    __but_create : QPushButton
        Signup button
    __but_exit : QPushButton
        Exit button

    Methods
    -----------------------
    __init__(parent: QWidget)
        Constructor
    __init_widgets() -> QVBoxLayout
        Sets up widgets, returns the layout containing them
    __init_connections()
        Inits connections

    Signals
    -----------------------
    login_requested[str, str]
        Broadcasts login request
    signup_requested[str, str]
        Broadcasts signup request
    exit_requested
        Broadcasts exit request

    Connections
    -----------------------
    __but_login.clicked
        -> login_requested.emit[user, passw]
    __but_create.clicked
        -> signup_requested.emit[user, passw]
    __but_exit.clicked
        -> exit_requested.emit
    """

    def __init__(self, parent: QWidget):
        """
        Constructor
        """

        super().__init__(parent)

        self.__txt_user = None
        self.__txt_pssw = None
        self.__but_login = None
        self.__but_create = None
        self.__but_exit = None

        lay = self.__init_widgets()

        self.__init_connections()

        self.setLayout(lay)

        self.show()




    def __init_widgets(self) -> QVBoxLayout:
        """
        Sets up widgets and layouts

        Return value
        -----------------------
        Returns the layout with the initialized widgets
        """

        self.__txt_user = QLineEdit(self)
        self.__txt_pssw = QLineEdit(self)

        layf = QFormLayout()
        layf.addRow('Username', self.__txt_user)
        layf.addRow('Password', self.__txt_pssw)

        self.__but_login = QPushButton('Login', self)
        self.__but_create = QPushButton('Create', self)
        self.__but_exit = QPushButton('Exit', self)

        layb = QHBoxLayout()
        layb.addSpacing(10)
        layb.addWidget(self.__but_login)
        layb.addSpacing(10)
        layb.addWidget(self.__but_create)
        layb.addSpacing(10)
        layb.addWidget(self.__but_exit)
        layb.addSpacing(10)

        lay = QVBoxLayout()
        lay.addLayout(layf)
        lay.addSpacing(50)
        lay.addLayout(layb)

        return lay




    def __init_connections(self):
        """
        Inits connections
        """

        self.__but_login.clicked.connect(
                lambda: self.login_requested.emit(
                    self.__txt_user.text(),
                    self.__txt_pssw.text(),
                )
        )
        self.__but_create.clicked.connect(
                lambda: self.signup_requested.emit(
                    self.__txt_user.text(),
                    self.__txt_pssw.text(),
                )
        )
        self.__but_exit.clicked.connect(
                lambda: self.exit_requested.emit()
        )




    login_requested = pyqtSignal(str, str)
    """
    Broadcasts login request

    Arguments
    -----------------------
    user : str
        Username for login
    pssw : str
        Password for login
    """




    signup_requested = pyqtSignal(str, str)
    """
    Broadcasts signup request

    Arguments
    -----------------------
    user : str
        Username for signup
    pssw : str
        Password for signup
    """



    exit_requested = pyqtSignal()
    """
    Broadcasts exit request
    """
