import logging
import os
import sys
import webbrowser
from itertools import chain

from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDateEdit, QFileDialog, QLineEdit, QMessageBox, QRadioButton
from showinfm import show_in_file_manager

import studentfastreg
from studentfastreg.serializers import SFRSerializer
from studentfastreg.serializers.plain import SFRPlainSerializer
from studentfastreg.settings import BASE_DIR, LOGGING, RESOURCE_PATH

logger = logging.getLogger(__name__)


class TryWorker(QObject):
    def run(self):
        try:
            return self.worker_fn()
        except:
            logger.exception("")
            sys.exit(-1)


class MainWindow(QtWidgets.QMainWindow, object):
    @property
    def editables(self):
        if not hasattr(self, "_editables") or not self._editables:
            self._editables = tuple(
                chain(
                    self.findChildren(QLineEdit),
                    self.findChildren(QRadioButton),
                    self.findChildren(QDateEdit),
                )
            )

        return self._editables

    # region Events

    @QtCore.pyqtSlot()
    def on_event_saveAsPushButton_clicked(self):
        class Worker(TryWorker):
            finished = pyqtSignal()

            def __init__(self, *args, **kwargs):
                self.serializer: SFRPlainSerializer = kwargs.pop("serializer", None)
                self.filename = kwargs.pop("filename", None)
                super().__init__(*args, **kwargs)

            def worker_fn(self):
                self.serializer.serialize(self.filename)
                self.finished.emit()

        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Сохранить как...",
            os.path.expanduser("~"),
            SFRSerializer.get_file_explorer_entries(),
        )

        if not filename:
            logger.debug("Refused to save file")
            return

        _, ext = os.path.splitext(filename)

        serializer = SFRSerializer.get_serializer_by_ext(ext)(self)

        self.work_thread = QThread()
        self.action_worker = Worker(serializer=serializer, filename=filename)
        self.action_worker.moveToThread(self.work_thread)

        self.work_thread.started.connect(self.action_worker.run)
        self.action_worker.finished.connect(self.work_thread.quit)
        self.action_worker.finished.connect(self.action_worker.deleteLater)
        self.work_thread.finished.connect(self.work_thread.deleteLater)

        logger.info(f"Started saving the data to file '{filename}'")
        self.setAllControlsEnabled(False)
        self.work_thread.start()

        self.work_thread.finished.connect(lambda: self.setAllControlsEnabled(True))
        self.work_thread.finished.connect(
            lambda: logger.info("The file has been saved!")
        )

    @QtCore.pyqtSlot()
    def on_event_openFilePushButton_clicked(self):
        class Worker(TryWorker):
            finished = pyqtSignal()

            def __init__(self, *args, **kwargs):
                self.serializer: SFRPlainSerializer = kwargs.pop("serializer", None)
                self.filename = kwargs.pop("filename", None)
                super().__init__(*args, **kwargs)

            def worker_fn(self):
                self.serializer.deserialize(self.filename)
                self.finished.emit()

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Открыть...",
            os.path.expanduser("~"),
            SFRSerializer.get_file_explorer_entries(),
        )

        if not filename:
            logger.debug("Refused to open file")
            return

        _, ext = os.path.splitext(filename)

        serializer = SFRSerializer.get_serializer_by_ext(ext)(self)

        self.work_thread = QThread()
        self.action_worker = Worker(serializer=serializer, filename=filename)
        self.action_worker.moveToThread(self.work_thread)

        self.work_thread.started.connect(self.action_worker.run)
        self.action_worker.finished.connect(self.work_thread.quit)
        self.action_worker.finished.connect(self.action_worker.deleteLater)
        self.work_thread.finished.connect(self.work_thread.deleteLater)

        logger.info(f"Started loading data from the file '{filename}'")
        self.setAllControlsEnabled(False)
        self.work_thread.start()

        self.work_thread.finished.connect(lambda: self.setAllControlsEnabled(True))
        self.work_thread.finished.connect(
            lambda: logger.info("The file has been loaded!")
        )

    # endregion

    def connectEvents(self):
        self.saveAsPushButton.clicked.connect(self.on_event_saveAsPushButton_clicked)
        self.openFilePushButton.clicked.connect(
            self.on_event_openFilePushButton_clicked
        )

    def setAllControlsEnabled(self, state=True):
        self.openFilePushButton.setEnabled(state)
        self.saveAsPushButton.setEnabled(state)

        for ed in self.editables:
            ed.setEnabled(state)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi(os.path.join(RESOURCE_PATH, "ui", "studentfastreg.ui"), self)

        self._editables = ()

        self.centralwidget.setContentsMargins(11, 11, 11, 11)
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(RESOURCE_PATH, "ui", "icons", "favicon.png"))
        )
        self.setWindowTitle(f"studentfastreg v{studentfastreg.__str_version__}")

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
