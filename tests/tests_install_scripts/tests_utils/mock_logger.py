import pytest

from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def logger_mock() -> MagicMock:
    """Create a mock logger."""
    logger = MagicMock()
    logger.red = MagicMock()
    logger.cyan = MagicMock()
    logger.yellow = MagicMock()
    logger.green = MagicMock()
    logger.blue = MagicMock()
    logger.magenta = MagicMock()
    return logger
