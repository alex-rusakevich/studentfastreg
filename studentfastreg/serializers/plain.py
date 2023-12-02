import time
from io import BufferedIOBase

import toml
from PyQt6.QtWidgets import QDateEdit, QLineEdit, QRadioButton

import studentfastreg
from studentfastreg.serializers import FileBrokenException, SFRSerializer


class SFRPlainSerializer(SFRSerializer):
    FORMAT = "text/sfr-plain"

    def serialize(self, file_out: BufferedIOBase) -> None:
        config = {}

        config["meta"] = {}
        config["meta"]["format"] = self.FORMAT
        config["meta"]["version"] = studentfastreg.__version__
        config["meta"]["timestamp"] = time.ctime()

        config["values"] = {}
        config["values"]["line"] = {}
        config["values"]["date"] = {}
        config["values"]["radiobutton"] = {}

        for widget in self.qt_window.editables:
            if (
                type(widget) == QLineEdit
                and widget.objectName() != "qt_spinbox_lineedit"
            ):
                config["values"]["line"][widget.objectName()] = widget.text()
            elif type(widget) == QDateEdit:
                config["values"]["date"][widget.objectName()] = widget.text()
            elif type(widget) == QRadioButton:
                config["values"]["radiobutton"][
                    widget.objectName()
                ] = widget.isChecked()

        toml.dump(config, file_out)

    def deserialize(self, file_in: BufferedIOBase) -> None:
        config = {}
        config.read(file_in)

        if config["metainf"]["format"] != self.FORMAT:
            raise FileBrokenException(
                f"Wrong file format: {config['metainf']['format']}"
            )
