import json
import logging
import logging.config
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("./.env", verbose=True)


PROGRAM_NAME = "studentfastreg"

HOME_DIR: Path = Path(
    os.environ.get(
        "SFR_HOME_DIR",
        os.path.join(os.path.expanduser("~"), ".alerus", ".studentfastreg"),
    )
)
HOME_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR: Path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# region Loading config
CONFIG_PATH = HOME_DIR / "config.json"
CONFIG_PATH.touch()

CONFIG_DEFAULTS = {"ui": {"openFileDirOnSave": True, "forceWinDarkMode": True}}

if not CONFIG_PATH.is_file() or len(CONFIG_PATH.read_text()) == 0:
    json.dump(CONFIG_DEFAULTS, open(CONFIG_PATH, "w", encoding="utf-8"), indent=4)

config = {}

for k, v in {**CONFIG_DEFAULTS, **json.load(CONFIG_PATH.open(encoding="utf8"))}.items():
    if type(v) is dict:
        config[k] = v

json.dump(config, open(CONFIG_PATH, "w", encoding="utf-8"), indent=4)
# endregion

DEBUG: bool = os.environ.get("SFR_DEBUG", False) in ["t", True, "true"]

LOG_LVL: str = "DEBUG" if DEBUG else "INFO"

LOG_DIR: Path = Path(os.path.join(HOME_DIR, "logs"))

RESOURCES_PATH = Path(getattr(sys, "_MEIPASS", BASE_DIR)) / "resources"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": LOG_LVL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "studentfastreg.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 2,
            "formatter": "standard",
            "encoding": "utf8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {"handlers": ["default", "console"], "level": LOG_LVL, "propagate": False},
        "invoke": {"handlers": ["default", "console"], "level": "WARNING"},
    },
}

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.config.dictConfig(LOGGING)

logger = logging.getLogger(__name__)

logger.info(f"Base dir is {HOME_DIR}")

if DEBUG:
    ORGANIZATION = "Тестовая организация"
    KMS_SERVER = "http://0.0.0.0:8888"
else:
    ORGANIZATION = (RESOURCES_PATH / "org.txt").read_text().strip()
    KMS_SERVER = "http://0.0.0.0:8888"
