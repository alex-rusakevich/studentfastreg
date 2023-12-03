import os

import studentfastreg.settings

__author__ = "Alexander Rusakevich"

CURR_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

__str_version__ = (
    open(os.path.join(CURR_SCRIPT_DIR, "VERSION.txt"), "r", encoding="utf8")
    .read()
    .strip()
)

__version__ = list(int(i) for i in (__str_version__.split(".")))
