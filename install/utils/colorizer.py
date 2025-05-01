from typing import Any, ClassVar

from install.utils.types import Color


class Colorizer:
    """
    Utility for colorizing text in terminal output.

    Provides methods to apply ANSI color codes to strings for
    improved readability in command-line interfaces.
    """

    color_codes: ClassVar[dict[str, str]] = {
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
        """
        Apply color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.
        color : Color
            The color to apply.

        Returns
        -------
        str
            Text with color formatting applied.
        """
        # Replace any existing reset codes for nested colors
        text = str(text).replace(cls.color_codes["reset"], cls.color_codes[color])
        return f"{cls.color_codes[color]}{text}{cls.color_codes['reset']}"

    @classmethod
    def red(cls, text: Any) -> str:
        """
        Apply red color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with red color formatting applied.
        """
        return cls.colorize(text, "red")

    @classmethod
    def green(cls, text: Any) -> str:
        """
        Apply green color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with green color formatting applied.
        """
        return cls.colorize(text, "green")

    @classmethod
    def yellow(cls, text: Any) -> str:
        """
        Apply yellow color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with yellow color formatting applied.
        """
        return cls.colorize(text, "yellow")

    @classmethod
    def blue(cls, text: Any) -> str:
        """
        Apply blue color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with blue color formatting applied.
        """
        return cls.colorize(text, "blue")

    @classmethod
    def magenta(cls, text: Any) -> str:
        """
        Apply magenta color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with magenta color formatting applied.
        """
        return cls.colorize(text, "magenta")

    @classmethod
    def cyan(cls, text: Any) -> str:
        """
        Apply cyan color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with cyan color formatting applied.
        """
        return cls.colorize(text, "cyan")

    @classmethod
    def white(cls, text: Any) -> str:
        """
        Apply white color formatting to text.

        Parameters
        ----------
        text : Any
            The text to colorize.

        Returns
        -------
        str
            Text with white color formatting applied.
        """
        return cls.colorize(text, "white")
