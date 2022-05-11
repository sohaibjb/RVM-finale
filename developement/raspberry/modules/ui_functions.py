# ///////////////////////////////////////////////////////////////
#
# BY: EZOUAGH YOUNESS
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0

# ///////////////////////////////////////////////////////////////

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from PyQt5.QtGui import QIcon
from main import *
from PyQt5 import QtCore

# GLOBALS
# ///////////////////////////////////////////////////////////////
from modules import Settings

class UIFunctions(MainWindow):
    # START - GUI DEFINITIONS
    # ///////////////////////////////////////////////////////////////
    def uiDefinitions(self):
        # STANDARD TITLE BAR
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)