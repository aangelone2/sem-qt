"""Common functions.

Functions
-----------------------
lockHeight()
    Change size policy locking height at free width.
lockSize()
    Change size policy locking both height and width.
ErrorMsg()
    Raise wrapped QMessageBox to generate an error message.
"""

# Copyright (c) 2022 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem-qt.
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

from PyQt6.QtWidgets import QWidget, QSizePolicy, QMessageBox


def lockHeight(widget: QWidget) -> QWidget:
    """Change size policy locking height at free width.

    Parameters
    -----------------------
    widget : QWidget
        Widget whose size policy will be changed

    Returns
    -----------------------
    QWidget
        The modified widget
    """
    widget.setSizePolicy(
        QSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Fixed,
        )
    )

    return widget


def lockSize(widget: QWidget) -> QWidget:
    """Change size policy locking both height and width.

    Parameters
    -----------------------
    widget : QWidget
        Widget whose size policy will be changed

    Returns
    -----------------------
    QWidget
        The modified widget
    """
    widget.setSizePolicy(
        QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    )

    return widget


def ErrorMsg(err: Exception):
    """Raise wrapped QMessageBox to generate an error message.

    Parameters
    -----------------------
    err : Exception
        Encountered message-carrying exception
    """
    QMessageBox.critical(None, "Error", f"{err}")
