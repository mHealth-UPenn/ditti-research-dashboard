# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from typing import Any

from install.utils.colorizer import Colorizer

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
