import sys
from logging import getLogger

from PyQt6.QtCore import QObject

logger = getLogger(__name__)


class TryWorker(QObject):
    def run(self):
        try:
            return self.worker_fn()
        except Exception:
            logger.exception("")
            sys.exit(-1)
