import os

import PyQt6

dirname = os.path.dirname(PyQt6.__file__)
plugin_path = os.path.join(dirname, "plugins", "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

from studentfastreg.gui import run_ui  # noqa: E402

if __name__ == "__main__":
    run_ui()
