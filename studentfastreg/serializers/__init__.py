from typing import Optional

from PyQt6 import QtWidgets


class SFRSerializer:
    STANDARD_CODE = "tregfnsgarqhgf"
    FILE_EXTENSION = ".plain"
    FILE_EXPLORER_ENTRY_DESC = "Plain"
    DIRECTIONS = ["serialize", "deserialize"]

    qt_window = None

    def __init__(self, qt_window: QtWidgets.QMainWindow) -> None:
        self.qt_window = qt_window

    def serialize(self, file_out: str, password: Optional[str] = None) -> None: ...

    def deserialize(self, file_out: str, password: Optional[str] = None) -> None: ...

    @staticmethod
    def get_file_explorer_entries(direction="both"):
        # FILE_EXTENSION = ".sfr"
        # FILE_EXPLORER_ENTRY_DESC = f"Файл полей данных"

        entries = []

        for c in SFRSerializer.__subclasses__():
            if direction != "both" and direction not in c.DIRECTIONS:
                continue

            entries.append(f"{c.FILE_EXPLORER_ENTRY_DESC} (*{c.FILE_EXTENSION})")

        return ";;".join(entries)

    @staticmethod
    def get_serializer_by_ext(ext: str):
        for c in SFRSerializer.__subclasses__():
            if c.FILE_EXTENSION == ext:
                return c

        return None
