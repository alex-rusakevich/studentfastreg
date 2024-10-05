import logging
import os
import platform
import signal
import sys
from itertools import chain

from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDateEdit, QFileDialog, QLineEdit, QMessageBox, QRadioButton

import studentfastreg
import studentfastreg.settings as settings
from studentfastreg import EXCEPTION_HOOK
from studentfastreg.serializers import SFRSerializer
from studentfastreg.serializers.plain import SFRPlainSerializer
from studentfastreg.settings import RESOURCE_PATH

logger = logging.getLogger(__name__)


class TryWorker(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            return self.worker_fn()
        except Exception:
            EXCEPTION_HOOK.exception_hook(*sys.exc_info())


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

    def show_help(self):
        help_msg = QMessageBox()
        help_msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
        help_msg.setIcon(QMessageBox.Icon.Information)
        help_msg.setWindowTitle("Информация")
        help_msg.setText(
            f"""
Программа создана Александром Русакевичем (<a href='https://github.com/alex-rusakevich/'>https://github.com/alex-rusakevich/</a>)
<br><br>
Файл конфигурации: "<a href='file:///{os.path.abspath(settings.CONFIG_PATH)}'>{os.path.abspath(settings.CONFIG_PATH)}</a>"
<br><br>
Отчеты об ошибках хранятся в папке "<a href='file:///{os.path.abspath(settings.LOG_DIR)}'>{os.path.abspath(settings.LOG_DIR)}</a>".
<br><br>
Сообщить о них можно по адресу <a href="mailto:mr.alexander.rusakevich@gmail.com">mr.alexander.rusakevich@gmail.com</a>, прикрепив к письму
файлы с отчетами
""".strip()
        )
        help_msg.setWindowIcon(
            QtGui.QIcon(os.path.join(RESOURCE_PATH, "ui", "icons", "information.png"))
        )
        help_msg.exec()

    def updateProgressCounter(self):
        counter = 0
        max_minus = 0

        radio_button_seqs = (
            (self.maleRadioButton, self.femaleRadioButton),
            (self.villageRadioButton, self.cityRadioButton),
        )

        for radio_button_seq in radio_button_seqs:
            for radio_button in radio_button_seq:
                if radio_button.isChecked():
                    counter += 1
                    break

            max_minus += len(radio_button_seq) - 1

        modified_editables = ()

        if self.cityRadioButton.isChecked():
            modified_editables = tuple(
                i
                for i in self.editables
                if i.objectName() not in ["councilLineEdit", "villageLineEdit"]
            )
        elif self.villageRadioButton.isChecked():
            modified_editables = tuple(
                i for i in self.editables if i.objectName() != "cityLineEdit"
            )

        for widget in modified_editables:
            if type(widget) in (QDateEdit, QLineEdit) and widget.text().strip() != "":
                counter += 1

        percent = counter / (len(modified_editables) - max_minus) * 100
        self.progressLabel.setText(f"Заполнено на {percent:.2f}%")

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

        filename, selected_filter = QFileDialog.getSaveFileName(
            None,
            "Сохранить как...",
            os.path.expanduser("~"),
            SFRSerializer.get_file_explorer_entries(direction="serialize"),
            options=QFileDialog.Option.DontUseNativeDialog,
        )

        ext = None

        for c in SFRSerializer.__subclasses__():
            if c.FILE_EXTENSION in selected_filter:
                ext = c.FILE_EXTENSION

        if not filename:
            logger.debug("Refused to save file")
            return

        if not filename.endswith(ext):
            filename += ext

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

        if settings.config["openFileDirOnSave"]:
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl(f"file:///{os.path.dirname(filename)}")
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
            SFRSerializer.get_file_explorer_entries(direction="deserialize"),
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
        self.work_thread.finished.connect(self.updateProgressCounter)
        self.work_thread.finished.connect(self.setVillageCityMode)
        self.work_thread.finished.connect(
            lambda: logger.info("The file has been loaded!")
        )

    # endregion

    def setVillageCityMode(self, country_or_city="auto"):
        if country_or_city == "village":
            self.councilLineEdit.setEnabled(True)
            self.villageLineEdit.setEnabled(True)
            self.cityLineEdit.setEnabled(False)
        elif country_or_city == "city":
            self.councilLineEdit.setEnabled(False)
            self.villageLineEdit.setEnabled(False)
            self.cityLineEdit.setEnabled(True)
        elif country_or_city == "auto":
            if self.villageRadioButton.isChecked():
                self.setVillageCityMode("village")
            else:
                self.setVillageCityMode("city")

    def connectEvents(self):
        self.saveAsPushButton.clicked.connect(self.on_event_saveAsPushButton_clicked)
        self.showHelpPushButton.clicked.connect(self.show_help)
        self.openFilePushButton.clicked.connect(
            self.on_event_openFilePushButton_clicked
        )

        self.villageRadioButton.clicked.connect(
            lambda: self.setVillageCityMode("village")
        )
        self.cityRadioButton.clicked.connect(lambda: self.setVillageCityMode("city"))

    def setAllControlsEnabled(self, state=True):
        self.openFilePushButton.setEnabled(state)
        self.saveAsPushButton.setEnabled(state)

        for ed in self.editables:
            ed.setEnabled(state)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi(os.path.join(RESOURCE_PATH, "ui", "studentfastreg.ui"), self)
        self.updateProgressCounter()

        self._editables = ()

        self.centralwidget.setContentsMargins(11, 11, 11, 11)
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(RESOURCE_PATH, "ui", "icons", "favicon.png"))
        )
        self.setWindowTitle(f"studentfastreg v{studentfastreg.__str_version__}")

        # region Initializing error window
        self.err_msg = QMessageBox()
        self.err_msg.setIcon(QMessageBox.Icon.Critical)
        self.err_msg.setWindowTitle("Ошибка")
        self.err_msg.setWindowIcon(
            QtGui.QIcon(
                os.path.join(RESOURCE_PATH, "ui", "icons", "exclamation-red.png")
            )
        )
        # endregion

        # region Check filled timer
        self.filled_timer = QtCore.QTimer()
        self.filled_timer.setInterval(1000)
        self.filled_timer.timeout.connect(self.updateProgressCounter)
        self.filled_timer.start()
        # endregion

        self.connectEvents()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F1:
            self.show_help()
        elif (
            e.key() == Qt.Key.Key_F5
            and e.modifiers() == Qt.KeyboardModifier.AltModifier
        ):
            self.setWindowTitle("I ❤️❤️❤️ you! :D")


def run_ui():
    if settings.config["forceWinDarkMode"] and platform.system() == "Windows":
        sys.argv += ["-platform", "windows:darkmode=2"]

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()

    window.show()
    app.exec()
