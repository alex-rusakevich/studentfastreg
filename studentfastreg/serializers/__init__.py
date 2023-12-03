from shutil import ExecError

from PyQt6 import QtWidgets


class FileBrokenException(Exception):
    ...


class VersionNotSupported(Exception):
    ...


class SFRSerializer:
    STANDARD_CODE = "tregfnsgarqhgf"
    FILE_EXTENSION = ".plain"
    FILE_EXPLORER_ENTRY_DESC = f"Plain"
    qt_window = None

    def __init__(self, qt_window: QtWidgets.QMainWindow) -> None:
        self.qt_window = qt_window

    def serialize(self, file_out: str) -> None:
        ...

    def deserialize(self, file_out: str) -> None:
        ...

    @staticmethod
    def get_file_explorer_entries():
        # FILE_EXTENSION = ".sfr"
        # FILE_EXPLORER_ENTRY_DESC = f"Файл полей данных"

        entries = []

        for c in SFRSerializer.__subclasses__():
            entries.append(f"{c.FILE_EXPLORER_ENTRY_DESC} (*{c.FILE_EXTENSION})")

        return ";;".join(entries)

    @staticmethod
    def get_serializer_by_ext(ext: str):
        for c in SFRSerializer.__subclasses__():
            if c.FILE_EXTENSION == ext:
                return c

        return None
