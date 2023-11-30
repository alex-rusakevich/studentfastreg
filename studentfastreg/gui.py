import logging
import os
import sys
import webbrowser

from PyQt6 import QtGui, QtWidgets, uic
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtWidgets import QMessageBox
from showinfm import show_in_file_manager

import studentfastreg
from studentfastreg.settings import BASE_DIR, LOGGING, RESOURCE_PATH

logger = logging.getLogger(__name__)


class TryWorker(QObject):
    def run(self):
        try:
            return self.worker_fn()
        except:
            logger.exception("")
            sys.exit(-1)


class MainWindow(QtWidgets.QMainWindow):
    # region Events
    # endregion

    def connectEvents(self):
        ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(RESOURCE_PATH, "ui", "studentfastreg.ui"), self)

        self.centralwidget.setContentsMargins(11, 11, 11, 11)
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(RESOURCE_PATH, "ui", "icons", "favicon.png"))
        )
        self.setWindowTitle(f"studentfastreg v{studentfastreg.__version__}")

        # region Initializing error window
        self.err_msg = QMessageBox()
        self.err_msg.setIcon(QMessageBox.Icon.Critical)
        self.err_msg.setWindowTitle("Error")
        self.err_msg.setWindowIcon(
            QtGui.QIcon(
                os.path.join(RESOURCE_PATH, "ui", "icons", "exclamation-red.png")
            )
        )
        # endregion
        self.connectEvents()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F1:
            webbrowser.open("https://github.com/alex-rusakevich/studentfastreg")
        elif (
            e.key() == Qt.Key.Key_F5
            and e.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.setWindowTitle("I ❤️❤️❤️ you! :D")


sys.argv += ["-platform", "windows:darkmode=2"]
app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")
window = MainWindow()


def run_ui():
    window.show()
    app.exec()
