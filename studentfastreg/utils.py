import os
import sys
from logging import getLogger

from PyQt6 import QtGui
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox

from studentfastreg.settings import RESOURCES_PATH

logger = getLogger(__name__)


class TryWorker(QObject):
    def run(self):
        try:
            return self.worker_fn()
        except Exception:
            logger.exception("")
            sys.exit(-1)


def warn_yes_no(text):
    reply = QMessageBox()
    reply.setWindowTitle("Anticopy")
    reply.setIcon(QMessageBox.Icon.Warning)
    reply.setText(text)

    reply.setWindowIcon(
        QtGui.QIcon(
            os.path.join(RESOURCES_PATH, "icons", "exclamation-circle-frame.png")
        )
    )

    reply.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    x = reply.exec()

    return x == QMessageBox.StandardButton.Yes


def show_error(text):
    reply = QMessageBox()
    reply.setWindowTitle("Anticopy")
    reply.setIcon(QMessageBox.Icon.Critical)
    reply.setText(text)

    reply.setWindowIcon(
        QtGui.QIcon(os.path.join(RESOURCES_PATH, "icons", "exclamation-red.png"))
    )

    return reply.exec()
