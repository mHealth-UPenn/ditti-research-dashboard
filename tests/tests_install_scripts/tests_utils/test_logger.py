import pytest
from pytest import CaptureFixture

from install_scripts.utils.logger import Logger


@pytest.fixture
def logger_mock():
    return Logger()


def test_init(logger_mock: Logger):
    """Test that the Logger initializes with the correct color codes."""
    assert "red" in logger_mock.color_codes
    assert "green" in logger_mock.color_codes
    assert "yellow" in logger_mock.color_codes
    assert "blue" in logger_mock.color_codes
    assert "magenta" in logger_mock.color_codes
    assert "cyan" in logger_mock.color_codes
    assert "reset" in logger_mock.color_codes


def test_call(logger_mock: Logger, capsys: CaptureFixture):
    """Test the __call__ method."""
    test_message = "Test message"
    logger_mock(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()


def test_print_colored(logger_mock: Logger, capsys: CaptureFixture):
    """Test the print_colored method."""
    test_message = "Colored message"
    logger_mock.print_colored(test_message, "red")
    captured = capsys.readouterr()
    assert test_message in captured.out
    assert captured.out.startswith(logger_mock.color_codes["red"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_red(logger_mock: Logger, capsys: CaptureFixture):
    """Test the red method."""
    test_message = "Red message"
    logger_mock.red(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["red"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_green(logger_mock: Logger, capsys: CaptureFixture):
    """Test the green method."""
    test_message = "Green message"
    logger_mock.green(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["green"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_yellow(logger_mock: Logger, capsys: CaptureFixture):
    """Test the yellow method."""
    test_message = "Yellow message"
    logger_mock.yellow(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["yellow"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_blue(logger_mock: Logger, capsys: CaptureFixture):
    """Test the blue method."""
    test_message = "Blue message"
    logger_mock.blue(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["blue"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_magenta(logger_mock: Logger, capsys: CaptureFixture):
    """Test the magenta method."""
    test_message = "Magenta message"
    logger_mock.magenta(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["magenta"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])


def test_cyan(logger_mock: Logger, capsys: CaptureFixture):
    """Test the cyan method."""
    test_message = "Cyan message"
    logger_mock.cyan(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out.strip()
    assert captured.out.startswith(logger_mock.color_codes["cyan"])
    assert captured.out.strip().endswith(logger_mock.color_codes["reset"])
