# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
