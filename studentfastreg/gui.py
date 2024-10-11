import logging
import platform
import signal
import sys

from PyQt6 import QtWidgets

import studentfastreg.settings as settings
from studentfastreg.forms.studentfastreg import StudentfastregForm

logger = logging.getLogger(__name__)


def run_ui():
    if settings.config["ui"]["forceWinDarkMode"] and platform.system() == "Windows":
        sys.argv += ["-platform", "windows:darkmode=2"]

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StudentfastregForm()

    window.show()
    app.exec()
