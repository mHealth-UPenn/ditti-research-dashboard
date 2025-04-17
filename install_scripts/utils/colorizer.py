from typing import Any

from install_scripts.utils.types import Color


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
        text = str(text).replace(cls.color_codes["reset"], cls.color_codes[color])
        return f"{cls.color_codes[color]}{text}{cls.color_codes["reset"]}"

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
