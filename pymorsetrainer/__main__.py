"""
(C) 2017 David Kolossa

This file is part of PyMorsetrainer.

PyMorsetrainer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMorsetrainer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMorsetrainer.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys

from PyQt5.QtWidgets import QApplication
from pymorsetrainer.pymorsetrainer import MainWindow

def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    if "--debug" in app.arguments():
        print("Debug active...")
        mw.enableDebugMode()
    return app.exec_()

if __name__ == "__main__":
    main()

