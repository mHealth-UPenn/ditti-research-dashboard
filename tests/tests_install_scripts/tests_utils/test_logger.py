import pytest
from pytest import CaptureFixture
from install_scripts.utils.logger import Logger


@pytest.fixture
def logger():
    return Logger()


class TestLogger:
    def test_init(self, logger: Logger):
        """Test that the Logger initializes with the correct color codes."""
        assert "red" in logger.color_codes
        assert "green" in logger.color_codes
        assert "yellow" in logger.color_codes
        assert "blue" in logger.color_codes
        assert "magenta" in logger.color_codes
        assert "cyan" in logger.color_codes
        assert "reset" in logger.color_codes


    def test_call(self, logger: Logger, capsys: CaptureFixture):
        """Test the __call__ method."""
        test_message = "Test message"
        logger(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()


    def test_print_colored(self, logger: Logger, capsys: CaptureFixture):
        """Test the print_colored method."""
        test_message = "Colored message"
        logger.print_colored(test_message, "red")
        captured = capsys.readouterr()
        assert test_message in captured.out
        assert captured.out.startswith(logger.color_codes["red"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_red(self, logger: Logger, capsys: CaptureFixture):
        """Test the red method."""
        test_message = "Red message"
        logger.red(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["red"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_green(self, logger: Logger, capsys: CaptureFixture):
        """Test the green method."""
        test_message = "Green message"
        logger.green(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["green"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_yellow(self, logger: Logger, capsys: CaptureFixture):
        """Test the yellow method."""
        test_message = "Yellow message"
        logger.yellow(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["yellow"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_blue(self, logger: Logger, capsys: CaptureFixture):
        """Test the blue method."""
        test_message = "Blue message"
        logger.blue(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["blue"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_magenta(self, logger: Logger, capsys: CaptureFixture):
        """Test the magenta method."""
        test_message = "Magenta message"
        logger.magenta(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["magenta"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])


    def test_cyan(self, logger: Logger, capsys: CaptureFixture):
        """Test the cyan method."""
        test_message = "Cyan message"
        logger.cyan(test_message)
        captured = capsys.readouterr()
        assert test_message in captured.out.strip()
        assert captured.out.startswith(logger.color_codes["cyan"])
        assert captured.out.strip().endswith(logger.color_codes["reset"])
