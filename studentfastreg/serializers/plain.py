import datetime
import logging
from io import TextIOWrapper
from typing import Optional

import py7zr
import py7zr.exceptions
import py7zr.py7zr
import toml
from PyQt6.QtWidgets import QDateEdit, QLineEdit, QRadioButton, QSpinBox

import studentfastreg
from studentfastreg.serializers import SFRSerializer
from studentfastreg.settings import ORGANIZATION
from studentfastreg.utils import show_error

logger = logging.getLogger(__name__)


class SFRPlainSerializer(SFRSerializer):
    FORMAT = "application/sfr"
    FILE_EXTENSION = ".sfr"
    FILE_EXPLORER_ENTRY_DESC = "Файл полей данных"

    DIRECTIONS = ["serialize", "deserialize"]

    def serialize(self, file_out: str, password: Optional[str] = None) -> None:
        meta_dict = {}
        meta_dict["format"] = self.FORMAT
        meta_dict["version"] = studentfastreg.__version__
        meta_dict["timestamp"] = datetime.datetime.now()
        meta_dict["organization"] = ORGANIZATION

        if password is None:
            meta_dict["encrypted"] = False
        else:
            meta_dict["encrypted"] = True

        meta_str = toml.dumps(meta_dict)

        data_dict = {}

        for widget in self.qt_window.editables:
            if (
                type(widget) is QLineEdit
                and widget.objectName() != "qt_spinbox_lineedit"
            ):
                data_dict[widget.property("dataset_name")] = widget.text().strip()
            elif type(widget) is QDateEdit:
                data_dict[widget.property("dataset_name")] = widget.date().toPyDate()
            elif type(widget) is QRadioButton:
                data_dict[widget.property("dataset_name")] = widget.isChecked()
            elif type(widget) is QSpinBox:
                data_dict[widget.property("dataset_name")] = widget.value()

        data_str = toml.dumps(data_dict)

        with py7zr.SevenZipFile(
            file_out,
            "w",
            password=password,
            header_encryption=True if password else False,
        ) as archive:
            archive.writestr(meta_str, "manifest.toml")
            archive.writestr(data_str, "data.toml")

    def deserialize(self, file_in: str, password: Optional[str] = None) -> None:
        with py7zr.SevenZipFile(
            file_in,
            "r",
            password=password,
            header_encryption=True if password else False,
        ) as archive:
            files = archive.readall()

        meta_dict = toml.load(TextIOWrapper(files["manifest.toml"], encoding="utf8"))
        data_dict = toml.load(TextIOWrapper(files["data.toml"], encoding="utf8"))

        # region Check meta
        if meta_dict["format"] != self.FORMAT:
            show_error(f"Неправильный формат файла манифеста: {meta_dict['format']}")
            return

        if meta_dict["version"] > studentfastreg.__version__:
            show_error(
                f"Версия файла выше, чем версия программы: \
{meta_dict['version']} > {studentfastreg.__version__}"
            )
            return

        if meta_dict["organization"] not in [ORGANIZATION, "any"]:
            file_org = meta_dict["organization"]
            show_error(
                f'Невозможно открыть файл: он создан не для организации "{ORGANIZATION}", а для "{file_org}"'
            )
            return

        # endregion

        for k, v in data_dict.items():
            widget = self.qt_window.find_widget_by_property_value("dataset_name", k)

            if (
                type(widget) is QLineEdit
                and widget.objectName() != "qt_spinbox_lineedit"
            ):
                widget: QLineEdit
                widget.setText(data_dict[k])
            elif type(widget) is QDateEdit:
                widget: QDateEdit
                widget.setDate(v)
            elif type(widget) is QRadioButton:
                widget: QRadioButton
                widget.setChecked(data_dict[k])
            elif type(widget) is QSpinBox:
                widget: QSpinBox
                widget.setValue(data_dict[k])
            else:
                show_error("Файл поврежден или создан для неподдерживаемой версии")
                return

    def does_file_has_password(self, file_in: str):
        try:
            with py7zr.SevenZipFile(
                file_in,
                "r",
                password=None,
            ) as archive:
                archive.readall()
        except py7zr.exceptions.PasswordRequired:
            return True
        else:
            return False

    def is_password_correct(self, file_in: str, password: str):
        try:
            with py7zr.SevenZipFile(
                file_in,
                "r",
                password=password,
            ) as archive:
                archive.readall()
        except Exception:
            return False
        else:
            return True
