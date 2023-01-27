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
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QWidget, QDialog, QLineEdit,\
        QPushButton
from PyQt6.QtWidgets import QFormLayout, QVBoxLayout,\
        QHBoxLayout




class login_dialog(QDialog):
    """
    Dialog to obtain/establish login credentials

    Attributes
    -----------------------
    __txt_user : QLineEdit
        Textbox for the username
    __txt_pssw : QLineEdit
        Textbox for the password
    __but_login : QPushButton
        Login button
    __but_signup : QPushButton
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
    __sweep() -> tuple[str]
        Extracts and clears textbox content

    Static methods
    -----------------------
    get_request() -> tuple[str, str, int]:
        Instantiates a login_dialog and returns user input

    Connections
    -----------------------
    __but_login.clicked
        -> self.done[int]
    __but_signup.clicked
        -> self.done[int]
    __but_exit.clicked
        -> self.done[int]
    """

    class request():
        login = 1
        signup = 2
        exit = 3




    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.__txt_user = None
        self.__txt_pssw = None
        self.__but_login = None
        self.__but_signup = None
        self.__but_exit = None

        lay = self.__init_widgets()

        self.__init_connections()

        self.setLayout(lay)




    def __init_widgets(self) -> QVBoxLayout:
        """
        Sets up widgets and layouts

        Return value
        -----------------------
        Returns the layout with the initialized widgets
        """

        self.__txt_user = QLineEdit(self)
        self.__txt_pssw = QLineEdit(self)
        self.__txt_pssw.setEchoMode(QLineEdit.EchoMode.Password)

        layf = QFormLayout()
        layf.addRow('Username', self.__txt_user)
        layf.addRow('Password', self.__txt_pssw)

        self.__but_login = QPushButton('Login', self)
        self.__but_signup = QPushButton('Create', self)
        self.__but_exit = QPushButton('Exit', self)

        layb = QHBoxLayout()
        layb.addSpacing(10)
        layb.addWidget(self.__but_login)
        layb.addSpacing(10)
        layb.addWidget(self.__but_signup)
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
                lambda: self.done(self.request.login)
        )
        self.__but_signup.clicked.connect(
                lambda: self.done(self.request.signup)
        )
        self.__but_exit.clicked.connect(
                lambda: self.done(self.request.exit)
        )




    def __sweep(self) -> tuple[str]:
        """
        Extracts and clears textbox content

        Return value
        -----------------------
        Returns a (user,pssw) tuple
        """

        u = self.__txt_user.text()
        self.__txt_user.setText('')

        p = self.__txt_pssw.text()
        self.__txt_pssw.setText('')

        return (u,p)




    @staticmethod
    def get_request() -> tuple[str, str, int]:
        """
        Instantiates a login_dialog and returns user input

        Return value
        -----------------------
        Returns a (user, pssw, login_dialog.result) tuple
        """

        dialog = login_dialog()
        request = dialog.exec()

        (u,p) = dialog.__sweep()
        return (u, p, request)
