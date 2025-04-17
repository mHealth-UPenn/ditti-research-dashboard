from install_scripts.local_providers.frontend_provider import FrontendProvider
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider


def frontend_provider() -> FrontendProvider:
    return FrontendProvider(
        logger=logger(),
        config=project_config_provider()
    )
