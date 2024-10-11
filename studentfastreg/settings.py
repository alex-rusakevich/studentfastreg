import logging
import logging.config
import os
import sys
from pathlib import Path

import toml
from dotenv import load_dotenv

load_dotenv("./.env", verbose=True)


HOME_DIR: Path = Path(
    os.environ.get(
        "SFR_HOME_DIR",
        os.path.join(os.path.expanduser("~"), ".alerus", ".studentfastreg"),
    )
)
HOME_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR: Path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# region Loading config
CONFIG_PATH = HOME_DIR / "config.toml"
CONFIG_PATH.touch()

CONFIG_DEFAULTS = {"ui": {"openFileDirOnSave": True, "forceWinDarkMode": True}}
CONFIG_PATH.touch()

config = {}

for k, v in {**CONFIG_DEFAULTS, **toml.load(CONFIG_PATH)}.items():
    if type(v) is dict:
        config[k] = v

toml.dump(config, open(CONFIG_PATH, "w", encoding="utf-8"))
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


ORGANIZATION = "Минский государственный лингвистический университет"
