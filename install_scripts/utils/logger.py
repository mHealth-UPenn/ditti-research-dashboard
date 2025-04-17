import logging

from install_scripts.utils.colorizer import Colorizer

logging.basicConfig(level=logging.INFO, format="%(message)s")


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __call__(self, text: str) -> None:
        self.info(text)

    def debug(self, text: str) -> None:
        self.logger.debug(Colorizer.colorize(text, "blue"))

    def info(self, text: str) -> None:
        self.logger.info(text)

    def warning(self, text: str) -> None:
        self.logger.warning(Colorizer.colorize(text, "yellow"))

    def error(self, text: str) -> None:
        self.logger.error(Colorizer.colorize(text, "red"))

    def critical(self, text: str) -> None:
        self.logger.critical(Colorizer.colorize(text, "red"))
