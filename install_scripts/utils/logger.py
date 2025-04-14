class Logger:
    def __init__(self):
        self.color_codes = {
            "red": "\033[0;31m",
            "green": "\033[0;32m",
            "yellow": "\033[0;33m",
            "blue": "\033[0;34m",
            "magenta": "\033[0;35m",
            "cyan": "\033[0;36m",
            "reset": "\033[0m",
        }

    def __call__(self, text: str) -> None:
        print(text)

    def print_colored(self, text: str, color: str) -> None:
        print(f"{self.color_codes[color]}{text}{self.color_codes['reset']}")

    def red(self, text: str) -> None:
        self.print_colored(text, "red")

    def green(self, text: str) -> None:
        self.print_colored(text, "green")

    def yellow(self, text: str) -> None:
        self.print_colored(text, "yellow")

    def blue(self, text: str) -> None:
        self.print_colored(text, "blue")

    def magenta(self, text: str) -> None:
        self.print_colored(text, "magenta")

    def cyan(self, text: str) -> None:
        self.print_colored(text, "cyan")
