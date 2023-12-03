import time

import py7zr
import toml
from PyQt6.QtWidgets import QDateEdit, QLineEdit, QRadioButton

import studentfastreg
from studentfastreg.serializers import FileBrokenException, SFRSerializer


class SFRPlainSerializer(SFRSerializer):
    FORMAT = "application/sfr"

    def serialize(self, file_out: str) -> None:
        meta_dict = {}
        meta_dict["format"] = self.FORMAT
        meta_dict["version"] = studentfastreg.__version__
        meta_dict["timestamp"] = time.ctime()

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
                data_dict["date"][widget.objectName()] = widget.text()
            elif type(widget) == QRadioButton:
                data_dict["radiobutton"][widget.objectName()] = widget.isChecked()

        data_str = toml.dumps(data_dict)

        with py7zr.SevenZipFile(file_out, "w") as archive:
            archive.writestr(meta_str, "manifest.toml")
            archive.writestr(data_str, "data.toml")

    def deserialize(self, file_in: str) -> None:
        config = {}
        config.read(file_in)

        if config["metainf"]["format"] != self.FORMAT:
            raise FileBrokenException(
                f"Wrong file format: {config['metainf']['format']}"
            )
