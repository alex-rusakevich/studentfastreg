import datetime
import logging
from io import TextIOWrapper
from typing import Optional

import py7zr
import toml
from PyQt6.QtWidgets import QDateEdit, QLineEdit, QRadioButton

import studentfastreg
from studentfastreg.exceptions import *
from studentfastreg.serializers import *

logger = logging.getLogger(__name__)


class SFRPlainSerializer(SFRSerializer):
    FORMAT = "application/sfr"
    FILE_EXTENSION = ".sfr"
    FILE_EXPLORER_ENTRY_DESC = f"Файл полей данных"

    def serialize(self, file_out: str, password: Optional[str] = None) -> None:
        meta_dict = {}
        meta_dict["format"] = self.FORMAT
        meta_dict["version"] = studentfastreg.__version__
        meta_dict["timestamp"] = datetime.datetime.now()

        meta_str = toml.dumps(meta_dict)

        data_dict = {}
        data_dict["line"] = {}
        data_dict["date"] = {}
        data_dict["radiobutton"] = {}

        for widget in self.qt_window.editables:
            if (
                type(widget) == QLineEdit
                and widget.objectName() != "qt_spinbox_lineedit"
            ):
                data_dict["line"][widget.objectName()] = widget.text()
            elif type(widget) == QDateEdit:
                data_dict["date"][widget.objectName()] = widget.date().toPyDate()
            elif type(widget) == QRadioButton:
                data_dict["radiobutton"][widget.objectName()] = widget.isChecked()

        data_str = toml.dumps(data_dict)

        with py7zr.SevenZipFile(file_out, "w", password=password) as archive:
            archive.writestr(meta_str, "manifest.toml")
            archive.writestr(data_str, "data.toml")

    def deserialize(self, file_in: str, password: Optional[str] = None) -> None:
        with py7zr.SevenZipFile(file_in, "r", password=password) as archive:
            files = archive.readall()

        # logger.debug(files)

        meta_dict = toml.load(TextIOWrapper(files["manifest.toml"], encoding="utf8"))
        data_dict = toml.load(TextIOWrapper(files["data.toml"], encoding="utf8"))

        # region Check meta
        if meta_dict["format"] != self.FORMAT:
            raise FileBrokenException(
                f"File manifest's wrong format: {meta_dict['format']}"
            )

        if meta_dict["version"] > studentfastreg.__version__:
            raise VersionNotSupported(
                f"File's version is newer than the program's: \
{meta_dict['version']} > {studentfastreg.__version__}"
            )

        # endregion

        for k, v in data_dict["line"].items():
            if widget := self.qt_window.findChild(QLineEdit, k):
                widget.setText(v)

        for k, v in data_dict["date"].items():
            if widget := self.qt_window.findChild(QDateEdit, k):
                widget.setDate(v)

        for k, v in data_dict["radiobutton"].items():
            if widget := self.qt_window.findChild(QRadioButton, k):
                widget.setChecked(v)
