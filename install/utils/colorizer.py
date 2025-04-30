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

from typing import Any

from install.utils.types import Color


class Colorizer:
    color_codes = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[0;33m",
        "blue": "\033[0;34m",
        "magenta": "\033[0;35m",
        "cyan": "\033[0;36m",
        "white": "\033[0;37m",
        "reset": "\033[0m",
    }

    @classmethod
    def colorize(cls, text: Any, color: Color) -> str:
        # Replace any existing reset codes for nested colors
        text = str(text).replace(
            cls.color_codes["reset"], cls.color_codes[color]
        )
        return f"{cls.color_codes[color]}{text}{cls.color_codes['reset']}"

    @classmethod
    def red(cls, text: Any) -> str:
        return cls.colorize(text, "red")

    @classmethod
    def green(cls, text: Any) -> str:
        return cls.colorize(text, "green")

    @classmethod
    def yellow(cls, text: Any) -> str:
        return cls.colorize(text, "yellow")

    @classmethod
    def blue(cls, text: Any) -> str:
        return cls.colorize(text, "blue")

    @classmethod
    def magenta(cls, text: Any) -> str:
        return cls.colorize(text, "magenta")

    @classmethod
    def cyan(cls, text: Any) -> str:
        return cls.colorize(text, "cyan")

    @classmethod
    def white(cls, text: Any) -> str:
        return cls.colorize(text, "white")
