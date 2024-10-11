import os

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QCheckBox, QLineEdit, QPushButton

from studentfastreg.settings import RESOURCES_PATH


class PasswordDialog(QtWidgets.QDialog):
    passwordLineEdit: QLineEdit
    showPasswordCheckBox: QCheckBox
    acceptPushButton: QPushButton

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.bindEvents()
        self.password = None

    def initUI(self):
        uic.loadUi(os.path.join(RESOURCES_PATH, "forms", "password_dialog.ui"), self)

    def on_acceptPushButton_clicked(self):
        self.password = self.passwordLineEdit.text()

        if self.password.strip() == "":
            self.password = None

        self.accept()

    def on_showPasswordCheckBox_clicked(self):
        if self.showPasswordCheckBox.isChecked():
            self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

    def bindEvents(self):
        self.acceptPushButton.clicked.connect(self.on_acceptPushButton_clicked)
        self.showPasswordCheckBox.clicked.connect(self.on_showPasswordCheckBox_clicked)
