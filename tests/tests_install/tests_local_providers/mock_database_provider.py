from install.local_providers import DatabaseProvider
from tests.tests_install.tests_utils.mock_logger import logger
from tests.tests_install.tests_project_config.mock_project_config_provider import project_config_provider


def database_provider():
    database_provider = DatabaseProvider(
        logger=logger(),
        config=project_config_provider(),
    )
    return database_provider
