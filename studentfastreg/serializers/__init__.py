from io import BufferedIOBase

from PyQt6 import QtWidgets


class FileBrokenException(Exception):
    ...


class SFRSerializer:
    qt_window = None

    def __init__(self, qt_window: QtWidgets.QMainWindow) -> None:
        self.qt_window = qt_window

    def serialize(self, file_out: str) -> None:
        ...

    def deserialize(self, file_out: str) -> None:
        ...
