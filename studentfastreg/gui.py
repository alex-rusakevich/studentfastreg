import logging
import platform
import signal
import sys

from PyQt6 import QtWidgets

import studentfastreg.settings as settings
from studentfastreg.forms.studentfastreg import StudentfastregForm
from studentfastreg.kms import is_org_act
from studentfastreg.utils import show_error

logger = logging.getLogger(__name__)


def run_ui():
    if settings.config["ui"]["forceWinDarkMode"] and platform.system() == "Windows":
        sys.argv += ["-platform", "windows:darkmode=2"]

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StudentfastregForm()

    if not is_org_act(settings.ORGANIZATION):
        show_error(
            f"У организации '{settings.ORGANIZATION}' истек срок лицензии, \
использование программы невозможно"
        )
        return

    window.show()
    app.exec()
