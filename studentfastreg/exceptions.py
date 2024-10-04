import logging
import os
import sys
import traceback

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox

import studentfastreg.settings as settings
from studentfastreg.settings import RESOURCE_PATH


class FileBrokenException(Exception): ...


class VersionNotSupported(Exception): ...


log = logging.getLogger(__name__)


def show_exception_box(log_msg):
    """Checks if a QApplication instance is available and shows a messagebox with the exception message.
    If unavailable (non-console application), log an additional notice.
    """
    if qt_instance := QtWidgets.QApplication.instance():
        err_msg = QMessageBox()
        err_msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
        err_msg.setIcon(QMessageBox.Icon.Critical)
        err_msg.setWindowTitle("Ошибка")
        err_msg.setText(
            "Произошла непредвиденная ошибка:\n\n{0}".format(log_msg).replace(
                "\n", "<br>"
            )
            + f"""
<br><br>
Отчеты об ошибках хранятся в папке "<a href='file:///{os.path.abspath(settings.LOG_DIR)}'>{os.path.abspath(settings.LOG_DIR)}</a>".
<br>
Сообщить о них можно по адресу <a href="mailto:mr.alexander.rusakevich@gmail.com">mr.alexander.rusakevich@gmail.com</a>, прикрепив к письму
файлы с отчетами
""".strip()
        )
        err_msg.setWindowIcon(
            QtGui.QIcon(
                os.path.join(RESOURCE_PATH, "ui", "icons", "exclamation-red.png")
            )
        )
        err_msg.exec()

        qt_instance.exit(1)
    else:
        log.debug("No QApplication instance available.")


class UncaughtHook(QtCore.QObject):
    _exception_caught = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        sys.excepthook = self.exception_hook
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = "\n".join(
                [
                    "".join(traceback.format_tb(exc_traceback)),
                    "{0}: {1}".format(exc_type.__name__, exc_value),
                ]
            )
            log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

            self._exception_caught.emit(log_msg)
