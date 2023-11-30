import logging
import logging.config
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("./.env", verbose=True)


BASE_DIR: Path = Path(
    os.environ.get(
        "SFR_BASE_DIR", os.path.join(os.path.expanduser("~"), ".studentfastreg")
    )
)

DEBUG: bool = os.environ.get("SFR_DEBUG", False) in ["t", True, "true"]

LOG_LVL: str = "DEBUG" if DEBUG else "INFO"

LOG_DIR: Path = Path(os.path.join(BASE_DIR, "logs"))

RESOURCE_PATH = Path(getattr(sys, "_MEIPASS", os.path.abspath(".")))

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
            "filename": LOG_DIR / "sfr.log",
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

BASE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.config.dictConfig(LOGGING)

logger = logging.getLogger(__name__)

logger.info(f"Base dir is {BASE_DIR}")
