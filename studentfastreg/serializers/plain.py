import configparser
import time
from io import BufferedIOBase

from isort import file

import studentfastreg
from studentfastreg.serializers import FileBrokenException, SFRSerializer


class SFRPlainSerializer(SFRSerializer):
    FORMAT = "text/srf-plain"

    def serialize(self, file_out: BufferedIOBase) -> None:
        config = configparser.ConfigParser()

        config["metainf"] = {}
        config["metainf"]["format"] = self.FORMAT
        config["metainf"]["version"] = studentfastreg.__version__
        config["metainf"]["timestamp"] = time.ctime()

        config.write(file_out)

    def deserialize(self, file_in: BufferedIOBase) -> None:
        config = configparser.ConfigParser()
        config.read(file_in)

        if config["metainf"]["format"] != self.FORMAT:
            raise FileBrokenException(
                f"Wrong file format: {config['metainf']['format']}"
            )
