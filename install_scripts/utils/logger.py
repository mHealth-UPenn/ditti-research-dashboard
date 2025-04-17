import logging
from typing import Any
from install_scripts.utils.colorizer import Colorizer

logging.basicConfig(level=logging.INFO, format="%(message)s")


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __call__(self, text: Any) -> None:
        self.info(str(text))

    def debug(self, text: Any) -> None:
        self.logger.debug(Colorizer.blue(str(text)))

    def info(self, text: Any) -> None:
        self.logger.info(str(text))

    def warning(self, text: Any) -> None:
        self.logger.warning(Colorizer.yellow(str(text)))

    def error(self, text: Any) -> None:
        self.logger.error(Colorizer.red(str(text)))

    def critical(self, text: Any) -> None:
        self.logger.critical(Colorizer.red(str(text)))
