import base64
import datetime
import json
import logging
import os
from io import BytesIO
from typing import Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
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
        meta_dict["timestamp"] = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
        meta_dict["organization"] = ORGANIZATION

        if password is None:
            meta_dict["encrypted"] = False
        else:
            meta_dict["encrypted"] = True

        data_dict = {}

        for widget in self.qt_window.editables:
            if (
                type(widget) is QLineEdit
                and widget.objectName() != "qt_spinbox_lineedit"
            ):
                data_dict[widget.property("dataset_name")] = widget.text().strip()
            elif type(widget) is QDateEdit:
                data_dict[widget.property("dataset_name")] = (
                    widget.date().toPyDate().strftime("%d.%m.%Y")
                )
            elif type(widget) is QRadioButton:
                data_dict[widget.property("dataset_name")] = widget.isChecked()
            elif type(widget) is QSpinBox:
                data_dict[widget.property("dataset_name")] = widget.value()

        file_dict = {"meta": meta_dict}

        if password is None:
            file_dict["data"] = data_dict
        else:
            salt = os.urandom(16)

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=390000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

            fernet = Fernet(key)
            enc_data_bytes = fernet.encrypt(
                json.dumps(
                    data_dict, ensure_ascii=False, separators=(",", ":")
                ).encode()
            )

            data = BytesIO()
            data.write(salt)
            data.write(enc_data_bytes)
            data.seek(0)

            file_dict["data"] = base64.b64encode(data.read()).decode("ascii")

        with open(file_out, "w", encoding="utf8") as f:
            json.dump(file_dict, f, ensure_ascii=False, separators=(",", ":"))

    def _load_data(
        self, file_in: str, password: Optional[str] = None
    ) -> Union[dict, dict]:
        with open(file_in, "r", encoding="utf8") as f:
            file_dict = json.load(f)

        meta_dict = file_dict["meta"]
        data = file_dict["data"]

        if meta_dict["encrypted"]:
            data = base64.b64decode(data)

            salt = data[:16]
            data = data[16:]

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=390000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

            fernet = Fernet(key)

            dec_data_bytes = fernet.decrypt(data).decode()

            data_dict = json.loads(dec_data_bytes)
        else:
            data_dict = data

        return (meta_dict, data_dict)

    def deserialize(self, file_in: str, password: Optional[str] = None) -> None:
        meta_dict, data_dict = self._load_data(file_in, password)

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

        # if meta_dict["organization"] != ORGANIZATION:
        #     file_org = meta_dict["organization"]
        #     show_error(
        #         f'Невозможно открыть файл: он создан не для организации "{ORGANIZATION}", а для "{file_org}"'
        #     )
        #     return

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
                v: str

                datetime_from_val = datetime.datetime.strptime(v, "%d.%m.%Y")
                widget.setDate(datetime_from_val)
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
        return (
            json.load(open(file_in, "r", encoding="utf8"))["meta"]["encrypted"] is True
        )

    def is_password_correct(self, file_in: str, password: str):
        try:
            self._load_data(file_in, password)
        except Exception as e:
            logger.exception(e)
            return False
        else:
            return True
