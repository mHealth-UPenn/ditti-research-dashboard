from install.local_providers.frontend_provider import FrontendProvider
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def frontend_provider() -> FrontendProvider:
    return FrontendProvider(logger=logger(), config=project_config_provider())
