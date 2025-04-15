from unittest.mock import MagicMock


def logger() -> MagicMock:
    """Create a mock logger."""
    logger = MagicMock()
    logger.red = MagicMock()
    logger.cyan = MagicMock()
    logger.yellow = MagicMock()
    logger.green = MagicMock()
    logger.blue = MagicMock()
    logger.magenta = MagicMock()
    return logger
