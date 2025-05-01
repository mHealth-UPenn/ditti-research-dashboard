import logging
from typing import Any

from install.utils.colorizer import Colorizer

logging.basicConfig(level=logging.INFO, format="%(message)s")


class Logger:
    """
    Custom logger for installation process.

    Provides colored logging output and convenience methods
    for different log levels.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __call__(self, text: Any) -> None:
        """
        Log a message at INFO level.

        Parameters
        ----------
        text : Any
            The message to log.
        """
        self.info(str(text))

    def debug(self, text: Any) -> None:
        """
        Log a message at DEBUG level.

        Parameters
        ----------
        text : Any
            The message to log with blue color.
        """
        self.logger.debug(Colorizer.blue(str(text)))

    def info(self, text: Any) -> None:
        """
        Log a message at INFO level.

        Parameters
        ----------
        text : Any
            The message to log.
        """
        self.logger.info(str(text))

    def warning(self, text: Any) -> None:
        """
        Log a message at WARNING level.

        Parameters
        ----------
        text : Any
            The message to log with yellow color.
        """
        self.logger.warning(Colorizer.yellow(str(text)))

    def error(self, text: Any) -> None:
        """
        Log a message at ERROR level.

        Parameters
        ----------
        text : Any
            The message to log with red color.
        """
        self.logger.error(Colorizer.red(str(text)))

    def critical(self, text: Any) -> None:
        """
        Log a message at CRITICAL level.

        Parameters
        ----------
        text : Any
            The message to log with red color.
        """
        self.logger.critical(Colorizer.red(str(text)))
